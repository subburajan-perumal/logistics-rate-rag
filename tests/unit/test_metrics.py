"""Metrics computation tests (docs/SPEC.md §7.3, docs/CORPUS.md §6.4). No network."""

from __future__ import annotations

from logistics_rate_rag.eval.metrics import (
    PerQuestion,
    compute_metrics,
    is_correct,
    is_fabricated,
    is_injection_leak,
    is_wrong_surfaced,
)

MANIFEST = {"rate_values": [2224, 1166, 3263]}


def _row(**overrides) -> PerQuestion:
    base = dict(
        id="G-001",
        set="golden",
        tag="lookup",
        expected_outcome="ANSWER",
        outcome="ANSWER",
        reason=None,
        rate_value=2224,
        currency="USD",
        valid_to="2026-12-31",
        includes_surcharge=True,
        source_chunk_id="meridian_tariff_2026_h2#000",
        policy_source_chunk_id=None,
        confidence_score=0.9,
        similarity_norm=0.9,
        rank=1,
        rerank_score=None,
        retrieved=("meridian_tariff_2026_h2#000",),
        latency_ms=1000,
        cache_hit=False,
        usage={"input_tokens": 100, "output_tokens": 10, "thought_tokens": 0},
        error=None,
        expected_rate_value=2224,
        expected_currency="USD",
        expected_valid_to="2026-12-31",
        expected_includes_surcharge=True,
        expected_policy_source_required=None,
        expected_must_not_contain=(),
    )
    base.update(overrides)
    return PerQuestion(**base)


def test_correct_answer_matches():
    assert is_correct(_row()) is True


def test_wrong_rate_value_not_correct():
    row = _row(rate_value=9999)
    assert is_correct(row) is False
    assert is_wrong_surfaced(row) is True


def test_cross_tag_requires_policy_source():
    row = _row(tag="cross", policy_source_chunk_id=None)
    assert is_correct(row) is False
    row_ok = _row(tag="cross", policy_source_chunk_id="rate_policy_note_2026#001")
    assert is_correct(row_ok) is True


def test_not_answer_expected_and_refused_is_correct():
    row = _row(
        expected_outcome="NOT_ANSWER",
        outcome="REFUSED",
        rate_value=None,
        expected_rate_value=None,
        expected_currency=None,
        expected_valid_to=None,
    )
    assert is_correct(row) is True


def test_not_answer_expected_but_surfaced_is_wrong():
    row = _row(expected_outcome="NOT_ANSWER", outcome="ANSWER")
    assert is_correct(row) is False
    assert is_wrong_surfaced(row) is True


def test_fabricated_value_not_in_manifest():
    row = _row(rate_value=42424242)
    assert is_fabricated(row, set(MANIFEST["rate_values"])) is True
    assert is_fabricated(_row(), set(MANIFEST["rate_values"])) is False


def test_injection_leak_detected():
    row = _row(rate_value=999, expected_must_not_contain=(999,))
    assert is_injection_leak(row) is True


def test_compute_metrics_aggregate():
    rows = [
        _row(id="G-001"),
        _row(id="G-025", expected_outcome="NOT_ANSWER", outcome="REFUSED", rate_value=None),
        _row(
            id="A-006",
            set="adversarial",
            expected_outcome="NOT_ANSWER",
            outcome="REJECT",
            reason="rule:not_expired",
            rate_value=None,
        ),
    ]
    metrics = compute_metrics(rows, MANIFEST, ("golden", "adversarial"))
    assert metrics["golden_accuracy"] == 1.0
    assert metrics["refusal_correctness"] == 1.0
    assert metrics["adversarial_rejection_rate"] == 1.0
    assert metrics["fabricated_values_surfaced"] == 0
    assert metrics["wrong_values_surfaced"] == 0
