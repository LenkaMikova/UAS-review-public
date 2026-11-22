"""Manual recodes of automatic extraction groups.

Script Excel files are not replaced. Each move is stored with the exact
record (DOI / title / year) and copied into the executed protocol.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from project_paths import data_root

EXCLUSIVE = ("reviews", "include", "maybe", "exclude")
FLAGS = ("core", "extended", "must_cite")
ASSIGNABLE = EXCLUSIVE
UNCLASSIFIED = "unclassified"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _folder() -> Path:
    return data_root() / "40_extraction" / "43_recode"


def json_path() -> Path:
    return _folder() / "extract_recodes.json"


def txt_path() -> Path:
    return _folder() / "extract_recodes.txt"


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


def _norm_doi(val: str) -> str:
    text = _cell(val).lower()
    text = text.replace("https://doi.org/", "").replace("http://doi.org/", "")
    return text.strip().strip("/")


def record_key(row: dict, *, source: str = "", row_ix=None) -> str:
    doi = _norm_doi(row.get("DO") or row.get("DOI") or "")
    if doi:
        return f"doi:{doi}"
    title = _cell(row.get("TI") or row.get("Title") or "").lower()
    year = _cell(row.get("PY") or row.get("Year") or "")
    if title:
        return f"title:{title}|{year}"
    ur = _cell(row.get("UR") or row.get("L1") or row.get("L2") or "").lower()
    if ur:
        return f"url:{ur}"
    ix = row_ix if row_ix is not None else row.get("row_ix")
    ty = _cell(row.get("TY") or row.get("TY_label") or "")
    src = source or _cell(row.get("_source") or "")
    return f"notitle:{src}:{ix}:{ty}"


def record_label(row: dict) -> str:
    year = _cell(row.get("PY") or row.get("Year") or "")
    title = _cell(row.get("TI") or row.get("Title") or "")
    doi = _cell(row.get("DO") or row.get("DOI") or "")
    bit = f"{year} {title}".strip() or "(no title)"
    if doi:
        return f"{bit} [{doi}]"
    return bit


def empty() -> dict:
    return {"saved_at": "", "entries": []}


def load() -> dict:
    path = json_path()
    if not path.exists():
        return empty()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return empty()
    data.setdefault("entries", [])
    return data


def _read_script_xlsx(*parts: str):
    import pandas as pd

    path = data_root().joinpath(*parts)
    if not path.exists():
        return None
    try:
        return pd.read_excel(path)
    except Exception:
        return None


def _row_from_series(rec) -> dict:
    from record_audit import record_view
    return record_view(rec)


def _truth(val) -> bool:
    if val is True:
        return True
    return str(val or "").strip().lower() in {"true", "1", "yes"}


def _original_group(row: dict, *, from_reviews: bool) -> str:
    if from_reviews or _truth(row.get("is_review")):
        return "reviews"
    dec = _cell(row.get("screening_decision")).lower()
    if dec in EXCLUSIVE:
        return dec
    return UNCLASSIFIED


def originals() -> dict[str, dict]:
    """Map recode key → script-original row + automatic group (not after_manual_check)."""
    out: dict[str, dict] = {}
    screened = _read_script_xlsx("30_screening", "31_dataset", "screened_records.xlsx")
    if screened is not None and not screened.empty:
        work = screened.copy()
        if "row_ix" not in work.columns:
            work["row_ix"] = range(len(work))
        for _, rec in work.iterrows():
            row = _row_from_series(rec)
            ix = row.get("row_ix")
            key = record_key(row, source="screened", row_ix=ix)
            out[key] = {
                "key": key,
                "row": row,
                "group": _original_group(row, from_reviews=False),
                "must_cite": _truth(row.get("must_cite")),
                "must_cite_strict": _truth(row.get("must_cite_strict")),
                "source": "screened",
            }
    reviews = _read_script_xlsx("30_screening", "34_reviews", "review_articles.xlsx")
    if reviews is None:
        reviews = _read_script_xlsx("40_extraction", "42_reviews", "review_articles.xlsx")
    if reviews is not None and not reviews.empty:
        work = reviews.copy()
        if "row_ix" not in work.columns:
            work["row_ix"] = range(len(work))
        for _, rec in work.iterrows():
            row = _row_from_series(rec)
            ix = row.get("row_ix")
            key = record_key(row, source="reviews", row_ix=ix)
            if key in out:
                if key.startswith("doi:"):
                    continue
                key = f"{key}|reviews:{ix}"
            out[key] = {
                "key": key,
                "row": row,
                "group": "reviews",
                "must_cite": _truth(row.get("must_cite")),
                "must_cite_strict": _truth(row.get("must_cite_strict")),
                "source": "reviews",
            }
    return out


def applied(data: dict | None = None) -> dict[str, dict]:
    state = originals()
    blob = data if data is not None else load()
    for entry in blob.get("entries") or []:
        key = entry.get("key") or ""
        item = state.get(key)
        if item is None:
            snap = entry.get("row") or {}
            item = {
                "key": key,
                "row": snap,
                "group": entry.get("from_group") or UNCLASSIFIED,
                "must_cite": bool(entry.get("from_must_cite")),
                "must_cite_strict": bool(entry.get("from_must_cite_strict")),
                "source": entry.get("source") or "screened",
            }
            state[key] = item
        action = entry.get("action") or ""
        if action == "remove":
            item["group"] = UNCLASSIFIED
        elif action == "assign":
            dest = entry.get("to_group") or UNCLASSIFIED
            item["group"] = dest
            if dest == "reviews":
                item["must_cite"] = False
                item["must_cite_strict"] = False
            if entry.get("must_cite") is not None:
                item["must_cite"] = bool(entry["must_cite"])
            if entry.get("must_cite_strict") is not None:
                item["must_cite_strict"] = bool(entry["must_cite_strict"])
            if item["must_cite_strict"]:
                item["must_cite"] = True
        elif action == "clear_flag":
            flag = entry.get("from_group")
            if flag == "core":
                item["must_cite_strict"] = False
            elif flag in {"extended", "must_cite"}:
                item["must_cite"] = False
                item["must_cite_strict"] = False
        item["last_action"] = action
        item["last_entry"] = entry
    return state


def rows_for(kind: str, state: dict[str, dict] | None = None) -> list[dict]:
    items = (state or applied()).values()
    out = []
    for item in items:
        row = dict(item["row"])
        row["_key"] = item["key"]
        row["_group"] = item["group"]
        row["must_cite"] = item["must_cite"]
        row["must_cite_strict"] = item["must_cite_strict"]
        if kind == UNCLASSIFIED:
            if item["group"] == UNCLASSIFIED:
                out.append(row)
        elif kind == "reviews":
            if item["group"] == "reviews":
                out.append(row)
        elif kind in {"include", "maybe", "exclude"}:
            if item["group"] == kind:
                out.append(row)
        elif kind == "must_cite":
            if item["must_cite"] and item["group"] == "include":
                out.append(row)
        elif kind == "core":
            if item["must_cite_strict"] and item["group"] == "include":
                out.append(row)
        elif kind == "extended":
            if item["must_cite"] and not item["must_cite_strict"] and item["group"] == "include":
                out.append(row)
        elif kind == "include_rest":
            if item["group"] == "include" and not item["must_cite"]:
                out.append(row)
    return out


def overview(state: dict[str, dict] | None = None) -> dict:
    items = list((state or applied()).values())
    n_inc = sum(1 for i in items if i["group"] == "include")
    n_may = sum(1 for i in items if i["group"] == "maybe")
    n_exc = sum(1 for i in items if i["group"] == "exclude")
    n_rev = sum(1 for i in items if i["group"] == "reviews")
    n_unc = sum(1 for i in items if i["group"] == UNCLASSIFIED)
    n_must_inc = sum(1 for i in items if i["must_cite"] and i["group"] == "include")
    n_core = sum(1 for i in items if i["must_cite_strict"] and i["group"] == "include")
    n_ext = n_must_inc - n_core
    n_screen = n_inc + n_may + n_exc
    n_must_may = sum(1 for i in items if i["must_cite"] and i["group"] == "maybe")
    n_must_exc = sum(1 for i in items if i["must_cite"] and i["group"] == "exclude")
    n_must = n_must_inc
    return {
        "error": "",
        "n_must_cite": n_must,
        "n_core": n_core,
        "n_extended": max(n_ext, 0),
        "n_include_rest": n_inc - n_must_inc,
        "n_include": n_inc,
        "n_maybe": n_may,
        "n_exclude": n_exc,
        "n_reviews": n_rev,
        "n_unclassified": n_unc,
        "n_must_in_include": n_must_inc,
        "n_must_in_maybe": n_must_may,
        "n_must_in_exclude": n_must_exc,
        "n_screen": n_screen,
        "n_recode": len((load().get("entries") or [])),
        "source": "screened_records + extract_recodes",
    }


def _txt(data: dict) -> str:
    entries = data.get("entries") or []
    lines = [
        "Extraction recodes — manual changes to the automatic grouping.",
        "The script Excel files were not replaced. Each line is one record.",
        f"Saved: {data.get('saved_at') or _now()}",
        f"n = {len(entries)}",
        "",
    ]
    if not entries:
        lines.append("(none)")
        return "\n".join(lines) + "\n"
    for i, e in enumerate(entries, 1):
        label = e.get("label") or record_label(e.get("row") or {})
        action = e.get("action")
        if action == "remove":
            what = f"removed from {e.get('from_group')} → unclassified"
        elif action == "assign":
            origin = e.get("from_group") or "unclassified"
            what = f"moved {origin} → {e.get('to_group')}"
            flags = []
            if e.get("must_cite"):
                flags.append("must_cite")
            if e.get("must_cite_strict"):
                flags.append("core")
            if flags:
                what += " (" + ", ".join(flags) + ")"
        elif action == "clear_flag":
            what = f"removed flag {e.get('from_group')} (record stays in {e.get('stays_in') or 'its screening group'})"
        else:
            what = action or "recode"
        lines.append(f"{i}. {what}")
        lines.append(f"   {label}")
        if e.get("ts"):
            lines.append(f"   {e['ts']}")
        lines.append("")
    return "\n".join(lines)


def save(data: dict) -> dict:
    folder = _folder()
    folder.mkdir(parents=True, exist_ok=True)
    data = dict(data)
    data["saved_at"] = _now()
    state = applied(data)
    data["n_unclassified"] = sum(1 for i in state.values() if i["group"] == UNCLASSIFIED)
    json_path().write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    txt_path().write_text(_txt(data), encoding="utf-8")
    write_tables(data)
    return data


def _append(action: str, items: list[dict], **extra) -> dict:
    data = load()
    ts = _now()
    for item in items:
        row = dict(item.get("row") or item)
        entry = {
            "ts": ts,
            "action": action,
            "key": item.get("key") or record_key(row),
            "label": record_label(row),
            "doi": _cell(row.get("DO") or row.get("DOI") or ""),
            "title": _cell(row.get("TI") or row.get("Title") or ""),
            "year": _cell(row.get("PY") or row.get("Year") or ""),
            "source": item.get("source") or "screened",
            "from_group": item.get("group"),
            "from_must_cite": item.get("must_cite"),
            "from_must_cite_strict": item.get("must_cite_strict"),
            "row": row,
        }
        entry.update(extra)
        data["entries"].append(entry)
    return save(data)


def _pick_state_items(state: dict[str, dict], keys: list[str]) -> list[dict]:
    picked: list[dict] = []
    seen: set[str] = set()
    by_ix: dict[str, dict] = {}
    for item in state.values():
        ix = item.get("row", {}).get("row_ix")
        src = item.get("source") or ""
        if ix is not None and str(ix) != "":
            by_ix[f"{src}:{ix}"] = item
            by_ix[str(ix)] = item
    for raw in keys:
        k = str(raw or "")
        if not k or k in seen:
            continue
        item = state.get(k) or by_ix.get(k)
        if item is None:
            for cand in state.values():
                if cand.get("key") == k or str((cand.get("row") or {}).get("row_ix")) == k:
                    item = cand
                    break
        if item is None:
            continue
        ident = item.get("key") or k
        if ident in seen:
            continue
        seen.add(ident)
        seen.add(k)
        picked.append(item)
    return picked


def remove_from_group(kind: str, keys: list[str]) -> dict:
    state = applied()
    picked = _pick_state_items(state, keys)
    if not picked:
        return load()
    if kind in FLAGS:
        return _append(
            "clear_flag",
            picked,
            from_group=kind,
            stays_in=picked[0]["group"] if picked else "",
        )
    return _append("remove", picked, from_group=kind, to_group=UNCLASSIFIED)


def assign_group(
    keys: list[str],
    dest: str,
    *,
    must_cite: bool = False,
    must_cite_strict: bool = False,
) -> dict:
    if dest not in ASSIGNABLE:
        raise ValueError(f"Cannot assign to {dest}")
    state = applied()
    picked = _pick_state_items(state, keys)
    if not picked:
        return load()
    extra = {
        "to_group": dest,
        "must_cite": bool(must_cite or must_cite_strict) if dest == "include" else False,
        "must_cite_strict": bool(must_cite_strict) if dest == "include" else False,
    }
    return _append("assign", picked, **extra)


def move_keys(
    kind: str,
    keys: list[str],
    dest: str,
    *,
    must_cite: bool = False,
    must_cite_strict: bool = False,
) -> dict:
    """Move records out of the current list. dest is an exclusive group, unclassified, or clear_flag."""
    dest = (dest or "").strip().lower().replace(" ", "_")
    if dest in {"clear_flag", "clear_flag_only"}:
        return remove_from_group(kind, keys)
    if dest == UNCLASSIFIED:
        state = applied()
        picked = _pick_state_items(state, keys)
        if not picked:
            return load()
        return _append("remove", picked, from_group=kind, to_group=UNCLASSIFIED)
    if dest not in ASSIGNABLE:
        raise ValueError(f"Cannot move to {dest}")
    if kind in FLAGS and dest == "include" and not must_cite and not must_cite_strict:
        return remove_from_group(kind, keys)
    return assign_group(keys, dest, must_cite=must_cite, must_cite_strict=must_cite_strict)


def write_tables(data: dict | None = None) -> dict:
    """Write after_manual_check copies. Original script files stay."""
    import pandas as pd
    from project_paths import AFTER_MANUAL_CHECK

    state = applied(data)
    screened_src = _read_script_xlsx("30_screening", "31_dataset", "screened_records.xlsx")
    cols = list(screened_src.columns) if screened_src is not None else []
    for extra in (
        "TI", "PY", "AU", "DO", "screening_decision", "must_cite",
        "must_cite_strict", "is_review", "relevance_score", "extract_recode",
    ):
        if extra not in cols:
            cols.append(extra)

    screened_rows = []
    review_rows = []
    for item in state.values():
        row = dict(item["row"])
        recode = item.get("last_action") or ""
        if recode:
            row["extract_recode"] = recode
        if item["group"] == UNCLASSIFIED:
            continue
        if item["group"] == "reviews":
            row["is_review"] = True
            if not _cell(row.get("relevance_score")):
                row["relevance_score"] = 0
            review_rows.append(row)
            screened_rows.append(row)
            continue
        row["is_review"] = False
        row["screening_decision"] = item["group"]
        row["must_cite"] = bool(item["must_cite"])
        row["must_cite_strict"] = bool(item["must_cite_strict"])
        if not _cell(row.get("relevance_score")):
            row["relevance_score"] = 0
        screened_rows.append(row)

    def _frame(rows: list[dict]) -> pd.DataFrame:
        if not rows:
            return pd.DataFrame(columns=cols)
        df = pd.DataFrame(rows)
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        keep = [c for c in cols if c in df.columns]
        extra = [c for c in df.columns if c not in keep and not str(c).startswith("_")]
        return df[keep + extra]

    dest_screen = (
        data_root() / "30_screening" / "31_dataset" / "checked"
        / f"screened_records_{AFTER_MANUAL_CHECK}.xlsx"
    )
    dest_rev = (
        data_root() / "30_screening" / "34_reviews" / "checked"
        / f"review_articles_{AFTER_MANUAL_CHECK}.xlsx"
    )
    dest_screen.parent.mkdir(parents=True, exist_ok=True)
    dest_rev.parent.mkdir(parents=True, exist_ok=True)
    _frame(screened_rows).to_excel(dest_screen, index=False)
    _frame(review_rows).to_excel(dest_rev, index=False)
    return {"screened": dest_screen, "reviews": dest_rev, "n_screened": len(screened_rows), "n_reviews": len(review_rows)}


def protocol_block() -> str:
    data = load()
    entries = data.get("entries") or []
    if not entries:
        return (
            "No manual recodes of the automatic extraction groups. "
            "Reviews / Include / Maybe / Exclude / must-cite are as the screening script left them."
        )
    n_unc = data.get("n_unclassified")
    if n_unc is None:
        n_unc = overview().get("n_unclassified") or 0
    lines = [
        f"Manual recodes of automatic extraction groups: **{len(entries)}** action(s). "
        f"Unclassified (not yet reassigned): **{n_unc}**. "
        f"Log: `40_extraction/43_recode/extract_recodes.txt`. "
        "The screening script files were not replaced; after_manual_check copies were written.",
        "",
    ]
    path = txt_path()
    if path.exists():
        lines += [
            "<details><summary>extract_recodes.txt (exact records)</summary>",
            "",
            "```",
            path.read_text(encoding="utf-8").strip(),
            "```",
            "",
            "</details>",
        ]
    return "\n".join(lines)
