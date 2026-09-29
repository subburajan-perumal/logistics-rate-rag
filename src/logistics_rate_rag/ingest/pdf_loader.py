"""PDF tariff loader (docs/SPEC.md §3.3, D-29)."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pdfplumber

from logistics_rate_rag.errors import CorpusFormatError, PdfTableError
from logistics_rate_rag.ingest.loaders import (
    CURRENCY_CELL,
    PORT_CELL,
    RATE_CELL,
    parse_table_header,
    parse_tariff_markdown,
    separator_row,
    table_header,
)
from logistics_rate_rag.ingest.models import LoadedDocument

_HEADER_PREFIXES = (
    "Carrier:",
    "Tariff reference:",
    "Status:",
    "Currency:",
    "Valid from:",
    "Valid to:",
    "Supersedes:",
    "Bunker Adjustment Factor",
    "Terminal handling",
)


def _collapse_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def extract_pdf_tariff(path: Path) -> tuple[str, tuple[str, ...], tuple[int, ...]]:
    """Returns (canonical_markdown, page_texts, page_numbers_per_row)."""
    with pdfplumber.open(str(path)) as pdf:
        pages = pdf.pages
        page_texts = tuple(page.extract_text() or "" for page in pages)

        page1_lines = [_collapse_ws(ln) for ln in page_texts[0].split("\n") if _collapse_ws(ln)]
        title_lines: list[str] = []
        idx = 0
        while idx < len(page1_lines) and not page1_lines[idx].startswith(_HEADER_PREFIXES):
            title_lines.append(page1_lines[idx])
            idx += 1
        title = " ".join(title_lines)

        header_lines: list[str] = []
        for line in page1_lines[idx:]:
            if line == "Rates by lane":
                break
            header_lines.append(f"- {line}")

        codes: list[str] | None = None
        rows: list[str] = []
        row_pages: list[int] = []
        for page in pages:
            for table in page.extract_tables():
                for row_index, row in enumerate(table):
                    cells = [(_collapse_ws(c) if c else "") for c in row]
                    if cells and cells[0] == "Origin":
                        header_codes = parse_table_header("| " + " | ".join(cells) + " |", path)
                        if codes is not None and header_codes != codes:
                            raise PdfTableError(path, page.page_number, row_index, cells)
                        codes = header_codes
                        continue
                    if codes is None or len(cells) != len(codes) + 4:
                        raise PdfTableError(path, page.page_number, row_index, cells)
                    origin, dest, currency, *rates, transit = cells
                    ok = (
                        re.fullmatch(PORT_CELL, origin)
                        and re.fullmatch(PORT_CELL, dest)
                        and re.fullmatch(CURRENCY_CELL, currency)
                        and all(re.fullmatch(RATE_CELL, r) for r in rates)
                        and re.fullmatch(r"\d{1,2}", transit)
                    )
                    if not ok:
                        raise PdfTableError(path, page.page_number, row_index, cells)
                    rows.append("| " + " | ".join(cells) + " |")
                    row_pages.append(page.page_number)

        if not rows or codes is None:
            raise CorpusFormatError(path, "no table rows extracted")

        last_page_lines = [
            _collapse_ws(ln) for ln in page_texts[-1].split("\n") if _collapse_ws(ln)
        ]
        try:
            start = last_page_lines.index("Remarks") + 1
        except ValueError:
            raise CorpusFormatError(path, "no 'Remarks' line found on the last page") from None
        remark_lines = []
        for line in last_page_lines[start:]:
            if line.startswith("Synthetic document"):
                break
            remark_lines.append(f"- {line}")

        canonical_markdown = (
            "\n".join(
                [
                    f"# {title}",
                    "",
                    *header_lines,
                    "",
                    "## Rates by lane",
                    "",
                    table_header(codes),
                    separator_row(len(codes) + 4),
                    *rows,
                    "",
                    "## Remarks",
                    "",
                    *remark_lines,
                ]
            )
            + "\n"
        )

        return canonical_markdown, page_texts, tuple(row_pages)


def _cache_dir() -> Path:
    from logistics_rate_rag.config import find_project_root

    return find_project_root(Path(__file__).resolve()) / ".cache" / "pdf_extract"


def extract_pdf_tariff_cached(path: Path) -> tuple[str, tuple[str, ...], tuple[int, ...]]:
    """`extract_pdf_tariff` memoised on disk by the PDF's sha256 (corpus v3's
    multi-page tariffs take ~10 s each to parse). A changed file has a new
    hash, so a stale entry can never be returned; a corrupt entry is a miss."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    entry = _cache_dir() / f"{digest}.json"
    if entry.exists():
        try:
            d = json.loads(entry.read_text(encoding="utf-8"))
            return d["markdown"], tuple(d["page_texts"]), tuple(d["row_pages"])
        except (json.JSONDecodeError, KeyError):
            pass
    markdown, page_texts, row_pages = extract_pdf_tariff(path)
    entry.parent.mkdir(parents=True, exist_ok=True)
    entry.write_text(
        json.dumps({"markdown": markdown, "page_texts": page_texts, "row_pages": row_pages}),
        encoding="utf-8",
    )
    return markdown, page_texts, row_pages


def load_pdf_tariff(path: Path) -> LoadedDocument:
    canonical_markdown, page_texts, row_page_numbers = extract_pdf_tariff_cached(path)
    doc = parse_tariff_markdown(
        canonical_markdown, path.name, "tariff_pdf", path, row_page_numbers=row_page_numbers
    )
    return LoadedDocument(
        source_doc=doc.source_doc,
        doc_type=doc.doc_type,
        text=doc.text,
        carrier=doc.carrier,
        tariff_ref=doc.tariff_ref,
        currency=doc.currency,
        valid_from=doc.valid_from,
        valid_to=doc.valid_to,
        status=doc.status,
        page_texts=page_texts,
        header_lines=doc.header_lines,
        table_header=doc.table_header,
        table_rows=doc.table_rows,
        remarks=doc.remarks,
        sections=doc.sections,
        row_page_numbers=doc.row_page_numbers,
    )
