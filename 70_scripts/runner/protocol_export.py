"""PRISMA-P markdown from runner settings (planned) or from executed reports."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
import sys

_RUNNER = Path(__file__).resolve().parent
sys.path.insert(0, str(_RUNNER))
sys.path.insert(0, str(_RUNNER.parent))
from project_paths import CODE_ROOT, data_root

from catalog import DEFAULT_SETTINGS, STEPS, format_type_counts
import prisma_flow

LINKS_PATH = Path(__file__).with_name("links.json")
SCREEN_CFG_SHIPPED = CODE_ROOT / "70_scripts" / "pipeline" / "screening_config.json"


def _root() -> Path:
    return data_root()


def _generated() -> Path:
    return _root() / "60_prisma" / "protocol" / "generated"


def _screen_cfg() -> Path:
    live = _root() / "30_screening" / "33_reports" / "screening_config.json"
    used = _root() / "30_screening" / "33_reports" / "screening_config_used.json"
    if used.exists():
        return used
    if live.exists():
        return live
    return SCREEN_CFG_SHIPPED


def _query_params() -> Path:
    return _root() / "00_search" / "02_final" / "final_query_params.json"


def _query_txt() -> Path:
    return _root() / "00_search" / "02_final" / "final_query.txt"


def _ris_meta() -> Path:
    return _root() / "10_data_raw" / "12_final" / "ris_meta.json"


def _merge_report() -> Path:
    return _root() / "20_data_clean" / "21_audit" / "processing_report.txt"


def _exclusion_log() -> Path:
    return _root() / "20_data_clean" / "21_audit" / "exclusion_log.json"


def _manual_log() -> Path:
    return _root() / "20_data_clean" / "21_audit" / "manual_exclusions.json"


def _classification_review() -> Path:
    return _root() / "20_data_clean" / "21_audit" / "classification_review.json"


def _screen_summary() -> Path:
    return _root() / "30_screening" / "33_reports" / "screening_summary.txt"


def _run_log() -> Path:
    return _root() / "run_journal.jsonl"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _json(path: Path, default=None):
    if not path.exists():
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _links() -> dict:
    return _json(LINKS_PATH, {}) or {}


def _settings() -> dict:
    data = dict(DEFAULT_SETTINGS)
    saved = _json(_root() / "run_settings.json", {}) or {}
    data.update({k: v for k, v in saved.items() if v is not None})
    return data


def _procedure_block() -> str:
    lines = [
        "The Review runner executes **one step at a time** (the step currently open). "
        "Outputs are written to the folder chosen in step 1. Script outputs are kept; "
        "a later manual check is uploaded as a new file. Replace existing script files "
        "only when starting a new automated run.",
        "",
    ]
    for spec in STEPS:
        if spec["id"] in {"output"}:
            continue
        lines.append(f"### {spec['title']}")
        lines.append("")
        lines.append(spec["what"].replace("\n\n", " ").replace("\n", " "))
        lines.append("")
        lines.append(f"- Input: {spec['inputs']}")
        lines.append(f"- Output: {spec['outputs']}")
        if spec.get("script"):
            lines.append(f"- Script: `{spec['script']}`")
        lines.append("")
    return "\n".join(lines)


def _search_block() -> str:
    params = _json(_query_params())
    txt = _read(_query_txt()).strip()
    if params:
        inp = params.get("input", params)
        groups = inp.get("groups") or []
        lines = ["Concept groups (AND):"]
        for i, g in enumerate(groups, 1):
            lines.append(f"{i}. `{', '.join(g.get('terms') or [])}` — field `{g.get('field', 'all')}`")
        for ex in inp.get("exclude") or []:
            lines.append(f"NOT `{', '.join(ex.get('terms') or [])}` — field `{ex.get('field', 'all')}`")
        y0, y1 = inp.get("year_from"), inp.get("year_to")
        if y0:
            lines.append(f"Years: {y0}–{y1}. Language: {inp.get('language') or 'not set'}.")
        dbs = params.get("databases") or inp.get("databases") or []
        if dbs:
            if isinstance(dbs, str):
                dbs = [dbs]
            lines.append("Databases: " + "; ".join(dbs))
        q = params.get("queries") or {}
        if q.get("boolean"):
            lines += ["", "**Boolean (adapt per database)**", "", "```", q["boolean"], "```"]
        if q.get("web_of_science"):
            lines += ["", "**Web of Science**", "", "```", q["web_of_science"], "```"]
        if q.get("scopus"):
            lines += ["", "**Scopus**", "", "```", q["scopus"], "```"]
        return "\n".join(lines)
    if txt:
        return "Frozen query (`00_search/02_final/final_query.txt`):\n\n```\n" + txt + "\n```"
    return "_Search strings have not been frozen yet._"


def _screening_cfg() -> dict:
    return _json(_screen_cfg()) or {}


def _md_table_data_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.startswith("|")]
    data = [
        ln for ln in lines[2:]
        if not re.match(r"^\|\s*:?-+:?[\s\|:-]*\|$", ln)
    ]
    return len(data) or None


def _screen_n(pattern: str) -> int | None:
    text = _read(_screen_summary())
    if not text:
        return None
    m = re.search(pattern, text, re.MULTILINE)
    return int(m.group(1)) if m else None


def _synthesis_block(retrospective: bool) -> str:
    if not retrospective:
        return (
            "As implemented by `extraction_templ.py` and any manual full-text fields. "
            "Quantitative meta-analysis is not part of the automated runner unless added later and logged."
        )
    must = _screen_n(r"^Must-cite: (\d+)")
    core = _screen_n(r"Must-cite \(core\): (\d+)")
    ext = _screen_n(r"Must-cite \(extended\): (\d+)")
    reviews = _screen_n(r"Review articles: (\d+)")
    n_studies = _md_table_data_rows(
        _root() / "90_review" / "92_appendix" / "or-09-inputs.qmd"
    )
    n_uav = _md_table_data_rows(
        _root() / "90_review" / "92_appendix" / "or-13-uav.qmd"
    )
    leftover = None
    if must is not None and n_studies is not None:
        leftover = must - n_studies
    s = _settings()
    inc_s = (s.get("prisma_included_studies") or "").strip() or n_studies
    inc_r = (s.get("prisma_included_reports") or "").strip() or inc_s
    lines = [
        "Automated (title/abstract/keywords): platform, sensor, domain, method, scaling, UAV flags, score, screening decision, must-cite flags.",
        "",
        "Manual full-text extraction is the must-cite (HIGH) subset. Outcomes are methodological (what was measured, how, and what was reported), not a pooled SM accuracy. **No meta-analysis.** Risk of bias, GRADE, and small-study bias were not assessed.",
        "",
        "Executed counts (`30_screening/33_reports/screening_summary.txt` and Online Resources 9 and 13):",
        "",
        f"- reviews set aside: {reviews if reviews is not None else '—'}",
        f"- must-cite: {must if must is not None else '—'} "
        f"(core {core if core is not None else '—'}; extended {ext if ext is not None else '—'})",
        f"- unique studies extracted (OR 9–11): {n_studies if n_studies is not None else '—'}",
        f"- UAV campaigns (OR 13): {n_uav if n_uav is not None else '—'}",
        f"- leftover must-cite records that are not additional studies: {leftover if leftover is not None else '—'} "
        "(Hussain 2025 correction, Surendran 2024 chapter, Montzka 2020 conference paper)",
        f"- PRISMA included studies / reports (runner boxes, else OR 9): {inc_s} / {inc_r}",
        "",
        "Keyword co-occurrence (VOSviewer) uses the must-cite RIS file. "
        "The Zenodo/manuscript narrative protocol is `60_prisma/protocol/PRISMA-P_retrospective_protocol.md` "
        "(Generate does not overwrite it). PRISMA 2020 for the article is Online Resource 4.",
    ]
    return "\n".join(lines)


def _screening_block(cfg: dict) -> str:
    w = cfg.get("weights") or {}
    t = cfg.get("thresholds") or {}
    terms = cfg.get("terms") or {}
    strict = cfg.get("must_cite_strict") or {}
    ext = cfg.get("must_cite_extended") or {}
    lines = [
        "Rule-based title–abstract–keyword screening (`screening_and_deep_classify.py`). "
        "This is **not** dual independent screening.",
        "",
        "Relevance score (sum of weights when the phrase group matches TI+AB+KW):",
        "",
        f"- soil moisture terms (`{', '.join(terms.get('soil_moisture') or ['soil moisture'])}`): +{w.get('soil_moisture', 2)}",
        f"- direct UAV (`{', '.join(terms.get('uav') or [])}`): +{w.get('uav_direct', 3)}",
        f"- scaling (`{', '.join(terms.get('scaling') or [])}`): +{w.get('scaling', 2)}",
        f"- agriculture (`{', '.join(terms.get('domain') or [])}`): +{w.get('agriculture', 1)}",
        "",
        "Decisions:",
        "",
        f"- include: score ≥ {t.get('include_min', 6)}",
        f"- maybe: score ≥ {t.get('maybe_min', 3)} and below include",
        f"- exclude: score < {t.get('maybe_min', 3)}",
        "",
        "Must-cite **strict / core**: "
        f"score ≥ {strict.get('score_min', 7)}"
        + (", direct UAV" if strict.get("require_direct_uav", True) else "")
        + (", scaling phrase" if strict.get("require_scaling", True) else "")
        + ".",
        "",
        "Must-cite flag (`must_cite`): "
        f"score ≥ {ext.get('score_min', 6)}; "
        "direct UAV + scaling"
        + (" **or** potential UAV + (scaling or passive optical)" if ext.get("branch_potential_and_scaling_or_passive", True) else "")
        + ". **Core** = strict subset; **extended studies** = must-cite but not core.",
        "",
        "Potential UAV (does **not** add score points): satellite platform "
        "(or MODIS / Landsat / Sentinel) **and** (high/fine resolution **or** scaling **or** "
        f"passive terms: `{', '.join(terms.get('passive') or [])}`).",
    ]
    return "\n".join(lines)


def _ris_block() -> str:
    meta = _json(_ris_meta()) or {}
    exports = list(meta.get("exports") or [])
    if not exports:
        for key, label in (("wos", "Web of Science"), ("scopus", "Scopus")):
            rec = meta.get(key) or {}
            if rec:
                rec = dict(rec)
                rec["database"] = rec.get("database") or label
                exports.append(rec)
    if not exports:
        return "RIS files are stored in `10_data_raw/`. Download dates have not been recorded yet."
    lines = ["Exports (as recorded in `ris_meta.json`):", ""]
    for rec in exports:
        lines.append(
            f"- **{rec.get('database') or rec.get('file')}**: {rec.get('downloaded_at') or 'date not set'}; "
            f"file `{rec.get('file') or ''}`; records {rec.get('n_records', '?')}"
        )
    return "\n".join(lines)


def _exclusion_block(retrospective: bool) -> str:
    if not retrospective:
        return (
            "At bibliographic audit, records will be **removed** only for: "
            "missing title or year; books / e-books (`TY` BOOK, EBOOK); "
            "duplicate DOI (identical year, title, authors and type: keep one, first keepable; "
            "copies that differ in year, title, authors or publication type are inspected "
            "and the kept record is logged); duplicate title + year. "
            "**Records without a DOI are retained**, flagged `doi_missing`, "
            "and still go through title–year duplicate checks. "
            "Their publication types (journal, conference, chapter) are listed at audit as information, not as an exclusion class. "
            "Conference papers and book chapters are kept; only books / e-books are removed by type. "
            "Journal-versus-conference conflicts and disputed DOIs are resolved manually and logged "
            "in `20_data_clean/21_audit/manual_exclusions.json` (n + reason)."
        )
    auto = _json(_exclusion_log()) or {}
    review = _json(_classification_review()) or {}
    manual = _json(_manual_log()) or {}
    lines = []
    if auto:
        lines.append(
            f"Script audit: retained {auto.get('retained')}, removed {auto.get('removed')}."
        )
        lines.append("")
        for e in auto.get("entries") or []:
            kept = "retained" if e.get("kept") else "removed"
            extra = " — cannot exclude" if e.get("cannot_exclude") else ""
            lines.append(f"- {kept}{extra}: n = {e.get('n')} — {e.get('status')}: {e.get('reason')}")
    doi_n = review.get("doi_missing_retained")
    if doi_n is None:
        doi_n = auto.get("doi_missing_retained")
    doi_types = format_type_counts(
        review.get("doi_missing_types") or auto.get("doi_missing_types") or []
    )
    if doi_n:
        extra = f" ({doi_types})" if doi_types else ""
        lines += [
            "",
            f"Records without a DOI retained among those going to screening: n = {doi_n}{extra} "
            "(information only; not excluded for missing DOI).",
        ]
    kept_types = format_type_counts(
        review.get("kept_types") or auto.get("kept_types") or []
    )
    if kept_types:
        lines.append(
            f"Publication types among script-kept records: {kept_types}. "
            "Conference papers and book chapters stayed; books were a remove class."
        )
    classes = review.get("classifications") or []
    if classes:
        lines += ["", "How each class was checked (n → remove → go forward):"]
        for c in classes:
            n = c.get("n")
            rm = c.get("remove")
            fw = c.get("forward")
            if fw is None and n is not None and rm is not None:
                fw = int(n) - int(rm)
            lines.append(
                f"- {c.get('status')}: n = {n}; check: {c.get('check') or 'not stated'}; "
                f"removed {rm if rm is not None else '—'}; go forward {fw if fw is not None else '—'}"
            )
    report = _read(_merge_report()).strip()
    if report:
        lines += ["", "<details><summary>processing_report.txt</summary>", "", "```", report, "```", "", "</details>"]
    rec_txt = _read(_root() / "20_data_clean" / "21_audit" / "record_decisions.txt").strip()
    try:
        import record_audit
        doi_block = record_audit.doi_audit_protocol_block()
    except Exception:
        doi_block = ""
    if doi_block:
        lines += [
            "",
            "Duplicate DOI inspection (how copies differed; which copy went forward and why):",
            "",
            doi_block,
        ]
    try:
        import record_audit as _ra_notes
        note_block = _ra_notes.audit_notes_protocol_lines()
    except Exception:
        note_block = []
    if note_block:
        lines += ["", *note_block]
    if rec_txt:
        lines += [
            "",
            "Record-level audit (which duplicate stayed; which records went to screening). "
            "The merge script files were not replaced.",
            "",
            "<details><summary>record_decisions.txt</summary>",
            "",
            "```",
            rec_txt,
            "```",
            "",
            "</details>",
        ]
    extras = review.get("extra") or (manual.get("entries") if isinstance(manual, dict) else manual) or []
    if extras:
        lines += ["", "Extra removals / notes:"]
        for e in extras:
            kept = "retained" if e.get("kept") else "removed"
            check = f"; check: {e.get('check')}" if e.get("check") else ""
            lines.append(
                f"- {kept}: n = {e.get('n')} — {e.get('reason')}{check}"
                + (f". {e.get('note')}" if e.get("note") else "")
            )
    screen = _read(_screen_summary()).strip()
    if screen:
        lines += ["", "<details><summary>screening_summary.txt</summary>", "", "```", screen, "```", "", "</details>"]
    return "\n".join(lines) if lines else "_No run yet. Generate the retrospective protocol after merge and screening._"


def _run_log_block() -> str:
    log = _run_log()
    if not log.exists():
        return "_No runner log yet._"
    rows = []
    for line in log.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not rows:
        return "_No runner log yet._"
    lines = ["| Time | Step | Action | Result | Detail |", "|---|---|---|---|---|"]
    for r in rows[-80:]:
        ok = "ok" if r.get("ok") else "error"
        detail = str(r.get("detail") or "").replace("|", "/").replace("\n", " ")
        if len(detail) > 120:
            detail = detail[:117] + "…"
        lines.append(
            f"| {r.get('ts', '')} | {r.get('step', '')} | {r.get('action', '')} | {ok} | {detail} |"
        )
    return "\n".join(lines)


def _data_work_path() -> Path:
    return _generated() / "data_work.jsonl"


def _data_work_md_path() -> Path:
    return _generated() / "data_work.md"


def _load_data_work() -> list[dict]:
    path = _data_work_path()
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _write_data_work_md(events: list[dict]) -> Path:
    dest = _data_work_md_path()
    dest.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Work with records (RIS → extraction)",
        "",
        "Written as the run proceeds, starting with the input RIS files. "
        "Every change to an automatic table lists the exact records (DOI / title / year).",
        "",
    ]
    if not events:
        lines.append("_No RIS files have been uploaded yet._")
        dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return dest
    for ev in events:
        lines.append(f"### {ev.get('ts') or ''} — {ev.get('kind') or ''}")
        lines.append("")
        if ev.get("summary"):
            lines.append(str(ev["summary"]))
            lines.append("")
        for name in ev.get("files") or []:
            lines.append(f"- file: `{name}`")
        records = ev.get("records") or []
        if records:
            lines.append("Exact records:")
            lines.append("")
            for rec in records:
                lines.append(f"- {rec}")
            lines.append("")
        elif ev.get("files"):
            lines.append("")
    dest.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return dest


def _data_work_block() -> str:
    events = _load_data_work()
    path = _data_work_md_path()
    if path.exists():
        text = path.read_text(encoding="utf-8").strip()
        if text:
            return text
    if not events:
        return (
            "This log is written from the first RIS import through extraction recodes. "
            "Nothing has been recorded yet."
        )
    _write_data_work_md(events)
    return _data_work_md_path().read_text(encoding="utf-8").strip()


_REFRESHING = False


def append_data_work(
    kind: str,
    summary: str,
    *,
    records: list[str] | None = None,
    files: list[str] | None = None,
    extra: dict | None = None,
) -> None:
    """Append one data-work event and refresh the executed protocol (no stamp)."""
    generated = _generated()
    generated.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "kind": kind,
        "summary": summary,
        "records": list(records or []),
        "files": list(files or []),
    }
    if extra:
        event.update(extra)
    path = _data_work_path()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    events = _load_data_work()
    _write_data_work_md(events)
    refresh_executed()


def refresh_executed() -> str | None:
    """Rewrite PRISMA-P_executed.md from current files. No dated stamp."""
    global _REFRESHING
    if _REFRESHING:
        return None
    try:
        _root()
    except Exception:
        return None
    _REFRESHING = True
    try:
        info = save_markdown("retrospective", stamp=False)
        return info.get("latest")
    except Exception:
        return None
    finally:
        _REFRESHING = False


def build_markdown(mode: str, extra: dict | None = None) -> str:
    extra = extra or {}
    s = _settings()
    s.update({k: v for k, v in extra.items() if v})
    retrospective = mode == "retrospective"
    stamp = datetime.now().isoformat(timespec="seconds")
    title = s.get("title") or "Systematic review"
    title_kind = "Retrospective (executed)" if retrospective else "Prospective (planned)"
    status = (
        "Generated **after** the runner steps. Each step was run separately. "
        "Script outputs are kept; a later manual check is stored as an additional file. "
        "Methods as executed. Not an a priori PROSPERO protocol."
        if retrospective
        else "Generated **before** running the pipeline. Protocol according to which the steps will proceed. "
        "Deposit the protocol DOI before database searches if this is a new review."
    )
    cfg = _screening_cfg()
    doi_p = s.get("doi_protocol") or "—"
    doi_d = s.get("doi_dataset") or "—"
    doi_c = s.get("doi_software") or "—"
    github = s.get("github") or "—"
    rationale = s.get("rationale") or "_Not specified in run settings._"
    objectives = s.get("objectives") or "_Not specified in run settings._"
    inclusion = s.get("inclusion") or "_See search groups._"
    authors_raw = s.get("authors") or "—"
    authors = "\n".join(f"- {line.strip()}" for line in str(authors_raw).splitlines() if line.strip()) or "—"
    support_lines = [ln.strip() for ln in str(s.get("support") or "").splitlines() if ln.strip()]
    if not support_lines:
        support = "Not specified."
    elif len(support_lines) == 1:
        support = support_lines[0]
    else:
        support = "\n".join(f"- {ln}" for ln in support_lines)
    dbs = s.get("databases") or []
    if isinstance(dbs, str):
        dbs = [x.strip() for x in dbs.replace(";", ",").split(",") if x.strip()]
    extra_db = (s.get("databases_other") or "").strip()
    if extra_db:
        dbs = list(dbs) + [extra_db]
    databases = "; ".join(dbs) if dbs else "Not specified."
    flow_block = prisma_flow.protocol_block(_root(), s)
    try:
        import extract_recode
        recode_block = extract_recode.protocol_block()
    except Exception:
        recode_block = "Extraction recodes could not be read."
    reg_type = s.get("registration_type") or "None"
    reg_id = (s.get("registration_id") or "").strip()
    if s.get("registration") and not s.get("registration_type"):
        registration = s["registration"]
    elif reg_type == "None":
        registration = "None."
    else:
        registration = f"{reg_type}: {reg_id}" if reg_id else reg_type
    body = f"""# {title_kind} PRISMA-P protocol — {title}

**Generated.** {stamp}  
**Runner.** One step at a time; outputs go to the folder chosen for this run.  
**Code.** {github}  
**Output DOIs.** protocol {doi_p}; dataset {doi_d}; software {doi_c}

**Status.** {status}

---

## Administrative information (PRISMA-P items 1–5)

### 1. Title

{title} ({'retrospective' if retrospective else 'planned'} protocol).

### 2. Registration

{registration} Protocol DOI: {doi_p}

### 3. Authors

{authors}

Contact: {s.get('contact') or '—'}

### 4. Amendments

Dated in this file and in the run journal. A new export does not overwrite previous stamped copies.

### 5. Support

{support}

---

## Introduction (items 6–7)

### 6. Rationale

{rationale}

### 7. Objectives

{objectives}

---

## Methods (items 8–17)

### 8. Eligibility criteria

**Inclusion**

{inclusion}

**Bibliographic audit (`merge_and_classify.py`)**

{_exclusion_block(retrospective)}

**Screening exclusions**

- Records flagged as reviews are set aside.
- Automated exclude: relevance score below the maybe threshold.

**Not used unless stated in the run journal**

- Independent dual screening.
- A second full-text eligibility round as the definition of the included set (must-cite is a priority subset).

### 9. Information sources

{databases}

{_ris_block()}

### 10. Search strategy

{_search_block()}

### 11. Study records

Data folders: `00_search`, `10_data_raw` (originals in `11_original/`, scripts read `12_final/`), `20_data_clean`, `30_screening`, `40_extraction`. Script outputs are kept. A later manual check is uploaded as a new file (`checked/` or `42_working/`).

**Procedure**

{_procedure_block()}

**Selection process**

{_screening_block(cfg)}

**Work with records (from RIS upload)**

{_data_work_block()}

**Extraction recodes (automatic groups)**

{recode_block}

**PRISMA flow extras**

{flow_block}

### 12–17. Data items, bias, synthesis

{_synthesis_block(retrospective)}

---

## Output identifiers

| Product | DOI |
|---|---|
| Protocol | {doi_p} |
| Dataset | {doi_d} |
| Software / scripts | {doi_c} |

---

## Runner log

{_run_log_block()}
"""
    return body.strip() + "\n"


def save_markdown(
    mode: str,
    extra: dict | None = None,
    destination: Path | None = None,
    *,
    stamp: bool = True,
) -> dict:
    generated = _generated()
    generated.mkdir(parents=True, exist_ok=True)
    md = build_markdown(mode, extra)
    latest_name = f"PRISMA-P_{'executed' if mode == 'retrospective' else 'planned'}.md"
    latest = generated / latest_name
    latest.write_text(md, encoding="utf-8")
    stamped_path = None
    copied = None
    if stamp:
        stamp_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        stamped_name = f"PRISMA-P_{'executed' if mode == 'retrospective' else 'planned'}_{stamp_id}.md"
        stamped_path = generated / stamped_name
        stamped_path.write_text(md, encoding="utf-8")
        if destination:
            dest = Path(destination)
            dest.mkdir(parents=True, exist_ok=True)
            copied = dest / stamped_name
            copied.write_text(md, encoding="utf-8")
    return {
        "mode": mode,
        "latest": str(latest),
        "stamped": str(stamped_path) if stamped_path else None,
        "copied": str(copied) if copied else None,
        "markdown": md,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["prospective", "retrospective"], required=True)
    args = parser.parse_args()
    info = save_markdown(args.mode)
    print(info["latest"])
