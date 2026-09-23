"""Result files (docs/SPEC.md §7.5)."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from logistics_rate_rag.eval.runner import RunResult


def _cost_note(usage_totals) -> str:
    return f"{usage_totals.live_calls} live calls, {usage_totals.cache_hits} cache hits"


def write_run(result: RunResult, results_dir: Path) -> Path:
    results_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": result.run_id,
        "created_at": result.created_at,
        "config": result.config,
        "metrics": result.metrics,
        "usage": asdict(result.usage_totals),
        "per_question": [asdict(r) for r in result.per_question],
    }
    json_path = results_dir / f"{result.run_id}.json"
    json_path.write_text(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md_lines = [
        f"# {result.run_id}",
        "",
        f"Created: {result.created_at} · {_cost_note(result.usage_totals)}",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
    ]
    for key, value in result.metrics.items():
        if key == "gate_breakdown":
            continue
        md_lines.append(f"| {key} | {value} |")
    md_lines += ["", "## Gate breakdown", "", "| set\\|outcome\\|reason | count |", "|---|---|"]
    for key, count in sorted(result.metrics["gate_breakdown"].items()):
        md_lines.append(f"| {key} | {count} |")
    md_lines += [
        "",
        "## Per-question",
        "",
        "| id | tag | expected | outcome | reason | rate_value | ms |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in result.per_question:
        md_lines.append(
            f"| {r.id} | {r.tag} | {r.expected_outcome} | {r.outcome} | {r.reason or ''} | "
            f"{r.rate_value if r.rate_value is not None else ''} | {r.latency_ms} |"
        )
    md_path = results_dir / f"{result.run_id}.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return json_path


def write_latest(results_dir: Path) -> Path:
    """Regenerates LATEST.md from the newest run per (store, retrieval,
    reranker, mode, enriched) key. Phase 3: only one combination exists
    (chroma/dense/none/baseline), so this degenerates to summarising that
    one run; Phase 8 adds the full before/after and lift tables once more
    combinations exist to compare."""
    run_files = sorted(results_dir.glob("*.json"))
    lines = ["# LATEST", ""]
    if not run_files:
        lines.append("No runs yet.")
    else:
        latest = json.loads(run_files[-1].read_text(encoding="utf-8"))
        lines.append(f"Most recent run: `{latest['run_id']}`")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|---|---|")
        for key, value in latest["metrics"].items():
            if key == "gate_breakdown":
                continue
            lines.append(f"| {key} | {value} |")
    path = results_dir / "LATEST.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
