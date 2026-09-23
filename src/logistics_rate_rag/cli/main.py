"""CLI entry point `rate-rag` (docs/SPEC.md §8).

Phase 2 implements `corpus generate`/`corpus questions` (delegating to
scripts/generate_corpus.py) and `index`. `ask`/`eval`/`recall` are added
in later phases as their underlying modules ship.
"""

from __future__ import annotations

import argparse
import dataclasses
import logging
import sys
from datetime import date
from pathlib import Path

from logistics_rate_rag.config import Settings, load_settings
from logistics_rate_rag.errors import ConfigError, MissingCredential, RateRagError
from logistics_rate_rag.ingest.chunking import chunk_corpus
from logistics_rate_rag.ingest.loaders import load_corpus
from logistics_rate_rag.store.chroma_backend import ChromaBackend
from logistics_rate_rag.store.embeddings import GeminiEmbedder

logger = logging.getLogger(__name__)


def _configure_logging(level: str) -> None:
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    for noisy in ("chromadb", "httpx", "flashrank", "pdfminer"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def _build_chroma_backend(settings: Settings, collection: str) -> ChromaBackend:
    embedder = GeminiEmbedder(
        settings.embedding_model, settings.embedding_dim, settings.google_api_key
    )
    persist_dir = settings.project_root / ".chroma"
    return ChromaBackend(persist_dir, collection, embedder)


def cmd_index(args: argparse.Namespace, settings: Settings) -> int:
    if args.enrich:
        raise NotImplementedError("--enrich ships in Phase 8 (chain/enrich.py)")

    docs = load_corpus(settings.project_root / "data" / "corpus")
    chunks = chunk_corpus(docs, settings.retrieval, settings.manifest.corpus_version)

    store_names = (
        ["chroma", "pinecone"] if args.store == "both" else [args.store or settings.vector_store]
    )

    for store_name in store_names:
        collection = f"rates_v{settings.manifest.corpus_version}"
        if store_name == "chroma":
            backend = _build_chroma_backend(settings, collection)
        else:
            from logistics_rate_rag.store.pinecone_backend import PineconeBackend

            backend = PineconeBackend(
                settings.pinecone_api_key or "",
                settings.pinecone_index,
                f"corpus-v{settings.manifest.corpus_version}",
                settings.embedding_dim,
            )

        if args.reset:
            backend.reset()

        have = backend.existing()
        first_index = not have
        want = {c.chunk_id: c for c in chunks}
        stale = [
            cid for cid, sha in have.items() if cid not in want or want[cid].content_sha256 != sha
        ]
        new = [c for c in chunks if c.chunk_id not in have or have[c.chunk_id] != c.content_sha256]

        backend.delete(stale)
        embedder = GeminiEmbedder(
            settings.embedding_model, settings.embedding_dim, settings.google_api_key
        )
        vectors = embedder.embed_documents([c.index_text for c in new]) if new else []
        backend.upsert(new, vectors)

        print(f"[{store_name}] {len(new)} upserted, {len(stale)} deleted, {backend.count()} total")
        if first_index and new:
            print(f"[{store_name}] dimension {settings.embedding_dim} confirmed")

    return 0


def _build_retriever_and_chain(settings: Settings, no_cache: bool):
    from logistics_rate_rag.chain.cache import ResponseCache
    from logistics_rate_rag.chain.candidate_chain import CandidateChain
    from logistics_rate_rag.chain.ratelimit import RateLimiter
    from logistics_rate_rag.store.retriever import RateRetriever

    docs = load_corpus(settings.project_root / "data" / "corpus")
    chunks = chunk_corpus(docs, settings.retrieval, settings.manifest.corpus_version)
    embedder = GeminiEmbedder(
        settings.embedding_model, settings.embedding_dim, settings.google_api_key
    )
    backend = _build_chroma_backend(settings, f"rates_v{settings.manifest.corpus_version}")
    all_chunks = backend.all_chunks() or chunks
    retriever = RateRetriever(
        backend=backend,
        embedder=embedder,
        k_retrieve=settings.retrieval.k_retrieve,
        k_final=settings.retrieval.k_final,
    )
    cache = None if no_cache else ResponseCache(settings.llm_cache_dir)
    limiter = RateLimiter(settings.llm_min_interval_s)
    return CandidateChain(settings, retriever, all_chunks, cache, limiter)


def cmd_ask(args: argparse.Namespace, settings: Settings) -> int:
    if args.retrieval not in (None, "dense"):
        raise NotImplementedError("hybrid retrieval ships in Phase 2b")
    if args.reranker not in (None, "none"):
        raise NotImplementedError("re-ranking ships in Phase 2b/7")
    if args.store not in (None, "chroma"):
        raise NotImplementedError("Pinecone ships in Phase 7")

    from logistics_rate_rag.guardrails.pipeline import run_gates, to_answer

    # Phase 3 only ever runs dense retrieval with no reranker regardless of
    # settings' env-sourced defaults (hybrid/flashrank) — reflect what
    # actually ran, not the aspirational config, so the printed line is
    # honest until Phase 2b/7 make hybrid/rerank real.
    effective_settings = dataclasses.replace(
        settings,
        gates_enabled=not args.no_gates,
        vector_store="chroma",
        retrieval_mode="dense",
        reranker="none",
    )
    chain = _build_retriever_and_chain(effective_settings, args.no_cache)
    as_of = date.fromisoformat(args.as_of) if args.as_of else settings.as_of_default
    result = chain.run(args.question, as_of)

    ctx = None
    if effective_settings.gates_enabled:
        from logistics_rate_rag.guardrails.context import build_question_context

        ctx = build_question_context(result)
    verdict = run_gates(result.candidate, result.parsing_error, ctx, effective_settings)
    answer = to_answer(verdict, result, effective_settings)

    if args.json:
        import json as jsonlib

        print(jsonlib.dumps(dataclasses.asdict(answer), default=str, indent=2))
    else:
        print(f"Outcome : {answer.outcome}")
        if answer.outcome.value == "ANSWER":
            print(
                f"Carrier : {answer.carrier}   Lane: {answer.origin} → {answer.destination}   "
                f"Type: {answer.container_type}"
            )
            print(
                f"Rate    : {answer.rate_value} {answer.currency}   "
                f"Valid: {answer.valid_from} → {answer.valid_to}   Includes BAF: "
                f"{'yes' if answer.includes_surcharge else 'no'}"
            )
        else:
            print(f"Reason  : {answer.reason or '(model judged this unanswerable)'}")
        for s in answer.sources:
            print(f"Source  : {s.source_doc}  chunk {s.chunk_id}  ({s.role})")
        print(
            f"Store   : {answer.store}   retrieval {answer.retrieval_mode}   "
            f"reranker {answer.reranker}   {answer.latency_ms} ms   "
            f"cache {'hit' if answer.cache_hit else 'miss'}   "
            f"tokens {answer.usage.input_tokens}/{answer.usage.output_tokens}"
        )
    return 0


def cmd_eval(args: argparse.Namespace, settings: Settings) -> int:
    from logistics_rate_rag.eval.report import write_latest, write_run
    from logistics_rate_rag.eval.runner import RunConfig, run_eval, tune_threshold

    if args.tune_threshold:
        store = args.store or settings.vector_store
        mode_key = (
            "with_reranker"
            if (args.reranker or settings.reranker) != "none"
            else "without_reranker"
        )
        result = tune_threshold(settings, store, mode_key)
        print(
            f"Tuned {mode_key} threshold={result.threshold} "
            f"({len(result.correct_scores)} correct, {len(result.incorrect_scores)} incorrect) "
            f"-> {result.run_id}"
        )
        return 0

    sets = ("golden", "adversarial") if args.set in (None, "all") else (args.set,)
    run_cfg = RunConfig(
        store=args.store or settings.vector_store,
        mode=args.mode or "baseline",
        retrieval_mode=args.retrieval or settings.retrieval_mode,
        reranker=args.reranker or settings.reranker,
        enriched=args.enriched,
        sets=sets,
        no_cache=args.no_cache,
    )
    result = run_eval(settings, run_cfg)
    results_dir = settings.project_root / "eval" / "results"
    path = write_run(result, results_dir)
    write_latest(results_dir)
    print(f"Wrote {path}")
    any_error = any(r.outcome == "ERROR" for r in result.per_question)
    return 1 if any_error else 0


def cmd_corpus(args: argparse.Namespace, settings: Settings) -> int:
    sys.path.insert(0, str(settings.project_root / "scripts"))
    import generate_corpus

    if args.corpus_command == "generate":
        manifest = generate_corpus.generate(settings.project_root / "data", force=args.force)
        print(
            f"Generated corpus_version={manifest['corpus_version']}, "
            f"{len(manifest['rates'])} rate entries."
        )
        return 0

    if args.corpus_command == "questions":
        import json

        manifest_path = settings.project_root / "data" / "corpus" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        eval_dir = settings.project_root / "data" / "eval"
        eval_dir.mkdir(parents=True, exist_ok=True)
        golden_path = eval_dir / "golden.yaml"
        adversarial_path = eval_dir / "adversarial.yaml"
        import yaml

        for p in (golden_path, adversarial_path):
            if p.exists() and not args.force:
                existing = yaml.safe_load(p.read_text(encoding="utf-8"))
                if existing.get("verified_by"):
                    print(f"{p} is verified; pass --force to overwrite.", file=sys.stderr)
                    return 2
        generate_corpus.write_yaml(golden_path, generate_corpus.draft_golden(manifest))
        generate_corpus.write_yaml(adversarial_path, generate_corpus.draft_adversarial(manifest))
        print(f"Drafted {golden_path} and {adversarial_path}.")
        return 0

    raise ConfigError(f"unknown corpus subcommand: {args.corpus_command}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rate-rag")
    parser.add_argument("--env-file", type=Path, default=None)
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING"])
    parser.add_argument("--project-root", type=Path, default=None)

    sub = parser.add_subparsers(dest="command", required=True)

    corpus = sub.add_parser("corpus")
    corpus_sub = corpus.add_subparsers(dest="corpus_command", required=True)
    corpus_gen = corpus_sub.add_parser("generate")
    corpus_gen.add_argument("--force", action="store_true")
    corpus_q = corpus_sub.add_parser("questions")
    corpus_q.add_argument("--force", action="store_true")

    index = sub.add_parser("index")
    index.add_argument("--store", choices=["chroma", "pinecone", "both"], default=None)
    index.add_argument("--reset", action="store_true")
    index.add_argument("--prune", action="store_true")
    index.add_argument("--enrich", action="store_true")

    ask = sub.add_parser("ask")
    ask.add_argument("question")
    ask.add_argument("--store", choices=["chroma", "pinecone"], default=None)
    ask.add_argument("--retrieval", choices=["hybrid", "dense"], default=None)
    ask.add_argument("--reranker", choices=["flashrank", "pinecone", "none"], default=None)
    ask.add_argument("--as-of", default=None)
    ask.add_argument("--no-gates", action="store_true")
    ask.add_argument("--no-cache", action="store_true")
    ask.add_argument("--json", action="store_true")

    ev = sub.add_parser("eval")
    ev.add_argument("--store", choices=["chroma", "pinecone", "both"], default=None)
    ev.add_argument("--mode", choices=["gated", "baseline", "both"], default=None)
    ev.add_argument("--retrieval", choices=["hybrid", "dense", "ablation"], default=None)
    ev.add_argument(
        "--reranker", choices=["flashrank", "pinecone", "none", "ablation"], default=None
    )
    ev.add_argument("--set", choices=["golden", "adversarial", "all"], default="all")
    ev.add_argument("--no-cache", action="store_true")
    ev.add_argument("--enriched", action="store_true")
    ev.add_argument("--tune-threshold", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    # Windows consoles default to a legacy codepage that can't encode the
    # arrows used in human-readable output below; UTF-8 is safe everywhere.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.log_level)

    try:
        settings = load_settings(env_file=args.env_file)
    except RateRagError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    try:
        if args.command == "corpus":
            return cmd_corpus(args, settings)
        if args.command == "index":
            return cmd_index(args, settings)
        if args.command == "ask":
            return cmd_ask(args, settings)
        if args.command == "eval":
            return cmd_eval(args, settings)
        raise ConfigError(f"unknown command: {args.command}")
    except MissingCredential as e:
        print(f"error: {e}", file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        return 130
    except RateRagError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
