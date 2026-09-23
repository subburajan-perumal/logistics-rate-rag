"""Gate 3a — grounding (docs/SPEC.md §6.4)."""

from __future__ import annotations

import re
from datetime import date

from logistics_rate_rag.guardrails.context import QuestionContext
from logistics_rate_rag.schema.answer import GateResult
from logistics_rate_rag.schema.candidate import RateCandidate

_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]  # fmt: skip


def number_variants(v: int) -> tuple[str, ...]:
    plain = str(v)
    comma = f"{v:,}"
    seen: list[str] = []
    for variant in (plain, comma, f"{plain}.00", f"{comma}.00"):
        if variant not in seen:
            seen.append(variant)
    return tuple(seen)


def date_variants(d: date) -> tuple[str, ...]:
    month = _MONTHS[d.month - 1]
    return (
        d.isoformat(),
        f"{d.day} {month[:3]} {d.year}",
        f"{month} {d.day}, {d.year}",
        f"{d.day} {month} {d.year}",
        f"{d.day:02d}/{d.month:02d}/{d.year}",
    )


def contains_number(text: str, v: int) -> bool:
    """A variant matches only where it can't be a truncated fragment of a
    bigger number. A bare comma (CSV field delimiter) is *not* excluded on
    its own — only "digit," / ",digit" (an actual thousands-separator
    shape) is, which is what makes "240" a false match inside "1,240" but
    keeps a CSV-delimited value like "...,1332,EUR,..." groundable. See
    PLAN.md D-42 — the naive `[\\d,.]` boundary from the original spec
    text breaks grounding for every comma-delimited (CSV/Halcyon) value,
    confirmed empirically against the real corpus.
    """
    for variant in number_variants(v):
        escaped = re.escape(variant)
        pattern = r"(?<!\d)(?<!\.)(?<!\d,)" + escaped + r"(?!\d)(?!\.)(?!,\d)"
        if re.search(pattern, text):
            return True
    return False


def contains_date(text: str, d: date) -> bool:
    for variant in date_variants(d):
        pattern = r"(?<![\w-])" + re.escape(variant) + r"(?![\w-])"
        if re.search(pattern, text):
            return True
    return False


def span_in_text(span: str, text: str) -> bool:
    return " ".join(span.split()) in " ".join(text.split())


def gate3_grounding(candidate: RateCandidate, ctx: QuestionContext) -> GateResult:
    chunk = ctx.chunks_by_id[candidate.source_chunk_id]
    text = chunk.text

    if not contains_number(text, candidate.rate_value):
        return GateResult(
            passed=False,
            gate="gate3_grounding",
            reason="ungrounded:rate_value",
            details={"rate_value": candidate.rate_value},
        )
    if not contains_date(text, candidate.valid_to):
        return GateResult(
            passed=False,
            gate="gate3_grounding",
            reason="ungrounded:valid_to",
            details={"valid_to": str(candidate.valid_to)},
        )
    if not span_in_text(candidate.source_span, text):
        return GateResult(
            passed=False,
            gate="gate3_grounding",
            reason="ungrounded:source_span",
            details={"source_span": candidate.source_span},
        )
    return GateResult(passed=True, gate="gate3_grounding", reason=None, details={})
