"""ResponseCache tests (docs/SPEC.md §5.5, D-15). No network."""

from __future__ import annotations

from datetime import date

from logistics_rate_rag.chain.cache import ResponseCache
from logistics_rate_rag.ingest.models import Chunk


def _chunk(chunk_id: str, sha: str) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        source_doc="doc.md",
        doc_type="policy_md",
        text="text",
        index_text="text",
        metadata={},
        content_sha256=sha,
    )


def test_key_is_deterministic(tmp_path):
    cache = ResponseCache(tmp_path)
    k1 = cache.key("model", "1", "question?", date(2026, 9, 1), [], [])
    k2 = cache.key("model", "1", "question?", date(2026, 9, 1), [], [])
    assert k1 == k2


def test_key_changes_with_content_sha(tmp_path):
    cache = ResponseCache(tmp_path)
    pinned_a = [_chunk("c#000", "sha-a")]
    pinned_b = [_chunk("c#000", "sha-b")]
    k1 = cache.key("model", "1", "q", date(2026, 9, 1), [], pinned_a)
    k2 = cache.key("model", "1", "q", date(2026, 9, 1), [], pinned_b)
    assert k1 != k2


def test_miss_then_put_then_hit(tmp_path):
    cache = ResponseCache(tmp_path)
    key = cache.key("model", "1", "q", date(2026, 9, 1), [], [])
    assert cache.get(key) is None
    cache.put(
        key,
        {"model": "model", "parsed": None, "parsing_error": None, "raw_text": "hi", "usage": {}},
    )
    cached = cache.get(key)
    assert cached is not None
    assert cached["raw_text"] == "hi"


def test_corrupt_file_treated_as_miss(tmp_path):
    cache = ResponseCache(tmp_path)
    key = "deadbeef"
    (tmp_path / f"{key}.json").write_text("not json{{{", encoding="utf-8")
    assert cache.get(key) is None
