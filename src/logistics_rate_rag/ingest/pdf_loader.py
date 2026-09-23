"""PDF tariff loader (docs/SPEC.md §3.3, D-29)."""

from __future__ import annotations

import re
from pathlib import Path

import pdfplumber

from logistics_rate_rag.errors import CorpusFormatError, PdfTableError
from logistics_rate_rag.ingest.loaders import parse_tariff_markdown
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
_EXPECTED_TABLE_HEADER = ["Origin", "Destination", "20DRY", "40DRY", "40HC", "Transit (days)"]


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

        rows: list[str] = []
        row_pages: list[int] = []
        for page in pages:
            for table in page.extract_tables():
                for row_index, row in enumerate(table):
                    cells = [(_collapse_ws(c) if c else "") for c in row]
                    if cells == _EXPECTED_TABLE_HEADER:
                        continue
                    if len(cells) != 6:
                        raise PdfTableError(path, page.page_number, row_index, cells)
                    c0, c1, c2, c3, c4, c5 = cells
                    if not re.match(r"^[A-Z]{5} [A-Za-z ]+$", c0):
                        raise PdfTableError(path, page.page_number, row_index, cells)
                    if not re.match(r"^[A-Z]{5} [A-Za-z ]+$", c1):
                        raise PdfTableError(path, page.page_number, row_index, cells)
                    for c in (c2, c3, c4):
                        if not re.match(r"^\d{1,3}(,\d{3})*$", c):
                            raise PdfTableError(path, page.page_number, row_index, cells)
                    if not re.match(r"^\d{1,2}$", c5):
                        raise PdfTableError(path, page.page_number, row_index, cells)
                    rows.append(f"| {c0} | {c1} | {c2} | {c3} | {c4} | {c5} |")
                    row_pages.append(page.page_number)

        if not rows:
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
                    "| Origin | Destination | 20DRY | 40DRY | 40HC | Transit (days) |",
                    "|---|---|---|---|---|---|",
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


def load_pdf_tariff(path: Path) -> LoadedDocument:
    canonical_markdown, page_texts, row_page_numbers = extract_pdf_tariff(path)
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
