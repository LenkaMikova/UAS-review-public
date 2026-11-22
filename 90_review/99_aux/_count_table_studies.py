"""Count data rows and citation keys in body + appendix tables.

Writes a JSON summary next to this script (not committed as a product).
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import openpyxl

AUX = Path(__file__).resolve().parent
HERE = AUX.parent
ROOT = HERE.parent
BODY = HERE / "review.qmd"
APPENDIX = HERE / "92_appendix" / "_online-resources.qmd"
SCREEN = ROOT / "30_screening" / "31_dataset" / "screened_records.xlsx"
REVIEWS = ROOT / "30_screening" / "34_reviews" / "review_articles.xlsx"
OUT = AUX / "_table_counts.json"

CITE = re.compile(r"@([A-Za-z][A-Za-z0-9_]+)")
CAPTION = re.compile(r"^:\s+.*\{#(tbl-[a-z0-9-]+)\}", re.M)
OR_ID = re.compile(r"^::: \{#(or-[a-z0-9-]+)\}", re.M)


def first_author_year_keys(au: str, py) -> set[str]:
    if not au or py is None:
        return set()
    year = str(py).strip()[:4]
    if not year.isdigit():
        return set()
    lead = str(au).split(";")[0]
    lead = lead.split(",")[0].strip()
    parts = re.split(r"[\s\-]+", lead)
    # Garcia Rodriguez 2026 -> GarciaRodriguez2026 and Garcia2026
    compact = "".join(p for p in parts if p)
    compact = re.sub(r"[^A-Za-z]", "", compact)
    last = re.sub(r"[^A-Za-z]", "", parts[-1] if parts else "")
    keys = set()
    if compact:
        keys.add(compact + year)
    if last:
        keys.add(last + year)
    return keys


def load_flags() -> tuple[set[str], set[str], set[str]]:
    must, core, review = set(), set(), set()

    def ingest(path: Path, is_review_file: bool = False):
        if not path.exists():
            return
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        rows = ws.iter_rows(values_only=True)
        header = [str(h) if h is not None else "" for h in next(rows)]
        idx = {h: i for i, h in enumerate(header)}
        au_i, py_i = idx.get("AU"), idx.get("PY")
        mc_i = idx.get("must_cite")
        st_i = idx.get("must_cite_strict")
        rv_i = idx.get("is_review")
        for row in rows:
            au = row[au_i] if au_i is not None else None
            py = row[py_i] if py_i is not None else None
            keys = first_author_year_keys(au, py)
            if is_review_file or (rv_i is not None and row[rv_i] in (True, "True", 1)):
                review.update(keys)
            if mc_i is not None and row[mc_i] in (True, "True", 1):
                must.update(keys)
            if st_i is not None and row[st_i] in (True, "True", 1):
                core.update(keys)
        wb.close()

    ingest(SCREEN)
    ingest(REVIEWS, is_review_file=True)
    return must, core, review


def split_tables(text: str, kind: str) -> list[dict]:
    """kind: body (caption after table) or or (div id then table)."""
    tables = []
    if kind == "or":
        parts = re.split(r"(?=^::: \{#or-)", text, flags=re.M)
        for part in parts:
            m = OR_ID.search(part)
            if not m:
                continue
            label = m.group(1)
            # first markdown table in the div
            tm = re.search(r"^\|.+\|\s*$", part, re.M)
            if not tm:
                tables.append({"label": label, "rows": 0, "keys": [], "kind": "or", "has_table": False})
                continue
            block = part[tm.start():]
            lines = []
            for line in block.splitlines():
                if line.startswith("|"):
                    lines.append(line)
                elif lines:
                    break
            data = [ln for ln in lines[2:] if not re.match(r"^\|\s*:?-+:?[\s\|:-]*\|$", ln)]
            keys = []
            for ln in data:
                keys.extend(CITE.findall(ln))
            tables.append({
                "label": label,
                "rows": len(data),
                "keys": sorted(set(keys)),
                "kind": "or",
                "has_table": True,
            })
        return tables

    # body: consecutive pipe-rows, then a Quarto caption `{#tbl-...}`
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if not lines[i].startswith("|"):
            i += 1
            continue
        block = []
        while i < len(lines) and lines[i].startswith("|"):
            block.append(lines[i])
            i += 1
        j = i
        while j < len(lines) and not lines[j].strip():
            j += 1
        cap = None
        if j < len(lines):
            cap = re.search(r"^:\s+.*\{#(tbl-[a-z0-9-]+)\}", lines[j])
        if not cap:
            continue
        data = [ln for ln in block[2:] if not re.match(r"^\|\s*:?-+:?[\s\|:-]*\|$", ln)]
        keys = []
        for ln in data:
            keys.extend(CITE.findall(ln))
        tables.append({
            "label": cap.group(1),
            "rows": len(data),
            "keys": sorted(set(keys)),
            "kind": "body",
            "has_table": True,
        })
    return tables


def classify_keys(keys: list[str], must: set[str], core: set[str], review: set[str]) -> dict:
    mc, cr, rv, other = [], [], [], []
    for k in keys:
        in_must = k in must
        in_core = k in core
        in_rev = k in review
        # also try stripping trailing a/b
        k2 = re.sub(r"[a-z]$", "", k) if k[-1:].islower() and k[-2:-1].isdigit() else k
        in_must = in_must or k2 in must
        in_core = in_core or k2 in core
        in_rev = in_rev or k2 in review
        if in_rev:
            rv.append(k)
        elif in_core:
            cr.append(k)
        elif in_must:
            mc.append(k)
        else:
            other.append(k)
    return {
        "n_cite": len(keys),
        "must_cite_extended": sorted(set(mc + cr)),
        "must_cite_core": sorted(set(cr)),
        "review": sorted(set(rv)),
        "other": sorted(set(other)),
    }


def main():
    must, core, review = load_flags()
    body = split_tables(BODY.read_text(encoding="utf-8"), "body")
    appendix = split_tables(APPENDIX.read_text(encoding="utf-8"), "or")
    all_tables = body + appendix
    for t in all_tables:
        t["class"] = classify_keys(t["keys"], must, core, review)
        t.pop("keys")

    out = {
        "must_cite_n": len(must),
        "core_n": len(core),
        "review_flag_n": len(review),
        "tables": all_tables,
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"must={len(must)} core={len(core)} review_keys={len(review)}")
    for t in all_tables:
        c = t["class"]
        print(
            f"{t['kind']:4} {t['label']:22} rows={t['rows']:3}  "
            f"cites={c['n_cite']:3}  must={len(c['must_cite_extended']):2}  "
            f"core={len(c['must_cite_core']):2}  rev={len(c['review']):2}  "
            f"other={len(c['other']):2}  {c['other'][:8]}"
        )


if __name__ == "__main__":
    main()
