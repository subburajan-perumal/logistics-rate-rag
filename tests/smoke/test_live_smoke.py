"""Live smoke tests (docs/SPEC.md §4.4, PLAN.md Phase 7). They call Gemini
and Pinecone, so they skip cleanly without keys and never run in CI
(`pytest tests/unit`). Run with `pytest tests/smoke -m smoke`."""

from __future__ import annotations

import uuid

import pytest

from logistics_rate_rag.config import load_settings
from logistics_rate_rag.ingest.chunking import chunk_corpus
from logistics_rate_rag.ingest.loaders import load_corpus

pytestmark = pytest.mark.smoke

SETTINGS = load_settings()


def _chunks():
    docs = load_corpus(SETTINGS.project_root / "data" / "corpus")
    chunks = chunk_corpus(docs, SETTINGS.retrieval, SETTINGS.manifest.corpus_version)
    meridian = next(c for c in chunks if c.metadata["carrier"] == "MERIDIAN")
    halcyon = next(c for c in chunks if c.metadata["carrier"] == "HALCYON")
    return [meridian, halcyon]


@pytest.fixture(scope="module")
def embedder():
    if not SETTINGS.google_api_key:
        pytest.skip("GOOGLE_API_KEY not set")
    from logistics_rate_rag.store.embeddings import GeminiEmbedder

    return GeminiEmbedder(SETTINGS.embedding_model, SETTINGS.embedding_dim, SETTINGS.google_api_key)


def _round_trip(backend, embedder):
    chunks = _chunks()
    backend.upsert(chunks, embedder.embed_documents([c.index_text for c in chunks]))
    assert backend.count() == 2
    assert set(backend.existing()) == {c.chunk_id for c in chunks}

    query = embedder.embed_query(chunks[1].text)
    hits = backend.query(query, 2, {"carrier": "HALCYON"})
    assert [h.chunk.chunk_id for h in hits] == [chunks[1].chunk_id]
    assert hits[0].chunk.text == chunks[1].text
    assert 0.5 < hits[0].similarity_norm <= 1.0


def test_chroma_half(embedder, tmp_path):
    from logistics_rate_rag.store.chroma_backend import ChromaBackend

    backend = ChromaBackend(tmp_path / ".chroma", "smoke", embedder)
    _round_trip(backend, embedder)


def test_pinecone_half_round_trips_and_cleans_up(embedder):
    if not SETTINGS.pinecone_api_key:
        pytest.skip("PINECONE_API_KEY not set")
    from logistics_rate_rag.store.pinecone_backend import PineconeBackend

    backend = PineconeBackend(
        SETTINGS.pinecone_api_key,
        SETTINGS.pinecone_index,
        f"smoke-{uuid.uuid4().hex[:8]}",
        SETTINGS.embedding_dim,
    )
    try:
        _round_trip(backend, embedder)
    finally:
        backend.reset()
    assert backend.count() == 0


def test_pinecone_reranker_live():
    if not SETTINGS.pinecone_api_key:
        pytest.skip("PINECONE_API_KEY not set")
    from logistics_rate_rag.rerank.pinecone_reranker import PineconeReranker

    chunks = _chunks()
    out = PineconeReranker(SETTINGS.pinecone_api_key).rerank(chunks[1].text, chunks, top_n=2)
    assert out[0][0].chunk_id == chunks[1].chunk_id
    assert all(0.0 <= s <= 1.0 for _, s in out)
