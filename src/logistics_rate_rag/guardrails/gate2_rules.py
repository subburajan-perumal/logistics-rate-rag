"""Gate 2 — business rules (docs/SPEC.md §6.3)."""

from __future__ import annotations

from collections.abc import Callable

from logistics_rate_rag.config import Settings
from logistics_rate_rag.guardrails.context import QuestionContext
from logistics_rate_rag.schema.answer import GateResult
from logistics_rate_rag.schema.candidate import RateCandidate

RuleFn = Callable[[RateCandidate, QuestionContext, Settings, dict], GateResult]


def _pass() -> GateResult:
    return GateResult(passed=True, gate="gate2", reason=None, details={})


def _fail(rule_name: str, details: dict) -> GateResult:
    return GateResult(passed=False, gate="gate2", reason=f"rule:{rule_name}", details=details)


def carrier_known(
    candidate: RateCandidate, ctx: QuestionContext, settings: Settings, params: dict
) -> GateResult:
    if candidate.carrier in settings.carriers:
        return _pass()
    return _fail("carrier_known", {"carrier": candidate.carrier})


def rate_in_range(
    candidate: RateCandidate, ctx: QuestionContext, settings: Settings, params: dict
) -> GateResult:
    key = (
        f"{candidate.carrier}|{candidate.origin}|{candidate.destination}|{candidate.container_type}"
    )
    lane_range = settings.rate_ranges.get(key)
    if lane_range is None:
        return _fail("rate_in_range", {"key": key, "missing": True})
    tol = params.get("tolerance_pct", 0) / 100
    lo = lane_range.min * (1 - tol)
    hi = lane_range.max * (1 + tol)
    if lo <= candidate.rate_value <= hi:
        return _pass()
    return _fail(
        "rate_in_range",
        {"key": key, "min": lane_range.min, "max": lane_range.max, "value": candidate.rate_value},
    )


def currency_matches_source(
    candidate: RateCandidate, ctx: QuestionContext, settings: Settings, params: dict
) -> GateResult:
    chunk = ctx.chunks_by_id.get(candidate.source_chunk_id)
    source_currency = chunk.metadata.get("currency") if chunk else None
    if candidate.currency == source_currency:
        return _pass()
    return _fail(
        "currency_matches_source", {"claimed": candidate.currency, "source": source_currency}
    )


def dates_ordered(
    candidate: RateCandidate, ctx: QuestionContext, settings: Settings, params: dict
) -> GateResult:
    if candidate.valid_from < candidate.valid_to:
        return _pass()
    return _fail(
        "dates_ordered",
        {"valid_from": str(candidate.valid_from), "valid_to": str(candidate.valid_to)},
    )


def not_expired(
    candidate: RateCandidate, ctx: QuestionContext, settings: Settings, params: dict
) -> GateResult:
    if candidate.valid_from <= ctx.as_of <= candidate.valid_to:
        return _pass()
    return _fail(
        "not_expired",
        {
            "as_of": str(ctx.as_of),
            "valid_from": str(candidate.valid_from),
            "valid_to": str(candidate.valid_to),
        },
    )


def surcharge_consistent(
    candidate: RateCandidate, ctx: QuestionContext, settings: Settings, params: dict
) -> GateResult:
    carrier_cfg = settings.carriers.get(candidate.carrier)
    expected = carrier_cfg.baf_included if carrier_cfg else None
    if candidate.includes_surcharge != expected:
        return _fail(
            "surcharge_consistent", {"expected": expected, "got": candidate.includes_surcharge}
        )
    if ctx.mentions_surcharge:
        policy_chunk = (
            ctx.chunks_by_id.get(candidate.policy_source_chunk_id)
            if candidate.policy_source_chunk_id
            else None
        )
        if policy_chunk is None or policy_chunk.doc_type != "policy_md":
            return _fail("surcharge_consistent", {"policy_source": "missing"})
    return _pass()


RULES: dict[str, RuleFn] = {
    "carrier_known": carrier_known,
    "rate_in_range": rate_in_range,
    "currency_matches_source": currency_matches_source,
    "dates_ordered": dates_ordered,
    "not_expired": not_expired,
    "surcharge_consistent": surcharge_consistent,
}


def gate2(candidate: RateCandidate, ctx: QuestionContext, settings: Settings) -> GateResult:
    for rule_spec in settings.guardrails.rules:
        fn = RULES[rule_spec.name]
        result = fn(candidate, ctx, settings, rule_spec.params or {})
        if not result.passed:
            return result
    return _pass()
