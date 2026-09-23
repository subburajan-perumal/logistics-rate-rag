"""CLI entry point `rate-rag` (docs/SPEC.md §8).

Phase 2 implements `corpus generate`/`corpus questions` (delegating to
scripts/generate_corpus.py) and `index`. `ask`/`eval`/`recall` are added
in later phases as their underlying modules ship.
"""

from __future__ import annotations

import argparse
import logging
import sys
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

    return parser


def main(argv: list[str] | None = None) -> int:
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
