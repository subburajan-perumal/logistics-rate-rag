"""Gate pipeline (docs/SPEC.md §6.6).

Phase 3 implements only the `gates_enabled=False` baseline-bypass branch
(D-13) — Gates 1-3 themselves ship in Phases 4-6. `run_gates` with
`gates_enabled=True` raises NotImplementedError until then, so the eval
CLI's `--mode gated` fails loudly rather than silently, same pattern as
the Pinecone backend stub.
"""

from __future__ import annotations

from typing import Any

from logistics_rate_rag.chain.candidate_chain import CandidateResult
from logistics_rate_rag.config import Ports, Settings
from logistics_rate_rag.schema.answer import RateAnswer, SourceRef, Verdict
from logistics_rate_rag.schema.candidate import RateCandidate
from logistics_rate_rag.schema.outcome import Outcome


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


def run_gates(
    candidate: RateCandidate | None, parsing_error: str | None, ctx: Any, settings: Settings
) -> Verdict:
    if settings.gates_enabled:
        raise NotImplementedError("Gates 1-3 ship in Phases 4-6; use gates_enabled=False for now")

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
