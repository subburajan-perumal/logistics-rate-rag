"""Gate 1 — schema validation (docs/SPEC.md §6.2)."""

from __future__ import annotations

from logistics_rate_rag.config import Carrier, Ports, Settings, resolve_container_type
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


def _normalize_carrier(name: str | None, carriers: dict[str, Carrier]) -> str | None:
    """Exact configured alias or display name -> canonical key (PLAN.md D-45).
    Anything else is returned unchanged for Gate 2's `carrier_known` to judge."""
    if name is None or name in carriers:
        return name
    lowered = name.lower()
    for key, carrier in carriers.items():
        if lowered == carrier.display_name.lower() or lowered in carrier.aliases:
            return key
    return name


def resolve_lane_key(
    carrier: str | None,
    origin: str | None,
    destination: str | None,
    container_type: str | None,
    settings: Settings,
) -> str | None:
    """`CARRIER|ORIGIN|DESTINATION|CONTAINER` in canonical codes, resolved the
    way Gate 1 resolves a candidate; None when any part is missing or not in
    the registries. Used by the per-lane fabricated metric (PLAN.md D-50)."""
    o, o_err = _normalize_port(origin, settings.ports)
    d, d_err = _normalize_port(destination, settings.ports)
    c = _normalize_carrier(carrier, settings.carriers)
    ct = resolve_container_type(container_type, settings.equipment)
    if o_err or d_err or o is None or d is None or ct is None or c not in settings.carriers:
        return None
    return f"{c}|{o}|{d}|{ct}"


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
    container_type = resolve_container_type(candidate.container_type, settings.equipment)
    if container_type is None:
        return (
            GateResult(
                passed=False,
                gate="gate1",
                reason="unknown_container_type",
                details={"container_type": candidate.container_type},
            ),
            None,
        )

    carrier = _normalize_carrier(candidate.carrier, settings.carriers)
    resolved = (origin, destination, carrier, container_type)
    current = (candidate.origin, candidate.destination, candidate.carrier, candidate.container_type)
    if resolved != current:
        candidate = candidate.model_copy(
            update={
                "origin": origin,
                "destination": destination,
                "carrier": carrier,
                "container_type": container_type,
            }
        )

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
