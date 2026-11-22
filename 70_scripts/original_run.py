"""Snapshot the September 2026 pipeline outputs and compare a later run to them.

Commands:
  python 70_scripts/original_run.py backup
  python 70_scripts/original_run.py compare
  python 70_scripts/original_run.py restore

Backup lives at 99_backup/original_run/. PDF full texts stay in
30_screening/32_exports/ (the scripts never rewrite those folders).
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from project_paths import CODE_ROOT  # noqa: E402

BACKUP_ROOT = CODE_ROOT / "99_backup"
ORIGINAL = BACKUP_ROOT / "original_run"
COMPARE_ROOT = BACKUP_ROOT / "compare"

COPY_DIRS = (
    "00_search",
    "10_data_raw",
    "20_data_clean",
    "30_screening",
    "40_extraction",
    "50_outputs",
    "60_prisma",
)
SKIP_DIR_NAMES = {"__pycache__", ".git"}
PDF_EXPORT_DIRS = {"must_cite", "other", "review", "review_uav"}
SKIP_SUFFIXES = {".pdf"}
PDF_PARENTS = (
    "30_screening/32_exports/must_cite",
    "30_screening/32_exports/other",
    "30_screening/32_exports/review",
    "30_screening/32_exports/review_uav",
)


def live_root(path: str | None = None) -> Path:
    """Always the manuscript project unless --live is passed.

    Do not follow REVIEW_DATA_ROOT: that may point at a runner test folder.
    """
    if path:
        return Path(path).expanduser().resolve()
    return CODE_ROOT


def _skip_rel(rel: Path) -> bool:
    parts = rel.parts
    if any(part in SKIP_DIR_NAMES for part in parts):
        return True
    if "32_exports" in parts and any(part in PDF_EXPORT_DIRS for part in parts):
        return True
    return False


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M")


def _cell(val) -> str:
    if val is None:
        return ""
    try:
        import pandas as pd
        if pd.isna(val):
            return ""
    except Exception:
        pass
    text = str(val).replace("\n", " ").strip()
    if text.lower() in {"nan", "none", "nat"}:
        return ""
    return text


def _norm_doi(val) -> str:
    text = _cell(val).lower()
    for prefix in (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    ):
        if text.startswith(prefix):
            text = text[len(prefix) :]
    return text.strip().rstrip(".")


def rec_key(doi, title, year) -> tuple[str, str]:
    d = _norm_doi(doi)
    if d:
        return ("doi", d)
    ti = _cell(title).lower()
    py = _cell(year)
    if "." in py:
        py = py.split(".")[0]
    return ("ty", f"{ti}||{py}")


def _pick(row, *names) -> str:
    for name in names:
        if name in row.index:
            return row[name]
    return ""


def row_key(row) -> tuple[str, str]:
    return rec_key(
        _pick(row, "DO", "DOI"),
        _pick(row, "TI", "Title"),
        _pick(row, "PY", "Year"),
    )


def row_label(row) -> dict:
    authors = _cell(_pick(row, "AU", "Authors"))
    if len(authors) > 80:
        authors = authors[:77] + "…"
    return {
        "key_kind": row_key(row)[0],
        "key": row_key(row)[1],
        "year": _cell(_pick(row, "PY", "Year")).split(".")[0],
        "authors": authors,
        "title": _cell(_pick(row, "TI", "Title")),
        "doi": _norm_doi(_pick(row, "DO", "DOI")),
    }


def _read_xlsx(path: Path, sheet=0):
    if path is None or not path.exists():
        return None
    import pandas as pd

    try:
        return pd.read_excel(path, sheet_name=sheet)
    except ValueError:
        return pd.read_excel(path, sheet_name=0)


def _index_rows(df) -> dict[tuple[str, str], dict]:
    out: dict[tuple[str, str], dict] = {}
    if df is None or df.empty:
        return out
    for _, row in df.iterrows():
        key = row_key(row)
        if key[1] in {"", "||"}:
            continue
        rec = row_label(row)
        rec["_row"] = row
        out.setdefault(key, rec)
    return out


def _copy_tree(src: Path, dest: Path) -> tuple[int, int]:
    n_files = 0
    n_bytes = 0
    dest.mkdir(parents=True, exist_ok=True)
    for path in src.rglob("*"):
        rel = path.relative_to(src)
        if _skip_rel(rel):
            continue
        if path.is_dir():
            (dest / rel).mkdir(parents=True, exist_ok=True)
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        n_files += 1
        n_bytes += path.stat().st_size
    return n_files, n_bytes


def _pdf_manifest(live: Path) -> list[dict]:
    rows = []
    for rel in PDF_PARENTS:
        folder = live / rel
        if not folder.exists():
            continue
        for pdf in sorted(folder.rglob("*.pdf")):
            rows.append(
                {
                    "path": str(pdf.relative_to(live)).replace("\\", "/"),
                    "bytes": pdf.stat().st_size,
                }
            )
    return rows


def cmd_backup(force: bool = False, live: str | None = None) -> int:
    live = live_root(live)
    if ORIGINAL.exists() and any(ORIGINAL.iterdir()) and not force:
        print(f"[ERROR] Backup already exists: {ORIGINAL}")
        print("        Pass --force only if you intend to replace it.")
        return 1
    if ORIGINAL.exists() and force:
        try:
            shutil.rmtree(ORIGINAL)
        except OSError:
            stamped = BACKUP_ROOT / f"original_run_replaced_{_stamp()}"
            ORIGINAL.rename(stamped)
            print(f"[WARN] Could not delete locked folder; moved it to {stamped.name}")
    ORIGINAL.mkdir(parents=True, exist_ok=True)
    total_files = 0
    total_bytes = 0
    copied = []
    for name in COPY_DIRS:
        src = live / name
        if not src.exists():
            print(f"[SKIP] {name} (missing)")
            continue
        n, b = _copy_tree(src, ORIGINAL / name)
        total_files += n
        total_bytes += b
        copied.append({"dir": name, "files": n, "bytes": b})
        print(f"[OK]   {name}: {n} files, {b / 1_048_576:.1f} MB")
    pdfs = _pdf_manifest(live)
    manifest = {
        "created": _now(),
        "source": str(live),
        "processing_report": "2026-09-06 (merge); screening from the same run",
        "copied": copied,
        "files": total_files,
        "bytes": total_bytes,
        "skipped_pdf_dirs": list(PDF_PARENTS),
        "pdfs_left_in_live_tree": len(pdfs),
        "pdfs": pdfs,
        "note": (
            "PDF full texts were not duplicated. They stay in "
            "30_screening/32_exports/{must_cite,review,review_uav,other}/. "
            "Pipeline scripts do not overwrite those folders."
        ),
    }
    (ORIGINAL / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nBackup: {ORIGINAL}")
    print(f"Files:  {total_files}  ({total_bytes / 1_048_576:.1f} MB)")
    print(f"PDFs:   {len(pdfs)} left in place (not copied)")
    return 0


def cmd_restore(yes: bool = False, live: str | None = None) -> int:
    if not ORIGINAL.exists():
        print(f"[ERROR] No backup at {ORIGINAL}")
        return 1
    live = live_root(live)
    if not yes:
        print("This writes the September 2026 tables back over:")
        for name in COPY_DIRS:
            print(f"  {live / name}")
        print("PDF folders are not touched.")
        ans = input("Type YES to restore: ").strip()
        if ans != "YES":
            print("Cancelled.")
            return 1
    for name in COPY_DIRS:
        src = ORIGINAL / name
        dest = live / name
        if not src.exists():
            continue
        dest.mkdir(parents=True, exist_ok=True)
        n, _b = _copy_tree(src, dest)
        print(f"[OK]   restored {name} ({n} files)")
    print("Done. PDF full texts were left as they were.")
    return 0


def _write_csv(path: Path, rows: list[dict], extra_fields: tuple[str, ...] = ()) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["key_kind", "key", "year", "authors", "title", "doi", *extra_fields]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def _diff_sets(old: dict, new: dict) -> tuple[list[dict], list[dict]]:
    added = [new[k] for k in new if k not in old]
    removed = [old[k] for k in old if k not in new]
    added.sort(key=lambda r: (r.get("year", ""), r.get("title", "")))
    removed.sort(key=lambda r: (r.get("year", ""), r.get("title", "")))
    return added, removed


def _changed_field(old: dict, new: dict, field: str, aliases: tuple[str, ...]) -> list[dict]:
    out = []
    for key in old:
        if key not in new:
            continue
        a = _cell(_pick(old[key]["_row"], *aliases))
        b = _cell(_pick(new[key]["_row"], *aliases))
        if a != b:
            rec = dict(new[key])
            rec["old"] = a
            rec["new"] = b
            rec["field"] = field
            out.append(rec)
    out.sort(key=lambda r: (r.get("year", ""), r.get("title", "")))
    return out


def _md_table(rows: list[dict], limit: int = 40) -> list[str]:
    if not rows:
        return ["(none)", ""]
    lines = [
        "| Year | Authors | Title | DOI |",
        "|---:|---|---|---|",
    ]
    for rec in rows[:limit]:
        title = rec.get("title", "").replace("|", "/")
        if len(title) > 90:
            title = title[:87] + "…"
        authors = rec.get("authors", "").replace("|", "/")
        lines.append(
            f"| {rec.get('year', '')} | {authors} | {title} | {rec.get('doi', '')} |"
        )
    if len(rows) > limit:
        lines.append(f"|  |  | … and {len(rows) - limit} more (see CSV) |  |")
    lines.append("")
    return lines


def _status_counts(df) -> dict[str, int]:
    if df is None or df.empty or "status" not in df.columns:
        return {}
    return {str(k): int(v) for k, v in df["status"].value_counts().items()}


def _decision_counts(df) -> dict[str, int]:
    if df is None or df.empty or "screening_decision" not in df.columns:
        return {}
    return {str(k): int(v) for k, v in df["screening_decision"].value_counts().items()}


class Stage:
    def __init__(self, name: str, live_path: Path | None, orig_path: Path | None, sheet=0):
        self.name = name
        self.live_path = live_path
        self.orig_path = orig_path
        self.live = _read_xlsx(live_path, sheet) if live_path else None
        self.orig = _read_xlsx(orig_path, sheet) if orig_path else None
        self.live_ix = _index_rows(self.live)
        self.orig_ix = _index_rows(self.orig)

    @property
    def ready(self) -> bool:
        return self.orig is not None

    @property
    def live_ready(self) -> bool:
        return self.live is not None


def cmd_compare(live: str | None = None) -> int:
    if not ORIGINAL.exists():
        print(f"[ERROR] No backup at {ORIGINAL}")
        print("        Run: python 70_scripts/original_run.py backup")
        return 1
    live = live_root(live)
    out_dir = COMPARE_ROOT / _stamp()
    out_dir.mkdir(parents=True, exist_ok=True)

    stages = {
        "merge_all": Stage(
            "Merge — all records",
            live / "20_data_clean" / "21_audit" / "all_records_with_status.xlsx",
            ORIGINAL / "20_data_clean" / "21_audit" / "all_records_with_status.xlsx",
        ),
        "clean": Stage(
            "Merge — clean_records (script kept)",
            live / "20_data_clean" / "clean_records.xlsx",
            ORIGINAL / "20_data_clean" / "clean_records.xlsx",
        ),
        "missing_doi": Stage(
            "Merge — missing DOI list",
            live / "20_data_clean" / "21_audit" / "missing_doi.xlsx",
            ORIGINAL / "20_data_clean" / "21_audit" / "missing_doi.xlsx",
        ),
        "original_kept": Stage(
            "Original kept list (1133)",
            ORIGINAL / "20_data_clean" / "21_audit" / "original_selection.xlsx",
            ORIGINAL / "20_data_clean" / "21_audit" / "original_selection.xlsx",
        ),
        "forward": Stage(
            "Audit — forward to screening",
            live / "20_data_clean" / "21_audit" / "forward_records.xlsx",
            ORIGINAL / "20_data_clean" / "21_audit" / "original_selection.xlsx",
        ),
        "screen": Stage(
            "Screening — non-review records",
            live / "30_screening" / "31_dataset" / "screened_records.xlsx",
            ORIGINAL / "30_screening" / "31_dataset" / "screened_records.xlsx",
        ),
        "reviews": Stage(
            "Screening — review articles",
            live / "30_screening" / "34_reviews" / "review_articles.xlsx",
            ORIGINAL / "30_screening" / "34_reviews" / "review_articles.xlsx",
        ),
        "must48": Stage(
            "Must-cite 48",
            live / "30_screening" / "32_exports" / "must_cite_list.xlsx",
            ORIGINAL / "30_screening" / "32_exports" / "must_cite_list.xlsx",
            sheet="48_must_cite",
        ),
        "must45": Stage(
            "Unique studies 45",
            live / "30_screening" / "32_exports" / "must_cite_list.xlsx",
            ORIGINAL / "30_screening" / "32_exports" / "must_cite_list.xlsx",
            sheet="45_unique_studies",
        ),
        "extract_refined": Stage(
            "Extraction — refined (include)",
            live / "40_extraction" / "41_input" / "extraction_input_refined.xlsx",
            ORIGINAL / "40_extraction" / "41_input" / "extraction_input_refined.xlsx",
        ),
        "extract_full": Stage(
            "Extraction — full (include + maybe)",
            live / "40_extraction" / "41_input" / "extraction_input_full.xlsx",
            ORIGINAL / "40_extraction" / "41_input" / "extraction_input_full.xlsx",
        ),
    }

    md: list[str] = [
        "# Porovnání nového běhu s původním (září 2026)",
        "",
        f"Live: `{live}`",
        f"Original: `{ORIGINAL}`",
        f"Written: `{_now()}`",
        "",
        "Identita článku = DOI (normalizované), jinak title + year.",
        "CSV u každého seznamu jsou v této složce.",
        "",
    ]

    orig_kept = stages["original_kept"]
    forward = stages["forward"]
    if forward.live_ready:
        added, removed = _diff_sets(orig_kept.orig_ix, forward.live_ix)
        md += [
            "## Články, které v novém běhu **přibyly** (jdou do screeningu, v původních 1133 nebyly)",
            "",
            f"**n = {len(added)}** (původní kept {len(orig_kept.orig_ix)} → forward {len(forward.live_ix)}; ubylo {len(removed)})",
            "",
        ]
        md += _md_table(added)
        _write_csv(out_dir / "ADDED_to_screening.csv", added)
        md += [
            "## Články, které z původních 1133 **nešly** do nového screeningu",
            "",
            f"**n = {len(removed)}**",
            "",
        ]
        md += _md_table(removed)
        _write_csv(out_dir / "REMOVED_from_screening.csv", removed)
    else:
        md += [
            "## Články navíc do screeningu",
            "",
            "Live `forward_records.xlsx` ještě není — Audit se neuložil. "
            "Po Save v kroku 5 se tady objeví přesný výčet (očekávaně záznamy bez DOI).",
            "",
        ]

    md += ["## Počty po krocích", "", "| Krok | Původní n | Nové n | Δ | Soubor nového běhu |", "|---|---:|---:|---:|---|"]

    for key, st in stages.items():
        if key == "original_kept":
            continue
        old_n = 0 if st.orig is None else len(st.orig)
        if not st.live_ready:
            md.append(f"| {st.name} | {old_n} | — | — | *(krok ještě neběžel)* |")
            continue
        new_n = len(st.live)
        delta = new_n - old_n
        sign = f"+{delta}" if delta > 0 else str(delta)
        rel = st.live_path.relative_to(live).as_posix() if st.live_path else ""
        md.append(f"| {st.name} | {old_n} | {new_n} | {sign} | `{rel}` |")
    md.append("")

    merge = stages["merge_all"]
    if merge.live_ready and merge.ready:
        old_s = _status_counts(merge.orig)
        new_s = _status_counts(merge.live)
        keys = sorted(set(old_s) | set(new_s))
        md += ["### Merge — status", "", "| Status | Původní | Nové | Δ |", "|---|---:|---:|---:|"]
        for k in keys:
            a, b = old_s.get(k, 0), new_s.get(k, 0)
            d = b - a
            md.append(f"| `{k}` | {a} | {b} | {d if d < 0 else f'+{d}'} |")
        md.append("")
        added, removed = _diff_sets(merge.orig_ix, merge.live_ix)
        changed = _changed_field(merge.orig_ix, merge.live_ix, "status", ("status",))
        _write_csv(out_dir / "merge_only_new.csv", added)
        _write_csv(out_dir / "merge_only_old.csv", removed)
        _write_csv(out_dir / "merge_status_changed.csv", changed, ("field", "old", "new"))
        md += [
            f"Jen v novém merge: **{len(added)}**. Jen v původním: **{len(removed)}**. "
            f"Stejný článek, jiné `status`: **{len(changed)}**.",
            "",
        ]
        if added:
            md += ["#### Jen v novém merge", ""] + _md_table(added)
        if changed:
            md += ["#### Změna status", "", "| Year | Title | DOI | Původní | Nové |", "|---:|---|---|---|---|"]
            for rec in changed[:40]:
                title = rec.get("title", "").replace("|", "/")[:80]
                md.append(
                    f"| {rec.get('year', '')} | {title} | {rec.get('doi', '')} | {rec.get('old', '')} | {rec.get('new', '')} |"
                )
            md.append("")

    miss = stages["missing_doi"]
    if miss.ready:
        md += ["### 22 záznamů bez DOI (původní seznam)", ""]
        md += _md_table(list(miss.orig_ix.values()), limit=30)
        _write_csv(out_dir / "original_missing_doi.csv", list(miss.orig_ix.values()))
        if miss.live_ready:
            added, removed = _diff_sets(miss.orig_ix, miss.live_ix)
            md.append(f"Nový seznam missing DOI: {len(miss.live_ix)} (přibylo {len(added)}, ubylo {len(removed)}).")
            md.append("")
            _write_csv(out_dir / "missing_doi_added.csv", added)
            _write_csv(out_dir / "missing_doi_removed.csv", removed)

    screen = stages["screen"]
    if screen.live_ready and screen.ready:
        old_d = _decision_counts(screen.orig)
        new_d = _decision_counts(screen.live)
        md += ["### Screening — rozhodnutí", "", "| Rozhodnutí | Původní | Nové | Δ |", "|---|---:|---:|---:|"]
        for k in sorted(set(old_d) | set(new_d)):
            a, b = old_d.get(k, 0), new_d.get(k, 0)
            d = b - a
            md.append(f"| {k} | {a} | {b} | {d if d < 0 else f'+{d}'} |")
        md.append("")
        added, removed = _diff_sets(screen.orig_ix, screen.live_ix)
        changed = _changed_field(
            screen.orig_ix, screen.live_ix, "screening_decision", ("screening_decision",)
        )
        _write_csv(out_dir / "screen_only_new.csv", added)
        _write_csv(out_dir / "screen_only_old.csv", removed)
        _write_csv(
            out_dir / "screen_decision_changed.csv", changed, ("field", "old", "new")
        )
        md += [
            f"Nové non-review záznamy (v původním screeningu nebyly): **{len(added)}**.",
            "",
        ]
        md += _md_table(added)
        if added:
            with_dec = []
            for rec in added:
                row = rec.get("_row")
                item = dict(rec)
                item["decision"] = _cell(_pick(row, "screening_decision")) if row is not None else ""
                item["score"] = _cell(_pick(row, "relevance_score")) if row is not None else ""
                item["must_cite"] = _cell(_pick(row, "must_cite")) if row is not None else ""
                with_dec.append(item)
            _write_csv(
                out_dir / "screen_only_new.csv",
                with_dec,
                ("decision", "score", "must_cite"),
            )
            md += ["Rozhodnutí u přidaných:", ""]
            for rec in with_dec:
                md.append(
                    f"- {rec.get('year', '')} — {rec.get('title', '')[:80]} "
                    f"→ **{rec.get('decision', '')}** (score {rec.get('score', '')}, "
                    f"must-cite {rec.get('must_cite', '')})"
                )
            md.append("")
        if changed:
            md.append(f"Stejný článek, jiné rozhodnutí: **{len(changed)}**.")
            md.append("")

    for key, label in (("must48", "must-cite 48"), ("must45", "45 unique studies")):
        st = stages[key]
        if not (st.live_ready and st.ready):
            if st.ready and not st.live_ready:
                md += [f"### {label}", "", "Nový soubor ještě není.", ""]
            continue
        added, removed = _diff_sets(st.orig_ix, st.live_ix)
        _write_csv(out_dir / f"{key}_added.csv", added)
        _write_csv(out_dir / f"{key}_removed.csv", removed)
        md += [
            f"### {label}",
            "",
            f"Původní {len(st.orig_ix)} → nové {len(st.live_ix)}. "
            f"Přibylo **{len(added)}**, ubylo **{len(removed)}**.",
            "",
        ]
        if added:
            md += ["**Nové v této množině (musíte vědět které):**", ""] + _md_table(added)
        if removed:
            md += ["**Už v ní nejsou:**", ""] + _md_table(removed)

    reviews = stages["reviews"]
    if reviews.live_ready and reviews.ready:
        added, removed = _diff_sets(reviews.orig_ix, reviews.live_ix)
        _write_csv(out_dir / "reviews_added.csv", added)
        _write_csv(out_dir / "reviews_removed.csv", removed)
        md += [
            "### Review články",
            "",
            f"Původní {len(reviews.orig_ix)} → nové {len(reviews.live_ix)}. "
            f"Přibylo {len(added)}, ubylo {len(removed)}.",
            "",
        ]
        if added:
            md += _md_table(added)

    report = out_dir / "summary.md"
    report.write_text("\n".join(md) + "\n", encoding="utf-8")
    latest = COMPARE_ROOT / "latest.md"
    latest.write_text(report.read_text(encoding="utf-8"), encoding="utf-8")
    print(report.read_text(encoding="utf-8"))
    print(f"\nReport: {report}")
    print(f"Copy:   {latest}")
    print(f"CSV:    {out_dir}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("backup", help="Copy current pipeline outputs to 99_backup/original_run/")
    b.add_argument("--force", action="store_true", help="Replace an existing backup")
    b.add_argument("--live", help="Project folder to copy from (default: this review repo)")
    c = sub.add_parser("compare", help="Diff live folders against the backup")
    c.add_argument("--live", help="Project folder to compare (default: this review repo)")
    r = sub.add_parser("restore", help="Copy the backup back over the live folders")
    r.add_argument("--yes", action="store_true", help="Do not ask for YES")
    r.add_argument("--live", help="Project folder to restore into (default: this review repo)")
    args = p.parse_args()
    if args.cmd == "backup":
        return cmd_backup(force=args.force, live=args.live)
    if args.cmd == "compare":
        return cmd_compare(live=args.live)
    if args.cmd == "restore":
        return cmd_restore(yes=args.yes, live=args.live)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
