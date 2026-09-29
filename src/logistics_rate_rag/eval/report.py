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
    sets = "+".join(sorted(c.get("sets", ["golden", "adversarial"])))
    return (c["store"], c["retrieval"], c["reranker"], mode, bool(c.get("enriched")), sets)


def _eval_runs(results_dir: Path) -> list[dict]:
    """Every eval run file, oldest first. Recall and tuning files have no
    `per_question` and are skipped."""
    runs = []
    for path in sorted(results_dir.glob("*.json")):
        run = json.loads(path.read_text(encoding="utf-8"))
        if "per_question" in run and "metrics" in run:
            runs.append(run)
    return runs


def _corpus_version(run: dict) -> int:
    return int(run["config"].get("corpus_version", 1))


def _latest_runs(runs: list[dict]) -> dict[tuple, dict]:
    """Newest run per (store, retrieval, reranker, mode, enriched, sets), on
    the newest corpus version only: runs on an older corpus answer different
    questions over different documents and are kept as history, not compared."""
    if not runs:
        return {}
    current = max(_corpus_version(r) for r in runs)
    return {_run_key(r): r for r in runs if _corpus_version(r) == current}


def _latest_recall(results_dir: Path) -> dict[tuple[str, bool, bool], dict]:
    runs = [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(results_dir.glob("*-recall*.json"))
    ]
    if not runs:
        return {}
    current = max(_corpus_version(r) for r in runs)
    latest: dict[tuple[str, bool, bool], dict] = {}
    for run in runs:
        c = run["config"]
        if _corpus_version(run) == current:
            key = (c["store"], bool(c.get("enriched")), bool(c.get("query_expansion", True)))
            latest[key] = run
    return latest


def _gated_accuracy(latest: dict[tuple, dict], store, retrieval, reranker) -> float | None:
    """Golden accuracy from the newest gated run of that configuration that
    included the golden set (a golden-only ablation run counts)."""
    runs = [
        r
        for k, r in latest.items()
        if k[:5] == (store, retrieval, reranker, "gated", False) and "golden" in k[5]
    ]
    newest = max(runs, key=lambda r: r["run_id"], default=None)
    return newest["metrics"].get("golden_accuracy") if newest else None


def _diff(a: float | None, b: float | None) -> float | None:
    return None if a is None or b is None else round(a - b, 4)


def write_latest(results_dir: Path) -> Path:
    """Regenerates LATEST.md (SPEC.md §7.5): before/after per store, the
    retrieval ladder, store parity, rerank and hybrid lift, total cost. It
    is a view over the committed run files and the only file overwritten."""
    runs = _eval_runs(results_dir)
    latest = _latest_runs(runs)
    recall = _latest_recall(results_dir)
    version = _corpus_version(next(iter(latest.values()))) if latest else None
    lines = [
        "# LATEST",
        "",
        f"Regenerated from the newest run per configuration on corpus v{version}. "
        "Runs on older corpus versions stay in this folder as history.",
        "",
    ]
    if not latest:
        lines.append("No runs yet.")
        path = results_dir / "LATEST.md"
        path.write_text(NL.join(lines) + NL, encoding="utf-8")
        return path

    lines += ["## Before / after the guardrails", ""]
    full = "adversarial+golden"
    configs = sorted({k[:3] for k in latest if not k[4] and k[5] == full})
    for store, retrieval, reranker in configs:
        base = latest.get((store, retrieval, reranker, "baseline", False, full))
        gated = latest.get((store, retrieval, reranker, "gated", False, full))
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
        "| store | retrieval | reranker | mode | sets | golden_accuracy | wrong | fabricated "
        "| adversarial_rejection | run |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for key in sorted(latest):
        run = latest[key]
        m = run["metrics"]
        store, retrieval, reranker, mode, enriched, sets = key
        lines.append(
            f"| {store} | {retrieval}{' (enriched)' if enriched else ''} | {reranker} | {mode} | "
            f"{sets.replace('+', ', ')} | {_fmt(m.get('golden_accuracy'))} | "
            f"{_fmt(m.get('wrong_values_surfaced'))} | {_fmt(m.get('fabricated_values_surfaced'))} "
            f"| {_fmt(m.get('adversarial_rejection_rate'))} | `{run['run_id']}` |"
        )
    lines.append("")
    # Live spend is recorded once, on the run that made the calls; re-runs
    # served from the cache cost 0. So sum every run file, not just the newest.
    total_cost = sum((r.get("usage", {}).get("cost_usd") or 0.0) for r in runs)
    current_cost = sum(
        (r.get("usage", {}).get("cost_usd") or 0.0) for r in runs if _corpus_version(r) == version
    )

    if recall:
        lines += [
            "## Retrieval ladder (LLM-free recall over golden ANSWER questions)",
            "",
            "| store | chunks | BM25 query expansion | dense | hybrid | reranked | run |",
            "|---|---|---|---|---|---|---|",
        ]
        for (store, enriched, expand), run in sorted(recall.items()):
            r = list(run["recall"].values())
            lines.append(
                f"| {store} | {'enriched' if enriched else 'raw'} | {'on' if expand else 'off'} "
                f"| {r[0]:.3f} | {r[1]:.3f} | {r[2]:.3f} | `{run['run_id']}` |"
            )
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
    raw, enr = recall.get(("chroma", False, True)), recall.get(("chroma", True, True))
    noexp = recall.get(("chroma", False, False))
    expansion_lift = (
        _diff(list(raw["recall"].values())[1], list(noexp["recall"].values())[1])
        if raw and noexp
        else None
    )
    enrichment_lift = (
        _diff(list(enr["recall"].values())[1], list(raw["recall"].values())[1])
        if raw and enr
        else None
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
        f"| enrichment_lift | {_fmt(enrichment_lift)} | chroma hybrid recall: enriched - raw |",
        f"| query_expansion_lift | {_fmt(expansion_lift)} | chroma hybrid recall: "
        "expansion on - off (D-48) |",
        "",
        f"Recorded LLM spend on corpus v{version}: **${current_cost:.4f}**; across all "
        f"{len(runs)} eval run files: ${total_cost:.4f} (answer generation only; cost "
        "tracking started 2026-09-29).",
    ]
    path = results_dir / "LATEST.md"
    path.write_text(NL.join(lines) + NL, encoding="utf-8")
    return path
