"""docs/CORPUS.md §1: regenerating into a temp dir must be byte-identical
to every committed corpus file, PDF included.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_corpus  # noqa: E402

COMMITTED_CORPUS_DIR = REPO_ROOT / "data" / "corpus"
CORPUS_FILES = [
    "meridian_tariff_2026_h2.pdf",
    "meridian_tariff_2026_q2.md",
    "halcyon_tariff_2026_h2.csv",
    "rate_policy_note_2026.md",
    "manifest.json",
]


def test_regeneration_is_byte_identical(tmp_path):
    generated_on = generate_corpus.json.loads(
        (COMMITTED_CORPUS_DIR / "manifest.json").read_text(encoding="utf-8")
    )["generated_on"]

    generate_corpus.generate(tmp_path / "data", force=True, generated_on=generated_on)

    for name in CORPUS_FILES:
        committed = (COMMITTED_CORPUS_DIR / name).read_bytes()
        regenerated = (tmp_path / "data" / "corpus" / name).read_bytes()
        assert committed == regenerated, f"{name} is not byte-identical on regeneration"


def test_post_conditions_hold():
    meridian_h2, halcyon_h2, meridian_q2, used = generate_corpus.generate_values()
    assert len(used) == 403  # corpus v2: 173 + 173 Meridian cells, 57 Halcyon lines
    assert used.isdisjoint(generate_corpus.RESERVED)
    for lane in generate_corpus.ALL_LANES:
        h2 = meridian_h2[lane]
        assert h2["40HC"] > h2["40DRY"] > h2["20DRY"]
        for ctype in generate_corpus.EQUIPMENT:
            offered = generate_corpus.meridian_offers(lane, ctype)
            assert (ctype in h2) == offered == (ctype in meridian_q2[lane])
            if offered:
                assert meridian_q2[lane][ctype] != h2[ctype]
    for rates in halcyon_h2.values():
        assert set(rates) <= {"20DRY", "40DRY", "40HC", "45HC", "20RF", "40RH"}


def test_generator_equipment_matches_registry():
    from logistics_rate_rag.config import load_equipment_codes

    assert list(load_equipment_codes()) == generate_corpus.EQUIPMENT


def test_v1_values_are_a_prefix_of_v2():
    """D-46: v2 draws come after the v1 sequence, so the first 60 Meridian H2
    dry values keep their v1 numbers (spot-checked against v1 golden answers)."""
    h2, halcyon, q2, _ = generate_corpus.generate_values()
    assert h2[1]["40HC"] == 2224  # G-001
    assert h2[2]["20DRY"] == 1166  # G-002
    assert q2[15]["20DRY"] == 878  # G-023
    assert halcyon[1]["40HC"] > 0
