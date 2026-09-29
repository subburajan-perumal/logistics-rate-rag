"""Second-stage rerankers (docs/SPEC.md §4.8)."""

from __future__ import annotations

from pathlib import Path

from logistics_rate_rag.rerank.base import Reranker
from logistics_rate_rag.rerank.noop import NoopReranker


def build_reranker(
    name: str, *, model_name: str, cache_dir: Path, pinecone_api_key: str | None
) -> Reranker:
    if name == "none":
        return NoopReranker()
    if name == "flashrank":
        from logistics_rate_rag.rerank.flashrank_reranker import FlashRankReranker

        return FlashRankReranker(model_name, cache_dir)
    if name == "pinecone":
        from logistics_rate_rag.rerank.pinecone_reranker import PineconeReranker

        return PineconeReranker(pinecone_api_key)
    raise ValueError(f"unknown reranker: {name}")
