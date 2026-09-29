"""Build config/ports_unlocode.csv from the official UN/LOCODE list (D-49).

Source: UNECE UN/LOCODE release 2024-2, as republished by the DataHub
`datasets/un-locode` repository (ODC-PDDL-1.0, public domain), pinned to one
commit so the build is reproducible. UNECE's own download server refuses
scripted requests, which is why the mirror is used; its datapackage names
UNECE as the source.

Keeps every location whose Function has "1" (seaport) in position 1 and is
not marked for removal. Writes one row per LOCODE with the official name,
the ASCII name and the country, plus config/ports_unlocode.meta.json with
the source commit, sha256 of the downloaded file and the row counts.

    python scripts/build_port_registry.py            # download + build
    python scripts/build_port_registry.py --check    # verify the committed file
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "datasets/un-locode"
COMMIT = "b1309b37edea63334a819a78c22b8967f61c37ad"
URL = f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/data/code-list.csv"
RELEASE = "UN/LOCODE 2024-2"
OUT = ROOT / "config" / "ports_unlocode.csv"
META = ROOT / "config" / "ports_unlocode.meta.json"
FIELDS = ["locode", "name", "name_ascii", "country", "subdivision", "status", "coordinates"]


def fetch() -> bytes:
    req = urllib.request.Request(URL, headers={"User-Agent": "logistics-rate-rag"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def build(raw: bytes) -> tuple[list[dict], dict]:
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    ports: dict[str, dict] = {}
    for r in rows:
        if not r["Location"] or r["Function"][:1] != "1" or r["Change"] == "X":
            continue
        code = r["Country"] + r["Location"]
        entry = {
            "locode": code,
            "name": r["Name"],
            "name_ascii": r["NameWoDiacritics"],
            "country": r["Country"],
            "subdivision": r["Subdivision"],
            "status": r["Status"],
            "coordinates": r["Coordinates"],
        }
        # a few LOCODEs appear twice with alternative names: keep the first
        # row and fold the other name into name_ascii-style alias handling
        if code in ports:
            ports[code]["alt_names"] = [*ports[code].get("alt_names", []), r["Name"]]
            continue
        ports[code] = entry
    out = sorted(ports.values(), key=lambda e: e["locode"])
    meta = {
        "release": RELEASE,
        "source": f"https://github.com/{REPO}/blob/{COMMIT}/data/code-list.csv",
        "upstream": "https://unece.org/trade/cefact/UNLOCODE-Download",
        "licence": "ODC-PDDL-1.0 (public domain)",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "locations_in_source": len(rows),
        "seaports_kept": len(out),
        "filter": "Function position 1 == '1' (port) and Change != 'X'",
    }
    return out, meta


def write(entries: list[dict], meta: dict) -> None:
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\n")
    w.writerow([*FIELDS, "alt_names"])
    for e in entries:
        w.writerow([e[f] for f in FIELDS] + ["|".join(e.get("alt_names", []))])
    OUT.write_bytes(buf.getvalue().encode("utf-8"))
    META.write_bytes((json.dumps(meta, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="rebuild in memory, compare")
    args = ap.parse_args(argv)
    raw = fetch()
    entries, meta = build(raw)
    if args.check:
        committed = json.loads(META.read_text("utf-8"))
        ok = committed["sha256"] == meta["sha256"] and committed["seaports_kept"] == len(entries)
        print("CURRENT" if ok else "STALE", meta["sha256"][:16], len(entries))
        return 0 if ok else 1
    write(entries, meta)
    print(f"{RELEASE}: {meta['locations_in_source']} locations, {len(entries)} seaports -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
