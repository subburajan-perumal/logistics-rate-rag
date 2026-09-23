"""Chroma store backend (docs/SPEC.md §4.3)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.store.base import Hit


def _similarity_norm_from_distance(distance: float) -> float:
    return max(0.0, min(1.0, (2.0 - distance) / 2.0))


class ChromaBackend:
    name = "chroma"

    def __init__(self, persist_dir: Path, collection: str, embedder: Embeddings) -> None:
        self.collection = collection
        self._persist_dir = persist_dir
        self._embedder = embedder
        self._store = self._new_store()

    def _new_store(self) -> Chroma:
        return Chroma(
            collection_name=self.collection,
            embedding_function=self._embedder,
            persist_directory=str(self._persist_dir),
            collection_metadata={"hnsw:space": "cosine"},
        )

    def existing(self) -> dict[str, str]:
        result = self._store.get(include=["metadatas"])
        return {m["chunk_id"]: m["content_sha256"] for m in result["metadatas"]}

    def upsert(self, chunks: Sequence[Chunk], vectors: Sequence[Sequence[float]]) -> int:
        if not chunks:
            return 0
        self._store._collection.upsert(
            ids=[c.chunk_id for c in chunks],
            embeddings=list(vectors),
            documents=[c.text for c in chunks],
            metadatas=[c.metadata for c in chunks],
        )
        return len(chunks)

    def delete(self, chunk_ids: Sequence[str]) -> None:
        if chunk_ids:
            self._store._collection.delete(ids=list(chunk_ids))

    def query(self, vector: Sequence[float], k: int, filter: dict | None) -> list[Hit]:
        chroma_filter = {"carrier": {"$eq": filter["carrier"]}} if filter else None
        result = self._store._collection.query(
            query_embeddings=[list(vector)],
            n_results=k,
            where=chroma_filter,
            include=["documents", "metadatas", "distances"],
        )
        hits: list[Hit] = []
        docs = result["documents"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]
        for rank, (doc_text, metadata, distance) in enumerate(
            zip(docs, metadatas, distances, strict=True), start=1
        ):
            chunk = _chunk_from_row(doc_text, metadata)
            hits.append(
                Hit(
                    chunk=chunk,
                    similarity_norm=_similarity_norm_from_distance(distance),
                    vector_rank=rank,
                )
            )
        return hits

    def all_chunks(self) -> list[Chunk]:
        result = self._store.get(include=["documents", "metadatas"])
        chunks = [
            _chunk_from_row(doc_text, metadata)
            for doc_text, metadata in zip(result["documents"], result["metadatas"], strict=True)
        ]
        return sorted(chunks, key=lambda c: c.chunk_id)

    def count(self) -> int:
        return self._store._collection.count()

    def reset(self) -> None:
        self._store._client.delete_collection(self.collection)
        self._store = self._new_store()


def _chunk_from_row(doc_text: str, metadata: dict) -> Chunk:
    description = metadata.get("description", "")
    index_text = f"{description}\n{doc_text}" if description else doc_text
    page_numbers_raw = metadata.get("page_numbers", "")
    page_numbers = tuple(int(p) for p in page_numbers_raw.split(",") if p)
    return Chunk(
        chunk_id=metadata["chunk_id"],
        source_doc=metadata["source_doc"],
        doc_type=metadata["doc_type"],
        text=doc_text,
        index_text=index_text,
        metadata=dict(metadata),
        content_sha256=metadata["content_sha256"],
        page_numbers=page_numbers,
    )
