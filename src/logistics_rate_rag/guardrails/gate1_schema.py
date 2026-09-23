"""Gate 1 — schema validation (docs/SPEC.md §6.2)."""

from __future__ import annotations

from logistics_rate_rag.config import Ports, Settings
from logistics_rate_rag.guardrails.context import QuestionContext
from logistics_rate_rag.schema.answer import GateResult
from logistics_rate_rag.schema.candidate import RateCandidate

VALUE_FIELDS = (
    "carrier",
    "origin",
    "destination",
    "container_type",
    "rate_value",
    "currency",
    "valid_from",
    "valid_to",
    "includes_surcharge",
    "source_span",
)
REQUIRED_WHEN_ANSWERABLE = (
    "carrier",
    "origin",
    "destination",
    "container_type",
    "rate_value",
    "currency",
    "valid_from",
    "valid_to",
    "includes_surcharge",
    "source_doc",
    "source_chunk_id",
    "source_span",
)


def _normalize_port(code: str | None, ports: Ports) -> tuple[str | None, str | None]:
    if code is None:
        return None, None
    if code in ports.locode:
        return code, None
    if code.lower() in ports.city_lower:
        return ports.city_lower[code.lower()], None
    return code, "unknown_port"


def gate1(
    candidate: RateCandidate | None,
    parsing_error: str | None,
    ctx: QuestionContext,
    settings: Settings,
) -> tuple[GateResult, RateCandidate | None]:
    if candidate is None:
        return (
            GateResult(
                passed=False,
                gate="gate1",
                reason="parse_error",
                details={"parsing_error": parsing_error},
            ),
            None,
        )

    if candidate.answerable is False:
        leaked = [f for f in VALUE_FIELDS if getattr(candidate, f) is not None]
        if leaked:
            return (
                GateResult(
                    passed=False, gate="gate1", reason="parse_error", details={"leaked": leaked}
                ),
                None,
            )
        return GateResult(passed=True, gate="gate1", reason="refused", details={}), candidate

    missing = [f for f in REQUIRED_WHEN_ANSWERABLE if getattr(candidate, f) is None]
    if missing:
        return (
            GateResult(
                passed=False, gate="gate1", reason="parse_error", details={"missing": missing}
            ),
            None,
        )

    origin, origin_reason = _normalize_port(candidate.origin, settings.ports)
    destination, dest_reason = _normalize_port(candidate.destination, settings.ports)
    if origin_reason or dest_reason:
        return (
            GateResult(
                passed=False,
                gate="gate1",
                reason="unknown_port",
                details={"origin": candidate.origin, "destination": candidate.destination},
            ),
            None,
        )
    if origin != candidate.origin or destination != candidate.destination:
        candidate = candidate.model_copy(update={"origin": origin, "destination": destination})

    if candidate.source_chunk_id not in ctx.retrieved_ids:
        return (
            GateResult(
                passed=False,
                gate="gate1",
                reason="unknown_source",
                details={"source_chunk_id": candidate.source_chunk_id},
            ),
            None,
        )
    if (
        candidate.policy_source_chunk_id is not None
        and candidate.policy_source_chunk_id not in ctx.retrieved_ids
    ):
        return (
            GateResult(
                passed=False,
                gate="gate1",
                reason="unknown_source",
                details={"policy_source_chunk_id": candidate.policy_source_chunk_id},
            ),
            None,
        )

    actual_doc = ctx.chunks_by_id[candidate.source_chunk_id].source_doc
    if candidate.source_doc != actual_doc:
        return (
            GateResult(
                passed=False,
                gate="gate1",
                reason="unknown_source",
                details={"claimed": candidate.source_doc, "actual": actual_doc},
            ),
            None,
        )

    return GateResult(passed=True, gate="gate1", reason=None, details={}), candidate
