"""Gate 3a — grounding tests (docs/SPEC.md §6.4, D-42). No network.

Includes the boundary worked examples plus a real-corpus check that
motivated D-42 (the naive comma-exclusion boundary breaks grounding for
every CSV-sourced value).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from logistics_rate_rag.guardrails.context import QuestionContext
from logistics_rate_rag.guardrails.gate3_grounding import (
    contains_date,
    contains_number,
    gate3_grounding,
    number_variants,
    span_in_text,
)
from logistics_rate_rag.ingest.loaders import load_corpus
from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.schema.candidate import RateCandidate

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS_DIR = REPO_ROOT / "data" / "corpus"


# --- contains_number: worked examples from the boundary regex ---------------------


def test_number_found_in_pipe_table_row():
    assert contains_number("| INMAA Chennai | NLRTM Rotterdam | 1,240 | 2,180 |", 1240) is True


def test_number_not_found_as_suffix_of_larger_number():
    assert contains_number("11,240", 1240) is False


def test_number_not_found_with_trailing_digit():
    assert contains_number("12400", 1240) is False


def test_number_not_found_with_trailing_digit_after_comma_variant():
    assert contains_number("1,2400", 1240) is False


def test_number_not_found_before_decimal_point():
    assert contains_number("1240.5", 1240) is False


def test_smaller_value_not_falsely_grounded_as_suffix():
    # This is the exact reason the corpus reserves BAF=240 as a non-rate
    # value: 240 must not be considered "found" just because it's the
    # tail of the comma-grouped "1,240".
    assert contains_number("1,240", 240) is False


def test_csv_delimited_value_grounds_correctly():
    # D-42: a bare CSV field delimiter is not a thousands separator and
    # must not block a legitimate match.
    assert contains_number(",1332,EUR,", 1332) is True


def test_real_halcyon_csv_chunk_grounds():
    docs = load_corpus(CORPUS_DIR)
    halcyon = next(d for d in docs if d.source_doc == "halcyon_tariff_2026_h2.csv")
    row = halcyon.table_rows[0]
    value = int(row.split(",")[7])
    assert contains_number(halcyon.text, value) is True


def test_number_variants_deduplicated_under_1000():
    # f"{240:,}" == "240", same as the plain string — no separate variant.
    variants = number_variants(240)
    assert len(variants) == len(set(variants))
    assert "240" in variants


# --- contains_date ------------------------------------------------------------------


def test_date_found_iso():
    assert contains_date("Valid to: 2026-12-31", date(2026, 12, 31)) is True


def test_date_not_found_wrong_date():
    assert contains_date("Valid to: 2026-12-30", date(2026, 12, 31)) is False


def test_date_found_in_csv_context():
    assert contains_date(",2026-07-01,2026-12-31,", date(2026, 12, 31)) is True


# --- span_in_text --------------------------------------------------------------------


def test_span_matches_ignoring_whitespace_differences():
    assert span_in_text("| INMAA   Chennai |", "prefix | INMAA Chennai | suffix") is True


def test_span_not_found():
    assert span_in_text("not present anywhere", "some other text") is False


# --- gate3_grounding (full check, in order) -----------------------------------------


def _ctx_with_chunk(chunk: Chunk) -> QuestionContext:
    return QuestionContext(
        as_of=date(2026, 9, 1),
        mentions_surcharge=False,
        retrieved_ids=frozenset({chunk.chunk_id}),
        chunks_by_id={chunk.chunk_id: chunk},
        ranks_by_id={chunk.chunk_id: 1},
        similarity_by_id={chunk.chunk_id: 0.9},
        rerank_by_id={chunk.chunk_id: None},
    )


def _grounded_chunk() -> Chunk:
    text = "| INMAA Chennai | NLRTM Rotterdam | 1,240 | 2,180 | 2,310 | 24 | valid to 2026-12-31"
    return Chunk(
        chunk_id="c#000",
        source_doc="doc.pdf",
        doc_type="tariff_pdf",
        text=text,
        index_text=text,
        metadata={},
        content_sha256="sha",
    )


def _candidate(**overrides) -> RateCandidate:
    base = dict(
        answerable=True,
        carrier="MERIDIAN",
        origin="INMAA",
        destination="NLRTM",
        container_type="40HC",
        rate_value=2310,
        currency="USD",
        valid_from=date(2026, 7, 1),
        valid_to=date(2026, 12, 31),
        includes_surcharge=True,
        source_doc="doc.pdf",
        source_chunk_id="c#000",
        source_span="| INMAA Chennai | NLRTM Rotterdam | 1,240 | 2,180 | 2,310 | 24 |",
        confidence=0.9,
    )
    base.update(overrides)
    return RateCandidate(**base)


def test_gate3_grounding_passes_for_grounded_candidate():
    ctx = _ctx_with_chunk(_grounded_chunk())
    result = gate3_grounding(_candidate(), ctx)
    assert result.passed is True


def test_gate3_grounding_fails_ungrounded_rate_value():
    ctx = _ctx_with_chunk(_grounded_chunk())
    candidate = _candidate(rate_value=999999)
    result = gate3_grounding(candidate, ctx)
    assert result.passed is False
    assert result.reason == "ungrounded:rate_value"


def test_gate3_grounding_fails_ungrounded_valid_to():
    ctx = _ctx_with_chunk(_grounded_chunk())
    candidate = _candidate(valid_to=date(2099, 1, 1))
    result = gate3_grounding(candidate, ctx)
    assert result.passed is False
    assert result.reason == "ungrounded:valid_to"


def test_gate3_grounding_fails_ungrounded_source_span():
    ctx = _ctx_with_chunk(_grounded_chunk())
    candidate = _candidate(source_span="this text is nowhere in the chunk")
    result = gate3_grounding(candidate, ctx)
    assert result.passed is False
    assert result.reason == "ungrounded:source_span"
