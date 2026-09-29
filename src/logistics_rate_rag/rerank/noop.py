"""Pass-through reranker: the ablation baseline (D-31)."""

from __future__ import annotations

from collections.abc import Sequence

from logistics_rate_rag.ingest.models import Chunk


class NoopReranker:
    name = "none"

    def rerank(
        self, query: str, chunks: Sequence[Chunk], top_n: int
    ) -> list[tuple[Chunk, float | None]]:
        return [(c, None) for c in chunks[:top_n]]
