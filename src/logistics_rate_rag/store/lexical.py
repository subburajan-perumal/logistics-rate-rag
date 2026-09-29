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


class QueryExpander:
    """Appends canonical codes for equipment and port names found in a
    question, for the BM25 leg only (PLAN.md D-48). Tables hold `20TK` and
    `INNSA`; people write "20' Tank" and "JNPT". Longest name wins, so
    "20' Tank" expands to 20TK and not also to the bare "20'" (20DRY)."""

    def __init__(self, names: dict[str, str]) -> None:
        # normalised name -> canonical code, longest names first
        self._names = sorted(names.items(), key=lambda kv: -len(kv[0]))

    @classmethod
    def from_registries(cls, equipment: dict, ports: object) -> QueryExpander:
        from logistics_rate_rag.config import _norm_name

        names: dict[str, str] = {}
        for code, eq in equipment.items():
            for n in (code, eq.display_name, *eq.iso_codes, *eq.aliases):
                names[_norm_name(n)] = code
        for name_lower, locode in ports.city_lower.items():
            names[_norm_name(name_lower)] = locode
        for locode in ports.locode:
            names[locode.lower()] = locode
        return cls(names)

    def codes_in(self, question: str) -> list[str]:
        from logistics_rate_rag.config import _norm_name

        text = " " + _norm_name(question) + " "
        taken: list[tuple[int, int]] = []
        found: list[str] = []
        for name, code in self._names:
            for m in re.finditer(r"(?<![\w'])" + re.escape(name) + r"(?![\w])", text):
                span = (m.start(), m.end())
                if any(s < span[1] and span[0] < e for s, e in taken):
                    continue
                taken.append(span)
                if code not in found:
                    found.append(code)
        return found

    def expand(self, question: str) -> str:
        codes = self.codes_in(question)
        return f"{question} {' '.join(codes)}" if codes else question


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
