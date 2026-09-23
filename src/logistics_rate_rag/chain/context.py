"""Context rendering (docs/SPEC.md §5.3, D-35, D-37).

Pulled forward from Phase 2b into Phase 3 because `CandidateChain.run`
(§5.4 step 2) calls these directly — Phase 2b's hybrid retrieval work
extends `RateRetriever`, not this module.
"""

from __future__ import annotations

from collections.abc import Sequence

from logistics_rate_rag.config import RetrievalConfig
from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.store.retriever import RetrievedChunk


def order_for_context(chunks: Sequence[RetrievedChunk]) -> list[RetrievedChunk]:
    return sorted(chunks, key=lambda rc: (rc.chunk.source_doc, rc.chunk.metadata["chunk_index"]))


def pin_global(
    retrieved: Sequence[RetrievedChunk], all_chunks: Sequence[Chunk], cfg: RetrievalConfig
) -> list[Chunk]:
    retrieved_ids = {rc.chunk.chunk_id for rc in retrieved}
    pinned_types = set(cfg.pinned_doc_types)
    candidates = [
        c for c in all_chunks if c.doc_type in pinned_types and c.chunk_id not in retrieved_ids
    ]
    candidates.sort(key=lambda c: c.chunk_id)
    return candidates[: cfg.pinned_cap]


def _header(c: Chunk) -> str:
    m = c.metadata
    return (
        f"[chunk_id: {c.chunk_id}] [doc: {c.source_doc}] [carrier: {m['carrier']}] "
        f"[tariff: {m['tariff_ref']}] [status: {m['status']}] "
        f"[valid: {m['valid_from']} → {m['valid_to']}]"
    )


def render_context(retrieved: Sequence[RetrievedChunk], pinned: Sequence[Chunk]) -> str:
    parts: list[str] = []
    for rc in retrieved:
        parts.append(f"{_header(rc.chunk)}\n{rc.chunk.text}\n---")
    if pinned:
        parts.append("--- POLICY (applies to all tariffs) ---")
        for c in pinned:
            parts.append(f"{_header(c)}\n{c.text}\n---")
    return "\n".join(parts)
