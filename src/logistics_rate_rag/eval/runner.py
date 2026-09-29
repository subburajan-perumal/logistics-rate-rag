"""Eval runner (docs/SPEC.md §7.2).

`mode="gated"` runs all three real gates (Phases 4-6). Hybrid retrieval
and re-ranking are real (Phase 2b), both stores work (Phase 7);
enrichment is the D-34 ablation. `run_recall` is the LLM-free retrieval check (D-31, D-33).
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
from logistics_rate_rag.chain.prompt import PROMPT_VERSION
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
from logistics_rate_rag.store import build_backend
from logistics_rate_rag.store.embeddings import GeminiEmbedder
from logistics_rate_rag.store.retriever import build_retriever


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
    store = run_cfg.store

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
    backend = build_backend(settings, store, embedder, enriched=run_cfg.enriched)
    all_chunks = backend.all_chunks() or chunks
    retriever = build_retriever(effective_settings, backend, embedder, all_chunks)
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
    usage_totals = sum_usage(usages, settings.prices)

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    run_id = f"{ts}-{run_cfg.store}-{run_cfg.retrieval_mode}-{run_cfg.reranker}-{run_cfg.mode}"
    config = {
        "chat_model": settings.chat_model,
        "thinking_level": settings.llm_thinking_level,
        "seed": settings.llm_seed,
        "embedding_model": settings.embedding_model,
        "dimension": settings.embedding_dim,
        "prompt_version": PROMPT_VERSION,
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


def tune_threshold(
    settings: Settings, store: str, mode_key: str, retrieval_mode: str | None = None
) -> TuneResult:
    """docs/PLAN.md §12 tuning procedure. Runs the golden set with Gates
    1-3a on and the confidence gate off (threshold 0), then sets the
    threshold from the observed score distribution.

    `with_reranker` tunes with settings' reranker (FlashRank unless it is
    set to pinecone); `without_reranker` always runs with no reranker."""
    if mode_key == "with_reranker":
        reranker = settings.reranker if settings.reranker != "none" else "flashrank"
    else:
        reranker = "none"

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
        retrieval_mode=retrieval_mode or settings.retrieval_mode,
        reranker=reranker,
    )

    docs = load_corpus(settings.project_root / "data" / "corpus")
    chunks = chunk_corpus(docs, settings.retrieval, settings.manifest.corpus_version)
    embedder = GeminiEmbedder(
        settings.embedding_model, settings.embedding_dim, settings.google_api_key
    )
    backend = build_backend(settings, store, embedder)
    all_chunks = backend.all_chunks() or chunks
    retriever = build_retriever(tuning_settings, backend, embedder, all_chunks)
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


@dataclass(frozen=True, slots=True)
class RecallRow:
    id: str
    tag: str
    target_chunk_ids: tuple[str, ...]
    dense_hit: bool
    hybrid_hit: bool
    reranked_hit: bool
    dense_top: tuple[str, ...]
    hybrid_top: tuple[str, ...]
    reranked_top: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RecallResult:
    run_id: str
    config: dict
    recall: dict[str, float]
    rows: list[RecallRow]


def _target_chunk_ids(chunks, q: Question) -> tuple[str, ...]:
    """SPEC.md §7.2: the chunk of `expected.source_doc` whose text contains
    the expected value (same number matcher as Gate 3a)."""
    from logistics_rate_rag.guardrails.gate3_grounding import contains_number

    e = q.expected
    return tuple(
        sorted(
            c.chunk_id
            for c in chunks
            if c.source_doc == e.source_doc and contains_number(c.text, e.rate_value)
        )
    )


def run_recall(
    settings: Settings,
    store: str,
    reranker: str | None = None,
    *,
    enriched: bool = False,
    expand: bool = True,
) -> RecallResult:
    """LLM-free recall@k_final over golden ANSWER questions for all three
    retrieval stages at once: dense, dense+BM25 fused (RRF), and the fused
    top-k_retrieve re-ranked. One query embedding per question."""
    from logistics_rate_rag.chain.planner import QueryPlanner
    from logistics_rate_rag.rerank import build_reranker
    from logistics_rate_rag.store.lexical import LexicalIndex, QueryExpander, fuse_rrf

    reranker_name = reranker or settings.reranker
    if reranker_name == "none":
        reranker_name = "flashrank"

    docs = load_corpus(settings.project_root / "data" / "corpus")
    chunks = chunk_corpus(docs, settings.retrieval, settings.manifest.corpus_version)
    embedder = GeminiEmbedder(
        settings.embedding_model, settings.embedding_dim, settings.google_api_key
    )
    backend = build_backend(settings, store, embedder, enriched=enriched)
    all_chunks = backend.all_chunks() or chunks
    lexical = LexicalIndex(all_chunks)
    expander = QueryExpander.from_registries(settings.equipment, settings.ports) if expand else None
    rr = build_reranker(
        reranker_name,
        model_name=settings.rerank_model,
        cache_dir=settings.flashrank_cache_dir,
        pinecone_api_key=settings.pinecone_api_key,
    )
    planner = QueryPlanner(settings.carriers, settings.guardrails.surcharge_keywords)
    k_retrieve, k_final = settings.retrieval.k_retrieve, settings.retrieval.k_final

    golden_path = settings.project_root / "data" / "eval" / "golden.yaml"
    qs = load_question_set(golden_path, settings.manifest.corpus_version)
    rows: list[RecallRow] = []
    for q in sorted(qs.questions, key=lambda q: q.id):
        if q.expected.outcome != "ANSWER":
            continue
        targets = set(_target_chunk_ids(all_chunks, q))
        plan = planner.plan(q.question, q.as_of)
        dense = backend.query(embedder.embed_query(plan.question), k_retrieve, plan.filter)
        lex_query = expander.expand(plan.question) if expander else plan.question
        lex = lexical.query(lex_query, k_retrieve)
        if plan.filter:
            allowed = (plan.filter["carrier"], "ALL")
            lex = [hit for hit in lex if hit[0].metadata.get("carrier") in allowed]
        fused = fuse_rrf(dense, lex, settings.retrieval.rrf_k)[:k_retrieve]
        reranked = rr.rerank(plan.question, [f.chunk for f in fused], top_n=k_final)

        dense_top = tuple(h.chunk.chunk_id for h in dense[:k_final])
        hybrid_top = tuple(f.chunk.chunk_id for f in fused[:k_final])
        reranked_top = tuple(c.chunk_id for c, _ in reranked)
        rows.append(
            RecallRow(
                id=q.id,
                tag=q.tag,
                target_chunk_ids=tuple(sorted(targets)),
                dense_hit=bool(targets & set(dense_top)),
                hybrid_hit=bool(targets & set(hybrid_top)),
                reranked_hit=bool(targets & set(reranked_top)),
                dense_top=dense_top,
                hybrid_top=hybrid_top,
                reranked_top=reranked_top,
            )
        )

    n = len(rows) or 1
    recall = {
        f"retrieval_recall@{k_final}_dense": round(sum(r.dense_hit for r in rows) / n, 4),
        f"retrieval_recall@{k_final}_hybrid": round(sum(r.hybrid_hit for r in rows) / n, 4),
        f"retrieval_recall@{k_final}_reranked": round(sum(r.reranked_hit for r in rows) / n, 4),
    }
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    suffix = ("-enriched" if enriched else "") + ("" if expand else "-noexpand")
    run_id = f"{ts}-{store}-recall{suffix}"
    config = {
        "store": store,
        "enriched": enriched,
        "query_expansion": expand,
        "reranker": reranker_name,
        "k_retrieve": k_retrieve,
        "k_final": k_final,
        "rrf_k": settings.retrieval.rrf_k,
        "questions": len(rows),
        "corpus_version": settings.manifest.corpus_version,
    }
    results_dir = settings.project_root / "eval" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / f"{run_id}.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "config": config,
                "recall": recall,
                "rows": [dataclasses.asdict(r) for r in rows],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return RecallResult(run_id=run_id, config=config, recall=recall, rows=rows)
