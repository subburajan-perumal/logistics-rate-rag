"""Enrichment guard (docs/SPEC.md §5.8, D-34): descriptions never carry rate values."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from logistics_rate_rag.chain.enrich import leaked_rate_values

REPO_ROOT = Path(__file__).resolve().parents[2]
ENRICH_CACHE = REPO_ROOT / ".cache" / "enrich"


def test_leak_detector_finds_plain_and_comma_values():
    assert leaked_rate_values("Rates from 2,224 USD", [2224, 930]) == [2224]
    assert leaked_rate_values("the 930 box", [2224, 930]) == [930]


def test_leak_detector_ignores_dates_and_longer_numbers():
    assert leaked_rate_values("valid 2026-12-31, ref MER-2026-H2-FCL", [2026, 12]) == []
    assert leaked_rate_values("value 12240", [2224, 1224]) == []


def test_leak_detector_ignores_prose_dates():
    text = (
        "valid from July 1, 2026, through December 31, 2026 (from 1 July 2026, the H2 2026 period)"
    )
    assert leaked_rate_values(text, [2026, 31, 1]) == []
    assert leaked_rate_values("from July 1, 2026 at 2,026 USD", [2026]) == [2026]


@pytest.mark.skipif(not ENRICH_CACHE.exists(), reason="no enrichment cache on this machine")
def test_cached_descriptions_contain_no_rate_values():
    manifest = json.loads((REPO_ROOT / "data" / "corpus" / "manifest.json").read_text("utf-8"))
    rate_values = [r["rate_value"] if isinstance(r, dict) else r for r in manifest["rate_values"]]
    for path in ENRICH_CACHE.glob("*.json"):
        description = json.loads(path.read_text(encoding="utf-8"))["description"]
        assert leaked_rate_values(description, rate_values) == [], path.name
