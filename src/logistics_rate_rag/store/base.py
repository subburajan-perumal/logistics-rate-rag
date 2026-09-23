"""Store backend protocol (docs/SPEC.md §4.1)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from logistics_rate_rag.ingest.models import Chunk


@dataclass(frozen=True, slots=True)
class Hit:
    chunk: Chunk
    similarity_norm: float
    vector_rank: int


@runtime_checkable
class StoreBackend(Protocol):
    name: str
    collection: str

    def existing(self) -> dict[str, str]: ...

    def upsert(self, chunks: Sequence[Chunk], vectors: Sequence[Sequence[float]]) -> int: ...

    def delete(self, chunk_ids: Sequence[str]) -> None: ...

    def query(self, vector: Sequence[float], k: int, filter: dict | None) -> list[Hit]: ...

    def all_chunks(self) -> list[Chunk]: ...

    def count(self) -> int: ...

    def reset(self) -> None: ...
