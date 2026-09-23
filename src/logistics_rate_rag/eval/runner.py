"""Eval runner (docs/SPEC.md §7.2).

`mode="gated"` runs all three real gates (Phases 4-6). `retrieval_mode`
must still be `"dense"` and `reranker` must still be `"none"` — those
ship in Phase 2b/7. Pinecone and enrichment are still Phase 7/8.
"""

from __future__ import annotations

import dataclasses
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

from logistics_rate_rag.chain.cache import ResponseCache
from logistics_rate_rag.chain.candidate_chain import CandidateChain
from logistics_rate_rag.chain.ratelimit import RateLimiter
from logistics_rate_rag.chain.usage import Usage, UsageTotals, sum_usage
from logistics_rate_rag.config import Settings
from logistics_rate_rag.eval.metrics import PerQuestion, compute_metrics
from logistics_rate_rag.eval.questions import Question, load_question_set
from logistics_rate_rag.guardrails.context import build_question_context
from logistics_rate_rag.guardrails.pipeline import run_gates, to_answer
from logistics_rate_rag.ingest.chunking import chunk_corpus
from logistics_rate_rag.ingest.loaders import load_corpus
from logistics_rate_rag.schema.outcome import Outcome
from logistics_rate_rag.store.chroma_backend import ChromaBackend
from logistics_rate_rag.store.embeddings import GeminiEmbedder
from logistics_rate_rag.store.retriever import RateRetriever


@dataclass(frozen=True, slots=True)
class RunConfig:
    store: Literal["chroma", "pinecone"]
    mode: Literal["gated", "baseline"]
    retrieval_mode: Literal["hybrid", "dense"]
    reranker: Literal["flashrank", "pinecone", "none"]
    enriched: bool
    sets: tuple[Literal["golden", "adversarial"], ...]
    no_cache: bool


@dataclass(frozen=True, slots=True)
class RunResult:
    run_id: str
    created_at: str
    config: dict
    metrics: dict
    usage_totals: UsageTotals
    per_question: list[PerQuestion]


def _expected_kwargs(q: Question) -> dict:
    e = q.expected
    return {
        "expected_rate_value": e.rate_value,
        "expected_currency": e.currency,
        "expected_valid_to": e.valid_to.isoformat() if e.valid_to else None,
        "expected_includes_surcharge": e.includes_surcharge,
        "expected_policy_source_required": e.policy_source_required,
        "expected_must_not_contain": tuple(e.must_not_contain or ()),
    }


def _run_one_question(
    chain: CandidateChain, q: Question, set_name: str, settings: Settings
) -> PerQuestion:
    try:
        result = chain.run(q.question, q.as_of)
        ctx = build_question_context(result) if settings.gates_enabled else None
        verdict = run_gates(result.candidate, result.parsing_error, ctx, settings)
        answer = to_answer(verdict, result, settings)
        policy_chunk_id = next((s.chunk_id for s in answer.sources if s.role == "policy"), None)
        rate_chunk_id = next((s.chunk_id for s in answer.sources if s.role == "rate"), None)
        return PerQuestion(
            id=q.id,
            set=set_name,
            tag=q.tag,
            expected_outcome=q.expected.outcome,
            outcome=str(answer.outcome),
            reason=answer.reason,
            rate_value=answer.rate_value,
            currency=answer.currency,
            valid_to=answer.valid_to.isoformat() if answer.valid_to else None,
            includes_surcharge=answer.includes_surcharge,
            source_chunk_id=rate_chunk_id,
            policy_source_chunk_id=policy_chunk_id,
            confidence_score=answer.confidence_score,
            similarity_norm=answer.similarity_norm,
            rank=answer.rank,
            rerank_score=answer.rerank_score,
            retrieved=tuple(rc.chunk.chunk_id for rc in result.retrieved),
            latency_ms=answer.latency_ms,
            cache_hit=answer.cache_hit,
            usage={
                "input_tokens": result.usage.input_tokens,
                "output_tokens": result.usage.output_tokens,
                "thought_tokens": result.usage.thought_tokens,
            },
            error=None,
            **_expected_kwargs(q),
        ), result.usage
    except Exception as e:
        return PerQuestion(
            id=q.id,
            set=set_name,
            tag=q.tag,
            expected_outcome=q.expected.outcome,
            outcome="ERROR",
            reason=f"{type(e).__name__}: {e}",
            rate_value=None,
            currency=None,
            valid_to=None,
            includes_surcharge=None,
            source_chunk_id=None,
            policy_source_chunk_id=None,
            confidence_score=None,
            similarity_norm=None,
            rank=None,
            rerank_score=None,
            retrieved=(),
            latency_ms=0,
            cache_hit=False,
            usage={"input_tokens": 0, "output_tokens": 0, "thought_tokens": 0},
            error=f"{type(e).__name__}: {e}",
            **_expected_kwargs(q),
        ), None


def run_eval(settings: Settings, run_cfg: RunConfig) -> RunResult:
    if run_cfg.retrieval_mode == "hybrid":
        raise NotImplementedError("hybrid retrieval ships in Phase 2b")
    if run_cfg.reranker != "none":
        raise NotImplementedError("re-ranking ships in Phase 2b/7")
    if run_cfg.store != "chroma":
        raise NotImplementedError("Pinecone ships in Phase 7")
    if run_cfg.enriched:
        raise NotImplementedError("enrichment ships in Phase 8")

    # Reflect what this run actually does (dense/none/chroma, gates off for
    # baseline mode), not settings' env-sourced aspirational defaults —
    # to_answer's store/retrieval_mode/reranker fields must be honest.
    effective_settings = dataclasses.replace(
        settings,
        gates_enabled=(run_cfg.mode == "gated"),
        vector_store=run_cfg.store,
        retrieval_mode=run_cfg.retrieval_mode,
        reranker=run_cfg.reranker,
    )

    docs = load_corpus(settings.project_root / "data" / "corpus")
    chunks = chunk_corpus(docs, settings.retrieval, settings.manifest.corpus_version)
    embedder = GeminiEmbedder(
        settings.embedding_model, settings.embedding_dim, settings.google_api_key
    )
    backend = ChromaBackend(
        settings.project_root / ".chroma", f"rates_v{settings.manifest.corpus_version}", embedder
    )
    all_chunks = backend.all_chunks() or chunks
    retriever = RateRetriever(
        backend=backend,
        embedder=embedder,
        k_retrieve=settings.retrieval.k_retrieve,
        k_final=settings.retrieval.k_final,
    )
    cache = None if run_cfg.no_cache else ResponseCache(settings.llm_cache_dir)
    limiter = RateLimiter(settings.llm_min_interval_s)
    chain = CandidateChain(effective_settings, retriever, all_chunks, cache, limiter)

    rows: list[PerQuestion] = []
    usages: list[Usage] = []
    for set_name in run_cfg.sets:
        path = settings.project_root / "data" / "eval" / f"{set_name}.yaml"
        qs = load_question_set(path, settings.manifest.corpus_version)
        for q in sorted(qs.questions, key=lambda q: q.id):
            row, usage = _run_one_question(chain, q, set_name, effective_settings)
            rows.append(row)
            if usage is not None:
                usages.append(usage)

    metrics = compute_metrics(rows, settings.manifest.model_dump(mode="json"), run_cfg.sets)
    usage_totals = sum_usage(usages)

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    run_id = f"{ts}-{run_cfg.store}-{run_cfg.retrieval_mode}-{run_cfg.reranker}-{run_cfg.mode}"
    config = {
        "chat_model": settings.chat_model,
        "thinking_level": settings.llm_thinking_level,
        "seed": settings.llm_seed,
        "embedding_model": settings.embedding_model,
        "dimension": settings.embedding_dim,
        "prompt_version": "1",
        "corpus_version": settings.manifest.corpus_version,
        "as_of_default": settings.as_of_default.isoformat(),
        "store": run_cfg.store,
        "retrieval": run_cfg.retrieval_mode,
        "reranker": run_cfg.reranker,
        "enriched": run_cfg.enriched,
        "k_retrieve": settings.retrieval.k_retrieve,
        "k_final": settings.retrieval.k_final,
        "rrf_k": settings.retrieval.rrf_k,
        "gates": []
        if run_cfg.mode == "baseline"
        else ["schema", "rules", "grounding", "confidence"],
        "sets": list(run_cfg.sets),
    }

    return RunResult(
        run_id=run_id,
        created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        config=config,
        metrics=metrics,
        usage_totals=usage_totals,
        per_question=rows,
    )


@dataclass(frozen=True, slots=True)
class TuneResult:
    mode_key: str
    threshold: float
    incorrect_scores: list[float]
    correct_scores: list[float]
    run_id: str


def _is_golden_correct(candidate, q: Question) -> bool:
    e = q.expected
    if (candidate.rate_value, candidate.currency, candidate.valid_to) != (
        e.rate_value,
        e.currency,
        e.valid_to,
    ):
        return False
    if q.tag == "cross":
        if candidate.includes_surcharge != e.includes_surcharge:
            return False
        if not candidate.policy_source_chunk_id:
            return False
    return True


def _percentile_low(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    rank = max(1, round(pct / 100 * len(ordered)))
    return ordered[rank - 1]


def _update_guardrails_yaml(
    project_root: Path, mode_key: str, threshold: float, run_id: str
) -> None:
    """The only code path that writes to config/ (SPEC.md §7.4)."""
    path = project_root / "config" / "guardrails.yaml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    raw["confidence"]["threshold"][mode_key] = threshold
    raw["confidence"]["tuned_on"][mode_key] = run_id
    path.write_text(
        yaml.safe_dump(raw, sort_keys=False, default_flow_style=False), encoding="utf-8"
    )


def tune_threshold(settings: Settings, store: str, mode_key: str) -> TuneResult:
    """docs/PLAN.md §12 tuning procedure. Runs the golden set with Gates
    1-3a on and the confidence gate off (threshold 0), then sets the
    threshold from the observed score distribution."""
    if mode_key != "without_reranker":
        raise NotImplementedError("with_reranker tuning ships once Phase 2b/7 build the reranker")
    if store != "chroma":
        raise NotImplementedError("Pinecone ships in Phase 7")

    zeroed_threshold = {**settings.guardrails.confidence.threshold, mode_key: 0.0}
    zeroed_confidence = settings.guardrails.confidence.model_copy(
        update={"threshold": zeroed_threshold}
    )
    zeroed_guardrails = settings.guardrails.model_copy(update={"confidence": zeroed_confidence})
    tuning_settings = dataclasses.replace(
        settings,
        guardrails=zeroed_guardrails,
        gates_enabled=True,
        vector_store=store,
        retrieval_mode="dense",
        reranker="none",
    )

    docs = load_corpus(settings.project_root / "data" / "corpus")
    chunks = chunk_corpus(docs, settings.retrieval, settings.manifest.corpus_version)
    embedder = GeminiEmbedder(
        settings.embedding_model, settings.embedding_dim, settings.google_api_key
    )
    backend = ChromaBackend(
        settings.project_root / ".chroma", f"rates_v{settings.manifest.corpus_version}", embedder
    )
    all_chunks = backend.all_chunks() or chunks
    retriever = RateRetriever(
        backend=backend,
        embedder=embedder,
        k_retrieve=settings.retrieval.k_retrieve,
        k_final=settings.retrieval.k_final,
    )
    cache = ResponseCache(settings.llm_cache_dir)
    limiter = RateLimiter(settings.llm_min_interval_s)
    chain = CandidateChain(tuning_settings, retriever, all_chunks, cache, limiter)

    golden_path = settings.project_root / "data" / "eval" / "golden.yaml"
    qs = load_question_set(golden_path, settings.manifest.corpus_version)

    correct_scores: list[float] = []
    incorrect_scores: list[float] = []
    for q in sorted(qs.questions, key=lambda q: q.id):
        result = chain.run(q.question, q.as_of)
        ctx = build_question_context(result)
        verdict = run_gates(result.candidate, result.parsing_error, ctx, tuning_settings)
        if verdict.outcome != Outcome.ANSWER:
            continue
        score = verdict.confidence_score
        if _is_golden_correct(verdict.candidate, q):
            correct_scores.append(score)
        else:
            incorrect_scores.append(score)

    if incorrect_scores:
        threshold = round(max(incorrect_scores) + 0.01, 6)
    else:
        p5 = _percentile_low(correct_scores, 5) if correct_scores else 0.50
        threshold = round(max(0.50, p5 - 0.01), 6)

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    run_id = f"{ts}-{store}-{mode_key}-tuning"

    results_dir = settings.project_root / "eval" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    tuning_path = results_dir / f"{run_id}.json"
    tuning_path.write_text(
        json.dumps(
            {
                "mode_key": mode_key,
                "threshold": threshold,
                "incorrect_scores": incorrect_scores,
                "correct_scores": correct_scores,
            },
            sort_keys=True,
            indent=2,
        ),
        encoding="utf-8",
    )

    _update_guardrails_yaml(settings.project_root, mode_key, threshold, run_id)

    return TuneResult(
        mode_key=mode_key,
        threshold=threshold,
        incorrect_scores=incorrect_scores,
        correct_scores=correct_scores,
        run_id=run_id,
    )
