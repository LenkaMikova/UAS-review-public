"""Helpers. Data always go to REVIEW_DATA_ROOT when the runner has set it."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from project_paths import CODE_ROOT, ENV_DATA_ROOT, data_root  # noqa: E402

from catalog import (
    AFTER_MANUAL_CHECK,
    DATABASE_ALIASES,
    DEFAULT_SETTINGS,
    MANUAL_CHECK_UPLOADS,
    PREVIEW_COLUMNS,
    SCRIPT_OUTPUTS,
    STEPS,
    format_type_counts,
    publication_type_counts,
    publication_type_label,
)
import record_audit

RUNNER = Path(__file__).resolve().parent
SCREEN_CFG_SHIPPED = SCRIPTS / "pipeline" / "screening_config.json"


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def set_data_root(path: Path) -> Path:
    root = path.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    os.environ[ENV_DATA_ROOT] = str(root)
    marker = root / "review_run.json"
    if not marker.exists():
        write_json(marker, {"started": now()})
    return root


def has_data_root() -> bool:
    return bool(os.environ.get(ENV_DATA_ROOT, "").strip())


def journal_path() -> Path:
    if has_data_root():
        return data_root() / "run_journal.jsonl"
    return RUNNER / "journal.jsonl"


def journal(step: str, action: str, ok: bool, detail: str = "", seconds: float | None = None) -> None:
    path = journal_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"ts": now(), "step": step, "action": action, "ok": ok, "detail": detail}
    if seconds is not None:
        row["seconds"] = round(seconds, 2)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def note_protocol(
    kind: str,
    summary: str,
    *,
    records: list[str] | None = None,
    files: list[str] | None = None,
    extra: dict | None = None,
) -> None:
    """Write one data-work event into the executed protocol (from RIS upload onward)."""
    if not has_data_root():
        return
    try:
        import protocol_export
        protocol_export.append_data_work(
            kind, summary, records=records, files=files, extra=extra,
        )
    except Exception:
        return


def _record_label_row(rec) -> str:
    year = str(rec.get("PY") or rec.get("Year") or "").strip()
    title = str(rec.get("TI") or rec.get("Title") or "").strip()
    doi = str(rec.get("DO") or rec.get("DOI") or "").strip()
    src = str(rec.get("Source") or "").strip()
    bit = f"{year} {title}".strip() or "(no title)"
    extra = [x for x in (src, doi) if x and x.lower() not in {"nan", "none"}]
    if extra:
        bit += " [" + "; ".join(extra) + "]"
    return bit


def _labels_for_status(*statuses: str, limit: int = 80) -> list[str]:
    path = p("20_data_clean", "21_audit", "all_records_with_status.xlsx")
    if not path.exists():
        return []
    try:
        import pandas as pd
        df = pd.read_excel(path)
    except Exception:
        return []
    if "status" not in df.columns:
        return []
    want = {s.lower() for s in statuses}
    mask = df["status"].astype(str).str.strip().str.lower().isin(want)
    rows = df.loc[mask]
    out = []
    for _, rec in rows.head(limit).iterrows():
        out.append(_record_label_row(rec))
    extra = int(len(rows) - len(out))
    if extra > 0:
        out.append(f"… and {extra} more")
    return out


def _note_script_protocol(rel_under_scripts: str) -> None:
    name = Path(rel_under_scripts).name
    if name == "merge_and_classify.py":
        auto = read_json(p("20_data_clean", "21_audit", "exclusion_log.json"), {}) or {}
        books = _labels_for_status("non_article_type")
        records = [
            f"retained {auto.get('retained')}, removed {auto.get('removed')}",
        ]
        for e in auto.get("entries") or []:
            records.append(
                f"{e.get('status')}: n={e.get('n')} — {e.get('reason')}"
            )
        if books:
            records.append("Books / e-books removed (exact records):")
            records.extend(books)
        note_protocol(
            "merge",
            "Merged RIS files. Duplicates and books classified; records without a DOI kept.",
            records=records,
            files=[
                "20_data_clean/21_audit/exclusion_log.json",
                "20_data_clean/21_audit/processing_report.txt",
            ],
        )
        return
    if name == "screening_and_deep_classify.py":
        summary = p("30_screening", "33_reports", "screening_summary.txt")
        records = []
        if summary.exists():
            records = [
                line.strip()
                for line in summary.read_text(encoding="utf-8", errors="replace").splitlines()
                if line.strip()
            ][:40]
        note_protocol(
            "screen",
            "Ran screening. Reviews set aside; include / maybe / exclude from scores.",
            records=records,
            files=["30_screening/33_reports/screening_summary.txt"],
        )
        return
    if name == "extraction_templ.py":
        note_protocol(
            "extract_templates",
            "Wrote extraction Excel templates from the current (recoded) screening table.",
            files=[
                "40_extraction/41_input/extraction_input_full.xlsx",
                "40_extraction/41_input/extraction_input_refined.xlsx",
            ],
        )


def _note_extract_recode(data: dict) -> None:
    entries = list(data.get("entries") or [])
    last = entries[-1] if entries else {}
    batch = [e for e in entries if e.get("ts") == last.get("ts")]
    records = []
    for e in batch:
        label = e.get("label") or ""
        action = e.get("action") or ""
        if action == "remove":
            what = f"removed from {e.get('from_group')} → unclassified"
        elif action == "assign":
            what = f"assigned → {e.get('to_group')}"
        elif action == "clear_flag":
            what = f"cleared flag {e.get('from_group')}"
        else:
            what = action
        records.append(f"{what}: {label}")
    note_protocol(
        "extract_recode",
        f"Extraction recode: {len(batch)} record(s). Script Excel not replaced.",
        records=records,
        files=["40_extraction/43_recode/extract_recodes.txt"],
    )


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def read_text(path: Path, limit: int = 80_000) -> str:
    if not path.exists():
        return f"(missing: {path})"
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) > limit:
        return text[:limit] + "\n… [truncated]"
    return text


def p(*parts: str) -> Path:
    return data_root().joinpath(*parts)


def ris_meta_path() -> Path:
    return p("10_data_raw", "12_final", "ris_meta.json")


def query_params_path() -> Path:
    return p("00_search", "02_final", "final_query_params.json")


def screening_config_path() -> Path:
    live = p("30_screening", "33_reports", "screening_config.json")
    return live if live.exists() else SCREEN_CFG_SHIPPED


def _has_xlsx(folder: Path) -> bool:
    return folder.exists() and any(folder.glob("*.xlsx"))


def step_complete(step_id: str) -> bool:
    if not has_data_root():
        return False
    if step_id == "output":
        return settings_path().exists()
    if step_id == "protocol_plan":
        return p("60_prisma", "protocol", "generated", "PRISMA-P_planned.md").exists()
    if step_id == "search":
        return p("00_search", "02_final", "final_query.txt").exists()
    if step_id == "raw":
        return p("20_data_clean", "21_audit", "exclusion_log.json").exists()
    if step_id == "clean":
        decisions = p("20_data_clean", "21_audit", "record_decisions.json")
        if classification_review_path().exists() and not decisions.exists():
            return True
        if not decisions.exists():
            return False
        data = record_audit.load_decisions()
        if record_audit.original_selection_path() and not data.get("original_applied"):
            return False
        return not record_audit.keep_both_unconfirmed(data)
    if step_id == "screen":
        return (
            p("30_screening", "31_dataset", "screened_records.xlsx").exists()
            or p("30_screening", "33_reports", "screening_summary.txt").exists()
        )
    if step_id == "extract":
        return _has_xlsx(p("40_extraction", "41_input"))
    if step_id == "protocol_run":
        folder = p("60_prisma", "protocol", "generated")
        return any(folder.glob("PRISMA-P_executed_*.md"))
    return False


def ensure_step_dirs(step_id: str) -> list[str]:
    spec = next((s for s in STEPS if s["id"] == step_id), None)
    if not spec or not has_data_root():
        return []
    created = []
    for rel in spec.get("folders") or []:
        folder = p(rel)
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
            created.append(rel)
    return created


def list_tree(max_depth: int = 3) -> str:
    root = data_root()
    if not root.exists():
        return ""
    lines = [str(root)]
    def walk(folder: Path, prefix: str, depth: int) -> None:
        if depth > max_depth:
            return
        try:
            kids = sorted(folder.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except OSError:
            return
        kids = [k for k in kids if not k.name.startswith(".")]
        for i, kid in enumerate(kids):
            last = i == len(kids) - 1
            branch = "└─ " if last else "├─ "
            extra = "/" if kid.is_dir() else ""
            lines.append(f"{prefix}{branch}{kid.name}{extra}")
            if kid.is_dir():
                walk(kid, prefix + ("   " if last else "│  "), depth + 1)
    walk(root, "", 1)
    return "\n".join(lines)


def list_files(rel: str) -> list[dict]:
    folder = p(rel)
    if not folder.exists():
        return []
    rows = []
    for item in sorted(folder.iterdir()):
        if item.is_file() and not item.name.startswith("."):
            rows.append({
                "name": item.name,
                "path": str(item),
                "kb": round(item.stat().st_size / 1024, 1),
                "mtime": datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            })
    return rows


def count_ris(path: Path) -> int:
    if not path.exists():
        return 0
    n = 0
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        for line in f:
            if line.startswith("ER  -"):
                n += 1
    return n


def canonical_database(name: str) -> str:
    key = re.sub(r"\s+", " ", (name or "").strip().lower())
    return DATABASE_ALIASES.get(key, (name or "").strip())


def _slug(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", canonical_database(name))
    return s.strip("_") or "database"


def ris_exports() -> list[dict]:
    meta = read_json(ris_meta_path(), {}) or {}
    rows = list(meta.get("exports") or [])
    if not rows:
        for key in ("wos", "scopus"):
            rec = meta.get(key)
            if rec:
                rec = dict(rec)
                rec.setdefault("database", "WoS" if key == "wos" else "Scopus")
                rows.append(rec)
    out = []
    seen: set[str] = set()
    for rec in rows:
        rec = dict(rec)
        rec["database"] = canonical_database(rec.get("database") or "") or rec.get("database") or ""
        key = rec["database"].casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(rec)
    return out


def iso_date(raw: str) -> str:
    text = (raw or "").strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d.%m.%y", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return datetime.now().strftime("%Y-%m-%d")


def _dated_export_name(name: str, slug: str) -> bool:
    """True for '{date} export_{slug}.ris' (ISO or D.M.Y, space or underscore)."""
    return bool(re.match(
        rf"^(\d{{4}}-\d{{2}}-\d{{2}}|\d{{1,2}}\.\d{{1,2}}\.\d{{2,4}})[ _]export_{re.escape(slug)}\.ris$",
        name,
        re.I,
    ))


def import_ris(database: str, src_path: Path, downloaded_at: str) -> dict:
    database = canonical_database(database)
    if not database:
        raise ValueError("Choose a database.")
    original_dir = p("10_data_raw", "11_original")
    final_dir = p("10_data_raw", "12_final")
    original_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)
    stamp = iso_date(downloaded_at)
    slug = _slug(database)
    dest_name = f"export_{slug}.ris"
    dest = final_dir / dest_name
    archived = original_dir / f"{stamp} export_{slug}.ris"
    src = src_path.resolve()
    if src != dest.resolve():
        shutil.copy2(src_path, dest)
    if src != archived.resolve():
        shutil.copy2(dest if dest.exists() else src_path, archived)
    keep = {archived.resolve()}
    for fp in original_dir.glob("*.ris"):
        if fp.resolve() in keep:
            continue
        if _dated_export_name(fp.name, slug):
            fp.unlink()
    n = count_ris(dest)
    rec = {
        "database": database,
        "file": dest_name,
        "original": archived.name if archived.exists() else "",
        "source": str(src_path),
        "source_name": src_path.name,
        "downloaded_at": stamp,
        "n_records": n,
        "imported": now(),
    }
    meta = read_json(ris_meta_path(), {}) or {}
    exports = [e for e in (meta.get("exports") or []) if e.get("file") != dest_name]
    exports.append(rec)
    meta["exports"] = exports
    write_json(ris_meta_path(), meta)
    return rec


def remove_ris_export(dest_name: str) -> None:
    meta = read_json(ris_meta_path(), {}) or {}
    exports = [e for e in (meta.get("exports") or []) if e.get("file") != dest_name]
    meta["exports"] = exports
    write_json(ris_meta_path(), meta)
    path = p("10_data_raw", "12_final", dest_name)
    if path.exists():
        path.unlink()


def _generic_boolean(params: dict) -> str:
    parts = []
    for g in params.get("groups") or []:
        inner = " OR ".join(f'"{t}"' for t in g.get("terms") or [])
        parts.append(f"({inner})")
    q = " AND ".join(parts)
    for ex in params.get("exclude") or []:
        inner = " OR ".join(f'"{t}"' for t in ex.get("terms") or [])
        q += f' NOT ({inner})'
    return q


def freeze_search(params: dict, databases: list[str]) -> Path:
    raw = p("00_search", "01_raw")
    final = p("00_search", "02_final")
    raw.mkdir(parents=True, exist_ok=True)
    final.mkdir(parents=True, exist_ok=True)
    dest = final / "final_query.txt"
    if dest.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy2(dest, raw / f"final_query_backup_{stamp}.txt")
    lines = ["## frozen", ""]
    if databases:
        lines.append("databases: " + "; ".join(databases))
    for group in params.get("groups") or []:
        lines.append(f"{', '.join(group['terms'])} | {group.get('field', 'all')}")
    for ex in params.get("exclude") or []:
        lines.append(f"NOT: {', '.join(ex['terms'])} | {ex.get('field', 'all')}")
    if params.get("year_from"):
        lines.append(f"year: {params['year_from']}-{params.get('year_to')}")
    if params.get("language"):
        lines.append(f"language: {params['language']}")
    lines += ["", "Boolean (adapt per database):", _generic_boolean(params), ""]
    dest.write_text("\n".join(lines), encoding="utf-8")
    write_json(
        final / "final_query_params.json",
        {
            "timestamp": datetime.now().isoformat(),
            "input": params,
            "databases": databases,
            "queries": {"boolean": _generic_boolean(params)},
        },
    )
    return dest


def save_search_draft(params: dict, databases: list[str]) -> Path:
    raw = p("00_search", "01_raw")
    raw.mkdir(parents=True, exist_ok=True)
    path = raw / "Query_combinations.txt"
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n\n---\n\n")
        if databases:
            f.write("databases: " + "; ".join(databases) + "\n")
        for group in params.get("groups") or []:
            f.write(f"{', '.join(group['terms'])} | {group.get('field', 'all')}\n")
        for ex in params.get("exclude") or []:
            f.write(f"NOT: {', '.join(ex['terms'])} | {ex.get('field', 'all')}\n")
        if params.get("year_from"):
            f.write(f"year: {params['year_from']}-{params.get('year_to')}\n")
        if params.get("language"):
            f.write(f"language: {params['language']}\n")
        f.write("\n" + _generic_boolean(params) + "\n")
    return path


def load_screening_config() -> dict:
    return read_json(screening_config_path(), {}) or {}


def save_screening_config(cfg: dict) -> Path:
    dest = p("30_screening", "33_reports", "screening_config.json")
    write_json(dest, cfg)
    return dest


def replace_ris_exports(rows: list[dict]) -> dict:
    """Copy only these RIS files into 12_final; delete leftover *.ris."""
    imported = []
    keep: set[str] = set()
    for row in rows:
        rec = import_ris(row["database"], Path(row["path"]), row.get("date") or "")
        imported.append(rec)
        keep.add(rec["file"])
    final_dir = p("10_data_raw", "12_final")
    removed = []
    for fp in final_dir.glob("*.ris"):
        if fp.name not in keep:
            fp.unlink()
            removed.append(fp.name)
    write_json(ris_meta_path(), {"exports": imported})
    files = []
    records = []
    for rec in imported:
        files.append(rec.get("original") or rec.get("file") or "")
        records.append(
            f"{rec.get('database')}: {rec.get('n_records')} records; "
            f"downloaded {rec.get('downloaded_at')}; "
            f"source `{rec.get('source_name') or rec.get('source') or ''}` → "
            f"`11_original/{rec.get('original') or ''}` / `12_final/{rec.get('file') or ''}`"
        )
    if removed:
        records.append("Left out leftover files: " + ", ".join(removed))
    note_protocol(
        "ris",
        f"Uploaded {len(imported)} RIS export(s).",
        records=records,
        files=files,
    )
    return {"exports": imported, "removed": removed}


def classification_review_path() -> Path:
    return p("20_data_clean", "21_audit", "classification_review.json")


def load_classification_review() -> dict:
    return read_json(classification_review_path(), {}) or {}


def save_classification_review(payload: dict) -> Path:
    payload = dict(payload)
    payload["saved"] = now()
    report_path = p("20_data_clean", "21_audit", "processing_report.txt")
    payload["technical_log_path"] = "20_data_clean/21_audit/processing_report.txt"
    if report_path.exists():
        payload["technical_log"] = report_path.read_text(encoding="utf-8", errors="replace")
    else:
        payload["technical_log"] = ""
    dest = classification_review_path()
    write_json(dest, payload)
    extras = []
    for row in payload.get("extra") or []:
        extras.append({
            "when": payload["saved"],
            "n": row.get("n"),
            "reason": row.get("reason") or "",
            "kept": bool(row.get("kept")),
            "check": row.get("check") or "",
            "note": row.get("note") or "",
        })
    write_json(p("20_data_clean", "21_audit", "manual_exclusions.json"), {"entries": extras})
    _write_audit_saved(payload)
    return dest


def _write_audit_saved(payload: dict) -> Path:
    dest = p("20_data_clean", "21_audit", "audit_saved.txt")
    dest.parent.mkdir(parents=True, exist_ok=True)
    classes = payload.get("classifications") or []
    extras = payload.get("extra") or []
    tot_rm = sum(int(c.get("remove") or 0) for c in classes)
    tot_fw = sum(int(c.get("forward") or 0) for c in classes)
    extra_n = sum(int(e.get("n") or 0) for e in extras)
    tot_rm += extra_n
    tot_fw = max(0, tot_fw - extra_n)
    lines = [
        "=== AUDIT SAVED ===",
        f"Date: {payload.get('saved')}",
        "",
        f"After check: {tot_rm} removed  ->  {tot_fw} go to screening",
    ]
    doi_n = int(payload.get("doi_missing_retained") or 0)
    doi_types = format_type_counts(payload.get("doi_missing_types") or [])
    if doi_n:
        extra = f" ({doi_types})" if doi_types else ""
        lines.append(
            f"Missing DOI among those going to screening: {doi_n}{extra} — kept, not deleted"
        )
    kept_types = format_type_counts(payload.get("kept_types") or [])
    if kept_types:
        lines.append(f"Publication types among script-kept records: {kept_types}")
        lines.append(
            "Books/e-books are not in that list (removed as a class). "
            "Conference papers and book chapters stay."
        )
    lines += ["", "n -> remove -> go forward:"]
    for c in classes:
        lines.append(
            f"- {c.get('label')}: n={c.get('n')}; check={c.get('check')}; "
            f"remove={c.get('remove')}; forward={c.get('forward')}"
        )
    decisions = record_audit.decision_summary()
    if decisions.get("has_file"):
        lines += [
            "",
            "Record-level decisions (forward_records.xlsx; merge files unchanged):",
            f"- go to screening: {decisions.get('n_forward')} (script kept {decisions.get('n_script')})",
            f"- DOI groups reviewed: {decisions.get('n_reviewed_doi')}; title: {decisions.get('n_reviewed_title')}",
            f"- swapped from script: {decisions.get('n_swapped')}; keep both: {decisions.get('n_kept_both')}",
            f"- extra drops: {decisions.get('n_exclude')}",
        ]
    if extras:
        lines += ["", "Extra removals:"]
        for e in extras:
            note = f"  {e.get('note')}" if e.get("note") else ""
            lines.append(
                f"- n={e.get('n')}  {e.get('reason')}  [{e.get('check')}]{note}"
            )
    logtxt = (payload.get("technical_log") or "").strip()
    if logtxt:
        lines += ["", "=== technical log (processing_report.txt at save) ===", "", logtxt]
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dest


AUDIT_LISTS = (
    ("duplicates_doi.xlsx", "DOI duplicates"),
    ("duplicates_title.xlsx", "Title duplicates"),
    ("missing_doi.xlsx", "Missing DOI"),
    ("all_records_with_status.xlsx", "All records"),
)


def _read_xlsx(*parts: str):
    path = p(*parts)
    if not path.exists():
        return None
    try:
        import pandas as pd
        return pd.read_excel(path)
    except Exception:
        return None


def _doi_blank_rows(df):
    if df is None or getattr(df, "empty", True):
        return None
    if "doi_missing" in df.columns:
        return df[df["doi_missing"] == True]  # noqa: E712
    if "DO" not in df.columns:
        return None
    s = df["DO"].astype(str).str.strip().str.lower()
    mask = df["DO"].isna() | s.eq("") | s.isin(["nan", "none", "na"])
    return df[mask]


def _types_from_df(df) -> list[dict]:
    if df is None or getattr(df, "empty", True) or "TY" not in getattr(df, "columns", []):
        return []
    return publication_type_counts(df["TY"].tolist())


def audit_summary() -> dict:
    """Plain counts for the Audit screen. Empty dict values if merge has not run."""
    log = read_json(p("20_data_clean", "21_audit", "exclusion_log.json"), {}) or {}
    review = load_classification_review() if has_data_root() else {}
    exports = ris_exports() if has_data_root() else []
    files = []
    for name, label in AUDIT_LISTS:
        path = p("20_data_clean", "21_audit", name)
        if path.exists():
            files.append({"name": name, "label": label, "path": path})
    doi_n = log.get("doi_missing_retained")
    if doi_n is None:
        doi_n = 0
        for e in log.get("entries") or []:
            if e.get("status") == "doi_missing" or e.get("cannot_exclude"):
                doi_n = int(e.get("n") or 0)
    if not doi_n:
        report = p("20_data_clean", "21_audit", "processing_report.txt")
        if report.exists():
            for line in report.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.lower().startswith("missing among retained"):
                    tail = line.split(":")[-1].strip()
                    try:
                        doi_n = int(tail)
                    except ValueError:
                        pass
    doi_types = list(log.get("doi_missing_types") or [])
    kept_types = list(log.get("kept_types") or [])
    if not doi_types or not kept_types:
        clean = _read_xlsx("20_data_clean", "clean_records.xlsx")
        if not kept_types:
            kept_types = _types_from_df(clean)
        if not doi_types:
            sub = _doi_blank_rows(clean)
            if sub is None or getattr(sub, "empty", True):
                sub = _read_xlsx("20_data_clean", "21_audit", "missing_doi.xlsx")
            doi_types = _types_from_df(sub)
            if not doi_n and sub is not None:
                doi_n = len(sub)
    return {
        "exports": exports,
        "retained": log.get("retained"),
        "removed": log.get("removed"),
        "doi_missing_retained": int(doi_n or 0),
        "doi_missing_types": doi_types,
        "kept_types": kept_types,
        "entries": list(log.get("entries") or []),
        "review": review,
        "files": files,
        "report": p("20_data_clean", "21_audit", "processing_report.txt"),
        "has_merge": p("20_data_clean", "21_audit", "exclusion_log.json").exists(),
        "record_decisions": record_audit.decision_summary(),
    }


def open_path(path: Path) -> None:
    if path.exists():
        os.startfile(path)


def script_file(rel_under_scripts: str) -> Path:
    rel = (rel_under_scripts or "").split()[0]
    return SCRIPTS / rel


AUDIT_PREVIEW = {
    "duplicate_doi": (("20_data_clean", "21_audit", "duplicates_doi.xlsx"), None),
    "duplicate_title": (("20_data_clean", "21_audit", "duplicates_title.xlsx"), None),
    "doi_missing": (("20_data_clean", "21_audit", "missing_doi.xlsx"), None),
    "correct_record": (("20_data_clean", "clean_records.xlsx"), None),
    "non_article_type": (("20_data_clean", "21_audit", "all_records_with_status.xlsx"), "non_article_type"),
    "incomplete_record": (("20_data_clean", "21_audit", "all_records_with_status.xlsx"), "incomplete_record"),
}


def preview_table(status: str, limit: int = 500) -> dict:
    spec = AUDIT_PREVIEW.get(status)
    if not spec:
        return {"error": "No list is attached to this row.", "columns": [], "rows": [], "n": 0, "file": ""}
    parts, filter_status = spec
    path = p(*parts)
    if not path.exists():
        return {"error": f"No file yet: {path}", "columns": [], "rows": [], "n": 0, "file": path.name}
    try:
        import pandas as pd
        df = pd.read_excel(path)
    except Exception as exc:
        return {"error": f"Could not read {path.name}: {exc}", "columns": [], "rows": [], "n": 0, "file": path.name}
    if filter_status and "status" in df.columns:
        df = df[df["status"] == filter_status]
    if status == "doi_missing" and "doi_missing" in df.columns:
        df = df[df["doi_missing"] == True]  # noqa: E712
    cols = [c for c, _h, _w in PREVIEW_COLUMNS if c in df.columns]
    if not cols:
        cols = list(df.columns[:6])
    headings = []
    widths = []
    known = {c: (h, w) for c, h, w in PREVIEW_COLUMNS}
    for c in cols:
        h, w = known.get(c, (c, 120))
        headings.append(h)
        widths.append(w)
    n = int(len(df))
    rows = []
    for _, rec in df.head(limit).iterrows():
        cells = []
        for c in cols:
            val = rec.get(c, "")
            if val is None or (isinstance(val, float) and val != val):
                val = ""
            if c == "TY":
                cells.append(publication_type_label(val) if str(val).strip() else "")
            else:
                cells.append(str(val).replace("\n", " ").strip()[:240])
        rows.append(cells)
    return {
        "error": "",
        "file": path.name,
        "path": str(path),
        "n": n,
        "columns": cols,
        "headings": headings,
        "widths": widths,
        "rows": rows,
        "truncated": n > limit,
    }


def _flag_mask(df, col: str):
    if df is None or col not in getattr(df, "columns", []):
        return None
    s = df[col]
    if getattr(s.dtype, "kind", "") == "b":
        return s.fillna(False)
    return s.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def _df_records(df) -> list[dict]:
    if df is None or getattr(df, "empty", True):
        return []
    out = df.copy()
    if "row_ix" not in out.columns:
        out["row_ix"] = range(len(out))
    return [record_audit.record_view(rec) for _, rec in out.iterrows()]


def _load_screened_xlsx():
    from project_paths import prefer_after_manual_check
    raw = p("30_screening", "31_dataset", "screened_records.xlsx")
    path = prefer_after_manual_check(raw)
    if not path.exists():
        return None, path
    try:
        import pandas as pd
        return pd.read_excel(path), path
    except Exception:
        return None, path


def _load_reviews_xlsx():
    from project_paths import prefer_after_manual_check
    for parts in (
        ("40_extraction", "42_reviews", "review_articles.xlsx"),
        ("30_screening", "34_reviews", "review_articles.xlsx"),
    ):
        raw = p(*parts)
        path = prefer_after_manual_check(raw)
        if path.exists():
            try:
                import pandas as pd
                return pd.read_excel(path), path
            except Exception:
                continue
    return None, None


def _filter_screen_group(df, kind: str):
    if df is None:
        return None
    if kind == "must_cite":
        m = _flag_mask(df, "must_cite")
        return df[m] if m is not None else df.iloc[0:0]
    if kind == "core":
        m = _flag_mask(df, "must_cite_strict")
        return df[m] if m is not None else df.iloc[0:0]
    if kind == "extended":
        mc = _flag_mask(df, "must_cite")
        st = _flag_mask(df, "must_cite_strict")
        if mc is None:
            return df.iloc[0:0]
        if st is None:
            return df[mc]
        return df[mc & ~st]
    if kind in {"include", "maybe", "exclude"}:
        if "screening_decision" not in df.columns:
            return df.iloc[0:0]
        return df[df["screening_decision"].astype(str).str.strip().str.lower() == kind]
    return df


def extract_overview(*, require_chosen_folder: bool = True) -> dict:
    """Nested screening counts after Extraction recodes (script files stay)."""
    empty = {
        "error": "",
        "n_must_cite": 0, "n_core": 0, "n_extended": 0, "n_include_rest": 0,
        "n_include": 0, "n_maybe": 0, "n_exclude": 0, "n_reviews": 0,
        "n_unclassified": 0, "n_recode": 0,
        "n_must_in_include": 0, "n_must_in_maybe": 0, "n_must_in_exclude": 0,
        "n_screen": 0, "source": "",
    }
    if require_chosen_folder and not has_data_root():
        return {**empty, "error": "No output folder."}
    import extract_recode
    screened = p("30_screening", "31_dataset", "screened_records.xlsx")
    if not extract_recode.originals() and not screened.exists():
        return {**empty, "error": "Run screening first."}
    ov = extract_recode.overview()
    if not screened.exists():
        ov["missing_screened"] = True
        ov["error"] = (
            "screened_records.xlsx is missing, so Include / Maybe / Exclude are empty. "
            "On Screening → Download, xlsx for screened_records cannot be off. Run screening again."
        )
    return ov


def extract_rows(kind: str) -> list[dict]:
    import extract_recode
    return extract_recode.rows_for(kind)


def extract_remove_from_group(kind: str, keys: list[str]) -> dict:
    import extract_recode
    data = extract_recode.remove_from_group(kind, keys)
    journal("extract", "recode", True, f"remove {kind} n={len(keys)}")
    _note_extract_recode(data)
    return data


def extract_assign_group(
    keys: list[str],
    dest: str,
    *,
    must_cite: bool = False,
    must_cite_strict: bool = False,
) -> dict:
    import extract_recode
    data = extract_recode.assign_group(
        keys, dest, must_cite=must_cite, must_cite_strict=must_cite_strict,
    )
    journal("extract", "recode", True, f"assign {dest} n={len(keys)}")
    _note_extract_recode(data)
    return data


def extract_move(
    kind: str,
    keys: list[str],
    dest: str,
    *,
    must_cite: bool = False,
    must_cite_strict: bool = False,
) -> dict:
    import extract_recode
    before = len((extract_recode.load().get("entries") or []))
    data = extract_recode.move_keys(
        keys=keys, kind=kind, dest=dest,
        must_cite=must_cite, must_cite_strict=must_cite_strict,
    )
    n = len(data.get("entries") or []) - before
    data = dict(data)
    data["n_moved"] = n
    if n > 0:
        journal("extract", "recode", True, f"move {kind} → {dest} n={n}")
        _note_extract_recode(data)
    return data


def extract_recode_summary() -> dict:
    import extract_recode
    ov = extract_recode.overview()
    return {
        "n": ov.get("n_recode") or 0,
        "n_unclassified": ov.get("n_unclassified") or 0,
        "txt": str(extract_recode.txt_path()),
    }


def preview_records(status: str, limit: int = 40) -> str:
    data = preview_table(status, limit=limit)
    if data.get("error"):
        return data["error"]
    heads = data.get("headings") or data.get("columns") or []
    lines = [f"{data.get('file')}  ·  {data.get('n')} rows", "  |  ".join(heads), ""]
    for row in data.get("rows") or []:
        lines.append("  |  ".join(row))
    if data.get("truncated"):
        lines.append(f"\n… more in the file")
    return "\n".join(lines)


def extra_formats(root: Path, formats: list[str], recursive: bool = False) -> list[str]:
    """Write csv/json copies of xlsx. Default is this folder only, not audit subfolders."""
    written = []
    paths = root.rglob("*.xlsx") if recursive else root.glob("*.xlsx")
    for xlsx in paths:
        written.extend(convert_xlsx(xlsx, formats))
    return written


def append_manual_exclusion(n: int, reason: str, kept: bool, note: str = "") -> dict:
    path = p("20_data_clean", "21_audit", "manual_exclusions.json")
    data = read_json(path, {"entries": []}) or {"entries": []}
    data.setdefault("entries", [])
    data["entries"].append({
        "when": now(),
        "n": int(n),
        "reason": reason.strip(),
        "kept": bool(kept),
        "note": note.strip(),
    })
    write_json(path, data)
    return data


def run_script(rel_under_scripts: str, extra_args: list[str] | None = None) -> dict:
    script = SCRIPTS / rel_under_scripts
    if not script.exists():
        return {"ok": False, "log": f"Missing script: {script}", "seconds": 0}
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    cmd = [sys.executable, str(script), *(extra_args or [])]
    t0 = datetime.now()
    proc = subprocess.run(
        cmd,
        cwd=str(script.parent),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    seconds = (datetime.now() - t0).total_seconds()
    log = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
    ok = proc.returncode == 0
    result = {"ok": ok, "log": log.strip() or f"(exit {proc.returncode})", "seconds": seconds, "cmd": " ".join(cmd)}
    if ok:
        _note_script_protocol(rel_under_scripts)
    return result


def convert_xlsx(path: Path, formats: list[str]) -> list[str]:
    written = []
    if not path.exists() or path.suffix.lower() not in {".xlsx", ".xls"}:
        return written
    try:
        import pandas as pd
    except ImportError:
        return written
    df = pd.read_excel(path)
    if "csv" in formats:
        out = path.with_suffix(".csv")
        df.to_csv(out, index=False, encoding="utf-8-sig")
        written.append(str(out))
    if "json" in formats:
        out = path.with_suffix(".json")
        df.to_json(out, orient="records", force_ascii=False, indent=2)
        written.append(str(out))
    return written


def existing_script_outputs(step: str) -> list[str]:
    found = []
    for parts in SCRIPT_OUTPUTS.get(step) or ():
        path = p(*parts)
        if path.exists():
            found.append("/".join(parts))
    return found


def _manual_check_stem(name: str) -> str:
    stem = Path(name).stem
    marker = f"_{AFTER_MANUAL_CHECK}"
    if stem.endswith(marker):
        return stem[: -len(marker)]
    return stem


def latest_manual_check(step: str) -> dict | None:
    spec = MANUAL_CHECK_UPLOADS.get(step) or {}
    if not spec or not has_data_root():
        return None
    folder = p(*spec["folder"])
    meta = folder / "after_manual_check.json"
    data = read_json(meta, None) if meta.exists() else None
    if isinstance(data, dict) and data.get("saved_as"):
        path = folder / str(data["saved_as"])
        if path.exists():
            return data
    matches = sorted(folder.glob(f"*_{AFTER_MANUAL_CHECK}.*"))
    if not matches:
        return None
    current = [m for m in matches if m.stem.endswith(AFTER_MANUAL_CHECK)]
    chosen = (current or matches)[-1]
    return {"saved_as": chosen.name, "ts": ""}


def save_checked_copy(step: str, src: Path) -> Path:
    """Store a file after manual check. Never replaces the script output."""
    spec = MANUAL_CHECK_UPLOADS[step]
    src = Path(src)
    folder = p(*spec["folder"])
    folder.mkdir(parents=True, exist_ok=True)
    stem = _manual_check_stem(src.name)
    dest = folder / f"{stem}_{AFTER_MANUAL_CHECK}{src.suffix}"
    if dest.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        archived = folder / f"{stem}_{AFTER_MANUAL_CHECK}_{stamp}{src.suffix}"
        dest.replace(archived)
    shutil.copy2(src, dest)
    row = {
        "ts": now(),
        "step": step,
        "source": src.name,
        "saved_as": dest.name,
        "marked_as": "after_manual_check",
        "script_outputs_left_in_place": list(existing_script_outputs(step)),
    }
    write_json(folder / "after_manual_check.json", row)
    log = folder / "checked_log.jsonl"
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    journal(step, "after_manual_check", True, dest.name)
    note_protocol(
        "after_manual_check",
        f"Uploaded a file after manual check on {step}. Script output was not replaced.",
        files=[dest.name, src.name],
        records=[f"{src.name} → {dest.name}"],
    )
    return dest


def settings_path() -> Path:
    return data_root() / "run_settings.json"


def load_settings() -> dict:
    data = dict(DEFAULT_SETTINGS)
    if has_data_root():
        saved = read_json(settings_path(), {}) or {}
        data.update({k: v for k, v in saved.items() if v is not None})
    return data


def save_settings(data: dict) -> Path:
    merged = dict(DEFAULT_SETTINGS)
    merged.update(data)
    if isinstance(merged.get("databases"), str):
        merged["databases"] = [x.strip() for x in merged["databases"].replace(";", ",").split(",") if x.strip()]
    write_json(settings_path(), merged)
    return settings_path()


def load_search_params(default: dict) -> dict:
    data = read_json(query_params_path())
    if data:
        return data.get("input", data)
    shipped = CODE_ROOT / "00_search" / "02_final" / "final_query_params.json"
    data = read_json(shipped)
    if data:
        return data.get("input", data)
    return json.loads(json.dumps(default))


def duplicate_groups(kind: str) -> list[dict]:
    return record_audit.duplicate_groups(kind)


def load_record_decisions() -> dict:
    return record_audit.load_decisions()


def save_record_decisions(data: dict):
    dest = record_audit.save_decisions(data)
    journal("clean", "record_decisions", True, dest.name)
    applied = record_audit.apply_decisions(data)
    labels = record_audit.doi_audit_protocol_lines(data)
    for line in record_audit.manual_intervention_lines(data, applied):
        if "(doi)" in line:
            continue
        labels.append(line)
    labels.extend(record_audit.audit_notes_protocol_lines(data))
    n_changed = sum(1 for line in labels if "changed from the script default" in line)
    note_protocol(
        "audit",
        f"Audit saved. Go to screening: {applied.get('n_forward')}. "
        f"Duplicate DOI: kept vs dropped logged; ticks changed from script: {n_changed}.",
        records=labels,
        files=["20_data_clean/21_audit/record_decisions.json", dest.name],
    )
    return dest


def set_duplicate_choice(data: dict, group: dict, action: str, keep: list[int]) -> dict:
    return record_audit.set_group_choice(data, group, action, keep)


def confirm_script_duplicates(kind: str, data: dict | None = None) -> dict:
    return record_audit.confirm_script_remaining(kind, data)


def set_record_exclude(data: dict, row_ix: int, reason: str, title: str = "", note: str = "") -> dict:
    return record_audit.set_exclude(data, row_ix, reason, title, note)


def records_for_picker() -> dict:
    return record_audit.records_for_picker()


def records_for_status(status: str) -> list[dict]:
    return record_audit.records_for_status(status)


def record_decision_summary() -> dict:
    return record_audit.decision_summary()


def audit_overview() -> dict:
    return record_audit.audit_overview()


def prisma_assemble(settings: dict | None = None) -> dict:
    import prisma_flow

    if not has_data_root():
        return {}
    return prisma_flow.assemble(
        settings if settings is not None else load_settings(),
        extract_overview(require_chosen_folder=False),
        data_root(),
    )


def save_prisma_flow(settings: dict | None = None) -> dict:
    import prisma_flow

    return prisma_flow.save(
        settings if settings is not None else load_settings(),
        extract_overview(require_chosen_folder=False),
        data_root(),
    )


def render_prisma_png() -> dict:
    import prisma_flow

    return prisma_flow.render_png(data_root())
