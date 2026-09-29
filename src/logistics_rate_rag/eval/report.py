"""Result files (docs/SPEC.md §7.5)."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from logistics_rate_rag.eval.runner import RunResult


def _cost_note(usage_totals) -> str:
    return (
        f"{usage_totals.live_calls} live calls, {usage_totals.cache_hits} cache hits, "
        f"${usage_totals.cost_usd:.4f}"
    )


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


NL = chr(10)

BEFORE_AFTER = (
    ("golden_accuracy", "≥ 0.90"),
    ("golden_abstention", "reported"),
    ("refusal_correctness", "1.00"),
    ("fabricated_values_surfaced", "0"),
    ("wrong_values_surfaced", "0"),
    ("adversarial_rejection_rate", "≥ 0.90"),
    ("injection_leak", "0"),
    ("latency_p50_ms", "reported"),
)


def _fmt(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _run_key(run: dict) -> tuple:
    c = run["config"]
    mode = "gated" if c.get("gates") else "baseline"
    return (c["store"], c["retrieval"], c["reranker"], mode, bool(c.get("enriched")))


def _latest_runs(results_dir: Path) -> dict[tuple, dict]:
    """Newest eval run per (store, retrieval, reranker, mode, enriched).
    Recall and tuning files have no `per_question` and are skipped."""
    latest: dict[tuple, dict] = {}
    for path in sorted(results_dir.glob("*.json")):
        run = json.loads(path.read_text(encoding="utf-8"))
        if "per_question" not in run or "metrics" not in run:
            continue
        latest[_run_key(run)] = run  # sorted by timestamped name: last wins
    return latest


def _latest_recall(results_dir: Path) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for path in sorted(results_dir.glob("*-recall*.json")):
        run = json.loads(path.read_text(encoding="utf-8"))
        latest[run["config"]["store"]] = run
    return latest


def _gated_accuracy(latest: dict[tuple, dict], store, retrieval, reranker) -> float | None:
    run = latest.get((store, retrieval, reranker, "gated", False))
    return run["metrics"].get("golden_accuracy") if run else None


def _diff(a: float | None, b: float | None) -> float | None:
    return None if a is None or b is None else round(a - b, 4)


def write_latest(results_dir: Path) -> Path:
    """Regenerates LATEST.md (SPEC.md §7.5): before/after per store, the
    retrieval ladder, store parity, rerank and hybrid lift, total cost. It
    is a view over the committed run files and the only file overwritten."""
    latest = _latest_runs(results_dir)
    recall = _latest_recall(results_dir)
    lines = ["# LATEST", "", "Regenerated from the newest run per configuration.", ""]
    if not latest:
        lines.append("No runs yet.")
        path = results_dir / "LATEST.md"
        path.write_text(NL.join(lines) + NL, encoding="utf-8")
        return path

    lines += ["## Before / after the guardrails", ""]
    configs = sorted({k[:3] for k in latest if not k[4]})
    for store, retrieval, reranker in configs:
        base = latest.get((store, retrieval, reranker, "baseline", False))
        gated = latest.get((store, retrieval, reranker, "gated", False))
        if not (base and gated):
            continue
        lines += [
            f"**{store} · {retrieval} · reranker {reranker}** "
            f"(`{base['run_id']}` vs `{gated['run_id']}`)",
            "",
            "| Metric | Baseline (gates off) | Gated | Target |",
            "|---|---|---|---|",
        ]
        for key, target in BEFORE_AFTER:
            lines.append(
                f"| {key} | {_fmt(base['metrics'].get(key))} | "
                f"{_fmt(gated['metrics'].get(key))} | {target} |"
            )
        lines.append("")

    lines += [
        "## Every configuration (newest run each)",
        "",
        "| store | retrieval | reranker | mode | golden_accuracy | wrong | fabricated "
        "| adversarial_rejection | cost_usd | run |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    total_cost = 0.0
    for key in sorted(latest):
        run = latest[key]
        m = run["metrics"]
        cost = run.get("usage", {}).get("cost_usd", 0.0) or 0.0
        total_cost += cost
        store, retrieval, reranker, mode, enriched = key
        lines.append(
            f"| {store} | {retrieval}{' (enriched)' if enriched else ''} | {reranker} | {mode} | "
            f"{_fmt(m.get('golden_accuracy'))} | {_fmt(m.get('wrong_values_surfaced'))} | "
            f"{_fmt(m.get('fabricated_values_surfaced'))} | "
            f"{_fmt(m.get('adversarial_rejection_rate'))} | {cost:.4f} | `{run['run_id']}` |"
        )
    lines.append("")

    if recall:
        lines += [
            "## Retrieval ladder (LLM-free recall over golden ANSWER questions)",
            "",
            "| store | dense | hybrid | reranked | run |",
            "|---|---|---|---|---|",
        ]
        for store, run in sorted(recall.items()):
            r = list(run["recall"].values())
            lines.append(f"| {store} | {r[0]:.3f} | {r[1]:.3f} | {r[2]:.3f} | `{run['run_id']}` |")
        lines.append("")

    parity = _diff(
        _gated_accuracy(latest, "chroma", "hybrid", "flashrank"),
        _gated_accuracy(latest, "pinecone", "hybrid", "flashrank"),
    )
    rerank_lift = _diff(
        _gated_accuracy(latest, "chroma", "hybrid", "flashrank"),
        _gated_accuracy(latest, "chroma", "hybrid", "none"),
    )
    hybrid_lift = _diff(
        _gated_accuracy(latest, "chroma", "hybrid", "flashrank"),
        _gated_accuracy(latest, "chroma", "dense", "flashrank"),
    )
    lines += [
        "## Lifts and parity (gated golden accuracy)",
        "",
        "| Metric | Value | Definition |",
        "|---|---|---|",
        f"| store_parity | {_fmt(abs(parity) if parity is not None else None)} "
        "| abs(chroma - pinecone), hybrid + flashrank; target <= 0.05 |",
        f"| rerank_lift | {_fmt(rerank_lift)} | chroma hybrid: flashrank - none |",
        f"| hybrid_lift | {_fmt(hybrid_lift)} | chroma flashrank: hybrid - dense |",
        "",
        f"Total LLM cost across the runs above: **${total_cost:.4f}**.",
    ]
    path = results_dir / "LATEST.md"
    path.write_text(NL.join(lines) + NL, encoding="utf-8")
    return path
