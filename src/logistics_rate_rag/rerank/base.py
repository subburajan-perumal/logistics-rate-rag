"""Reranker protocol (docs/SPEC.md §4.8, D-28)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from logistics_rate_rag.ingest.models import Chunk


@runtime_checkable
class Reranker(Protocol):
    name: str

    def rerank(
        self, query: str, chunks: Sequence[Chunk], top_n: int
    ) -> list[tuple[Chunk, float | None]]: ...
