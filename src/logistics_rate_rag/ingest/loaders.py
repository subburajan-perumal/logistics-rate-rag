"""Document loaders (docs/SPEC.md §3.2, docs/CORPUS.md §4)."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path

from logistics_rate_rag.errors import CorpusFormatError
from logistics_rate_rag.ingest.models import LoadedDocument

DISPLAY_NAMES = {"MERIDIAN": "Meridian Ocean Lines", "HALCYON": "Halcyon Container Line"}
ALLOWED_CONTAINER_TYPES = {"20DRY", "40DRY", "40HC"}

_ROW_RE = re.compile(
    r"^\| [A-Z]{5} [A-Za-z ]+ \| [A-Z]{5} [A-Za-z ]+ \| "
    r"\d{1,3}(,\d{3})* \| \d{1,3}(,\d{3})* \| \d{1,3}(,\d{3})* \| \d{1,2} \|$"
)
_HEADER_ROW = "| Origin | Destination | 20DRY | 40DRY | 40HC | Transit (days) |"
_SEPARATOR_ROW = "|---|---|---|---|---|---|"


def _read_normalized(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    return raw.replace("\r\n", "\n").replace("\r", "\n")


def parse_tariff_markdown(
    text: str,
    source_doc: str,
    doc_type: str,
    error_path: object,
    row_page_numbers: tuple[int, ...] = (),
) -> LoadedDocument:
    """Shared parser for markdown-shaped tariff text (SPEC.md §3.2 step 1-3),
    used by both `load_markdown_tariff` and `load_pdf_tariff` (SPEC.md §3.3
    step 5: "parses the canonical Markdown with the same code path")."""
    lines = text.split("\n")

    if not lines or not lines[0].startswith("# "):
        raise CorpusFormatError(error_path, "line 1 must start with '# '")
    idx = 1
    if idx >= len(lines) or lines[idx] != "":
        raise CorpusFormatError(error_path, "expected a blank line after the title")
    idx += 1

    header_lines: list[str] = []
    while idx < len(lines) and lines[idx].startswith("- "):
        header_lines.append(lines[idx])
        idx += 1

    fields: dict[str, str] = {}
    for hl in header_lines:
        if m := re.match(r"^- Carrier: .*\((?P<code>[A-Z]+)\)$", hl):
            fields["carrier"] = m["code"]
        elif m := re.match(r"^- Tariff reference: (?P<ref>[A-Z]+-\d{4}-[A-Z0-9]+-FCL)$", hl):
            fields["tariff_ref"] = m["ref"]
        elif m := re.match(r"^- Status: (?P<status>CURRENT|SUPERSEDED.*)$", hl):
            fields["status_raw"] = m["status"]
        elif m := re.match(r"^- Currency: (?P<cur>[A-Z]{3}) per container$", hl):
            fields["currency"] = m["cur"]
        elif m := re.match(r"^- Valid from: (?P<d>\d{4}-\d{2}-\d{2})$", hl):
            fields["valid_from"] = m["d"]
        elif m := re.match(r"^- Valid to: (?P<d>\d{4}-\d{2}-\d{2})$", hl):
            fields["valid_to"] = m["d"]

    required = ("carrier", "tariff_ref", "status_raw", "currency", "valid_from", "valid_to")
    missing = [f for f in required if f not in fields]
    if missing:
        raise CorpusFormatError(error_path, f"header missing fields: {missing}")

    if idx >= len(lines) or lines[idx] != "":
        raise CorpusFormatError(error_path, "expected a blank line after the header bullets")
    idx += 1
    if idx >= len(lines) or lines[idx] != "## Rates by lane":
        raise CorpusFormatError(error_path, "expected '## Rates by lane'")
    idx += 1
    if idx >= len(lines) or lines[idx] != "":
        raise CorpusFormatError(error_path, "expected a blank line after '## Rates by lane'")
    idx += 1
    if idx >= len(lines) or lines[idx] != _HEADER_ROW:
        raise CorpusFormatError(error_path, f"expected table header row, got {lines[idx]!r}")
    table_header = lines[idx]
    idx += 1
    if idx >= len(lines) or lines[idx] != _SEPARATOR_ROW:
        raise CorpusFormatError(error_path, "expected table separator row")
    idx += 1

    table_rows: list[str] = []
    while idx < len(lines) and lines[idx] != "":
        if not _ROW_RE.match(lines[idx]):
            raise CorpusFormatError(error_path, f"bad table row: {lines[idx]!r}")
        table_rows.append(lines[idx])
        idx += 1
    idx += 1  # skip the blank line

    if idx >= len(lines) or lines[idx] != "## Remarks":
        raise CorpusFormatError(error_path, "expected '## Remarks'")
    idx += 1
    if idx >= len(lines) or lines[idx] != "":
        raise CorpusFormatError(error_path, "expected a blank line after '## Remarks'")
    idx += 1

    remark_lines = lines[idx:]
    while remark_lines and remark_lines[-1] == "":
        remark_lines.pop()
    remarks = "\n".join(remark_lines)

    status = "SUPERSEDED" if fields["status_raw"].startswith("SUPERSEDED") else "CURRENT"

    if row_page_numbers and len(row_page_numbers) != len(table_rows):
        raise CorpusFormatError(error_path, "row_page_numbers length must match table_rows")

    return LoadedDocument(
        source_doc=source_doc,
        doc_type=doc_type,  # type: ignore[arg-type]
        text=text,
        carrier=fields["carrier"],
        tariff_ref=fields["tariff_ref"],
        currency=fields["currency"],
        valid_from=date.fromisoformat(fields["valid_from"]),
        valid_to=date.fromisoformat(fields["valid_to"]),
        status=status,
        header_lines=tuple(header_lines),
        table_header=table_header,
        table_rows=tuple(table_rows),
        remarks=remarks,
        row_page_numbers=row_page_numbers,
    )


def load_markdown_tariff(path: Path) -> LoadedDocument:
    text = _read_normalized(path)
    return parse_tariff_markdown(text, path.name, "tariff_md", path)


_CSV_HEADER = (
    "carrier",
    "tariff_ref",
    "origin_locode",
    "origin_city",
    "destination_locode",
    "destination_city",
    "container_type",
    "base_rate",
    "currency",
    "baf",
    "valid_from",
    "valid_to",
    "notes",
)


def load_csv_tariff(path: Path) -> LoadedDocument:
    text = _read_normalized(path)
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]

    reader = csv.DictReader(lines)
    if tuple(reader.fieldnames or ()) != _CSV_HEADER:
        raise CorpusFormatError(path, f"unexpected CSV header: {reader.fieldnames}")

    rows = list(reader)
    if not rows:
        raise CorpusFormatError(path, "no data rows")

    first = rows[0]
    carrier, tariff_ref, currency = first["carrier"], first["tariff_ref"], first["currency"]
    valid_from, valid_to = first["valid_from"], first["valid_to"]

    for row in rows:
        if (
            row["carrier"],
            row["tariff_ref"],
            row["currency"],
            row["valid_from"],
            row["valid_to"],
        ) != (
            carrier,
            tariff_ref,
            currency,
            valid_from,
            valid_to,
        ):
            raise CorpusFormatError(path, f"inconsistent document-level fields in row: {row}")
        if not row["base_rate"].isdigit() or not row["baf"].isdigit():
            raise CorpusFormatError(path, f"base_rate/baf must be integers: {row}")
        if row["container_type"] not in ALLOWED_CONTAINER_TYPES:
            raise CorpusFormatError(path, f"unknown container_type: {row['container_type']}")

    header_lines = (
        f"- Carrier: {DISPLAY_NAMES.get(carrier, carrier)} ({carrier})",
        f"- Tariff reference: {tariff_ref}",
        "- Status: CURRENT",
        f"- Currency: {currency} per container (BAF quoted separately in the baf column)",
        f"- Valid from: {valid_from}",
        f"- Valid to: {valid_to}",
    )

    return LoadedDocument(
        source_doc=path.name,
        doc_type="tariff_csv",
        text=text,
        carrier=carrier,
        tariff_ref=tariff_ref,
        currency=currency,
        valid_from=date.fromisoformat(valid_from),
        valid_to=date.fromisoformat(valid_to),
        status="CURRENT",
        header_lines=header_lines,
        table_header=lines[0],
        table_rows=tuple(lines[1:]),
    )


def load_policy(path: Path) -> LoadedDocument:
    text = _read_normalized(path)
    lines = text.split("\n")

    if not lines or not lines[0].startswith("# "):
        raise CorpusFormatError(path, "line 1 must start with '# '")
    if len(lines) < 2 or lines[1] != "":
        raise CorpusFormatError(path, "expected a blank line after the title")

    header_lines = tuple(lines[2:5])
    if not header_lines[0].startswith("- Applies to:"):
        raise CorpusFormatError(path, "expected '- Applies to:' bullet")
    m = re.match(r"^- Effective: (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})$", header_lines[1])
    if not m:
        raise CorpusFormatError(path, "expected '- Effective: <from> to <to>' bullet")
    if header_lines[2] != "- Document type: policy":
        raise CorpusFormatError(path, "expected '- Document type: policy' bullet")

    idx = 5
    if idx >= len(lines) or lines[idx] != "":
        raise CorpusFormatError(path, "expected a blank line after the header bullets")
    idx += 1

    sections: list[tuple[str, str]] = []
    current_title: str | None = None
    current_body: list[str] = []

    def flush() -> None:
        if current_title is not None:
            body = "\n".join(current_body).strip("\n")
            sections.append((current_title, body))

    for line in lines[idx:]:
        if line.startswith("## "):
            flush()
            current_title = line[3:]
            current_body = []
        else:
            current_body.append(line)
    flush()

    return LoadedDocument(
        source_doc=path.name,
        doc_type="policy_md",
        text=text,
        carrier="ALL",
        tariff_ref="POLICY-2026",
        currency="NA",
        valid_from=date.fromisoformat(m[1]),
        valid_to=date.fromisoformat(m[2]),
        status="CURRENT",
        header_lines=header_lines,
        sections=tuple(sections),
    )


def load_corpus(corpus_dir: Path) -> list[LoadedDocument]:
    from logistics_rate_rag.ingest.pdf_loader import load_pdf_tariff

    with (corpus_dir / "manifest.json").open(encoding="utf-8") as f:
        manifest = json.load(f)

    docs: list[LoadedDocument] = []
    for filename, expected_sha in manifest["files"].items():
        path = corpus_dir / filename
        actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_sha != expected_sha:
            raise CorpusFormatError(path, "hash mismatch")

        doc_type = manifest["documents"][filename]["doc_type"]
        if path.suffix == ".pdf":
            docs.append(load_pdf_tariff(path))
        elif path.suffix == ".csv":
            docs.append(load_csv_tariff(path))
        elif path.suffix == ".md":
            docs.append(
                load_policy(path) if doc_type == "policy_md" else load_markdown_tariff(path)
            )
        else:
            raise CorpusFormatError(path, f"unsupported extension: {path.suffix}")
    return docs
