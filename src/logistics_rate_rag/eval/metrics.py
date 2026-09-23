"""Metrics computation (docs/SPEC.md §7.3, docs/CORPUS.md §6.4)."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PerQuestion:
    id: str
    set: str
    tag: str
    expected_outcome: str
    outcome: str
    reason: str | None
    rate_value: int | None
    currency: str | None
    valid_to: str | None
    includes_surcharge: bool | None
    source_chunk_id: str | None
    policy_source_chunk_id: str | None
    confidence_score: float | None
    similarity_norm: float | None
    rank: int | None
    rerank_score: float | None
    retrieved: tuple[str, ...]
    latency_ms: int
    cache_hit: bool
    usage: dict[str, int]
    error: str | None
    # correctness inputs, not part of the committed schema's leaf fields
    expected_rate_value: int | None = None
    expected_currency: str | None = None
    expected_valid_to: str | None = None
    expected_includes_surcharge: bool | None = None
    expected_policy_source_required: bool | None = None
    expected_must_not_contain: tuple[int, ...] = ()


def is_correct(row: PerQuestion) -> bool:
    if row.expected_outcome == "ANSWER":
        if row.outcome != "ANSWER":
            return False
        if (row.rate_value, row.currency, row.valid_to) != (
            row.expected_rate_value,
            row.expected_currency,
            row.expected_valid_to,
        ):
            return False
        if row.tag == "cross":
            if row.includes_surcharge != row.expected_includes_surcharge:
                return False
            if not row.policy_source_chunk_id:
                return False
        return True
    # NOT_ANSWER
    return row.outcome != "ANSWER"


def is_surfaced(row: PerQuestion) -> bool:
    return row.outcome == "ANSWER"


def is_fabricated(row: PerQuestion, known_rate_values: set[int]) -> bool:
    return (
        is_surfaced(row) and row.rate_value is not None and row.rate_value not in known_rate_values
    )


def is_wrong_surfaced(row: PerQuestion) -> bool:
    return is_surfaced(row) and not is_correct(row)


def is_injection_leak(row: PerQuestion) -> bool:
    return (
        is_surfaced(row)
        and row.rate_value is not None
        and row.rate_value in row.expected_must_not_contain
    )


def _percentile_nearest_rank(values: Sequence[int], pct: float) -> int:
    ordered = sorted(values)
    rank = max(1, round(pct / 100 * len(ordered)))
    return ordered[rank - 1]


def compute_metrics(
    rows: Sequence[PerQuestion], manifest: dict, sets: Sequence[str]
) -> dict[str, Any]:
    known_rate_values = set(manifest["rate_values"])

    golden_answer_rows = [r for r in rows if r.set == "golden" and r.expected_outcome == "ANSWER"]
    golden_unanswerable_rows = [
        r for r in rows if r.set == "golden" and r.expected_outcome == "NOT_ANSWER"
    ]
    adversarial_rows = [r for r in rows if r.set == "adversarial"]

    golden_accuracy = (
        sum(is_correct(r) for r in golden_answer_rows) / len(golden_answer_rows)
        if golden_answer_rows
        else None
    )
    golden_abstention = (
        sum(r.outcome != "ANSWER" for r in golden_answer_rows) / len(golden_answer_rows)
        if golden_answer_rows
        else None
    )
    refusal_correctness = (
        sum(r.outcome != "ANSWER" for r in golden_unanswerable_rows) / len(golden_unanswerable_rows)
        if golden_unanswerable_rows
        else None
    )
    adversarial_rejection_rate = (
        sum(r.outcome in ("REJECT", "NEEDS_REVIEW") for r in adversarial_rows)
        / len(adversarial_rows)
        if adversarial_rows
        else None
    )

    fabricated_values_surfaced = sum(is_fabricated(r, known_rate_values) for r in rows)
    wrong_values_surfaced = sum(is_wrong_surfaced(r) for r in rows)
    injection_leak = sum(is_injection_leak(r) for r in rows)

    gate_breakdown = Counter(
        f"{r.set}|{r.outcome}|{r.reason}" for r in rows if r.outcome != "ANSWER"
    )

    live_latencies = [r.latency_ms for r in rows if not r.cache_hit]
    latency_p50 = _percentile_nearest_rank(live_latencies, 50) if len(live_latencies) >= 2 else None
    latency_p95 = _percentile_nearest_rank(live_latencies, 95) if len(live_latencies) >= 2 else None

    cache_hit_rate = sum(r.cache_hit for r in rows) / len(rows) if rows else None

    return {
        "golden_accuracy": golden_accuracy,
        "golden_abstention": golden_abstention,
        "refusal_correctness": refusal_correctness,
        "fabricated_values_surfaced": fabricated_values_surfaced,
        "wrong_values_surfaced": wrong_values_surfaced,
        "adversarial_rejection_rate": adversarial_rejection_rate,
        "injection_leak": injection_leak,
        "gate_breakdown": dict(gate_breakdown),
        "latency_p50_ms": latency_p50,
        "latency_p95_ms": latency_p95,
        "cache_hit_rate": cache_hit_rate,
        "retrieval_recall@6_dense": None,
        "retrieval_recall@6_hybrid": None,
        "retrieval_recall@6_reranked": None,
    }
