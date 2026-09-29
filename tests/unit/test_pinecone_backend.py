"""PineconeBackend against an in-memory fake client (no network, no key)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from logistics_rate_rag.errors import DimensionMismatch, MissingCredential, StoreError
from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.store.base import StoreBackend
from logistics_rate_rag.store.pinecone_backend import PineconeBackend, _similarity_norm_from_score


def _chunk(cid: str, carrier: str = "MERIDIAN") -> Chunk:
    return Chunk(
        chunk_id=cid,
        source_doc="meridian_tariff_2026_h2.pdf",
        doc_type="tariff_pdf",
        text=f"| INMAA Chennai | {cid} |",
        index_text=f"| INMAA Chennai | {cid} |",
        metadata={
            "chunk_id": cid,
            "source_doc": "meridian_tariff_2026_h2.pdf",
            "doc_type": "tariff_pdf",
            "carrier": carrier,
            "content_sha256": f"sha-{cid}",
            "page_numbers": "1,2",
        },
        content_sha256=f"sha-{cid}",
        page_numbers=(1, 2),
    )


class FakeIndex:
    """Just enough of pinecone's Index. `lag` hides writes for N stats calls."""

    def __init__(self, lag: int = 0) -> None:
        self.ns: dict[str, dict[str, dict]] = {}
        self.lag = lag
        self.upsert_batches = 0

    def upsert(self, *, vectors, namespace, show_progress=True):
        self.upsert_batches += 1
        for v in vectors:
            self.ns.setdefault(namespace, {})[v["id"]] = v

    def describe_index_stats(self):
        if self.lag:
            self.lag -= 1
            return SimpleNamespace(namespaces={})
        return SimpleNamespace(
            namespaces={n: SimpleNamespace(vector_count=len(v)) for n, v in self.ns.items() if v}
        )

    def list(self, *, namespace):
        ids = sorted(self.ns.get(namespace, {}))
        for start in range(0, len(ids), 2):  # small pages exercise paging
            yield ids[start : start + 2]

    def fetch(self, *, ids, namespace):
        store = self.ns.get(namespace, {})
        return SimpleNamespace(
            vectors={i: SimpleNamespace(metadata=store[i]["metadata"]) for i in ids if i in store}
        )

    def query(self, *, vector, top_k, namespace, filter, include_metadata):
        items = list(self.ns.get(namespace, {}).values())
        if filter:
            items = [v for v in items if v["metadata"]["carrier"] == filter["carrier"]["$eq"]]
        items.sort(key=lambda v: v["id"])
        matches = [
            {"id": v["id"], "score": 0.9 - 0.1 * i, "metadata": v["metadata"]}
            for i, v in enumerate(items[:top_k])
        ]
        return SimpleNamespace(matches=matches)

    def delete(self, *, ids=None, delete_all=False, namespace=""):
        if delete_all:
            self.ns.pop(namespace, None)
        else:
            for i in ids:
                self.ns.get(namespace, {}).pop(i, None)


class FakeClient:
    def __init__(self, exists: bool = True, dimension: int = 768, lag: int = 0) -> None:
        self.exists = exists
        self.dimension = dimension
        self.created = None
        self.index = FakeIndex(lag)
        self._ready_polls = 0

    def has_index(self, name):
        return self.exists

    def create_index(self, **kwargs):
        self.created = kwargs
        self.exists = True

    def describe_index(self, name):
        self._ready_polls += 1
        return {"dimension": self.dimension, "status": {"ready": self._ready_polls > 1}}

    def Index(self, name):  # mirrors pinecone's API
        return self.index


def _backend(client: FakeClient, ns: str = "corpus-v1") -> PineconeBackend:
    return PineconeBackend(None, "idx", ns, 768, client=client, sleep=lambda s: None)


def test_score_normalisation_matches_spec():
    assert _similarity_norm_from_score(1.0) == 1.0
    assert _similarity_norm_from_score(-1.0) == 0.0
    assert _similarity_norm_from_score(0.5) == 0.75


def test_missing_key_without_client_raises():
    with pytest.raises(MissingCredential):
        PineconeBackend(None, "idx", "corpus-v1", 768)


def test_creates_cosine_index_when_missing_and_waits_until_ready():
    client = FakeClient(exists=False)
    _backend(client)
    assert client.created["metric"] == "cosine"
    assert client.created["dimension"] == 768


def test_existing_index_with_wrong_dimension_is_rejected():
    with pytest.raises(DimensionMismatch):
        _backend(FakeClient(dimension=3072))


def test_satisfies_store_protocol():
    assert isinstance(_backend(FakeClient()), StoreBackend)


def test_upsert_then_existing_all_chunks_and_count_round_trip():
    client = FakeClient()
    b = _backend(client)
    chunks = [_chunk(f"m#{i:03d}") for i in range(5)]
    assert b.upsert(chunks, [[0.1] * 768 for _ in chunks]) == 5
    assert b.count() == 5
    assert b.existing() == {c.chunk_id: c.content_sha256 for c in chunks}
    rebuilt = b.all_chunks()
    assert [c.chunk_id for c in rebuilt] == [c.chunk_id for c in chunks]
    assert rebuilt[0].text == chunks[0].text
    assert rebuilt[0].page_numbers == (1, 2)
    assert "text" not in rebuilt[0].metadata


def test_upsert_batches_by_100():
    client = FakeClient()
    chunks = [_chunk(f"m#{i:03d}") for i in range(250)]
    _backend(client).upsert(chunks, [[0.1] * 768 for _ in chunks])
    assert client.index.upsert_batches == 3


def test_upsert_waits_for_eventual_consistency():
    client = FakeClient(lag=3)
    b = _backend(client)
    b.upsert([_chunk("m#000")], [[0.1] * 768])
    assert b.count() == 1


def test_upsert_times_out_when_writes_never_appear():
    client = FakeClient()
    b = _backend(client)
    client.index.describe_index_stats = lambda: SimpleNamespace(namespaces={})
    with pytest.raises(StoreError):
        b.upsert([_chunk("m#000")], [[0.1] * 768])


def test_query_translates_carrier_filter_and_normalises_scores():
    client = FakeClient()
    b = _backend(client)
    chunks = [_chunk("m#000"), _chunk("h#000", carrier="HALCYON")]
    b.upsert(chunks, [[0.1] * 768 for _ in chunks])
    hits = b.query([0.1] * 768, 6, {"carrier": "HALCYON"})
    assert [h.chunk.chunk_id for h in hits] == ["h#000"]
    assert hits[0].vector_rank == 1
    assert hits[0].similarity_norm == pytest.approx(0.95)


def test_delete_and_reset():
    client = FakeClient()
    b = _backend(client)
    chunks = [_chunk(f"m#{i:03d}") for i in range(3)]
    b.upsert(chunks, [[0.1] * 768 for _ in chunks])
    b.delete(["m#000"])
    assert b.count() == 2
    b.reset()
    assert b.count() == 0


def test_prune_drops_only_other_corpus_versions():
    client = FakeClient()
    for ns in ("corpus-v0", "corpus-v1", "smoke-abc"):
        _backend(client, ns).upsert([_chunk("m#000")], [[0.1] * 768])
    dropped = _backend(client, "corpus-v1").prune(keep="corpus-v1")
    assert dropped == ["corpus-v0"]
    assert set(client.index.ns) == {"corpus-v1", "smoke-abc"}
