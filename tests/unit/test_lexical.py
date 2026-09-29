"""BM25 lexical index and RRF fusion (docs/SPEC.md §4.5, D-33)."""

from __future__ import annotations

import pytest

from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.store.base import Hit
from logistics_rate_rag.store.lexical import LexicalIndex, fuse_rrf, tokenize


def _chunk(cid: str, text: str, carrier: str = "MERIDIAN") -> Chunk:
    return Chunk(
        chunk_id=cid,
        source_doc="doc",
        doc_type="tariff_md",
        text=text,
        index_text=text,
        metadata={"chunk_id": cid, "carrier": carrier},
        content_sha256=cid,
    )


def test_tokenize_splits_on_pipes_commas_and_whitespace():
    assert tokenize("| INMAA Chennai | 1,240 |") == ["inmaa", "chennai", "1", "240"]


def test_tokenize_splits_punctuation_and_en_dash():
    # D-43: the real G-008 question; the old `[\s|,]+` split kept these glued
    assert tokenize("Meridian's 20DRY rate on the Mundra\u2013Barcelona lane?") == [
        "meridian",
        "s",
        "20dry",
        "rate",
        "on",
        "the",
        "mundra",
        "barcelona",
        "lane",
    ]


def test_tokenize_keeps_codes_whole():
    assert tokenize("HAL-2026-H2-FCL") == ["hal-2026-h2-fcl"]


def test_fuse_rrf_hand_computed_example():
    a, b, c = _chunk("A", "a"), _chunk("B", "b"), _chunk("C", "c")
    dense = [Hit(a, 0.9, 1), Hit(b, 0.8, 2), Hit(c, 0.7, 3)]
    lexical = [(c, 5.0, 1), (a, 3.0, 2)]
    fused = fuse_rrf(dense, lexical, k=60)
    assert [f.chunk.chunk_id for f in fused] == ["A", "C", "B"]
    assert fused[0].rrf_score == pytest.approx(1 / 61 + 1 / 62)
    assert fused[1].rrf_score == pytest.approx(1 / 63 + 1 / 61)
    assert fused[2].rrf_score == pytest.approx(1 / 62)
    assert [f.fused_rank for f in fused] == [1, 2, 3]


def test_fuse_rrf_keeps_per_leg_numbers():
    a, c = _chunk("A", "a"), _chunk("C", "c")
    fused = {f.chunk.chunk_id: f for f in fuse_rrf([Hit(a, 0.9, 1)], [(c, 2.5, 1)])}
    assert (fused["A"].vector_rank, fused["A"].lexical_rank) == (1, None)
    assert fused["A"].similarity_norm == 0.9
    assert (fused["C"].vector_rank, fused["C"].lexical_rank) == (None, 1)
    assert fused["C"].bm25_score == 2.5
    assert fused["C"].similarity_norm is None


def test_fuse_rrf_breaks_ties_by_chunk_id():
    x, y = _chunk("X", "x"), _chunk("Y", "y")
    fused = fuse_rrf([Hit(y, 0.9, 1)], [(x, 1.0, 1)])
    assert [f.chunk.chunk_id for f in fused] == ["X", "Y"]


def test_lexical_query_ranks_code_match_first_and_drops_zero_scores():
    chunks = [
        _chunk("m#000", "| INMAA Chennai | NLRTM Rotterdam | 2,224 |"),
        _chunk("h#000", "HAL-2026-H2-FCL Halcyon tariff, USNYC New York"),
        _chunk("p#000", "Policy: rates exclude terminal handling charges"),
    ]
    hits = LexicalIndex(chunks).query("what does HAL-2026-H2-FCL say about USNYC", k=12)
    assert [c.chunk_id for c, _, _ in hits] == ["h#000"]
    assert hits[0][2] == 1
    assert hits[0][1] > 0


def test_lexical_query_respects_k():
    chunks = [_chunk(f"c#{i:03d}", f"inmaa row {i}") for i in range(5)]
    assert len(LexicalIndex(chunks).query("inmaa", k=3)) == 3
