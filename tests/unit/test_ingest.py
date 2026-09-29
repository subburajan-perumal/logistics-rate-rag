"""Ingestion + chunking tests (docs/PLAN.md Phase 2 acceptance).

No network, no API keys — loaders/chunking are pure functions over the
committed corpus.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from logistics_rate_rag.config import RetrievalConfig
from logistics_rate_rag.errors import CorpusFormatError
from logistics_rate_rag.ingest.chunking import chunk_corpus, chunk_document
from logistics_rate_rag.ingest.loaders import (
    load_corpus,
    load_csv_tariff,
    load_markdown_tariff,
    load_policy,
)
from logistics_rate_rag.ingest.pdf_loader import load_pdf_tariff

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS_DIR = REPO_ROOT / "data" / "corpus"

RETRIEVAL_CFG = RetrievalConfig(
    k_retrieve=12,
    k_final=6,
    rrf_k=60,
    rows_per_chunk_md=4,
    rows_per_chunk_csv=6,
    pinned_doc_types=["policy_md"],
    pinned_cap=9,
)


def test_load_corpus_returns_thirteen_documents():
    docs = load_corpus(CORPUS_DIR)
    names = {d.source_doc for d in docs}
    assert len(names) == 13  # corpus v3: 12 tariffs of 10 carriers + the policy note
    assert {"meridian_tariff_2026_h2.pdf", "meridian_tariff_2026_q2.md",
            "solstice_tariff_2026_q2.md", "rate_policy_note_2026.md"} <= names  # fmt: skip
    assert {d.doc_type for d in docs} == {"tariff_pdf", "tariff_md", "tariff_csv", "policy_md"}


def test_load_markdown_tariff_fields():
    doc = load_markdown_tariff(CORPUS_DIR / "meridian_tariff_2026_q2.md")
    assert doc.doc_type == "tariff_md"
    assert doc.carrier == "MERIDIAN"
    assert doc.tariff_ref == "MER-2026-Q2-FCL"
    assert doc.status == "SUPERSEDED"
    assert doc.valid_from.isoformat() == "2026-04-01"
    assert doc.valid_to.isoformat() == "2026-06-30"
    assert doc.currency == "MIXED"  # each line states its own currency (D-50)
    assert len(doc.table_rows) == 320


def test_load_pdf_tariff_matches_markdown_shape():
    doc = load_pdf_tariff(CORPUS_DIR / "meridian_tariff_2026_h2.pdf")
    assert doc.doc_type == "tariff_pdf"
    assert doc.carrier == "MERIDIAN"
    assert doc.status == "CURRENT"
    assert len(doc.table_rows) == 320
    assert len(doc.row_page_numbers) == 320
    assert doc.row_page_numbers[0] == 1
    assert doc.row_page_numbers[-1] == 13
    assert len(doc.page_texts) == 13


def test_load_csv_tariff_fields():
    doc = load_csv_tariff(CORPUS_DIR / "halcyon_tariff_2026_h2.csv")
    assert doc.doc_type == "tariff_csv"
    assert doc.carrier == "HALCYON"
    assert doc.currency == "MIXED"  # USD and EUR trades (D-50)
    assert len(doc.table_rows) == 1384
    single = load_csv_tariff(CORPUS_DIR / "corvid_tariff_2026_h2.csv")
    assert single.currency == "USD"


def test_load_policy_sections():
    doc = load_policy(CORPUS_DIR / "rate_policy_note_2026.md")
    assert doc.doc_type == "policy_md"
    assert doc.carrier == "ALL"
    titles = [t for t, _ in doc.sections]
    assert titles == [
        "Scope",
        "Bunker Adjustment Factor (BAF)",
        "Currency",
        "Terminal Handling Charges",
        "Validity and Expiry",
        "Container Types",
        "Quoting Rules",
        "Peak Season Surcharge",
        "Synthetic Notice",
    ]


def test_chunk_corpus_total_count():
    docs = load_corpus(CORPUS_DIR)
    chunks = chunk_corpus(docs, RETRIEVAL_CFG, corpus_version=3)
    assert len(chunks) == 1324  # corpus v3: 1,315 tariff chunks + 9 policy sections


def test_chunk_headers_stay_with_rows():
    docs = load_corpus(CORPUS_DIR)
    md_doc = next(d for d in docs if d.source_doc == "meridian_tariff_2026_q2.md")
    chunks = chunk_document(md_doc, RETRIEVAL_CFG, corpus_version=1)
    rate_chunks = [c for c in chunks if c.metadata["section"] == "rates"]
    assert len(rate_chunks) == 80  # 320 rows, 4 per chunk
    for c in rate_chunks:
        assert "- Carrier: Meridian Ocean Lines (MERIDIAN)" in c.text
        assert "## Rates by lane" in c.text
        assert "| Origin | Destination | Currency | 20DRY |" in c.text
        assert "|" + "---|" * 17 in c.text  # 13 equipment columns + 4
    remarks_chunks = [c for c in chunks if c.metadata["section"] == "remarks"]
    assert len(remarks_chunks) == 1


def test_every_chunk_metadata_has_valid_to():
    docs = load_corpus(CORPUS_DIR)
    chunks = chunk_corpus(docs, RETRIEVAL_CFG, corpus_version=1)
    for c in chunks:
        assert c.metadata["valid_to"], f"{c.chunk_id} missing valid_to"


def test_pdf_chunk_page_numbers_present():
    docs = load_corpus(CORPUS_DIR)
    pdf_doc = next(d for d in docs if d.source_doc == "meridian_tariff_2026_h2.pdf")
    chunks = chunk_document(pdf_doc, RETRIEVAL_CFG, corpus_version=1)
    rate_chunks = [c for c in chunks if c.metadata["section"] == "rates"]
    for c in rate_chunks:
        assert c.metadata["page_numbers"] != ""
    remarks_chunk = next(c for c in chunks if c.metadata["section"] == "remarks")
    assert remarks_chunk.metadata["page_numbers"] == ""


def test_policy_chunks_scoped_global():
    docs = load_corpus(CORPUS_DIR)
    policy_doc = next(d for d in docs if d.source_doc == "rate_policy_note_2026.md")
    chunks = chunk_document(policy_doc, RETRIEVAL_CFG, corpus_version=1)
    assert all(c.metadata["scope"] == "global" for c in chunks)

    tariff_doc = next(d for d in docs if d.source_doc == "halcyon_tariff_2026_h2.csv")
    tariff_chunks = chunk_document(tariff_doc, RETRIEVAL_CFG, corpus_version=1)
    assert all(c.metadata["scope"] == "specific" for c in tariff_chunks)


def test_hash_mismatch_raises(tmp_path):
    import shutil

    tmp_corpus = tmp_path / "corpus"
    shutil.copytree(CORPUS_DIR, tmp_corpus)
    (tmp_corpus / "rate_policy_note_2026.md").write_text("tampered", encoding="utf-8")

    with pytest.raises(CorpusFormatError):
        load_corpus(tmp_corpus)
