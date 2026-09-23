"""Gate 3b — confidence (docs/SPEC.md §6.5, docs/PLAN.md §12, D-14/D-30)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from logistics_rate_rag.config import Settings
from logistics_rate_rag.guardrails.context import QuestionContext
from logistics_rate_rag.schema.answer import GateResult
from logistics_rate_rag.schema.candidate import RateCandidate

if TYPE_CHECKING:
    from logistics_rate_rag.config import WeightsWithoutReranker, WeightsWithReranker


def confidence_score(
    model_conf: float,
    similarity_norm: float,
    rank: int,
    rerank_score: float | None,
    weights: WeightsWithReranker | WeightsWithoutReranker,
) -> float:
    score = (
        weights.w_model * model_conf + weights.w_sim * similarity_norm + weights.w_rank * (1 / rank)
    )
    if rerank_score is not None:
        score += weights.w_rerank * rerank_score
    return round(score, 6)


def gate3_confidence(
    candidate: RateCandidate, ctx: QuestionContext, settings: Settings
) -> tuple[GateResult, float]:
    chunk_id = candidate.source_chunk_id
    if chunk_id in ctx.ranks_by_id:
        rank = ctx.ranks_by_id[chunk_id]
        similarity_norm = ctx.similarity_by_id[chunk_id]
        rerank_score = ctx.rerank_by_id.get(chunk_id)
    else:
        # Pinned (non-retrieved) chunk, e.g. a policy citation.
        rank = settings.retrieval.k_final + 1
        similarity_norm = 0.5
        rerank_score = None

    mode = "with_reranker" if rerank_score is not None else "without_reranker"
    weights = getattr(settings.guardrails.confidence.weights, mode)
    score = confidence_score(candidate.confidence, similarity_norm, rank, rerank_score, weights)
    threshold = settings.guardrails.confidence.threshold[mode]

    if score >= threshold:
        return GateResult(
            passed=True, gate="gate3_confidence", reason=None, details={"score": score}
        ), score
    return (
        GateResult(
            passed=False,
            gate="gate3_confidence",
            reason="low_confidence",
            details={"score": score, "threshold": threshold},
        ),
        score,
    )
