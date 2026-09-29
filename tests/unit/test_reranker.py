"""Rerankers (docs/SPEC.md §4.8, D-28) and the hybrid retriever wiring."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest
from langchain_core.embeddings import Embeddings

from logistics_rate_rag.errors import MissingCredential
from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.rerank import build_reranker
from logistics_rate_rag.rerank.base import Reranker
from logistics_rate_rag.rerank.noop import NoopReranker
from logistics_rate_rag.store.base import Hit
from logistics_rate_rag.store.lexical import LexicalIndex
from logistics_rate_rag.store.retriever import RateRetriever

REPO_ROOT = Path(__file__).resolve().parents[2]


def _chunk(cid: str, text: str, carrier: str = "MERIDIAN") -> Chunk:
    return Chunk(
        chunk_id=cid,
        source_doc="doc",
        doc_type="tariff_md",
        text=text,
        index_text=text,
        metadata={"chunk_id": cid, "carrier": carrier},
        content_sha256=cid,
    )


class FakeReranker:
    """Scores by query-token overlap, so tests can predict the order."""

    name = "fake"

    def rerank(self, query: str, chunks: Sequence[Chunk], top_n: int):
        q = set(query.lower().split())
        scored = [(c, len(q & set(c.text.lower().split())) / max(len(q), 1)) for c in chunks]
        scored.sort(key=lambda cs: (-cs[1], cs[0].chunk_id))
        return scored[:top_n]


class FakeEmbedder(Embeddings):
    def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0] for _ in texts]


class FakeBackend:
    name = "fake"
    collection = "fake"

    def __init__(self, chunks: list[Chunk]) -> None:
        self._chunks = chunks

    def query(self, vector, k, filter):
        allowed = (filter["carrier"], "ALL") if filter else None
        hits = [c for c in self._chunks if allowed is None or c.metadata["carrier"] in allowed]
        return [Hit(c, 0.9 - 0.1 * i, i + 1) for i, c in enumerate(hits[:k])]

    def all_chunks(self):
        return list(self._chunks)

    def existing(self):
        return {}

    def upsert(self, chunks, vectors):
        return 0

    def delete(self, chunk_ids):
        return None

    def count(self):
        return len(self._chunks)

    def reset(self):
        return None


def test_noop_keeps_order_and_has_no_scores():
    chunks = [_chunk(f"c#{i}", "x") for i in range(4)]
    out = NoopReranker().rerank("q", chunks, top_n=2)
    assert [(c.chunk_id, s) for c, s in out] == [("c#0", None), ("c#1", None)]


def test_implementations_satisfy_protocol():
    assert isinstance(NoopReranker(), Reranker)
    assert isinstance(FakeReranker(), Reranker)


def test_build_reranker_pinecone_without_key_raises(tmp_path):
    with pytest.raises(MissingCredential):
        build_reranker("pinecone", model_name="m", cache_dir=tmp_path, pinecone_api_key=None)


def test_build_reranker_unknown_name(tmp_path):
    with pytest.raises(ValueError):
        build_reranker("bogus", model_name="m", cache_dir=tmp_path, pinecone_api_key=None)


def test_hybrid_retriever_pulls_in_lexical_only_chunk_and_reranks():
    dense_only = [_chunk(f"d#{i}", f"dense filler {i}") for i in range(3)]
    code_chunk = _chunk("h#000", "HAL-2026-H2-FCL halcyon usnyc rate")
    retriever = RateRetriever(
        backend=FakeBackend(dense_only),
        embedder=FakeEmbedder(),
        lexical=LexicalIndex([*dense_only, code_chunk]),
        reranker=FakeReranker(),
        k_retrieve=12,
        k_final=2,
    )
    out = retriever.retrieve("halcyon usnyc rate HAL-2026-H2-FCL", None)
    assert out[0].chunk.chunk_id == "h#000"
    assert out[0].vector_rank is None
    assert out[0].lexical_rank == 1
    assert out[0].rrf_score is not None
    assert out[0].rerank_score == 1.0
    # a dense-missing chunk takes the floor similarity (SPEC.md §4.6 step 4)
    assert out[0].similarity_norm == pytest.approx(0.7)
    assert [rc.rank for rc in out] == [1, 2]


def test_hybrid_retriever_applies_carrier_filter_to_lexical_leg():
    meridian = _chunk("m#000", "chennai rotterdam rate", carrier="MERIDIAN")
    halcyon = _chunk("h#000", "chennai rotterdam rate", carrier="HALCYON")
    policy = _chunk("p#000", "chennai rate policy", carrier="ALL")
    # unrelated filler keeps BM25's IDF positive for the query terms
    filler = [_chunk(f"f#{i}", f"unrelated text {i}", carrier="ALL") for i in range(6)]
    retriever = RateRetriever(
        backend=FakeBackend([meridian]),
        embedder=FakeEmbedder(),
        lexical=LexicalIndex([meridian, halcyon, policy, *filler]),
        reranker=NoopReranker(),
        k_retrieve=12,
        k_final=6,
    )
    out = retriever.retrieve("chennai rotterdam rate", {"carrier": "MERIDIAN"})
    assert {rc.chunk.chunk_id for rc in out} == {"m#000", "p#000"}


def test_dense_retriever_without_reranker_is_unchanged():
    chunks = [_chunk(f"d#{i}", "x") for i in range(8)]
    retriever = RateRetriever(
        backend=FakeBackend(chunks), embedder=FakeEmbedder(), k_retrieve=12, k_final=6
    )
    out = retriever.retrieve("q", None)
    assert [rc.chunk.chunk_id for rc in out] == [f"d#{i}" for i in range(6)]
    assert all(rc.rrf_score is None and rc.rerank_score is None for rc in out)


@pytest.mark.slow
def test_flashrank_is_deterministic():
    from logistics_rate_rag.rerank.flashrank_reranker import FlashRankReranker

    rr = FlashRankReranker("ms-marco-MiniLM-L-12-v2", REPO_ROOT / ".cache" / "flashrank")
    chunks = [
        _chunk("a", "Meridian 40HC Chennai to Rotterdam 2,224 USD valid to 2026-12-31"),
        _chunk("b", "Policy: bunker adjustment factor applies to all lanes"),
        _chunk("c", "Halcyon 20DRY Nhava Sheva to New York 1,332 EUR"),
    ]
    q = "Meridian 40HC Chennai Rotterdam rate"
    first = rr.rerank(q, chunks, top_n=3)
    second = rr.rerank(q, chunks, top_n=3)
    assert [(c.chunk_id, s) for c, s in first] == [(c.chunk_id, s) for c, s in second]
    assert first[0][0].chunk_id == "a"
    assert all(0.0 <= s <= 1.0 for _, s in first)
