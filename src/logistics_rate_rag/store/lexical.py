"""BM25 lexical index and reciprocal-rank fusion (docs/SPEC.md §4.5, D-33).

Pure functions over in-memory chunks: no network, no embeddings. BM25 is
for names and codes (LOCODEs, tariff refs, container types); rate values
are found by dense retrieval and checked by Gate 3, so splitting numbers
at the thousands separator is accepted.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.store.base import Hit

# Split on anything that isn't a word character or a hyphen (PLAN.md D-43).
# SPEC.md §4.5's original `[\s|,]+` left punctuation glued on, so the
# question "Mundra<en dash>Barcelona lane?" produced one glued token for
# both ports plus "lane?", and never matched either port.
TOKEN_SPLIT = re.compile(r"[^\w-]+")


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_SPLIT.split(text.lower()) if t]


@dataclass(frozen=True, slots=True)
class FusedHit:
    chunk: Chunk
    similarity_norm: float | None
    vector_rank: int | None
    bm25_score: float | None
    lexical_rank: int | None
    rrf_score: float | None
    fused_rank: int | None = None


class LexicalIndex:
    def __init__(self, chunks: Sequence[Chunk]) -> None:
        self._chunks = list(chunks)
        self._bm25 = BM25Okapi([tokenize(c.index_text) for c in self._chunks])

    def query(self, text: str, k: int) -> list[tuple[Chunk, float, int]]:
        scores = self._bm25.get_scores(tokenize(text))
        ranked = sorted(
            (
                (chunk, float(score))
                for chunk, score in zip(self._chunks, scores, strict=True)
                if score > 0
            ),
            key=lambda cs: (-cs[1], cs[0].chunk_id),
        )
        return [(chunk, score, rank) for rank, (chunk, score) in enumerate(ranked[:k], start=1)]


def fuse_rrf(
    dense: Sequence[Hit], lexical: Sequence[tuple[Chunk, float, int]], k: int = 60
) -> list[FusedHit]:
    dense_by_id = {h.chunk.chunk_id: h for h in dense}
    lex_by_id = {chunk.chunk_id: (chunk, score, rank) for chunk, score, rank in lexical}

    rrf: dict[str, float] = {}
    for h in dense:
        rrf[h.chunk.chunk_id] = rrf.get(h.chunk.chunk_id, 0.0) + 1.0 / (k + h.vector_rank)
    for chunk, _score, rank in lexical:
        rrf[chunk.chunk_id] = rrf.get(chunk.chunk_id, 0.0) + 1.0 / (k + rank)

    fused: list[FusedHit] = []
    for fused_rank, cid in enumerate(sorted(rrf, key=lambda c: (-rrf[c], c)), start=1):
        d = dense_by_id.get(cid)
        lex = lex_by_id.get(cid)
        fused.append(
            FusedHit(
                chunk=d.chunk if d else lex[0],
                similarity_norm=d.similarity_norm if d else None,
                vector_rank=d.vector_rank if d else None,
                bm25_score=lex[1] if lex else None,
                lexical_rank=lex[2] if lex else None,
                rrf_score=rrf[cid],
                fused_rank=fused_rank,
            )
        )
    return fused
