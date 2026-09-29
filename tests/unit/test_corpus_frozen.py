"""docs/CORPUS.md §1: regenerating into a temp dir must be byte-identical
to every committed corpus file, PDFs included, and the committed question
sets must verify against the committed documents (PLAN.md D-50).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_corpus  # noqa: E402
import verify_questions  # noqa: E402

COMMITTED_CORPUS_DIR = REPO_ROOT / "data" / "corpus"
MANIFEST = json.loads((COMMITTED_CORPUS_DIR / "manifest.json").read_text(encoding="utf-8"))


def test_regeneration_is_byte_identical(tmp_path):
    generate_corpus.generate(tmp_path / "data", force=True, generated_on=MANIFEST["generated_on"])

    regenerated_dir = tmp_path / "data" / "corpus"
    committed = sorted(p.name for p in COMMITTED_CORPUS_DIR.iterdir())
    assert sorted(p.name for p in regenerated_dir.iterdir()) == committed
    for name in committed:
        assert (COMMITTED_CORPUS_DIR / name).read_bytes() == (
            regenerated_dir / name
        ).read_bytes(), f"{name} is not byte-identical on regeneration"
    assert (REPO_ROOT / "config" / "rate_ranges.json").read_bytes() == (
        tmp_path / "config" / "rate_ranges.json"
    ).read_bytes()


def test_manifest_shape_v3():
    assert MANIFEST["corpus_version"] == 3
    assert len(MANIFEST["rates"]) == 16_110
    assert len(MANIFEST["files"]) == 13  # 12 tariffs + the policy note
    carriers = {d["carrier"] for d in MANIFEST["documents"].values()} - {"ALL"}
    assert len(carriers) == 10
    superseded = sorted(n for n, d in MANIFEST["documents"].items() if d["status"] == "SUPERSEDED")
    assert superseded == ["meridian_tariff_2026_q2.md", "solstice_tariff_2026_q2.md"]


def test_post_conditions_hold():
    values = generate_corpus.generate_values()
    registry = yaml.safe_load((REPO_ROOT / "config" / "carriers.yaml").read_text("utf-8"))
    for c in generate_corpus.CARRIERS:
        cfg = registry["carriers"][c.code]
        h2, q2 = values[c.code]["h2"], values[c.code]["q2"]
        assert cfg["baf_included"] == c.baf_included
        for (o, d), row in h2.items():
            r = row["rates"]
            assert r["40HC"] > r["40DRY"] > r["20DRY"] > 0
            assert row["currency"] in cfg["currencies"], (c.code, o, d, row["currency"])
            assert ("baf" in row) == (not c.baf_included)
            for ctype in generate_corpus.EQUIPMENT:
                assert (ctype in r) == generate_corpus.offers(c, o, d, ctype)
            if q2 is not None:
                # a superseded value never equals the current one on its lane
                assert q2[(o, d)]["rates"].keys() == r.keys()
                assert all(q2[(o, d)]["rates"][k] != v for k, v in r.items())
        assert (q2 is not None) == c.superseded


def test_generator_equipment_matches_registry():
    from logistics_rate_rag.config import load_equipment_codes

    assert list(load_equipment_codes()) == generate_corpus.EQUIPMENT


def test_question_sets_verify_against_documents(capsys):
    """scripts/verify_questions.py re-parses every tariff independently and
    checks every golden and adversarial expectation (CORPUS.md §6)."""
    assert verify_questions.main() == 0, capsys.readouterr().out[-2000:]
    for name, key, n in (("golden", "questions", 100), ("adversarial", "prompts", 30)):
        qs = yaml.safe_load((REPO_ROOT / "data" / "eval" / f"{name}.yaml").read_text("utf-8"))
        assert qs["corpus_version"] == MANIFEST["corpus_version"]
        assert len(qs[key]) == n
        assert qs["verified_by"]
