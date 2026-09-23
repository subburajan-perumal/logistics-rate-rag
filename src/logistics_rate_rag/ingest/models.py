"""Ingestion data models (docs/SPEC.md §3.1)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

DocType = Literal["tariff_pdf", "tariff_md", "tariff_csv", "policy_md"]


@dataclass(frozen=True, slots=True)
class LoadedDocument:
    source_doc: str
    doc_type: DocType
    text: str
    carrier: str
    tariff_ref: str
    currency: str
    valid_from: date
    valid_to: date
    status: str
    page_texts: tuple[str, ...] = ()
    header_lines: tuple[str, ...] = ()
    table_header: str = ""
    table_rows: tuple[str, ...] = ()
    remarks: str = ""
    sections: tuple[tuple[str, str], ...] = ()
    # PDF only: the source page number for each entry in table_rows, same
    # index alignment. Not in the original SPEC.md §3.1 field list; added
    # per PLAN.md D-40 since §3.3/§3.4 both assume per-row page numbers
    # exist somewhere and this is the only place they can live.
    row_page_numbers: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class Chunk:
    chunk_id: str
    source_doc: str
    doc_type: DocType
    text: str
    index_text: str
    metadata: dict[str, str | int | bool]
    content_sha256: str
    page_numbers: tuple[int, ...] = ()
