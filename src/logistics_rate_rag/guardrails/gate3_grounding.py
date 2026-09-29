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


NOT_OFFERED = chr(0x2014)  # em dash: equipment not offered on that lane (D-46)
NO_TABLE = object()  # the cited chunk holds no rate table (e.g. a policy section)


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def cell_for(text: str, origin: str, destination: str, container_type: str) -> object:
    """The table cell for (origin, destination, container_type) in a chunk
    (PLAN.md D-47): a pipe-table row whose Origin/Destination cells start with
    the LOCODEs, or a CSV line with those fields. Returns the cell text, None
    when the chunk has a table but no such row or column, or NO_TABLE."""
    lines = text.split("\n")
    header = next((ln for ln in lines if ln.startswith("| Origin | Destination |")), None)
    if header is not None:
        columns = _cells(header)
        if container_type not in columns:
            return None
        col = columns.index(container_type)
        for ln in lines:
            if not ln.startswith("| ") or ln == header:
                continue
            cells = _cells(ln)
            if (
                len(cells) == len(columns)
                and cells[0].split(" ")[0] == origin
                and cells[1].split(" ")[0] == destination
            ):
                return cells[col]
        return None

    csv_header = next((ln for ln in lines if ln.startswith("carrier,tariff_ref,")), None)
    if csv_header is not None:
        import csv

        start = lines.index(csv_header)
        for row in csv.DictReader(ln for ln in lines[start:] if ln):
            key = (row["origin_locode"], row["destination_locode"], row["container_type"])
            if key == (origin, destination, container_type):
                return row["base_rate"]
        return None
    return NO_TABLE


def _cell_matches(cell: object, rate_value: int) -> bool:
    if cell is NO_TABLE:
        return True
    if cell is None or cell == NOT_OFFERED:
        return False
    return str(cell).replace(",", "") == str(rate_value)


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
    # The number being somewhere in the chunk is not enough once a row holds
    # 13 equipment columns: it must be the cell for this lane and equipment.
    cell = cell_for(text, candidate.origin, candidate.destination, candidate.container_type)
    if not _cell_matches(cell, candidate.rate_value):
        return GateResult(
            passed=False,
            gate="gate3_grounding",
            reason="ungrounded:cell",
            details={
                "container_type": candidate.container_type,
                "cell": None if cell is None or cell is NO_TABLE else str(cell),
                "rate_value": candidate.rate_value,
            },
        )
    return GateResult(passed=True, gate="gate3_grounding", reason=None, details={})
