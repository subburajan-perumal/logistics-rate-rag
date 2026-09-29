"""LATEST.md regeneration (docs/SPEC.md §7.5). No network."""

from __future__ import annotations

import json

from logistics_rate_rag.eval.report import write_latest


def _run(path, run_id, store, retrieval, reranker, gated, accuracy, cost=0.01, sets=None):
    path.joinpath(f"{run_id}.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "config": {
                    "store": store,
                    "retrieval": retrieval,
                    "reranker": reranker,
                    "enriched": False,
                    "gates": ["schema"] if gated else [],
                    "sets": sets or ["golden", "adversarial"],
                },
                "metrics": {"golden_accuracy": accuracy, "wrong_values_surfaced": 0},
                "usage": {"cost_usd": cost},
                "per_question": [],
            }
        ),
        encoding="utf-8",
    )


def test_latest_uses_newest_run_per_key_and_skips_non_eval_files(tmp_path):
    _run(tmp_path, "20260101T000000Z-a", "chroma", "hybrid", "flashrank", True, 0.5)
    _run(tmp_path, "20260102T000000Z-b", "chroma", "hybrid", "flashrank", True, 0.9)
    _run(tmp_path, "20260102T000000Z-c", "chroma", "hybrid", "flashrank", False, 0.8)
    _run(tmp_path, "20260102T000000Z-d", "chroma", "hybrid", "none", True, 0.85)
    _run(tmp_path, "20260102T000000Z-e", "chroma", "dense", "flashrank", True, 0.875)
    # a newer golden-only ablation must not displace the full run in before/after
    _run(
        tmp_path, "20260102T010000Z-f", "chroma", "hybrid", "flashrank", True, 0.9, 0.0, ["golden"]
    )
    tmp_path.joinpath("20260103T000000Z-chroma-with_reranker-tuning.json").write_text(
        json.dumps({"mode_key": "with_reranker", "threshold": 0.66}), encoding="utf-8"
    )
    tmp_path.joinpath("20260103T000000Z-chroma-recall.json").write_text(
        json.dumps(
            {
                "run_id": "20260103T000000Z-chroma-recall",
                "config": {"store": "chroma", "enriched": False},
                "recall": {"d": 1.0, "h": 0.9583, "r": 1.0},
            }
        ),
        encoding="utf-8",
    )

    text = write_latest(tmp_path).read_text(encoding="utf-8")

    assert "20260101T000000Z-a" not in text  # superseded by -b
    assert "| golden_accuracy | 0.800 | 0.900 |" in text
    assert "| rerank_lift | 0.050 |" in text
    assert "| hybrid_lift | 0.025 |" in text
    assert "| chroma | raw | on | 1.000 | 0.958 | 1.000 |" in text
    assert "20260102T000000Z-b" in text.split("## Every configuration")[0]
    assert "**$0.0500**" in text  # every run file, including the superseded one


def test_latest_with_no_runs(tmp_path):
    assert "No runs yet." in write_latest(tmp_path).read_text(encoding="utf-8")
