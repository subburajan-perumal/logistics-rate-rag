"""Gate pipeline (docs/SPEC.md §6.6).

Phase 3 built the `gates_enabled=False` baseline-bypass branch (D-13).
Phases 4-6 added the real `gates_enabled=True` path with all three
gates. This is the full pipeline now — no more short-circuiting to
ANSWER after a partial gate set.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from logistics_rate_rag.config import Ports, Settings
from logistics_rate_rag.guardrails.context import QuestionContext
from logistics_rate_rag.guardrails.gate1_schema import gate1
from logistics_rate_rag.guardrails.gate2_rules import gate2
from logistics_rate_rag.guardrails.gate3_confidence import gate3_confidence
from logistics_rate_rag.guardrails.gate3_grounding import gate3_grounding
from logistics_rate_rag.schema.answer import RateAnswer, SourceRef, Verdict
from logistics_rate_rag.schema.candidate import RateCandidate
from logistics_rate_rag.schema.outcome import Outcome

if TYPE_CHECKING:
    # Deferred: guardrails/ may not import chain/ at runtime (import-purity
    # rule, SPEC.md §1) — this is a type hint only, under
    # `from __future__ import annotations`.
    from logistics_rate_rag.chain.candidate_chain import CandidateResult


def normalize_ports(candidate: RateCandidate, ports: Ports) -> tuple[RateCandidate, str | None]:
    def norm(code: str | None) -> tuple[str | None, str | None]:
        if code is None:
            return None, None
        if code in ports.locode:
            return code, None
        if code.lower() in ports.city_lower:
            return ports.city_lower[code.lower()], None
        return code, "unknown_port"

    origin, reason1 = norm(candidate.origin)
    destination, reason2 = norm(candidate.destination)
    reason = reason1 or reason2
    if reason:
        return candidate, reason
    if origin != candidate.origin or destination != candidate.destination:
        candidate = candidate.model_copy(update={"origin": origin, "destination": destination})
    return candidate, None


def _run_gates_baseline(candidate: RateCandidate | None, parsing_error: str | None) -> Verdict:
    if candidate is None:
        return Verdict(
            outcome=Outcome.REJECT,
            reason="parse_error",
            gate_results=(),
            confidence_score=None,
            candidate=None,
            sources=(),
        )
    if candidate.answerable is False:
        return Verdict(
            outcome=Outcome.REFUSED,
            reason=None,
            gate_results=(),
            confidence_score=None,
            candidate=None,
            sources=(),
        )
    return candidate


def nearest(ctx: QuestionContext, n: int = 3) -> tuple[SourceRef, ...]:
    top = sorted(ctx.ranks_by_id.items(), key=lambda kv: kv[1])[:n]
    return tuple(
        SourceRef(
            source_doc=ctx.chunks_by_id[cid].source_doc, chunk_id=cid, span=None, role="nearest"
        )
        for cid, _ in top
    )


def _rate_ref(candidate: RateCandidate) -> SourceRef:
    return SourceRef(
        source_doc=candidate.source_doc,
        chunk_id=candidate.source_chunk_id,
        span=candidate.source_span,
        role="rate",
    )


def _policy_ref(candidate: RateCandidate, ctx: QuestionContext) -> SourceRef | None:
    if not candidate.policy_source_chunk_id:
        return None
    return SourceRef(
        source_doc=ctx.chunks_by_id[candidate.policy_source_chunk_id].source_doc,
        chunk_id=candidate.policy_source_chunk_id,
        span=None,
        role="policy",
    )


def run_gates(
    candidate: RateCandidate | None,
    parsing_error: str | None,
    ctx: QuestionContext | None,
    settings: Settings,
) -> Verdict:
    if settings.gates_enabled:
        if ctx is None:
            raise ValueError("gates_enabled=True requires a QuestionContext")
        g1, normalized = gate1(candidate, parsing_error, ctx, settings)
        if not g1.passed:
            return Verdict(
                outcome=Outcome.REJECT,
                reason=g1.reason,
                gate_results=(g1,),
                confidence_score=None,
                candidate=None,
                sources=nearest(ctx),
            )
        if g1.reason == "refused":
            return Verdict(
                outcome=Outcome.REFUSED,
                reason=None,
                gate_results=(g1,),
                confidence_score=None,
                candidate=None,
                sources=nearest(ctx),
            )
        g2 = gate2(normalized, ctx, settings)
        if not g2.passed:
            return Verdict(
                outcome=Outcome.REJECT,
                reason=g2.reason,
                gate_results=(g1, g2),
                confidence_score=None,
                candidate=None,
                sources=(_rate_ref(normalized), *nearest(ctx)),
            )

        g3a = gate3_grounding(normalized, ctx)
        if not g3a.passed:
            return Verdict(
                outcome=Outcome.REJECT,
                reason=g3a.reason,
                gate_results=(g1, g2, g3a),
                confidence_score=None,
                candidate=None,
                sources=(_rate_ref(normalized),),
            )

        g3b, score = gate3_confidence(normalized, ctx, settings)
        sources = (_rate_ref(normalized),)
        policy_ref = _policy_ref(normalized, ctx)
        if policy_ref is not None:
            sources = (*sources, policy_ref)
        if not g3b.passed:
            return Verdict(
                outcome=Outcome.NEEDS_REVIEW,
                reason=g3b.reason,
                gate_results=(g1, g2, g3a, g3b),
                confidence_score=score,
                candidate=None,
                sources=(*sources, *nearest(ctx)),
            )

        return Verdict(
            outcome=Outcome.ANSWER,
            reason=None,
            gate_results=(g1, g2, g3a, g3b),
            confidence_score=score,
            candidate=normalized,
            sources=sources,
        )

    baseline = _run_gates_baseline(candidate, parsing_error)
    if isinstance(baseline, Verdict):
        return baseline
    candidate = baseline  # answerable=True, still needs port normalisation

    normalized, port_reason = normalize_ports(candidate, settings.ports)
    if port_reason:
        return Verdict(
            outcome=Outcome.REJECT,
            reason=port_reason,
            gate_results=(),
            confidence_score=None,
            candidate=None,
            sources=(),
        )

    sources = (
        SourceRef(
            source_doc=normalized.source_doc or "",
            chunk_id=normalized.source_chunk_id or "",
            span=normalized.source_span,
            role="rate",
        ),
    )
    if normalized.policy_source_chunk_id:
        sources = (
            *sources,
            SourceRef(
                source_doc="", chunk_id=normalized.policy_source_chunk_id, span=None, role="policy"
            ),
        )

    return Verdict(
        outcome=Outcome.ANSWER,
        reason=None,
        gate_results=(),
        confidence_score=normalized.confidence,
        candidate=normalized,
        sources=sources,
    )


def to_answer(verdict: Verdict, result: CandidateResult, settings: Settings) -> RateAnswer:
    c = verdict.candidate if verdict.outcome == Outcome.ANSWER else None
    top = result.retrieved[0] if result.retrieved else None
    return RateAnswer(
        outcome=verdict.outcome,
        reason=verdict.reason,
        carrier=c.carrier if c else None,
        origin=c.origin if c else None,
        destination=c.destination if c else None,
        container_type=c.container_type if c else None,
        rate_value=c.rate_value if c else None,
        currency=c.currency if c else None,
        valid_from=c.valid_from if c else None,
        valid_to=c.valid_to if c else None,
        includes_surcharge=c.includes_surcharge if c else None,
        sources=verdict.sources,
        confidence_score=verdict.confidence_score,
        similarity_norm=top.similarity_norm if top else None,
        rank=top.rank if top else None,
        rerank_score=top.rerank_score if top else None,
        store=settings.vector_store,
        retrieval_mode=settings.retrieval_mode,
        reranker=settings.reranker,
        latency_ms=result.latency_ms,
        cache_hit=result.cache_hit,
        usage=result.usage,
    )
