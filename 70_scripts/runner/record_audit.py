"""Record-level audit: which duplicate stays, which records go to screening.

The merge script files are not replaced. Decisions live in record_decisions.json
and the set that proceeds is written to forward_records.xlsx.
"""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

from catalog import AUDIT_TABS, publication_type_label
from project_paths import CODE_ROOT, data_root

KEEPABLE = {"correct_record", "missing_doi"}
SHOW = ("Source", "TY", "PY", "TI", "AU", "DO", "T2", "M3", "status")


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _audit() -> Path:
    return data_root() / "20_data_clean" / "21_audit"


def decisions_path() -> Path:
    return _audit() / "record_decisions.json"


def forward_path() -> Path:
    return _audit() / "forward_records.xlsx"


def master_path() -> Path:
    return _audit() / "all_records_with_status.xlsx"


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


FILL_FROM_SIBLING = ("M3", "AB", "KW", "AU", "T2", "JO", "UR", "SN", "N1", "DT")


def fill_blank_fields_from_duplicates(df):
    """Copy blank bibliographic fields from the other copy in a DOI or title–year group.

    The donor may have no DOI. Kept rows then carry M3 (review, article, …) into
    forward_records / screening.
    """
    if df is None or getattr(df, "empty", True):
        return df

    out = df.copy()
    for col in FILL_FROM_SIBLING:
        if col not in out.columns:
            out[col] = ""

    def _is_blank(val) -> bool:
        return _cell(val) == ""

    if "DO" in out.columns:
        doi_key = out["DO"].map(_norm_doi)
        work = out.assign(_doi_k=doi_key)
        nonempty = work["_doi_k"].ne("")
        if bool(nonempty.any()):
            for _, idx in work.loc[nonempty].groupby("_doi_k", sort=False).groups.items():
                if len(idx) < 2:
                    continue
                chunk = out.loc[idx]
                for col in FILL_FROM_SIBLING:
                    values = [_cell(v) for v in chunk[col].tolist() if not _is_blank(v)]
                    if not values:
                        continue
                    pick = values[0]
                    if col == "M3":
                        for v in values:
                            if "review" in v.lower():
                                pick = v
                                break
                    blank = chunk[col].map(_is_blank)
                    if blank.any():
                        out.loc[chunk.index[blank], col] = pick
    if "TI" in out.columns and "PY" in out.columns:
        ti = out["TI"].map(_cell).str.lower()
        py = out["PY"].map(_cell)
        work = out.assign(_ti_k=ti + "||" + py)
        nonempty = work["_ti_k"].map(lambda s: not str(s).startswith("||") and str(s) != "")
        for _, idx in work.loc[nonempty].groupby("_ti_k", sort=False).groups.items():
            if len(idx) < 2:
                continue
            chunk = out.loc[idx]
            for col in FILL_FROM_SIBLING:
                values = [_cell(v) for v in chunk[col].tolist() if not _is_blank(v)]
                if not values:
                    continue
                pick = values[0]
                if col == "M3":
                    for v in values:
                        if "review" in v.lower():
                            pick = v
                            break
                blank = chunk[col].map(_is_blank)
                if blank.any():
                    out.loc[chunk.index[blank], col] = pick
    return out


_MASTER = {"path": None, "mtime": None, "df": None}


def _load_master_raw():
    import pandas as pd

    path = master_path()
    if not path.exists():
        _MASTER.update(path=None, mtime=None, df=None)
        return None
    mtime = path.stat().st_mtime
    if _MASTER["df"] is not None and _MASTER["path"] == path and _MASTER["mtime"] == mtime:
        return _MASTER["df"]
    df = pd.read_excel(path)
    df = df.reset_index(drop=True)
    df["row_ix"] = df.index.astype(int)
    _MASTER.update(path=path, mtime=mtime, df=df)
    return df


def apply_doi_assignments(df, data: dict | None = None):
    """Overlay DOIs assigned in Audit. The merge file is not rewritten."""
    if df is None or df.empty:
        return df
    data = data if data is not None else load_decisions()
    rows = data.get("doi_assign") or []
    if not rows:
        return df
    if "DO" not in df.columns:
        df["DO"] = ""
    for rec in rows:
        try:
            ix = int(rec.get("row_ix"))
        except (TypeError, ValueError):
            continue
        doi = _cell(rec.get("DO"))
        if not doi or ix not in df.index:
            continue
        df.at[ix, "DO"] = doi
        if "doi_missing" in df.columns:
            df.at[ix, "doi_missing"] = False
    return df


def _load_master():
    raw = _load_master_raw()
    if raw is None:
        return None
    return apply_doi_assignments(raw.copy())


def donor_doi_for_group(group: dict) -> tuple[str, int | None]:
    """If the group has exactly one unique DOI, return it and the donor row."""
    found: list[tuple[str, int]] = []
    for m in group.get("members") or []:
        doi = _cell(m.get("DO"))
        if _norm_doi(doi):
            found.append((doi, int(m["row_ix"])))
    keys = {_norm_doi(d) for d, _ix in found}
    if len(keys) != 1:
        return "", None
    return found[0]


def assign_doi(data: dict, row_ix: int, doi: str, from_row_ix: int | None = None) -> dict:
    ix = int(row_ix)
    text = _norm_doi(doi) or _cell(doi)
    data = dict(data)
    data.setdefault("doi_assign", [])
    data["doi_assign"] = [e for e in data["doi_assign"] if int(e.get("row_ix")) != ix]
    if text:
        blob = {"row_ix": ix, "DO": text, "ts": _now()}
        if from_row_ix is not None:
            blob["from_row_ix"] = int(from_row_ix)
        data["doi_assign"].append(blob)
        data.setdefault("reviewed", {})
        data["reviewed"]["both"] = False
        data.setdefault("events", []).append({
            "ts": _now(), "kind": "doi_assign", "row_ix": ix,
            "DO": text, "from_row_ix": from_row_ix,
        })
    return data


def record_note_map(data: dict | None = None) -> dict[int, str]:
    data = data or load_decisions()
    out: dict[int, str] = {}
    raw = data.get("record_notes") or {}
    if isinstance(raw, list):
        items = raw
    else:
        items = [{"row_ix": k, "note": v} for k, v in raw.items()]
    for rec in items:
        try:
            ix = int(rec.get("row_ix"))
        except (TypeError, ValueError, AttributeError):
            continue
        text = _cell(rec.get("note") if isinstance(rec, dict) else rec)
        if text:
            out[ix] = text
    return out


def set_record_note(data: dict, row_ix: int, note: str, title: str = "") -> dict:
    ix = int(row_ix)
    text = _cell(note)
    notes = record_note_map(data)
    if notes.get(ix, "") == text:
        return data
    if text:
        notes[ix] = text
    else:
        notes.pop(ix, None)
    data["record_notes"] = [
        {"row_ix": k, "note": v, "ts": _now()} for k, v in sorted(notes.items())
    ]
    if text:
        data.setdefault("events", []).append({
            "ts": _now(), "kind": "record_note", "row_ix": ix, "note": text, "TI": title,
        })
    return data


def set_group_note(data: dict, kind: str, note: str) -> dict:
    text = _cell(note)
    data.setdefault("group_notes", {})
    if text:
        data["group_notes"][str(kind)] = text
    else:
        data["group_notes"].pop(str(kind), None)
    return data


def audit_notes_protocol_lines(data: dict | None = None) -> list[str]:
    data = data or load_decisions()
    labels = dict(AUDIT_TABS)
    lines: list[str] = []
    group_notes = data.get("group_notes") or {}
    if group_notes:
        lines.append("Notes on audit groups:")
        for key, _lab in AUDIT_TABS:
            text = _cell(group_notes.get(key))
            if text:
                lines.append(f"- {labels.get(key, key)}: {text}")
    notes = record_note_map(data)
    if notes:
        applied = apply_decisions(data)
        df = applied.get("df")
        lines.append("Notes on records:")
        for ix, text in sorted(notes.items()):
            lines.append(f"- {record_label_ix(df, ix)} — {text}")
    return lines


PREFERRED_COLS = (
    "PY", "TI", "AU", "DO", "Source", "TY", "status", "AB", "KW", "T2", "M3", "JO", "SN", "UR",
)

KEEP_ON = "☑"
KEEP_OFF = "☐"


def full_record(rec) -> dict:
    row = {}
    for key in rec.index:
        if str(key) == "row_ix":
            continue
        row[str(key)] = _cell(rec[key])
    row["row_ix"] = int(rec["row_ix"])
    row["TY_label"] = publication_type_label(row.get("TY") or "") if row.get("TY") else ""
    row["keepable"] = (row.get("status") or "") in KEEPABLE
    return row


def record_view(rec) -> dict:
    return full_record(rec)


def record_label_ix(df, ix: int) -> str:
    """Year, title, source and DOI for a row_ix — used in the protocol."""
    ix = int(ix)
    if df is None:
        return f"row {ix}"
    hit = None
    if "row_ix" in getattr(df, "columns", ()):
        sub = df.loc[df["row_ix"].astype(int) == ix]
        if not sub.empty:
            hit = sub.iloc[0]
    if hit is None and hasattr(df, "index") and ix in df.index:
        hit = df.loc[ix]
    if hit is None:
        return f"row {ix}"
    rec = {str(k): hit[k] for k in hit.index} if hasattr(hit, "index") else dict(hit)
    year = _cell(rec.get("PY"))
    title = _cell(rec.get("TI"))
    doi = _cell(rec.get("DO"))
    src = _cell(rec.get("Source"))
    bit = f"{year} {title}".strip() or f"row {ix}"
    extra = [x for x in (src, doi) if x]
    if extra:
        bit += " [" + "; ".join(extra) + "]"
    return bit


def manual_intervention_lines(data: dict, applied: dict) -> list[str]:
    """Audit choices that differ from the script default — exact records."""
    df = applied.get("df")
    lines: list[str] = []
    for kind in ("doi", "title"):
        items = (data.get("duplicates") or {}).get(kind) or {}
        for rec in items.values():
            keep = [int(x) for x in (rec.get("keep") or [])]
            drop = [int(x) for x in (rec.get("drop") or [])]
            script = rec.get("script_keep")
            try:
                script_ix = int(script) if script is not None else None
            except (TypeError, ValueError):
                script_ix = None
            changed = rec.get("action") != "keep_one" or keep != ([script_ix] if script_ix is not None else keep)
            if not changed:
                continue
            action = rec.get("action") or "keep_one"
            for ix in keep:
                lines.append(f"{action} / kept ({kind}): {record_label_ix(df, ix)}")
            for ix in drop:
                lines.append(f"{action} / dropped ({kind}): {record_label_ix(df, ix)}")
    for row in data.get("exclude") or []:
        ix = row.get("row_ix")
        why = row.get("reason") or "unchecked"
        title = row.get("TI") or (record_label_ix(df, ix) if ix is not None else "")
        lines.append(f"extra exclude ({why}): {title}")
    for row in data.get("doi_assign") or []:
        ix = row.get("row_ix")
        lines.append(
            f"assigned DOI {row.get('DO') or ''} → {record_label_ix(df, ix) if ix is not None else 'row ?'}"
        )
    return lines


def list_columns(rows: list[dict]) -> list[str]:
    seen: list[str] = []
    skip = {"row_ix", "keepable", "TY_label", "forward", "_group", "_kind", "_key", "_doi_from"}
    for key in PREFERRED_COLS:
        if any(row.get(key) for row in rows) and key not in seen:
            seen.append(key)
    extra = []
    for row in rows:
        for key in row:
            if key in skip or key in seen or key in extra:
                continue
            extra.append(key)
    used = [key for key in extra if any(row.get(key) for row in rows)]
    return seen + used


def duplicate_groups(kind: str) -> list[dict]:
    """Groups of 2+ records the script treated as the same work.

    DOI groups first. Title groups are what remains after DOI (including a
    title match where only one copy has a DOI).
    """
    df = _load_master()
    if df is None or df.empty:
        return []
    if kind == "doi":
        if "DO" not in df.columns:
            return []
        doi = df["DO"].map(_norm_doi)
        marked = doi.ne("") & doi.duplicated(keep=False)
        sub = df.loc[marked].copy()
        sub["_gk"] = doi[marked]
    else:
        if "TI" not in df.columns or "PY" not in df.columns:
            return []
        marked = df.duplicated(subset=["TI", "PY"], keep=False)
        sub = df.loc[marked].copy()
        if "status" in sub.columns:
            sub = sub[sub["status"].map(_cell) != "duplicate_doi"]
        ti = sub["TI"].map(_cell).str.lower()
        py = sub["PY"].map(_cell)
        sub["_gk"] = ti + "||" + py
    groups = []
    for gk, chunk in sub.groupby("_gk", sort=False):
        members = [record_view(rec) for _, rec in chunk.iterrows()]
        if kind == "title":
            members = [m for m in members if m.get("status") != "duplicate_doi"]
        if len(members) < 2:
            continue
        script_keep = next((m["row_ix"] for m in members if m["keepable"]), members[0]["row_ix"])
        groups.append({
            "kind": kind,
            "key": str(gk),
            "label": _group_label(kind, members),
            "script_keep": script_keep,
            "members": members,
        })
    if kind == "title":
        groups = [g for g in groups if _title_group_needs_look(g)]
    return groups


def keep_set_for_group(group: dict, saved_rec: dict | None = None) -> set[int]:
    """Ticks that match a saved choice, otherwise whoever the merge already kept."""
    if saved_rec:
        return {int(x) for x in saved_rec.get("keep") or []}
    kept = {int(m["row_ix"]) for m in group["members"] if m.get("keepable")}
    return kept or {int(group["script_keep"])}


JOUR_TY = {"JOUR"}
CONF_TY = {"CONF", "CPAPER", "INPR"}

DOI_FORM_FILTERS = (
    ("all", "All pairs"),
    ("both_jour", "Both journal (JOUR)"),
    ("both_conf", "Both conference (CONF / CPAPER)"),
    ("mixed", "Different forms"),
    ("same_other", "Same other type"),
)

DOI_MATCH_FILTERS = (
    ("all", "All matches"),
    ("identical", "Identical (year, title, authors, type)"),
    ("title_diff", "Title differs"),
    ("author_diff", "Authors differ"),
    ("title_and_author", "Title and authors differ"),
    ("year_diff", "Year differs"),
    ("type_diff", "Type differs"),
    ("year_and_type", "Year and type differ"),
)


def _ty_form(code) -> str:
    c = str(code or "").strip().upper()
    if c in JOUR_TY:
        return "jour"
    if c in CONF_TY:
        return "conf"
    if c and c not in {"NAN", "NONE", "NA"}:
        return c.lower()
    return "unknown"


def doi_pair_form(group: dict) -> str:
    """How TY codes in a duplicate-DOI group relate: both journal, both conference, mixed, or same other."""
    forms = {_ty_form(m.get("TY")) for m in group.get("members") or []}
    if forms == {"jour"}:
        return "both_jour"
    if forms == {"conf"}:
        return "both_conf"
    if len(forms) >= 2:
        return "mixed"
    return "same_other"


def _norm_text(val) -> str:
    text = unicodedata.normalize("NFKC", _cell(val)).casefold()
    text = text.replace("\u00ad", "")
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def _norm_year(val) -> str:
    found = re.search(r"(?:19|20)\d{2}", _cell(val))
    return found.group(0) if found else _cell(val).strip()


def _collapse_initials(text: str) -> str:
    """J. C. / J.C. / JC as the same token after punctuation has been stripped."""
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"\b([a-z])\s+(?=[a-z]\b)", r"\1", text)
    return text


def _norm_authors(val) -> str:
    parts = [_collapse_initials(_norm_text(p)) for p in re.split(r"[;\n]+", _cell(val))]
    return " | ".join(sorted(p for p in parts if p))


def _norm_ty_code(val) -> str:
    return str(val or "").strip().upper()


def doi_field_sameness(group: dict) -> dict[str, bool]:
    members = group.get("members") or []
    return {
        "title": len({_norm_text(m.get("TI")) for m in members}) <= 1,
        "authors": len({_norm_authors(m.get("AU")) for m in members}) <= 1,
        "year": len({_norm_year(m.get("PY")) for m in members}) <= 1,
        "type": len({_norm_ty_code(m.get("TY")) for m in members}) <= 1,
    }


def doi_field_diffs(group: dict) -> list[str]:
    same = doi_field_sameness(group)
    return [name for name in ("year", "title", "authors", "type") if not same[name]]


def doi_pair_match(group: dict) -> str:
    """How copies with the same DOI differ (exclusive class)."""
    same = doi_field_sameness(group)
    if all(same.values()):
        return "identical"
    if not same["title"] and not same["authors"]:
        return "title_and_author"
    if not same["title"]:
        return "title_diff"
    if not same["authors"]:
        return "author_diff"
    if not same["year"] and not same["type"]:
        return "year_and_type"
    if not same["year"]:
        return "year_diff"
    return "type_diff"


def sort_doi_groups(groups: list[dict]) -> list[dict]:
    match_order = {key: i for i, (key, _lab) in enumerate(DOI_MATCH_FILTERS)}
    form_order = {key: i for i, (key, _lab) in enumerate(DOI_FORM_FILTERS)}
    return sorted(
        groups,
        key=lambda g: (
            match_order.get(doi_pair_match(g), 9),
            form_order.get(doi_pair_form(g), 9),
            (g.get("label") or "").casefold(),
        ),
    )


def _filter_label(filters: tuple, key: str) -> str:
    for k, lab in filters:
        if k == key:
            return lab
    return key


def _member_protocol_line(m: dict) -> str:
    bits = [
        _cell(m.get("PY")),
        _cell(m.get("TY")),
        _cell(m.get("Source")),
        (_cell(m.get("TI")) or "")[:100],
    ]
    au = _cell(m.get("AU"))
    if au:
        bits.append("AU: " + au[:90])
    doi = _cell(m.get("DO"))
    if doi:
        bits.append(doi)
    return " · ".join(x for x in bits if x)


def _doi_choice_why(match: str, action: str, followed: bool) -> str:
    if action == "keep_both":
        base = "both copies kept"
    elif followed:
        base = "one copy kept (script default: first keepable record)"
    else:
        base = "one copy kept (changed from the script default)"
    if match == "identical":
        return f"{base}; records matched on year, title, authors and type"
    lab = _filter_label(DOI_MATCH_FILTERS, match)
    return f"{base}; copies differed ({lab.lower()})"


def doi_audit_protocol_lines(data: dict | None = None) -> list[str]:
    """Counts of how DOI copies differed, plus kept vs dropped for non-identical / changed pairs."""
    data = data or load_decisions()
    groups = duplicate_groups("doi")
    if not groups:
        return ["No duplicate-DOI groups."]
    from collections import Counter

    groups = sort_doi_groups(groups)
    match_n = Counter(doi_pair_match(g) for g in groups)
    form_n = Counter(doi_pair_form(g) for g in groups)
    n_records = sum(len(g.get("members") or []) for g in groups)
    saved = (data.get("duplicates") or {}).get("doi") or {}
    lines = [
        f"Duplicate DOI: {len(groups)} groups ({n_records} records).",
        "Form: "
        + "; ".join(
            f"{lab} {form_n.get(key, 0)}"
            for key, lab in DOI_FORM_FILTERS
            if key != "all" and form_n.get(key)
        )
        + ".",
        "How copies differed:",
    ]
    for key, lab in DOI_MATCH_FILTERS:
        if key == "all":
            continue
        n = int(match_n.get(key, 0))
        if n:
            lines.append(f"- {lab}: {n}")
    n_script = n_changed = n_both = 0
    details: list[str] = []
    for g in groups:
        rec = saved.get(g["key"])
        match = doi_pair_match(g)
        keep_ix = keep_set_for_group(g, rec)
        action = (rec or {}).get("action") or ("keep_both" if len(keep_ix) > 1 else "keep_one")
        followed = action == "keep_one" and keep_ix == {int(g["script_keep"])}
        if action == "keep_both":
            n_both += 1
        elif followed:
            n_script += 1
        else:
            n_changed += 1
        list_pair = (
            match != "identical"
            and not (match == "author_diff" and followed)
        ) or (not followed) or action == "keep_both"
        if not list_pair:
            continue
        why = _doi_choice_why(match, action, followed)
        doi = _cell((g.get("members") or [{}])[0].get("DO"))
        diffs = doi_field_diffs(g)
        if diffs:
            details.append(f"DOI {doi} — differed in {', '.join(diffs)}. {why}.")
        else:
            details.append(f"DOI {doi} — {why}.")
        for m in g.get("members") or []:
            tag = "kept" if int(m["row_ix"]) in keep_ix else "dropped"
            details.append(f"  {tag}: {_member_protocol_line(m)}")
    lines += [
        "",
        "Rule: identical copies keep one (script: first keepable record). "
        "If year, title, authors or type differ, both records are inspected; "
        "the kept copy is the ticked row (script default unless the ticks were changed).",
        f"Decisions: script default {n_script}; changed from script {n_changed}; keep both {n_both}.",
    ]
    if match_n.get("author_diff"):
        lines.append(
            "Author-only pairs that followed the script default are counted above, not listed "
            "(usually WoS vs Scopus initials). Year, title, type, keep-both, and any changed ticks are listed:"
        )
    else:
        lines.append("Groups that were not identical, or where the ticks differed from the script:")
    lines.extend(details or ["(none — all DOI pairs were identical and followed the script default)"])
    return lines


def doi_audit_protocol_block(data: dict | None = None) -> str:
    return "\n".join(doi_audit_protocol_lines(data))


def _norm_doi(val) -> str:
    text = _cell(val).lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/"):
        if text.startswith(prefix):
            text = text[len(prefix):]
    return text.strip()


def original_selection_path() -> Path | None:
    """Frozen kept list from the original review, if present."""
    dest = _audit() / "original_selection.xlsx"
    if dest.exists():
        return dest
    for path in (
        CODE_ROOT / "20_data_clean" / "21_audit" / "original_selection.xlsx",
        CODE_ROOT / "99_backup" / "original_run" / "20_data_clean" / "21_audit" / "original_selection.xlsx",
        CODE_ROOT / "20_data_clean" / "clean_records.xlsx",
    ):
        if path.exists():
            return path
    return None


def freeze_original_selection() -> Path | None:
    dest = _audit() / "original_selection.xlsx"
    if dest.exists():
        return dest
    src = original_selection_path()
    if src is None:
        return None
    import shutil
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    archive = CODE_ROOT / "20_data_clean" / "21_audit" / "original_selection.xlsx"
    if not archive.exists() and src.resolve() != archive.resolve():
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, archive)
    return dest if dest.exists() else src


def _original_keys(path: Path) -> tuple[set[str], set[str], int]:
    import pandas as pd

    df = pd.read_excel(path)
    dois: set[str] = set()
    tys: set[str] = set()
    for _, rec in df.iterrows():
        doi = _norm_doi(rec["DO"] if "DO" in rec.index else "")
        if doi:
            dois.add(doi)
        else:
            ti = _cell(rec["TI"] if "TI" in rec.index else "").lower()
            py = _cell(rec["PY"] if "PY" in rec.index else "")
            tys.add(f"{ti}||{py}")
    return dois, tys, int(len(df))


def apply_original_kept(data: dict) -> dict:
    """Lock the forward set to the original kept list (clean_records.xlsx)."""
    src = freeze_original_selection()
    df = _load_master()
    if src is None or df is None or df.empty:
        return data
    dois, tys, n_file = _original_keys(src)
    dcol = df["DO"].map(_norm_doi) if "DO" in df.columns else pd_empty_str(df)
    ty = (
        df["TI"].map(_cell).str.lower() + "||" + df["PY"].map(_cell)
        if "TI" in df.columns and "PY" in df.columns
        else pd_empty_str(df)
    )
    match = (dcol.ne("") & dcol.isin(dois)) | (dcol.eq("") & ty.isin(tys))
    script_fwd = _script_forward(df)
    # Original list is 1133 records with a DOI. Hold back extra DOI rows not
    # on that list. Records without a DOI stay in the complete forward set.
    extra = [
        int(i)
        for i in df.loc[df["row_ix"].isin(script_fwd) & ~match & dcol.ne(""), "row_ix"].tolist()
    ]
    data = dict(data)
    data["exclude"] = [
        e for e in data.get("exclude") or []
        if e.get("reason") != "Not in original kept list"
    ]
    for ix in extra:
        title = _cell(df.at[ix, "TI"]) if "TI" in df.columns else ""
        status = _cell(df.at[ix, "status"]) if "status" in df.columns else ""
        set_row_keep(data, ix, False, title, status, reason="Not in original kept list")
    data["original_applied"] = True
    data["original_source"] = str(src)
    data["n_original"] = n_file
    data["n_extra_excluded"] = len(extra)
    return data


def release_nodoi_original_excludes(data: dict) -> tuple[dict, int]:
    """Put no-DOI rows back if the original lock had held them out."""
    df = _load_master()
    if df is None or df.empty:
        return data, 0
    dcol = df["DO"].map(_norm_doi) if "DO" in df.columns else pd_empty_str(df)
    no_doi = set(int(i) for i in df.loc[dcol.eq(""), "row_ix"].tolist())
    kept = []
    n_drop = 0
    for e in data.get("exclude") or []:
        if e.get("reason") == "Not in original kept list":
            try:
                ix = int(e.get("row_ix"))
            except (TypeError, ValueError):
                kept.append(e)
                continue
            if ix in no_doi:
                n_drop += 1
                continue
        kept.append(e)
    if not n_drop:
        return data, 0
    data = dict(data)
    data["exclude"] = kept
    data["n_extra_excluded"] = len(
        [e for e in kept if e.get("reason") == "Not in original kept list"]
    )
    return data, n_drop


def pd_empty_str(df):
    import pandas as pd
    return pd.Series("", index=df.index)


def keep_both_groups() -> list[dict]:
    """Pairs where two copies currently stay (same DOI after lowercasing, or saved keep_both)."""
    data = load_decisions()
    applied = apply_decisions(data)
    df = applied.get("df")
    if df is None or df.empty:
        return []
    fwd = set(applied.get("forward") or [])
    saved_title = (data.get("duplicates") or {}).get("title") or {}
    groups: list[dict] = []
    if "DO" in df.columns:
        dnorm = df["DO"].map(_norm_doi)
        kept = dnorm.where(df["row_ix"].isin(fwd), other="")
        nonempty = kept[kept.ne("")]
        sizes = nonempty.groupby(nonempty).size() if len(nonempty) else nonempty
        both = set(sizes[sizes >= 2].index) if len(nonempty) else set()
        if both:
            sub = df.loc[dnorm.isin(both)].copy()
            sub["_gk"] = dnorm.loc[sub.index]
            for gk, chunk in sub.groupby("_gk", sort=False):
                members = [record_view(rec) for _, rec in chunk.iterrows()]
                if len(members) < 2:
                    continue
                script_keep = next((m["row_ix"] for m in members if m["keepable"]), members[0]["row_ix"])
                groups.append({
                    "kind": "doi",
                    "key": str(gk),
                    "label": _group_label("doi", members),
                    "script_keep": script_keep,
                    "members": members,
                })
    title_need = [key for key, rec in saved_title.items() if len(rec.get("keep") or []) >= 2]
    if title_need:
        by_key = {g["key"]: g for g in duplicate_groups("title")}
        for key in title_need:
            if key in by_key:
                groups.append(by_key[key])
    out = []
    for g in groups:
        n_fwd = sum(1 for m in g["members"] if int(m["row_ix"]) in fwd)
        if n_fwd > 1:
            out.append(g)
    return out


def _n_keep_both_from_applied(applied: dict) -> int:
    df = applied.get("df")
    if df is None or df.empty or "DO" not in df.columns:
        return 0
    fwd = set(applied.get("forward") or [])
    d = df.loc[df["row_ix"].isin(fwd), "DO"].map(_norm_doi)
    sizes = d[d.ne("")].groupby(d[d.ne("")]).size()
    return int((sizes >= 2).sum())


def keep_both_count(data: dict | None = None) -> int:
    return _n_keep_both_from_applied(apply_decisions(data))


def keep_both_unconfirmed(data: dict | None = None) -> bool:
    data = data or load_decisions()
    if (data.get("reviewed") or {}).get("both"):
        return False
    return keep_both_count(data) > 0


def seed_missing_duplicate_choices(data: dict) -> dict:
    """Fill unreviewed duplicate groups from the current keepable status. Do not overwrite."""
    data = dict(data)
    data.setdefault("duplicates", {}).setdefault("doi", {})
    data.setdefault("duplicates", {}).setdefault("title", {})
    for kind in ("doi", "title"):
        bucket = data["duplicates"][kind]
        for group in duplicate_groups(kind):
            if group["key"] in bucket:
                continue
            keep = sorted(keep_set_for_group(group, None))
            members = [int(m["row_ix"]) for m in group["members"]]
            bucket[group["key"]] = {
                "action": "keep_both" if len(keep) > 1 else "keep_one",
                "keep": keep,
                "drop": [i for i in members if i not in keep],
                "script_keep": int(group["script_keep"]),
                "ts": _now(),
                "label": group.get("label") or "",
                "from_status": True,
            }
    return data


def _title_dois_need_look(dois: list[str], statuses: list[str] | None = None) -> bool:
    """Title group after DOI: skip same-DOI copies; keep mixed / no-DOI / different-DOI."""
    norm = [_norm_doi(d) for d in dois]
    nonempty = [d for d in norm if d]
    n_blank = sum(1 for d in norm if not d)
    if n_blank and nonempty:
        return True
    if n_blank >= 2:
        return True
    if nonempty and n_blank == 0 and len(set(nonempty)) == 1:
        return False
    if statuses is not None:
        keepable = sum(1 for s in statuses if s in KEEPABLE | {"duplicate_title"})
        return keepable >= 2
    return len(norm) >= 2


def _title_group_needs_look(group: dict) -> bool:
    members = [m for m in group["members"] if m.get("status") != "duplicate_doi"]
    if len(members) < 2:
        return False
    return _title_dois_need_look(
        [m.get("DO") or "" for m in members],
        [m.get("status") or "" for m in members],
    )


def _title_chunk_needs_look(chunk) -> bool:
    if "status" in chunk.columns:
        chunk = chunk[chunk["status"].map(_cell) != "duplicate_doi"]
    if len(chunk) < 2:
        return False
    dois = chunk["DO"].tolist() if "DO" in chunk.columns else [""] * len(chunk)
    statuses = chunk["status"].map(_cell).tolist() if "status" in chunk.columns else None
    return _title_dois_need_look(dois, statuses)


def _dup_stats(df, kind: str) -> tuple[int, int]:
    """Unique duplicate groups, and how many records sit in those groups."""
    if df is None or df.empty:
        return 0, 0
    if kind == "doi":
        if "DO" not in df.columns:
            return 0, 0
        doi = df["DO"].map(_norm_doi)
        marked = doi.ne("") & doi.duplicated(keep=False)
        if not marked.any():
            return 0, 0
        return int(doi[marked].nunique()), int(marked.sum())
    if "TI" not in df.columns or "PY" not in df.columns:
        return 0, 0
    mask = _title_dup_row_mask(df)
    if mask is None or not bool(mask.any()):
        return 0, 0
    sub = df.loc[mask].copy()
    sub["_gk"] = sub["TI"].map(_cell).str.lower() + "||" + sub["PY"].map(_cell)
    return int(sub["_gk"].nunique()), int(mask.sum())


def _title_dup_row_mask(df):
    import pandas as pd

    if df is None or df.empty or "TI" not in df.columns or "PY" not in df.columns:
        return pd.Series(False, index=getattr(df, "index", None))
    marked = df.duplicated(subset=["TI", "PY"], keep=False)
    mask = pd.Series(False, index=df.index)
    if not marked.any():
        return mask
    sub = df.loc[marked].copy()
    if "status" in sub.columns:
        sub = sub[sub["status"].map(_cell) != "duplicate_doi"]
    sub["_gk"] = sub["TI"].map(_cell).str.lower() + "||" + sub["PY"].map(_cell)
    for _gk, chunk in sub.groupby("_gk", sort=False):
        if len(chunk) >= 2 and _title_chunk_needs_look(chunk):
            mask.loc[chunk.index] = True
    return mask


def _dup_group_count(df, kind: str) -> int:
    return _dup_stats(df, kind)[0]


def _nodoi_mask(df):
    """Keepable records with no DOI that were not already in DOI or title groups."""
    if df is None or df.empty or "DO" not in df.columns:
        return None
    dcol = df["DO"].map(_norm_doi)
    keep = df["status"].map(_cell).isin(KEEPABLE) if "status" in df.columns else True
    in_title = _title_dup_row_mask(df)
    return dcol.eq("") & keep & ~in_title


def audit_overview() -> dict:
    """Counts for the Audit landing page — one Excel read, no per-row copies."""
    data = load_decisions()
    applied = apply_decisions(data)
    empty = {
        "error": applied.get("error") or "",
        "n_master": 0,
        "n_doi": 0, "n_doi_records": 0,
        "n_title": 0, "n_title_records": 0,
        "n_book": 0, "n_nodoi": 0, "n_kept": 0, "n_keep_both": 0,
        "n_script": applied.get("n_script") or 0,
        "n_forward": applied.get("n_forward") or 0,
        "original_applied": bool(data.get("original_applied")),
        "n_original": data.get("n_original") or 0,
        "n_extra_excluded": data.get("n_extra_excluded") or 0,
    }
    df = applied.get("df")
    if applied.get("error") or df is None or df.empty:
        return empty
    status = df["status"].map(_cell) if "status" in df.columns else None
    n_doi, n_doi_records = _dup_stats(df, "doi")
    n_title, n_title_records = _dup_stats(df, "title")
    nodoi = _nodoi_mask(df)
    return {
        "error": "",
        "n_master": int(len(df)),
        "n_doi": n_doi,
        "n_doi_records": n_doi_records,
        "n_title": n_title,
        "n_title_records": n_title_records,
        "n_book": int((status == "non_article_type").sum()) if status is not None else 0,
        "n_nodoi": int(nodoi.sum()) if nodoi is not None else 0,
        "n_kept": int(status.isin(KEEPABLE).sum()) if status is not None else 0,
        "n_keep_both": _n_keep_both_from_applied(applied),
        "n_script": applied.get("n_script") or 0,
        "n_forward": applied.get("n_forward") or 0,
        "original_applied": bool(data.get("original_applied")),
        "n_original": data.get("n_original") or 0,
        "n_extra_excluded": data.get("n_extra_excluded") or 0,
    }


def _group_label(kind: str, members: list[dict]) -> str:
    title = (members[0].get("TI") or "")[:72]
    if kind == "doi":
        doi = members[0].get("DO") or ""
        return f"{doi or 'no DOI'}  ·  {title}"
    year = members[0].get("PY") or ""
    return f"{year}  ·  {title}"


def load_decisions() -> dict:
    empty = {
        "events": [], "duplicates": {"doi": {}, "title": {}},
        "exclude": [], "include": [], "reviewed": {}, "doi_assign": [],
        "record_notes": [], "group_notes": {},
    }
    path = decisions_path()
    if not path.exists():
        return dict(empty)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return dict(empty)
    data.setdefault("events", [])
    data.setdefault("duplicates", {"doi": {}, "title": {}})
    data.setdefault("exclude", [])
    data.setdefault("include", [])
    data.setdefault("reviewed", {})
    data["duplicates"].setdefault("doi", {})
    data["duplicates"].setdefault("title", {})
    data.setdefault("doi_assign", [])
    data.setdefault("record_notes", [])
    data.setdefault("group_notes", {})
    return data


def _script_forward(df) -> set[int]:
    if "status" not in df.columns:
        return set(int(i) for i in df["row_ix"].tolist())
    return set(int(i) for i in df.loc[df["status"].isin(KEEPABLE), "row_ix"].tolist())


def apply_decisions(data: dict | None = None) -> dict:
    """Script keep-set, then duplicate choices, then extra excludes."""
    df = _load_master()
    if df is None:
        return {"error": "No all_records_with_status.xlsx yet.", "forward": [], "n_script": 0}
    df = fill_blank_fields_from_duplicates(df)
    data = data or load_decisions()
    forward = _script_forward(df)
    n_script = len(forward)
    for kind in ("doi", "title"):
        for rec in (data.get("duplicates") or {}).get(kind, {}).values():
            keep = {int(x) for x in rec.get("keep") or []}
            drop = {int(x) for x in rec.get("drop") or []}
            forward -= drop
            forward |= keep
    for row in data.get("include") or []:
        try:
            forward.add(int(row.get("row_ix")))
        except (TypeError, ValueError):
            continue
    for row in data.get("exclude") or []:
        try:
            forward.discard(int(row.get("row_ix")))
        except (TypeError, ValueError):
            continue
    return {
        "error": "",
        "df": df,
        "forward": sorted(forward),
        "n_script": n_script,
        "n_forward": len(forward),
    }


def decision_summary(data: dict | None = None) -> dict:
    data = data or load_decisions()
    applied = apply_decisions(data)
    swapped = 0
    kept_both = 0
    reviewed = 0
    for kind in ("doi", "title"):
        for rec in (data.get("duplicates") or {}).get(kind, {}).values():
            reviewed += 1
            action = rec.get("action") or "keep_one"
            if action == "keep_both":
                kept_both += 1
            script = rec.get("script_keep")
            keep = [int(x) for x in rec.get("keep") or []]
            if action == "keep_one" and script is not None and keep and int(keep[0]) != int(script):
                swapped += 1
    return {
        "error": applied.get("error") or "",
        "n_script": applied.get("n_script") or 0,
        "n_forward": applied.get("n_forward") or 0,
        "n_exclude": len(data.get("exclude") or []),
        "n_reviewed_doi": len((data.get("duplicates") or {}).get("doi") or {}),
        "n_reviewed_title": len((data.get("duplicates") or {}).get("title") or {}),
        "n_swapped": swapped,
        "n_kept_both": kept_both,
        "has_file": decisions_path().exists(),
        "has_forward": forward_path().exists(),
    }


def save_decisions(data: dict) -> Path:
    data = dict(data)
    data["saved"] = _now()
    applied = apply_decisions(data)
    if applied.get("error"):
        raise FileNotFoundError(applied["error"])
    df = applied["df"]
    forward_ix = set(applied["forward"])
    data["forward_row_ix"] = sorted(forward_ix)
    data["n_script"] = applied["n_script"]
    data["n_forward"] = applied["n_forward"]
    dest = decisions_path()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = df[df["row_ix"].isin(forward_ix)].copy()
    out["audit_forward"] = True
    out.to_excel(forward_path(), index=False)
    _write_decisions_txt(data, applied)
    return dest


def _write_decisions_txt(data: dict, applied: dict) -> Path:
    dest = _audit() / "record_decisions.txt"
    lines = [
        "=== RECORD DECISIONS (after manual check) ===",
        f"Date: {data.get('saved')}",
        "",
        f"Script kept: {applied.get('n_script')}",
        f"Go to screening: {applied.get('n_forward')}",
        f"DOI groups reviewed: {len((data.get('duplicates') or {}).get('doi') or {})}",
        f"Title groups reviewed: {len((data.get('duplicates') or {}).get('title') or {})}",
        f"Original kept list: {data.get('n_original') or '—'}",
        f"Held back (not in original): {data.get('n_extra_excluded') or 0}",
        f"Keep-both groups: {keep_both_count(data)}",
        f"Keep both confirmed: {bool((data.get('reviewed') or {}).get('both'))}",
        f"DOI assigned: {len(data.get('doi_assign') or [])}",
        f"Record notes: {len(record_note_map(data))}",
        f"Extra excludes: {len(data.get('exclude') or [])}",
        "",
        "Duplicate DOI — how copies differed and what was kept:",
    ]
    lines.extend(doi_audit_protocol_lines(data))
    lines += [
        "",
        "Duplicate groups:",
    ]
    for kind in ("doi", "title"):
        items = (data.get("duplicates") or {}).get(kind) or {}
        if not items:
            continue
        lines.append(f"  [{kind}]")
        for key, rec in items.items():
            keep = rec.get("keep") or []
            drop = rec.get("drop") or []
            lines.append(
                f"  - {key[:80]}  action={rec.get('action')}  "
                f"keep={keep}  drop={drop}  script_keep={rec.get('script_keep')}"
            )
    if data.get("exclude"):
        lines += ["", "Extra excludes:"]
        for row in data["exclude"]:
            lines.append(
                f"  - row {row.get('row_ix')}: {row.get('reason') or ''}  "
                f"{(row.get('TI') or '')[:80]}"
            )
    interventions = manual_intervention_lines(data, applied)
    lines += ["", f"Manual interventions — exact records (n={len(interventions)}):"]
    if interventions:
        lines.extend(f"  - {line}" for line in interventions)
    else:
        lines.append("  (none — script defaults kept)")
    note_lines = audit_notes_protocol_lines(data)
    if note_lines:
        lines += ["", *note_lines]
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dest


def set_group_choice(data: dict, group: dict, action: str, keep: list[int]) -> dict:
    kind = group["kind"]
    members = [int(m["row_ix"]) for m in group["members"]]
    keep_ix = [int(x) for x in keep]
    drop = [i for i in members if i not in keep_ix]
    data.setdefault("duplicates", {}).setdefault(kind, {})
    blob = {
        "action": action,
        "keep": keep_ix,
        "drop": drop,
        "script_keep": int(group["script_keep"]),
        "ts": _now(),
        "label": group.get("label") or "",
    }
    if kind == "doi":
        blob["match"] = doi_pair_match(group)
        blob["form"] = doi_pair_form(group)
        blob["diffs"] = doi_field_diffs(group)
    data["duplicates"][kind][group["key"]] = blob
    data.setdefault("events", []).append({
        "ts": _now(),
        "kind": f"{kind}_group",
        "key": group["key"],
        "action": action,
        "keep": keep_ix,
        "drop": drop,
        "changed_from_script": action != "keep_one" or keep_ix != [int(group["script_keep"])],
    })
    return data


def confirm_script_remaining(kind: str, data: dict | None = None) -> dict:
    data = data or load_decisions()
    chosen = (data.get("duplicates") or {}).get(kind) or {}
    for group in duplicate_groups(kind):
        if group["key"] in chosen:
            continue
        set_group_choice(data, group, "keep_one", [int(group["script_keep"])])
    return data


def records_without_doi() -> list[dict]:
    """Keepable records with no DOI. Default: they go forward unless unchecked."""
    applied = apply_decisions()
    if applied.get("error"):
        return []
    df = applied.get("df")
    mask = _nodoi_mask(df)
    if df is None or mask is None or not bool(mask.any()):
        return []
    forward = set(applied.get("forward") or [])
    rows = []
    for _, rec in df.loc[mask].iterrows():
        view = record_view(rec)
        view["forward"] = view["row_ix"] in forward
        rows.append(view)
    return rows


def records_for_status(status: str) -> list[dict]:
    applied = apply_decisions()
    if applied.get("error"):
        return []
    df = applied["df"]
    if df is None or "status" not in df.columns:
        return []
    forward = set(applied["forward"])
    if status == "correct_record":
        mask = df["status"].isin(KEEPABLE)
    else:
        mask = df["status"] == status
    rows = []
    for _, rec in df.loc[mask].iterrows():
        view = record_view(rec)
        view["forward"] = view["row_ix"] in forward
        rows.append(view)
    return rows


def set_row_keep(
    data: dict, row_ix: int, keep: bool, title: str = "", status: str = "", reason: str = "",
) -> dict:
    ix = int(row_ix)
    data.setdefault("include", [])
    data.setdefault("exclude", [])
    data["include"] = [e for e in data["include"] if int(e.get("row_ix")) != ix]
    data["exclude"] = [e for e in data["exclude"] if int(e.get("row_ix")) != ix]
    blob = {"row_ix": ix, "TI": title, "status": status, "ts": _now()}
    why = reason or "Unchecked in audit list"
    if keep:
        data["include"].append(blob)
    else:
        data["exclude"].append({**blob, "reason": why})
        data.setdefault("events", []).append({
            "ts": _now(), "kind": "exclude", "row_ix": ix, "reason": why, "TI": title,
        })
    return data


def set_exclude(data: dict, row_ix: int, reason: str, title: str = "", note: str = "") -> dict:
    data.setdefault("exclude", [])
    data["exclude"] = [e for e in data["exclude"] if int(e.get("row_ix")) != int(row_ix)]
    if reason:
        data["exclude"].append({
            "row_ix": int(row_ix),
            "reason": reason,
            "TI": title,
            "note": note,
            "ts": _now(),
        })
        data.setdefault("events", []).append({
            "ts": _now(),
            "kind": "exclude",
            "row_ix": int(row_ix),
            "reason": reason,
            "TI": title,
        })
    return data


def records_for_picker() -> dict:
    """Kept-by-script plus any currently forwarded duplicate, for the go-forward list."""
    applied = apply_decisions()
    if applied.get("error"):
        return applied
    df = applied["df"]
    forward = set(applied["forward"])
    rows = []
    for _, rec in df.iterrows():
        view = record_view(rec)
        view["forward"] = view["row_ix"] in forward
        if view["keepable"] or view["forward"] or view.get("status") in {"duplicate_doi", "duplicate_title"}:
            rows.append(view)
    return {
        "error": "",
        "rows": rows,
        "n_forward": len(forward),
        "n_script": applied["n_script"],
    }
