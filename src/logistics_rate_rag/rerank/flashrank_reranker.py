"""Local cross-encoder reranker (docs/SPEC.md §4.8, D-28).

ONNX, no torch; the model downloads into `cache_dir` on first use and is
deterministic for a given input order.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from flashrank import Ranker, RerankRequest

from logistics_rate_rag.ingest.models import Chunk


class FlashRankReranker:
    name = "flashrank"

    def __init__(self, model_name: str, cache_dir: Path) -> None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        self._ranker = Ranker(model_name=model_name, cache_dir=str(cache_dir), log_level="WARNING")

    def rerank(
        self, query: str, chunks: Sequence[Chunk], top_n: int
    ) -> list[tuple[Chunk, float | None]]:
        if not chunks:
            return []
        by_id = {c.chunk_id: c for c in chunks}
        passages = [{"id": c.chunk_id, "text": c.text, "meta": {}} for c in chunks]
        results = self._ranker.rerank(RerankRequest(query=query, passages=passages))
        return [(by_id[r["id"]], float(r["score"])) for r in results[:top_n]]
