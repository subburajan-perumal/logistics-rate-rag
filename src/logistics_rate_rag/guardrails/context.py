"""QuestionContext (docs/SPEC.md §6.1)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from logistics_rate_rag.ingest.models import Chunk

if TYPE_CHECKING:
    from logistics_rate_rag.chain.candidate_chain import CandidateResult


@dataclass(frozen=True, slots=True)
class QuestionContext:
    as_of: date
    mentions_surcharge: bool
    retrieved_ids: frozenset[str]
    chunks_by_id: Mapping[str, Chunk]
    ranks_by_id: Mapping[str, int]
    similarity_by_id: Mapping[str, float]
    rerank_by_id: Mapping[str, float | None]


def build_question_context(result: CandidateResult) -> QuestionContext:
    chunks_by_id: dict[str, Chunk] = {}
    ranks_by_id: dict[str, int] = {}
    similarity_by_id: dict[str, float] = {}
    rerank_by_id: dict[str, float | None] = {}
    for rc in result.retrieved:
        chunks_by_id[rc.chunk.chunk_id] = rc.chunk
        ranks_by_id[rc.chunk.chunk_id] = rc.rank
        similarity_by_id[rc.chunk.chunk_id] = rc.similarity_norm
        rerank_by_id[rc.chunk.chunk_id] = rc.rerank_score
    for c in result.pinned:
        chunks_by_id.setdefault(c.chunk_id, c)
    return QuestionContext(
        as_of=result.plan.as_of,
        mentions_surcharge=result.plan.mentions_surcharge,
        retrieved_ids=frozenset(chunks_by_id.keys()),
        chunks_by_id=chunks_by_id,
        ranks_by_id=ranks_by_id,
        similarity_by_id=similarity_by_id,
        rerank_by_id=rerank_by_id,
    )
