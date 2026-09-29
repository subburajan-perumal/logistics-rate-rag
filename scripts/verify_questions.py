"""Independent verification of data/eval/*.yaml against the corpus files.

Re-parses every tariff with pdfplumber / plain text / the csv module (none of
the package's loaders and none of generate_corpus.py's value tables) and
checks every expectation (docs/CORPUS.md §6, PLAN.md D-46, D-50). The only
package import is the port registry (config, not corpus data), so a question
that says "JNPT" or "Port of Felixstowe" is matched the way a user's would be.

- golden ANSWER: the question names the key's carrier, both ports and the
  equipment (code, display name, ISO code or alias); the expected value is
  exactly that carrier's cell for the lane and equipment in the expected
  document; the currency is that line's own currency; valid_to is the
  document's; the as-of date falls inside that document's validity window and
  no other document of the carrier is in force then; BAF treatment matches
  the policy note's carrier list and the document itself.
- golden NOT_ANSWER on a named lane: every document of the carrier in force
  at the as-of date has a dash or no line for that equipment.
- adversarial must_not_contain, judged per lane (D-50): a superseded value is
  that lane's cell in a SUPERSEDED document and differs from the current
  cell; a substitution value is the carrier's current cell for another
  equipment on a lane where the requested equipment is a dash; any other
  value is invented, i.e. not a cell of any carrier on the lane named.

Exit code 0 when everything holds; prints each check.
"""

from __future__ import annotations

import csv
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from logistics_rate_rag.config import load_ports  # noqa: E402

CORPUS = ROOT / "data" / "corpus"
DASH = "—"
MAX_NGRAM = 6


def norm(s: str) -> str:
    s = s.lower()
    for ch in (*(chr(c) for c in (0x2019, 0x2018, 0x2032)), "`", '"'):
        s = s.replace(ch, "'")
    return " ".join(s.replace("-", " ").split())


def _token(t: str) -> str:
    """Drop sentence dots and possessives ("meridian's", "lines'") but keep a
    foot mark after a digit ("20'")."""
    t = re.sub(r"'s$", "", t.strip("."))
    return re.sub(r"(?<=[a-z])'$", "", t)


def tokens(text: str) -> list[str]:
    return [t for t in map(_token, re.split(r"[\s,?:;!\u2014\u2013]+", norm(text))) if t]


def ngrams(text: str) -> set[str]:
    t = tokens(text)
    return {" ".join(t[i : i + n]) for n in range(1, MAX_NGRAM + 1) for i in range(len(t) - n + 1)}


@dataclass
class Doc:
    name: str
    carrier: str
    status: str
    valid_from: str
    valid_to: str
    baf_included: bool
    # (origin, destination) -> {"currency": ..., equipment code: cell text}
    lanes: dict = field(default_factory=dict)

    def cell(self, o: str, d: str, ctype: str) -> str | None:
        return self.lanes.get((o, d), {}).get(ctype)

    def in_force(self, as_of: str) -> bool:
        return self.valid_from <= as_of <= self.valid_to


def header_field(text: str, label: str) -> str:
    m = re.search(rf"{re.escape(label)}:? (\S+)", text)
    return m.group(1) if m else ""


def from_table(name: str, rows: list[list[str]], text: str) -> Doc:
    header = rows[0]
    assert header[:3] == ["Origin", "Destination", "Currency"], (name, header)
    codes = header[3:-1]
    lanes = {}
    for r in rows[1:]:
        if r == header:
            continue
        cells = dict(zip(codes, r[3:-1], strict=True))
        cells["currency"] = r[2]
        lanes[(r[0].split(" ")[0], r[1].split(" ")[0])] = cells
    carrier = re.search(r"Carrier: .*\((\w+)\)", text).group(1)
    baf = re.search(r"Bunker Adjustment Factor \(BAF\): (.*)", text).group(1)
    return Doc(
        name=name,
        carrier=carrier,
        status=header_field(text, "Status"),
        valid_from=header_field(text, "Valid from"),
        valid_to=header_field(text, "Valid to"),
        baf_included=baf.startswith("included"),
        lanes=lanes,
    )


def parse_pdf(path: Path) -> Doc:
    rows: list[list[str]] = []
    text = ""
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
            for t in page.extract_tables():
                rows.extend([" ".join((c or "").split()) for c in r] for r in t)
    return from_table(path.name, rows, text)


def parse_md(path: Path) -> Doc:
    text = path.read_text("utf-8")
    rows = [
        [c.strip() for c in ln.strip().strip("|").split("|")]
        for ln in text.splitlines()
        if ln.startswith("| ") and not ln.startswith("|---")
    ]
    return from_table(path.name, rows, text)


def parse_csv(path: Path) -> Doc:
    lines = list(csv.DictReader(path.read_text("utf-8").splitlines()))
    lanes: dict = {}
    for r in lines:
        cells = lanes.setdefault((r["origin_locode"], r["destination_locode"]), {})
        cells[r["container_type"]] = r["base_rate"]
        # a CSV states currency per line; one lane's lines share it
        assert cells.setdefault("currency", r["currency"]) == r["currency"], (path.name, r)
    first = lines[0]
    assert {(r["carrier"], r["valid_from"], r["valid_to"]) for r in lines} == {
        (first["carrier"], first["valid_from"], first["valid_to"])
    }, path.name
    return Doc(
        name=path.name,
        carrier=first["carrier"],
        status="CURRENT",
        valid_from=first["valid_from"],
        valid_to=first["valid_to"],
        baf_included=not any(r["baf"] for r in lines) and "baf" not in first,
        lanes=lanes,
    )


def parse(path: Path) -> Doc:
    return {".pdf": parse_pdf, ".md": parse_md, ".csv": parse_csv}[path.suffix](path)


def value(cell: str | None) -> int | None:
    return None if cell in (None, DASH) else int(cell.replace(",", ""))


def policy_baf_carriers(policy: str) -> set[str]:
    """Display-name first words from the note's "X, Y and Z include the Bunker
    Adjustment Factor" sentence."""
    m = re.search(r"\n([A-Z][\w ,]+?) include the Bunker Adjustment Factor", policy)
    return {w.lower() for w in re.split(r",\s*|\s+and\s+", m.group(1))}


def main() -> int:
    eq = yaml.safe_load((ROOT / "config" / "equipment.yaml").read_text("utf-8"))["equipment"]
    carriers = yaml.safe_load((ROOT / "config" / "carriers.yaml").read_text("utf-8"))["carriers"]
    ports = load_ports(ROOT / "config")

    eq_names = {c: {norm(n) for n in (c, v["display_name"], *v["iso_codes"], *v["aliases"])}
                for c, v in eq.items()}  # fmt: skip
    carrier_names = {c: {norm(n) for n in (c, v["display_name"], *v["aliases"])}
                     for c, v in carriers.items()}  # fmt: skip
    # name -> every LOCODE it can mean; "Manzanillo" or "Sydney" name several
    # ports, and the documents decide which lane a question means
    port_of: dict[str, set[str]] = {}
    for name, code in ports.city_lower.items():
        port_of.setdefault(norm(name), set()).add(code)
    for name, codes in ports.ambiguous_lower.items():
        port_of.setdefault(norm(name), set()).update(codes)
    for c in ports.locode:
        port_of.setdefault(norm(c), set()).add(c)

    docs = {p.name: parse(p) for p in sorted(CORPUS.iterdir()) if "tariff" in p.name}
    by_carrier: dict[str, list[Doc]] = {}
    for d in docs.values():
        by_carrier.setdefault(d.carrier, []).append(d)
    policy = (CORPUS / "rate_policy_note_2026.md").read_text("utf-8")
    baf_in_policy = policy_baf_carriers(policy)
    print(f"parsed {len(docs)} tariffs, {sum(len(d.lanes) for d in docs.values())} lanes; "
          f"policy BAF-included carriers: {sorted(baf_in_policy)}")  # fmt: skip

    failures: list[str] = []

    def check(ok: bool, msg: str) -> None:
        print(("ok   " if ok else "FAIL ") + msg)
        if not ok:
            failures.append(msg)

    def equipment_in(text: str) -> str | None:
        """The most specific equipment named: "20' Tank" over the bare "20'"."""
        grams = ngrams(text)
        hits = [(len(n), c) for c, ns in eq_names.items() for n in ns & grams]
        return max(hits)[1] if hits else None

    def found_in(text: str, pool: list[Doc]) -> tuple[str | None, tuple | None, str | None]:
        """Carrier, the (origin, destination) lane and the equipment named. Port
        names are read left to right, longest first; an ambiguous name keeps
        all its LOCODEs and the lane is the combination a document in `pool`
        (or, failing that, any document) actually has."""
        grams = ngrams(text)
        carrier = next((c for c, ns in carrier_names.items() if ns & grams), None)
        toks = tokens(text)
        found: list[set[str]] = []
        i = 0
        while i < len(toks):
            for n in range(min(MAX_NGRAM, len(toks) - i), 0, -1):
                codes = port_of.get(" ".join(toks[i : i + n]))
                if codes and not (n == 1 and toks[i] in {"to", "from", "in", "of", "the"}):
                    found.append(codes)
                    i += n
                    break
            else:
                i += 1
        lane = None
        if len(found) >= 2:
            combos = [(o, d) for o in sorted(found[0]) for d in sorted(found[1]) if o != d]
            if carrier:
                pool = by_carrier[carrier]
            lane = next((ln for ln in combos if any(ln in x.lanes for x in pool)),
                        next((ln for ln in combos if any(ln in x.lanes for x in docs.values())),
                             combos[0] if len(combos) == 1 else None))  # fmt: skip
        return carrier, lane, equipment_in(text)

    def lanes_meant(text: str, doc: Doc) -> list[tuple[str, str]]:
        """Every lane of `doc` the question's port names could mean, origin
        named first, reading an ambiguous name as all its LOCODEs ("Manzanillo"
        is MX and PA)."""
        toks = tokens(text)
        first: dict[str, int] = {}  # LOCODE -> earliest token position named
        for n in range(1, MAX_NGRAM + 1):
            for i in range(len(toks) - n + 1):
                for code in port_of.get(" ".join(toks[i : i + n]), ()):
                    first[code] = min(first.get(code, i), i)
        return sorted(
            ln for ln in doc.lanes
            if ln[0] in first and ln[1] in first and first[ln[0]] < first[ln[1]]
        )  # fmt: skip

    def names_ok(text: str, carrier: str, o: str, d: str, ctype: str) -> bool:
        grams = ngrams(text)
        return bool(
            carrier_names[carrier] & grams
            and any(o in port_of[g] for g in grams if g in port_of)
            and any(d in port_of[g] for g in grams if g in port_of)
            and eq_names[ctype] & grams
        )

    golden = yaml.safe_load((ROOT / "data" / "eval" / "golden.yaml").read_text("utf-8"))
    for q in golden["questions"]:
        e, k, text, as_of = q["expected"], q.get("key"), q["question"], str(q["as_of"])
        if e["outcome"] == "ANSWER":
            doc = docs[e["source_doc"]]
            o, d, ct = k["origin"], k["destination"], k["container_type"]
            cell = doc.cell(o, d, ct)
            check(
                doc.carrier == k["carrier"] and value(cell) == e["rate_value"],
                f"{q['id']} value {e['rate_value']} is {k['carrier']}'s {ct} cell {o}->{d} "
                f"in {doc.name} (cell {cell!r})",
            )
            check(names_ok(text, k["carrier"], o, d, ct),
                  f"{q['id']} question names carrier, both ports and {ct}")  # fmt: skip
            meant = lanes_meant(text, doc)
            check(meant == [(o, d)], f"{q['id']} port names mean one lane in {doc.name}: {meant}")
            currency = doc.lanes.get((o, d), {}).get("currency")
            check(
                currency == e["currency"] and doc.valid_to == str(e["valid_to"]),
                f"{q['id']} line currency {currency} / valid_to {doc.valid_to}",
            )
            live = [x.name for x in by_carrier[k["carrier"]] if x.in_force(as_of)]
            check(live == [doc.name], f"{q['id']} as_of {as_of}: in force {live}")
            first_word = carriers[k["carrier"]]["display_name"].split()[0].lower()
            check(
                e["includes_surcharge"] == doc.baf_included == (first_word in baf_in_policy),
                f"{q['id']} includes_surcharge={e['includes_surcharge']} per document and policy",
            )
            if q["tag"] == "cross":
                check(e.get("policy_source_required") is True,
                      f"{q['id']} cross question requires the policy source")  # fmt: skip
        else:
            carrier, lane, ctype = found_in(text, [])
            if carrier and ctype and lane:
                live = [x for x in by_carrier[carrier] if x.in_force(as_of)]
                o, d = lane
                cells = [x.cell(o, d, ctype) for x in live]
                check(
                    all(c in (None, DASH) for c in cells),
                    f"{q['id']} unanswerable: {carrier} {ctype} {o}->{d} -> {cells}",
                )
            else:
                print(
                    f"skip {q['id']} unanswerable by construction (no lane to look up: "
                    f"{carrier} {ctype} {lane})"
                )

    adversarial = yaml.safe_load((ROOT / "data" / "eval" / "adversarial.yaml").read_text("utf-8"))
    for a in adversarial["prompts"]:
        check(a["expected"]["outcome"] == "NOT_ANSWER", f"{a['id']} expects NOT_ANSWER")
        carrier, lane, ctype = found_in(a["question"], list(docs.values()))
        pool = by_carrier.get(carrier, []) if carrier else list(docs.values())
        for v in a["expected"].get("must_not_contain") or []:
            if a["tag"] == "superseded":
                old = [x for x in pool if x.status.startswith("SUPERSEDED")]
                cur = [x for x in pool if x.status == "CURRENT"]
                ok = bool(lane and ctype) and any(value(x.cell(*lane, ctype)) == v for x in old) \
                    and all(value(x.cell(*lane, ctype)) != v for x in cur)  # fmt: skip
                where = f"superseded {carrier} {ctype} {lane}, not the current cell"
            elif a["tag"] == "substitution":
                cur = [x for x in pool if x.status == "CURRENT" and x.in_force(str(a["as_of"]))]
                m = re.search(r"lists no (.+?) rate", a["question"])
                want = equipment_in(m.group(1)) if m else None
                ok = bool(lane and want) and any(
                    x.cell(*lane, want) in (None, DASH)
                    and v in {value(c) for k2, c in x.lanes.get(lane, {}).items()
                              if k2 not in ("currency", want)}
                    for x in cur
                )  # fmt: skip
                where = f"{carrier}'s other-equipment cell on {lane}; {want} is a dash"
            else:
                cells = {
                    value(c)
                    for x in pool
                    for ln in ([lane] if lane else list(x.lanes))
                    for k2, c in x.lanes.get(ln, {}).items()
                    if k2 != "currency"
                }
                ok = v not in cells
                who, where_lane = carrier or "any carrier", lane or "any lane"
                where = f"invented: not a cell of {who} on {where_lane}"
            check(ok, f"{a['id']} ({a['tag']}) must_not_contain {v}: {where}")

    print(f"\n{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
