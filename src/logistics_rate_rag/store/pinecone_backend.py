"""Pinecone store backend (docs/SPEC.md §4.4, D-24).

One serverless index (cosine, `embedding_dim`), one namespace per corpus
version (`corpus-v{N}`). Chunk text travels in metadata (`text`) so a
query result rebuilds the full `Chunk` without a second store.

`existing()`/`all_chunks()` page through `list()` and `fetch()` instead of
SPEC.md §4.4's zero-vector query (PLAN.md D-44): Pinecone rejects an
all-zero dense vector under cosine, and list+fetch has no 10k cap.
"""

from __future__ import annotations

import time
from collections.abc import Iterator, Sequence
from typing import Any

from logistics_rate_rag.errors import DimensionMismatch, MissingCredential, StoreError
from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.store.base import Hit

BATCH = 100
POLL_S = 2.0
READY_TIMEOUT_S = 120.0
VISIBLE_TIMEOUT_S = 60.0


def _similarity_norm_from_score(score: float) -> float:
    """Pinecone cosine score s in [-1, 1] -> [0, 1] (SPEC.md §4.7)."""
    return max(0.0, min(1.0, (score + 1.0) / 2.0))


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Pinecone responses are objects in some paths and dicts in others."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _chunk_from_metadata(metadata: dict) -> Chunk:
    meta = dict(metadata)
    text = meta.pop("text")
    description = meta.get("description", "")
    page_numbers_raw = meta.get("page_numbers", "")
    return Chunk(
        chunk_id=meta["chunk_id"],
        source_doc=meta["source_doc"],
        doc_type=meta["doc_type"],
        text=text,
        index_text=f"{description}\n{text}" if description else text,
        metadata=meta,
        content_sha256=meta["content_sha256"],
        page_numbers=tuple(int(p) for p in str(page_numbers_raw).split(",") if p),
    )


class PineconeBackend:
    name = "pinecone"

    def __init__(
        self,
        api_key: str | None,
        index_name: str,
        namespace: str,
        dim: int,
        *,
        client: Any = None,
        sleep=time.sleep,
    ) -> None:
        self.collection = namespace
        self._ns = namespace
        self._sleep = sleep
        if client is None:
            if not api_key:
                raise MissingCredential("PINECONE_API_KEY")
            from pinecone import Pinecone

            client = Pinecone(api_key=api_key)
        self._pc = client

        if not self._pc.has_index(index_name):
            from pinecone import ServerlessSpec

            self._pc.create_index(
                name=index_name,
                dimension=dim,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            self._wait(
                lambda: bool(_get(_get(self._pc.describe_index(index_name), "status"), "ready")),
                READY_TIMEOUT_S,
                f"pinecone index {index_name} did not become ready",
            )
        else:
            got = _get(self._pc.describe_index(index_name), "dimension")
            if got != dim:
                raise DimensionMismatch(dim, got)
        self._index = self._pc.Index(index_name)

    def _wait(self, done, timeout_s: float, message: str) -> None:
        waited = 0.0
        while not done():
            if waited >= timeout_s:
                raise StoreError(message)
            self._sleep(POLL_S)
            waited += POLL_S

    def _ids(self) -> Iterator[str]:
        for page in self._index.list(namespace=self._ns):
            # v10 yields lists of ids; tolerate an object with `.vectors` too
            if isinstance(page, list | tuple):
                yield from page
            else:
                for v in _get(page, "vectors", []) or []:
                    yield _get(v, "id")

    def _fetch_metadata(self) -> list[dict]:
        ids = list(self._ids())
        out: list[dict] = []
        for start in range(0, len(ids), BATCH):
            resp = self._index.fetch(ids=ids[start : start + BATCH], namespace=self._ns)
            for vec in (_get(resp, "vectors") or {}).values():
                out.append(dict(_get(vec, "metadata") or {}))
        return out

    def existing(self) -> dict[str, str]:
        return {m["chunk_id"]: m["content_sha256"] for m in self._fetch_metadata()}

    def upsert(self, chunks: Sequence[Chunk], vectors: Sequence[Sequence[float]]) -> int:
        if not chunks:
            return 0
        have = self.existing()
        expected = len(have) + sum(1 for c in chunks if c.chunk_id not in have)
        records = [
            {"id": c.chunk_id, "values": list(v), "metadata": {**c.metadata, "text": c.text}}
            for c, v in zip(chunks, vectors, strict=True)
        ]
        for start in range(0, len(records), BATCH):
            self._index.upsert(
                vectors=records[start : start + BATCH], namespace=self._ns, show_progress=False
            )
        # Pinecone is eventually consistent: wait until the writes are countable
        self._wait(
            lambda: self.count() >= expected,
            VISIBLE_TIMEOUT_S,
            "pinecone upsert did not become visible",
        )
        return len(chunks)

    def delete(self, chunk_ids: Sequence[str]) -> None:
        if chunk_ids:
            self._index.delete(ids=list(chunk_ids), namespace=self._ns)

    def query(self, vector: Sequence[float], k: int, filter: dict | None) -> list[Hit]:
        pc_filter = {"carrier": {"$eq": filter["carrier"]}} if filter else None
        resp = self._index.query(
            vector=list(vector),
            top_k=k,
            namespace=self._ns,
            filter=pc_filter,
            include_metadata=True,
        )
        return [
            Hit(
                chunk=_chunk_from_metadata(dict(_get(m, "metadata"))),
                similarity_norm=_similarity_norm_from_score(float(_get(m, "score"))),
                vector_rank=rank,
            )
            for rank, m in enumerate(_get(resp, "matches") or [], start=1)
        ]

    def all_chunks(self) -> list[Chunk]:
        return sorted(
            (_chunk_from_metadata(m) for m in self._fetch_metadata()), key=lambda c: c.chunk_id
        )

    def count(self) -> int:
        namespaces = _get(self._index.describe_index_stats(), "namespaces") or {}
        summary = namespaces.get(self._ns)
        return int(_get(summary, "vector_count", 0) or 0) if summary is not None else 0

    def reset(self) -> None:
        if self.count():
            self._index.delete(delete_all=True, namespace=self._ns)
            self._wait(lambda: self.count() == 0, VISIBLE_TIMEOUT_S, "pinecone reset timed out")

    def prune(self, keep: str) -> list[str]:
        """Delete every other `corpus-v*` namespace (`rate-rag index --prune`)."""
        namespaces = _get(self._index.describe_index_stats(), "namespaces") or {}
        dropped = sorted(n for n in namespaces if n.startswith("corpus-v") and n != keep)
        for n in dropped:
            self._index.delete(delete_all=True, namespace=n)
        return dropped
