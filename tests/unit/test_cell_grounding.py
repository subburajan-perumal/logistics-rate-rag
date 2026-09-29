"""Cell-level grounding (PLAN.md D-47) on real corpus v2 chunks. No network."""

from __future__ import annotations

from pathlib import Path

from logistics_rate_rag.config import load_settings
from logistics_rate_rag.guardrails.gate3_grounding import NO_TABLE, cell_for
from logistics_rate_rag.ingest.chunking import chunk_corpus
from logistics_rate_rag.ingest.loaders import load_corpus

SETTINGS = load_settings()
CHUNKS = {
    c.chunk_id: c
    for c in chunk_corpus(
        load_corpus(Path(__file__).resolve().parents[2] / "data" / "corpus"),
        SETTINGS.retrieval,
        SETTINGS.manifest.corpus_version,
    )
}
PDF_000 = CHUNKS["meridian_tariff_2026_h2#000"].text  # lanes 1-4, incl. INMAA -> DEHAM
PDF_001 = CHUNKS["meridian_tariff_2026_h2#001"].text  # lanes 5-8, incl. INMAA -> AEJEA
DASH = chr(0x2014)


def _rate(origin, dest, ctype, doc="meridian_tariff_2026_h2.pdf"):
    return next(
        r.rate_value
        for r in SETTINGS.manifest.rates
        if (r.doc, r.origin, r.destination, r.container_type) == (doc, origin, dest, ctype)
    )


def test_cell_is_found_for_lane_and_equipment():
    cell = cell_for(PDF_001, "INMAA", "AEJEA", "40RH")
    assert cell.replace(",", "") == str(_rate("INMAA", "AEJEA", "40RH"))


def test_neighbouring_column_is_a_different_cell():
    # the 40RH and 40NOR values sit side by side in the same row: grounding
    # by "number appears in the chunk" would accept either for either
    rh, nor = _rate("INMAA", "AEJEA", "40RH"), _rate("INMAA", "AEJEA", "40NOR")
    assert cell_for(PDF_001, "INMAA", "AEJEA", "40NOR").replace(",", "") == str(nor)
    assert str(rh) != str(nor)


def test_not_offered_equipment_is_a_dash():
    assert cell_for(PDF_000, "INMAA", "NLRTM", "20RF") == DASH  # G-028 stays unanswerable


def test_row_not_in_chunk_is_none():
    assert cell_for(PDF_000, "INCOK", "ITGOA", "20DRY") is None


def test_csv_line_lookup():
    csv_chunk = next(c for c in CHUNKS.values() if "carrier,tariff_ref," in c.text)
    line = next(ln for ln in csv_chunk.text.splitlines() if ln.startswith("HALCYON,"))
    fields = line.split(",")
    origin, dest, ctype, base = fields[2], fields[4], fields[6], fields[7]
    assert cell_for(csv_chunk.text, origin, dest, ctype) == base
    assert cell_for(csv_chunk.text, origin, dest, "20TK") is None  # Halcyon has no tanks


def test_policy_chunk_has_no_table():
    policy = next(c for c in CHUNKS.values() if c.doc_type == "policy_md")
    assert cell_for(policy.text, "INMAA", "NLRTM", "20DRY") is NO_TABLE


def test_gate3_rejects_value_from_wrong_column():
    from datetime import date

    from logistics_rate_rag.guardrails.context import QuestionContext
    from logistics_rate_rag.guardrails.gate3_grounding import gate3_grounding
    from logistics_rate_rag.schema.candidate import RateCandidate

    chunk = CHUNKS["meridian_tariff_2026_h2#001"]
    row = next(ln for ln in chunk.text.splitlines() if "AEJEA Jebel Ali" in ln)
    ctx = QuestionContext(
        as_of=date(2026, 9, 1),
        mentions_surcharge=False,
        retrieved_ids=frozenset({chunk.chunk_id}),
        chunks_by_id={chunk.chunk_id: chunk},
        ranks_by_id={chunk.chunk_id: 1},
        similarity_by_id={chunk.chunk_id: 0.9},
        rerank_by_id={chunk.chunk_id: None},
    )

    def candidate(ctype: str, value: int) -> RateCandidate:
        return RateCandidate(
            answerable=True, carrier="MERIDIAN", origin="INMAA", destination="AEJEA",
            container_type=ctype, rate_value=value, currency="USD",
            valid_from=date(2026, 7, 1), valid_to=date(2026, 12, 31), includes_surcharge=True,
            source_doc="meridian_tariff_2026_h2.pdf", source_chunk_id=chunk.chunk_id,
            source_span=row, confidence=0.9,
        )  # fmt: skip

    good = gate3_grounding(candidate("40NOR", _rate("INMAA", "AEJEA", "40NOR")), ctx)
    assert good.passed
    swapped = gate3_grounding(candidate("40NOR", _rate("INMAA", "AEJEA", "40RH")), ctx)
    assert not swapped.passed
    assert swapped.reason == "ungrounded:cell"
