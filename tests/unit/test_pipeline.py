"""Gate pipeline tests (docs/SPEC.md §6.6). No network."""

from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from logistics_rate_rag.chain.planner import QueryPlan
from logistics_rate_rag.chain.usage import Usage
from logistics_rate_rag.config import load_settings
from logistics_rate_rag.guardrails.context import build_question_context
from logistics_rate_rag.guardrails.pipeline import run_gates, to_answer
from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.schema.candidate import RateCandidate
from logistics_rate_rag.schema.outcome import Outcome


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
        # currency must match _answerable_candidate()'s USD so Gate 2's
        # currency_matches_source rule doesn't reject these fixtures.
        metadata={"currency": "USD"},
        content_sha256="sha",
    )


class _FakeRetrievedChunk:
    def __init__(self, chunk: Chunk, rank: int) -> None:
        self.chunk = chunk
        self.rank = rank
        self.similarity_norm = 0.9
        self.vector_rank = rank
        self.bm25_score = None
        self.lexical_rank = None
        self.rrf_score = None
        self.rerank_score = None


class _FakeCandidateResult:
    def __init__(self, candidate, parsing_error, retrieved, pinned, as_of):
        self.candidate = candidate
        self.parsing_error = parsing_error
        self.raw_text = ""
        self.retrieved = tuple(retrieved)
        self.pinned = tuple(pinned)
        self.plan = QueryPlan(
            question="q", filter=None, as_of=as_of, mentions_surcharge=False, carriers_mentioned=()
        )
        self.usage = Usage(
            model="m", input_tokens=1, output_tokens=1, thought_tokens=0, cached=False
        )
        self.latency_ms = 100
        self.cache_hit = False
        self.prompt_version = "1"
        self.model = "m"


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
        source_span="row",
        confidence=0.9,
    )
    base.update(overrides)
    return RateCandidate(**base)


def test_baseline_none_candidate_is_reject(settings):
    baseline_settings = replace(settings, gates_enabled=False)
    verdict = run_gates(None, "boom", None, baseline_settings)
    assert verdict.outcome == Outcome.REJECT
    assert verdict.reason == "parse_error"


def test_baseline_refused_candidate(settings):
    baseline_settings = replace(settings, gates_enabled=False)
    verdict = run_gates(RateCandidate(answerable=False), None, None, baseline_settings)
    assert verdict.outcome == Outcome.REFUSED


def test_baseline_answerable_becomes_answer(settings):
    baseline_settings = replace(settings, gates_enabled=False)
    candidate = _answerable_candidate()
    verdict = run_gates(candidate, None, None, baseline_settings)
    assert verdict.outcome == Outcome.ANSWER
    assert verdict.candidate.rate_value == 2224


def test_gated_requires_context(settings):
    gated_settings = replace(settings, gates_enabled=True)
    with pytest.raises(ValueError):
        run_gates(_answerable_candidate(), None, None, gated_settings)


def test_gated_reject_includes_nearest_sources(settings):
    gated_settings = replace(settings, gates_enabled=True)
    chunk = _chunk("meridian_tariff_2026_h2#000", "meridian_tariff_2026_h2.pdf")
    result = _FakeCandidateResult(
        None, "boom", [_FakeRetrievedChunk(chunk, 1)], [], date(2026, 9, 1)
    )
    ctx = build_question_context(result)
    verdict = run_gates(None, "boom", ctx, gated_settings)
    assert verdict.outcome == Outcome.REJECT
    assert verdict.sources[0].role == "nearest"


def test_gated_clean_candidate_answers(settings):
    gated_settings = replace(settings, gates_enabled=True)
    chunk = _chunk("meridian_tariff_2026_h2#000", "meridian_tariff_2026_h2.pdf")
    candidate = _answerable_candidate()
    result = _FakeCandidateResult(
        candidate, None, [_FakeRetrievedChunk(chunk, 1)], [], date(2026, 9, 1)
    )
    ctx = build_question_context(result)
    verdict = run_gates(candidate, None, ctx, gated_settings)
    assert verdict.outcome == Outcome.ANSWER
    assert verdict.sources[0].role == "rate"

    answer = to_answer(verdict, result, gated_settings)
    assert answer.outcome == Outcome.ANSWER
    assert answer.rate_value == 2224
    assert answer.similarity_norm == 0.9


def test_to_answer_only_fills_values_on_answer(settings):
    gated_settings = replace(settings, gates_enabled=True)
    result = _FakeCandidateResult(None, "boom", [], [], date(2026, 9, 1))
    ctx = build_question_context(result)
    verdict = run_gates(None, "boom", ctx, gated_settings)
    answer = to_answer(verdict, result, gated_settings)
    assert answer.outcome == Outcome.REJECT
    assert answer.rate_value is None
    assert answer.carrier is None
