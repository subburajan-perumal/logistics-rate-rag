"""Independent verification of data/eval/*.yaml against the corpus files.

Re-parses the three tariffs with pdfplumber / plain text / the csv module
(none of the package's loaders and none of generate_corpus.py's value
tables) and checks every expectation (docs/CORPUS.md §6, PLAN.md D-46):

- golden ANSWER: the question text names the key's carrier, both ports and
  the equipment (by code, display name, ISO code or alias); the expected
  value is exactly the cell for that lane and equipment in the expected
  document; currency, valid_to and BAF treatment match the document.
- golden NOT_ANSWER on a known lane: the cell is a dash or the carrier has
  no line for that equipment.
- adversarial must_not_contain: every listed value is a real corpus value
  other than a valid answer to the prompt (superseded, or another
  equipment's rate), or an invented number that appears nowhere.

Exit code 0 when everything holds; prints each check.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pdfplumber
import yaml

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "corpus"
DASH = "—"


def norm(s: str) -> str:
    s = s.lower()
    for ch in (*(chr(c) for c in (0x2019, 0x2018, 0x2032)), "`", '"'):
        s = s.replace(ch, "'")
    return " ".join(s.replace("-", " ").split())


def load_registry():
    eq = yaml.safe_load((ROOT / "config" / "equipment.yaml").read_text("utf-8"))["equipment"]
    ports = yaml.safe_load((ROOT / "config" / "ports.yaml").read_text("utf-8"))["ports"]
    eq_names = {c: [c, v["display_name"], *v["iso_codes"], *v["aliases"]] for c, v in eq.items()}
    port_names = {c: [c, v["city"], *v.get("aliases", [])] for c, v in ports.items()}
    return eq_names, port_names


def table_from_rows(rows: list[list[str]]) -> dict:
    header = rows[0]
    codes = header[2:-1]
    out = {}
    for r in rows[1:]:
        if r == header:
            continue
        o, d = r[0].split(" ")[0], r[1].split(" ")[0]
        out[(o, d)] = dict(zip(codes, r[2:-1], strict=True))
    return out


def parse_pdf(path: Path) -> tuple[dict, str]:
    rows: list[list[str]] = []
    text = ""
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
            for t in page.extract_tables():
                rows.extend([" ".join((c or "").split()) for c in r] for r in t)
    return table_from_rows(rows), text


def parse_md(path: Path) -> tuple[dict, str]:
    text = path.read_text("utf-8")
    rows = [
        [c.strip() for c in ln.strip().strip("|").split("|")]
        for ln in text.splitlines()
        if ln.startswith("| ") and not ln.startswith("|---")
    ]
    return table_from_rows(rows), text


def parse_csv(path: Path) -> tuple[dict, str]:
    text = path.read_text("utf-8")
    out: dict = {}
    for r in csv.DictReader(text.splitlines()):
        out.setdefault((r["origin_locode"], r["destination_locode"]), {})[r["container_type"]] = r[
            "base_rate"
        ]
    return out, text


def field(text: str, label: str) -> str:
    m = re.search(rf"{label}:? (\S+)", text)
    return m.group(1) if m else ""


def mentions(question: str, names: list[str]) -> bool:
    q = " " + norm(question) + " "
    return any(re.search(r"(?<![\w'])" + re.escape(norm(n)) + r"(?![\w])", q) for n in names if n)


def main() -> int:
    eq_names, port_names = load_registry()
    docs = {
        "meridian_tariff_2026_h2.pdf": parse_pdf(CORPUS / "meridian_tariff_2026_h2.pdf"),
        "meridian_tariff_2026_q2.md": parse_md(CORPUS / "meridian_tariff_2026_q2.md"),
        "halcyon_tariff_2026_h2.csv": parse_csv(CORPUS / "halcyon_tariff_2026_h2.csv"),
    }
    policy = (CORPUS / "rate_policy_note_2026.md").read_text("utf-8")
    all_values = {
        int(v.replace(",", ""))
        for table, _ in docs.values()
        for cells in table.values()
        for v in cells.values()
        if v != DASH
    }
    failures: list[str] = []

    def check(ok: bool, msg: str) -> None:
        print(("ok   " if ok else "FAIL ") + msg)
        if not ok:
            failures.append(msg)

    carrier_names = {"MERIDIAN": ["meridian"], "HALCYON": ["halcyon"]}
    doc_for = {"MERIDIAN": "meridian_tariff_2026_h2.pdf", "HALCYON": "halcyon_tariff_2026_h2.csv"}

    golden = yaml.safe_load((ROOT / "data" / "eval" / "golden.yaml").read_text("utf-8"))
    for q in golden["questions"]:
        e, k, text = q["expected"], q.get("key"), q["question"]
        if e["outcome"] == "ANSWER":
            table, doc_text = docs[e["source_doc"]]
            cell = table.get((k["origin"], k["destination"]), {}).get(k["container_type"])
            check(
                cell is not None and cell != DASH and int(cell.replace(",", "")) == e["rate_value"],
                f"{q['id']} value {e['rate_value']} is the {k['container_type']} cell "
                f"{k['origin']}->{k['destination']} in {e['source_doc']} (cell {cell!r})",
            )
            check(
                mentions(text, carrier_names[k["carrier"]])
                and mentions(text, port_names[k["origin"]])
                and mentions(text, port_names[k["destination"]])
                and mentions(text, eq_names[k["container_type"]]),
                f"{q['id']} question names carrier, both ports and {k['container_type']}",
            )
            if e["source_doc"].endswith(".csv"):
                currency = re.search(r",([A-Z]{3}),\d+,", doc_text).group(1)
                valid_to = re.search(r",(\d{4}-\d{2}-\d{2}),[^,\n]*$", doc_text, re.M).group(1)
            else:
                currency = field(doc_text, "Currency")
                valid_to = field(doc_text, "Valid to")
            check(
                currency == e["currency"] and valid_to == str(e["valid_to"]),
                f"{q['id']} currency {currency} / valid_to {valid_to}",
            )
            baf_in = k["carrier"] == "MERIDIAN"
            check(
                e["includes_surcharge"] == baf_in
                and ("included in every base rate" in policy)
                and ("is not included in the base rate" in policy),
                f"{q['id']} includes_surcharge={e['includes_surcharge']} per the policy note",
            )
        else:
            found = []
            for code, names in port_names.items():
                if mentions(text, names):
                    found.append(code)
            carrier = next((c for c, n in carrier_names.items() if mentions(text, n)), None)
            # the most specific name wins: "20' Tank" over the bare "20'"
            hits = [
                (len(norm(n)), c) for c, ns in eq_names.items() for n in ns if mentions(text, [n])
            ]
            ctype = max(hits)[1] if hits else None
            if carrier and ctype and len(found) == 2:
                table, _ = docs[doc_for[carrier]]
                lanes = [(a, b) for a in found for b in found if a != b and (a, b) in table]
                cells = [table[ln].get(ctype) for ln in lanes]
                check(
                    all(c in (None, DASH) for c in cells),
                    f"{q['id']} unanswerable: {carrier} {ctype} {found} -> {cells or 'no lane'}",
                )
            else:
                print(
                    f"skip {q['id']} unanswerable by construction (no port/carrier/equipment "
                    f"to look up: {carrier} {ctype} {found})"
                )

    adversarial = yaml.safe_load((ROOT / "data" / "eval" / "adversarial.yaml").read_text("utf-8"))
    q2_values = {
        int(v.replace(",", ""))
        for cells in docs["meridian_tariff_2026_q2.md"][0].values()
        for v in cells.values()
        if v != DASH
    }
    for a in adversarial["prompts"]:
        check(a["expected"]["outcome"] == "NOT_ANSWER", f"{a['id']} expects NOT_ANSWER")
        for v in a["expected"].get("must_not_contain") or []:
            where = (
                "superseded Q2 value" if v in q2_values
                else "a real corpus value (wrong equipment/lane)" if v in all_values
                else "an invented number, absent from the corpus"
            )  # fmt: skip
            ok = (
                (a["tag"] == "superseded") == (v in q2_values)
                or v not in all_values
                or (a["tag"] == "substitution" and v in all_values)
            )
            check(ok, f"{a['id']} ({a['tag']}) must_not_contain {v}: {where}")

    print(f"\n{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
