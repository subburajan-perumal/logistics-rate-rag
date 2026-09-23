"""Chunking (docs/SPEC.md §3.4-3.5)."""

from __future__ import annotations

import hashlib
import itertools
from pathlib import Path

from logistics_rate_rag.config import RetrievalConfig
from logistics_rate_rag.ingest.models import Chunk, LoadedDocument

_SEPARATOR_ROW = "|---|---|---|---|---|---|"


def _build_chunk(
    chunk_id: str,
    doc: LoadedDocument,
    text: str,
    section: str,
    page_numbers: tuple[int, ...],
    pinned_doc_types: set[str],
    corpus_version: int,
) -> Chunk:
    content_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
    chunk_index = int(chunk_id.rsplit("#", 1)[1])
    scope = "global" if doc.doc_type in pinned_doc_types else "specific"
    metadata: dict[str, str | int | bool] = {
        "chunk_id": chunk_id,
        "source_doc": doc.source_doc,
        "doc_type": doc.doc_type,
        "carrier": doc.carrier,
        "tariff_ref": doc.tariff_ref,
        "currency": doc.currency,
        "valid_from": doc.valid_from.isoformat(),
        "valid_to": doc.valid_to.isoformat(),
        "status": doc.status,
        "scope": scope,
        "section": section,
        "chunk_index": chunk_index,
        "corpus_version": corpus_version,
        "content_sha256": content_sha256,
        "page_numbers": ",".join(str(p) for p in page_numbers),
        "description": "",
    }
    return Chunk(
        chunk_id=chunk_id,
        source_doc=doc.source_doc,
        doc_type=doc.doc_type,
        text=text,
        index_text=text,
        metadata=metadata,
        content_sha256=content_sha256,
        page_numbers=page_numbers,
    )


def chunk_document(doc: LoadedDocument, cfg: RetrievalConfig, corpus_version: int) -> list[Chunk]:
    slug = Path(doc.source_doc).stem
    pinned_doc_types = set(cfg.pinned_doc_types)
    chunks: list[Chunk] = []

    if doc.doc_type in ("tariff_md", "tariff_pdf"):
        rows_per = cfg.rows_per_chunk_md
        for i, batch in enumerate(itertools.batched(doc.table_rows, rows_per)):
            text = "\n".join(
                [
                    *doc.header_lines,
                    "",
                    "## Rates by lane",
                    "",
                    doc.table_header,
                    _SEPARATOR_ROW,
                    *batch,
                ]
            )
            page_numbers: tuple[int, ...] = ()
            if doc.row_page_numbers:
                start = i * rows_per
                end = start + len(batch)
                page_numbers = tuple(sorted(set(doc.row_page_numbers[start:end])))
            chunks.append(
                _build_chunk(
                    f"{slug}#{i:03d}",
                    doc,
                    text,
                    "rates",
                    page_numbers,
                    pinned_doc_types,
                    corpus_version,
                )
            )
        remarks_text = "\n".join([*doc.header_lines, "", "## Remarks", "", doc.remarks])
        chunks.append(
            _build_chunk(
                f"{slug}#{len(chunks):03d}",
                doc,
                remarks_text,
                "remarks",
                (),
                pinned_doc_types,
                corpus_version,
            )
        )

    elif doc.doc_type == "tariff_csv":
        rows_per = cfg.rows_per_chunk_csv
        for i, batch in enumerate(itertools.batched(doc.table_rows, rows_per)):
            text = "\n".join([*doc.header_lines, "", doc.table_header, *batch])
            chunks.append(
                _build_chunk(
                    f"{slug}#{i:03d}", doc, text, "rates", (), pinned_doc_types, corpus_version
                )
            )

    elif doc.doc_type == "policy_md":
        for i, (title, body) in enumerate(doc.sections):
            text = f"## {title}\n\n{body}"
            chunks.append(
                _build_chunk(
                    f"{slug}#{i:03d}", doc, text, title, (), pinned_doc_types, corpus_version
                )
            )

    else:
        raise ValueError(f"unknown doc_type: {doc.doc_type}")

    return chunks


def chunk_corpus(
    docs: list[LoadedDocument], cfg: RetrievalConfig, corpus_version: int
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for doc in docs:
        chunks.extend(chunk_document(doc, cfg, corpus_version))
    return chunks
