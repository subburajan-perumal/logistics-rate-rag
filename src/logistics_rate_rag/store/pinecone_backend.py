"""Pinecone store backend (docs/SPEC.md §4.4).

Stub for Phase 2 — Pinecone isn't wired up until Phase 7. Every method
raises NotImplementedError so `VECTOR_STORE=pinecone` fails loudly rather
than silently, per docs/PLAN.md Phase 2's checklist ("Pinecone stub raises
NotImplemented").
"""

from __future__ import annotations

from collections.abc import Sequence

from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.store.base import Hit


class PineconeBackend:
    name = "pinecone"

    def __init__(self, api_key: str, index_name: str, namespace: str, dim: int) -> None:
        raise NotImplementedError("Pinecone backend ships in Phase 7")

    def existing(self) -> dict[str, str]:
        raise NotImplementedError

    def upsert(self, chunks: Sequence[Chunk], vectors: Sequence[Sequence[float]]) -> int:
        raise NotImplementedError

    def delete(self, chunk_ids: Sequence[str]) -> None:
        raise NotImplementedError

    def query(self, vector: Sequence[float], k: int, filter: dict | None) -> list[Hit]:
        raise NotImplementedError

    def all_chunks(self) -> list[Chunk]:
        raise NotImplementedError

    def count(self) -> int:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError
