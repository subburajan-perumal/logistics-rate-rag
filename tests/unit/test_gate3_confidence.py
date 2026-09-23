"""Gate 3b — confidence tests (docs/SPEC.md §6.5, docs/PLAN.md §12). No network."""

from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from logistics_rate_rag.config import load_settings
from logistics_rate_rag.guardrails.context import QuestionContext
from logistics_rate_rag.guardrails.gate3_confidence import confidence_score, gate3_confidence
from logistics_rate_rag.schema.candidate import RateCandidate


@pytest.fixture
def settings():
    return load_settings()


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
        source_chunk_id="c#000",
        source_span="row",
        confidence=0.9,
    )
    base.update(overrides)
    return RateCandidate(**base)


def _ctx(rank: int = 1, similarity: float = 0.9, rerank: float | None = None) -> QuestionContext:
    return QuestionContext(
        as_of=date(2026, 9, 1),
        mentions_surcharge=False,
        retrieved_ids=frozenset({"c#000"}),
        chunks_by_id={},
        ranks_by_id={"c#000": rank},
        similarity_by_id={"c#000": similarity},
        rerank_by_id={"c#000": rerank},
    )


def test_confidence_score_without_reranker(settings):
    weights = settings.guardrails.confidence.weights.without_reranker
    score = confidence_score(
        model_conf=0.9, similarity_norm=0.9, rank=1, rerank_score=None, weights=weights
    )
    expected = round(weights.w_model * 0.9 + weights.w_sim * 0.9 + weights.w_rank * 1.0, 6)
    assert score == expected


def test_confidence_score_with_reranker(settings):
    weights = settings.guardrails.confidence.weights.with_reranker
    score = confidence_score(
        model_conf=0.8, similarity_norm=0.7, rank=2, rerank_score=0.95, weights=weights
    )
    expected = round(
        weights.w_model * 0.8
        + weights.w_sim * 0.7
        + weights.w_rerank * 0.95
        + weights.w_rank * 0.5,
        6,
    )
    assert score == expected


def test_gate3_confidence_uses_pinned_fallback_for_untracked_chunk(settings):
    # source_chunk_id not in ranks_by_id at all -> pinned-chunk defaults
    # (rank = k_final + 1, similarity_norm = 0.5, rerank_score = None).
    ctx = QuestionContext(
        as_of=date(2026, 9, 1),
        mentions_surcharge=False,
        retrieved_ids=frozenset(),
        chunks_by_id={},
        ranks_by_id={},
        similarity_by_id={},
        rerank_by_id={},
    )
    candidate = _candidate()
    _result, score = gate3_confidence(candidate, ctx, settings)
    weights = settings.guardrails.confidence.weights.without_reranker
    expected = round(
        weights.w_model * 0.9
        + weights.w_sim * 0.5
        + weights.w_rank * (1 / (settings.retrieval.k_final + 1)),
        6,
    )
    assert score == expected


def test_gate3_confidence_passes_with_zero_threshold(settings):
    ctx = _ctx()
    result, _score = gate3_confidence(_candidate(), ctx, settings)
    assert result.passed is True  # untuned guardrails.yaml default is 0.0


def test_gate3_confidence_fails_when_threshold_raised(settings):
    raised = {**settings.guardrails.confidence.threshold, "without_reranker": 0.99}
    new_confidence = settings.guardrails.confidence.model_copy(update={"threshold": raised})
    new_guardrails = settings.guardrails.model_copy(update={"confidence": new_confidence})
    tuned_settings = replace(settings, guardrails=new_guardrails)

    ctx = _ctx()
    result, _score = gate3_confidence(_candidate(), ctx, tuned_settings)
    assert result.passed is False
    assert result.reason == "low_confidence"
    assert result.details["threshold"] == 0.99


def test_gate3_confidence_equality_at_threshold_passes(settings):
    ctx = _ctx()
    _, score = gate3_confidence(_candidate(), ctx, settings)
    exact = {**settings.guardrails.confidence.threshold, "without_reranker": score}
    new_confidence = settings.guardrails.confidence.model_copy(update={"threshold": exact})
    new_guardrails = settings.guardrails.model_copy(update={"confidence": new_confidence})
    exact_settings = replace(settings, guardrails=new_guardrails)

    result, _ = gate3_confidence(_candidate(), ctx, exact_settings)
    assert result.passed is True
