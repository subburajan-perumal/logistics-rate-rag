"""Gate 1 tests (docs/SPEC.md §6.2). No network."""

from __future__ import annotations

from datetime import date

import pytest

from logistics_rate_rag.config import load_settings
from logistics_rate_rag.guardrails.context import QuestionContext
from logistics_rate_rag.guardrails.gate1_schema import gate1
from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.schema.candidate import RateCandidate


@pytest.fixture
def settings():
    return load_settings()


def _chunk(chunk_id: str, source_doc: str) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        source_doc=source_doc,
        doc_type="tariff_pdf",
        text="text",
        index_text="text",
        metadata={},
        content_sha256="sha",
    )


def _ctx(retrieved_chunks: list[Chunk]) -> QuestionContext:
    chunks_by_id = {c.chunk_id: c for c in retrieved_chunks}
    return QuestionContext(
        as_of=date(2026, 9, 1),
        mentions_surcharge=False,
        retrieved_ids=frozenset(chunks_by_id),
        chunks_by_id=chunks_by_id,
        ranks_by_id={cid: i + 1 for i, cid in enumerate(chunks_by_id)},
        similarity_by_id={cid: 0.9 for cid in chunks_by_id},
        rerank_by_id={cid: None for cid in chunks_by_id},
    )


def _answerable_candidate(**overrides) -> RateCandidate:
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
        source_span="| INMAA Chennai | NLRTM Rotterdam | ... |",
        confidence=0.9,
    )
    base.update(overrides)
    return RateCandidate(**base)


def test_none_candidate_is_parse_error(settings):
    ctx = _ctx([])
    result, cand = gate1(None, "boom", ctx, settings)
    assert result.passed is False
    assert result.reason == "parse_error"
    assert result.details["parsing_error"] == "boom"
    assert cand is None


def test_clean_refusal_passes(settings):
    ctx = _ctx([])
    candidate = RateCandidate(answerable=False)
    result, cand = gate1(candidate, None, ctx, settings)
    assert result.passed is True
    assert result.reason == "refused"
    assert cand is not None


def test_refusal_with_leaked_fields_is_parse_error(settings):
    ctx = _ctx([])
    candidate = RateCandidate(answerable=False, rate_value=100)
    result, cand = gate1(candidate, None, ctx, settings)
    assert result.passed is False
    assert result.reason == "parse_error"
    assert "rate_value" in result.details["leaked"]
    assert cand is None


def test_answerable_missing_fields_is_parse_error(settings):
    ctx = _ctx([])
    candidate = RateCandidate(answerable=True, carrier="MERIDIAN")
    result, cand = gate1(candidate, None, ctx, settings)
    assert result.passed is False
    assert result.reason == "parse_error"
    assert "rate_value" in result.details["missing"]
    assert cand is None


def test_valid_candidate_passes():
    settings = load_settings()
    chunk = _chunk("meridian_tariff_2026_h2#000", "meridian_tariff_2026_h2.pdf")
    ctx = _ctx([chunk])
    candidate = _answerable_candidate()
    result, cand = gate1(candidate, None, ctx, settings)
    assert result.passed is True
    assert result.reason is None
    assert cand.origin == "INMAA"


def test_city_name_normalised_to_locode():
    settings = load_settings()
    chunk = _chunk("meridian_tariff_2026_h2#000", "meridian_tariff_2026_h2.pdf")
    ctx = _ctx([chunk])
    candidate = _answerable_candidate(origin="Chennai")
    result, cand = gate1(candidate, None, ctx, settings)
    assert result.passed is True
    assert cand.origin == "INMAA"


def test_unknown_port_rejected():
    settings = load_settings()
    chunk = _chunk("meridian_tariff_2026_h2#000", "meridian_tariff_2026_h2.pdf")
    ctx = _ctx([chunk])
    candidate = _answerable_candidate(origin="USNYC")
    result, cand = gate1(candidate, None, ctx, settings)
    assert result.passed is False
    assert result.reason == "unknown_port"
    assert cand is None


def test_source_chunk_id_not_retrieved_is_unknown_source():
    settings = load_settings()
    ctx = _ctx([])  # nothing retrieved
    candidate = _answerable_candidate()
    result, cand = gate1(candidate, None, ctx, settings)
    assert result.passed is False
    assert result.reason == "unknown_source"
    assert cand is None


def test_source_doc_mismatch_is_unknown_source():
    settings = load_settings()
    chunk = _chunk("meridian_tariff_2026_h2#000", "halcyon_tariff_2026_h2.csv")
    ctx = _ctx([chunk])
    candidate = _answerable_candidate(source_doc="meridian_tariff_2026_h2.pdf")
    result, _cand = gate1(candidate, None, ctx, settings)
    assert result.passed is False
    assert result.reason == "unknown_source"
    assert result.details["claimed"] == "meridian_tariff_2026_h2.pdf"
    assert result.details["actual"] == "halcyon_tariff_2026_h2.csv"


def test_policy_source_chunk_id_not_retrieved_is_unknown_source():
    settings = load_settings()
    chunk = _chunk("meridian_tariff_2026_h2#000", "meridian_tariff_2026_h2.pdf")
    ctx = _ctx([chunk])
    candidate = _answerable_candidate(policy_source_chunk_id="rate_policy_note_2026#001")
    result, _cand = gate1(candidate, None, ctx, settings)
    assert result.passed is False
    assert result.reason == "unknown_source"
    assert result.details["policy_source_chunk_id"] == "rate_policy_note_2026#001"
