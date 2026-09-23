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
    meridian_h2, _halcyon_h2, meridian_q2, used = generate_corpus.generate_values()
    assert len(used) == 150
    assert used.isdisjoint(generate_corpus.RESERVED)
    for lane in range(1, 21):
        h2 = meridian_h2[lane]
        assert h2["40HC"] > h2["40DRY"] > h2["20DRY"]
    for lane in range(1, 21):
        for ctype in generate_corpus.CONTAINER_TYPES:
            assert meridian_q2[lane][ctype] != meridian_h2[lane][ctype]
