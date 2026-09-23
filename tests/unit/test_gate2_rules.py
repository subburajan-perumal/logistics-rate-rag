"""Gate 2 tests (docs/SPEC.md §6.3). No network."""

from __future__ import annotations

from datetime import date

import pytest

from logistics_rate_rag.config import load_settings
from logistics_rate_rag.guardrails.context import QuestionContext
from logistics_rate_rag.guardrails.gate2_rules import (
    carrier_known,
    currency_matches_source,
    dates_ordered,
    gate2,
    not_expired,
    rate_in_range,
    surcharge_consistent,
)
from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.schema.candidate import RateCandidate


@pytest.fixture
def settings():
    return load_settings()


def _chunk(chunk_id: str, source_doc: str, doc_type: str = "tariff_pdf", **metadata) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        source_doc=source_doc,
        doc_type=doc_type,
        text="text",
        index_text="text",
        metadata=metadata,
        content_sha256="sha",
    )


def _ctx(
    chunks: list[Chunk], as_of: date = date(2026, 9, 1), mentions_surcharge: bool = False
) -> QuestionContext:
    chunks_by_id = {c.chunk_id: c for c in chunks}
    return QuestionContext(
        as_of=as_of,
        mentions_surcharge=mentions_surcharge,
        retrieved_ids=frozenset(chunks_by_id),
        chunks_by_id=chunks_by_id,
        ranks_by_id={cid: i + 1 for i, cid in enumerate(chunks_by_id)},
        similarity_by_id={cid: 0.9 for cid in chunks_by_id},
        rerank_by_id={cid: None for cid in chunks_by_id},
    )


def _candidate(**overrides) -> RateCandidate:
    base = dict(
        answerable=True,
        carrier="MERIDIAN",
        origin="INMAA",
        destination="NLRTM",
        container_type="40HC",
        rate_value=2224,
        currency="USD",
        valid_from=date(2026, 7, 1),
        valid_to=date(2026, 12, 31),
        includes_surcharge=True,
        source_doc="meridian_tariff_2026_h2.pdf",
        source_chunk_id="meridian_tariff_2026_h2#000",
        source_span="row",
        confidence=0.9,
    )
    base.update(overrides)
    return RateCandidate(**base)


# --- carrier_known -------------------------------------------------------------


def test_carrier_known_passes(settings):
    result = carrier_known(_candidate(), _ctx([]), settings, {})
    assert result.passed is True


def test_carrier_known_fails_for_unknown_carrier(settings):
    candidate = _candidate().model_copy(update={"carrier": "ZZZZZ"})
    result = carrier_known(candidate, _ctx([]), settings, {})
    assert result.passed is False
    assert result.reason == "rule:carrier_known"


# --- rate_in_range --------------------------------------------------------------


def test_rate_in_range_passes_for_real_lane(settings):
    # 2224 is the actual manifest value for MERIDIAN|INMAA|NLRTM|40HC.
    result = rate_in_range(_candidate(), _ctx([]), settings, {"tolerance_pct": 0})
    assert result.passed is True


def test_rate_in_range_fails_outside_range(settings):
    candidate = _candidate(rate_value=999999)
    result = rate_in_range(candidate, _ctx([]), settings, {"tolerance_pct": 0})
    assert result.passed is False
    assert result.reason == "rule:rate_in_range"
    assert result.details["value"] == 999999


def test_rate_in_range_missing_lane(settings):
    candidate = _candidate(origin="INVTZ", destination="NLRTM")
    result = rate_in_range(candidate, _ctx([]), settings, {"tolerance_pct": 0})
    assert result.passed is False
    assert result.details["missing"] is True


# --- currency_matches_source -----------------------------------------------------


def test_currency_matches_source_passes(settings):
    chunk = _chunk("meridian_tariff_2026_h2#000", "meridian_tariff_2026_h2.pdf", currency="USD")
    result = currency_matches_source(_candidate(), _ctx([chunk]), settings, {})
    assert result.passed is True


def test_currency_matches_source_fails_on_mismatch(settings):
    chunk = _chunk("meridian_tariff_2026_h2#000", "meridian_tariff_2026_h2.pdf", currency="EUR")
    result = currency_matches_source(_candidate(), _ctx([chunk]), settings, {})
    assert result.passed is False
    assert result.reason == "rule:currency_matches_source"
    assert result.details == {"claimed": "USD", "source": "EUR"}


# --- dates_ordered ---------------------------------------------------------------


def test_dates_ordered_passes(settings):
    result = dates_ordered(_candidate(), _ctx([]), settings, {})
    assert result.passed is True


def test_dates_ordered_fails_when_reversed(settings):
    candidate = _candidate(valid_from=date(2026, 12, 31), valid_to=date(2026, 7, 1))
    result = dates_ordered(candidate, _ctx([]), settings, {})
    assert result.passed is False
    assert result.reason == "rule:dates_ordered"


# --- not_expired -----------------------------------------------------------------


def test_not_expired_passes_when_as_of_inside_window(settings):
    ctx = _ctx([], as_of=date(2026, 9, 1))
    result = not_expired(_candidate(), ctx, settings, {})
    assert result.passed is True


def test_not_expired_fails_for_the_q2_trap(settings):
    # Meridian Q2 tariff: valid 2026-04-01..2026-06-30, superseded by H2.
    # An adversarial prompt confirming it as current (as_of 2026-09-01)
    # must fail this rule — this is the exact defect Phase 3's baseline
    # surfaced (A-002/A-003 leaked the superseded value verbatim).
    candidate = _candidate(valid_from=date(2026, 4, 1), valid_to=date(2026, 6, 30))
    ctx = _ctx([], as_of=date(2026, 9, 1))
    result = not_expired(candidate, ctx, settings, {})
    assert result.passed is False
    assert result.reason == "rule:not_expired"


# --- surcharge_consistent ---------------------------------------------------------


def test_surcharge_consistent_passes_for_meridian_baf_included(settings):
    result = surcharge_consistent(_candidate(), _ctx([]), settings, {})
    assert result.passed is True


def test_surcharge_consistent_fails_on_wrong_baf_flag():
    # This is G-015's real defect from the Phase 3 baseline: correct rate,
    # wrong includes_surcharge (conflated with the separate THC fact).
    settings = load_settings()
    candidate = _candidate(includes_surcharge=False)
    result = surcharge_consistent(candidate, _ctx([]), settings, {})
    assert result.passed is False
    assert result.reason == "rule:surcharge_consistent"
    assert result.details == {"expected": True, "got": False}


def test_surcharge_consistent_requires_policy_citation_when_asked():
    settings = load_settings()
    ctx = _ctx([], mentions_surcharge=True)
    candidate = _candidate(policy_source_chunk_id=None)
    result = surcharge_consistent(candidate, ctx, settings, {})
    assert result.passed is False
    assert result.details == {"policy_source": "missing"}


def test_surcharge_consistent_passes_with_valid_policy_citation():
    settings = load_settings()
    policy_chunk = _chunk(
        "rate_policy_note_2026#001", "rate_policy_note_2026.md", doc_type="policy_md"
    )
    ctx = _ctx([policy_chunk], mentions_surcharge=True)
    candidate = _candidate(policy_source_chunk_id="rate_policy_note_2026#001")
    result = surcharge_consistent(candidate, ctx, settings, {})
    assert result.passed is True


# --- gate2 (runs configured rules in order, first failure wins) ------------------


def test_gate2_passes_clean_candidate(settings):
    chunk = _chunk("meridian_tariff_2026_h2#000", "meridian_tariff_2026_h2.pdf", currency="USD")
    result = gate2(_candidate(), _ctx([chunk]), settings)
    assert result.passed is True


def test_gate2_first_failure_wins(settings):
    # carrier_known runs before rate_in_range per guardrails.yaml's order;
    # an unknown carrier should report carrier_known, not rate_in_range.
    candidate = _candidate(carrier="ZZZZZ", rate_value=999999)
    result = gate2(candidate, _ctx([]), settings)
    assert result.reason == "rule:carrier_known"


def test_gate2_rejects_the_q2_trap(settings):
    candidate = _candidate(valid_from=date(2026, 4, 1), valid_to=date(2026, 6, 30))
    chunk = _chunk("meridian_tariff_2026_h2#000", "meridian_tariff_2026_h2.pdf", currency="USD")
    ctx = _ctx([chunk], as_of=date(2026, 9, 1))
    result = gate2(candidate, ctx, settings)
    assert result.passed is False
    assert result.reason == "rule:not_expired"
