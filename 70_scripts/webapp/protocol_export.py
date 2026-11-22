"""Build a PRISMA-P markdown protocol from current runner settings or from executed outputs.

Two modes
---------
prospective  — written *before* searches / screening. Plan according to which the
               pipeline will run. Deposit this (Zenodo protocol DOI) if starting a
               new review.
retrospective — written *after* a run. Reconstructs what the scripts actually did
               from reports, exclusion_log.json, screening_config_used.json, RIS dates.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from project_paths import PROJECT_ROOT

GENERATED = PROJECT_ROOT / "60_prisma" / "protocol" / "generated"
LINKS_PATH = Path(__file__).with_name("links.json")
SCREEN_CFG = PROJECT_ROOT / "70_scripts" / "pipeline" / "screening_config.json"
SCREEN_USED = PROJECT_ROOT / "30_screening" / "33_reports" / "screening_config_used.json"
QUERY_PARAMS = PROJECT_ROOT / "00_search" / "02_final" / "final_query_params.json"
QUERY_TXT = PROJECT_ROOT / "00_search" / "02_final" / "final_query.txt"
RIS_META = PROJECT_ROOT / "10_data_raw" / "12_final" / "ris_meta.json"
MERGE_REPORT = PROJECT_ROOT / "20_data_clean" / "21_audit" / "processing_report.txt"
EXCLUSION_LOG = PROJECT_ROOT / "20_data_clean" / "21_audit" / "exclusion_log.json"
MANUAL_LOG = PROJECT_ROOT / "20_data_clean" / "21_audit" / "manual_exclusions.json"
SCREEN_SUMMARY = PROJECT_ROOT / "30_screening" / "33_reports" / "screening_summary.txt"
RUN_LOG = Path(__file__).with_name("run_log.jsonl")


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


def _search_block() -> str:
    params = _json(QUERY_PARAMS)
    txt = _read(QUERY_TXT).strip()
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
        q = params.get("queries") or {}
        if q.get("web_of_science"):
            lines += ["", "**Web of Science**", "", "```", q["web_of_science"], "```"]
        if q.get("scopus"):
            lines += ["", "**Scopus**", "", "```", q["scopus"], "```"]
        return "\n".join(lines)
    if txt:
        return "Frozen query (`00_search/02_final/final_query.txt`):\n\n```\n" + txt + "\n```"
    return "_Search strings have not been frozen yet._"


def _screening_cfg() -> dict:
    return _json(SCREEN_USED) or _json(SCREEN_CFG) or {}


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
        "Must-cite **extended**: "
        f"score ≥ {ext.get('score_min', 6)}; "
        "direct UAV + scaling"
        + (" **or** potential UAV + (scaling or passive optical)" if ext.get("branch_potential_and_scaling_or_passive", True) else "")
        + ".",
        "",
        "Potential UAV (does **not** add score points): satellite platform "
        "(or MODIS / Landsat / Sentinel) **and** (high/fine resolution **or** scaling **or** "
        f"passive terms: `{', '.join(terms.get('passive') or [])}`).",
    ]
    return "\n".join(lines)


def _ris_block() -> str:
    meta = _json(RIS_META) or {}
    if not meta:
        return (
            "RIS exports live in `10_data_raw/11_original/` (archive) and "
            "`10_data_raw/12_final/export_WoS.ris` / `export_Scopus.ris` (script input). "
            "Download dates have not been stored yet."
        )
    lines = ["Download dates (as recorded in `ris_meta.json`):", ""]
    for key in ("wos", "scopus"):
        rec = meta.get(key) or {}
        if not rec:
            continue
        lines.append(
            f"- **{key.upper()}**: {rec.get('downloaded_at') or 'date not set'}; "
            f"file `{rec.get('file') or ''}`; records {rec.get('n_records', '?')}; "
            f"original `{rec.get('original') or ''}`"
        )
    return "\n".join(lines) if len(lines) > 2 else "_No RIS metadata yet._"


def _exclusion_block(retrospective: bool) -> str:
    if not retrospective:
        return (
            "At bibliographic audit, records will be **removed** only for: "
            "missing title or year; books / e-books (`TY` BOOK, EBOOK); "
            "duplicate DOI (keep first); duplicate title + year. "
            "**Records without a DOI are retained**, flagged `doi_missing`, "
            "and still go through title–year duplicate checks. "
            "Journal-versus-conference conflicts are resolved manually and logged "
            "in `20_data_clean/21_audit/manual_exclusions.json` (n + reason)."
        )
    auto = _json(EXCLUSION_LOG) or {}
    manual = _json(MANUAL_LOG) or {}
    lines = []
    if auto:
        lines.append(
            f"Script audit: retained {auto.get('retained')}, removed {auto.get('removed')}."
        )
        lines.append("")
        for e in auto.get("entries") or []:
            kept = "retained" if e.get("kept") else "removed"
            lines.append(f"- {kept}: n = {e.get('n')} — {e.get('status')}: {e.get('reason')}")
    report = _read(MERGE_REPORT).strip()
    if report:
        lines += ["", "<details><summary>processing_report.txt</summary>", "", "```", report, "```", "", "</details>"]
    entries = (manual.get("entries") if isinstance(manual, dict) else manual) or []
    if entries:
        lines += ["", "Manual exclusions / notes:"]
        for e in entries:
            kept = "retained" if e.get("kept") else "removed"
            lines.append(
                f"- {kept}: n = {e.get('n')} — {e.get('reason')}"
                + (f". {e.get('note')}" if e.get("note") else "")
            )
    screen = _read(SCREEN_SUMMARY).strip()
    if screen:
        lines += ["", "<details><summary>screening_summary.txt</summary>", "", "```", screen, "```", "", "</details>"]
    return "\n".join(lines) if lines else "_No run yet. Generate the retrospective protocol after merge and screening._"


def _run_log_block() -> str:
    if not RUN_LOG.exists():
        return "_No runner log yet._"
    rows = []
    for line in RUN_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not rows:
        return "_No runner log yet._"
    lines = ["| Time | Step | Result | Seconds |", "|---|---|---|---|"]
    for r in rows[-40:]:
        ok = "ok" if r.get("ok") else "error"
        lines.append(
            f"| {r.get('ts', '')} | {r.get('step', '')} | {ok} | {r.get('seconds', '')} |"
        )
    return "\n".join(lines)


def build_markdown(mode: str, extra: dict | None = None) -> str:
    extra = extra or {}
    retrospective = mode == "retrospective"
    stamp = datetime.now().isoformat(timespec="seconds")
    links = _links()
    zenodo = links.get("zenodo") or {}
    title_kind = "Retrospective (executed)" if retrospective else "Prospective (planned)"
    status = (
        "This document was generated **after** pipeline steps from the Review runner. "
        "It records methods **as executed**. It is not an a priori PROSPERO protocol."
        if retrospective
        else "This document was generated **before** running (or re-running) the pipeline. "
        "Use it as the protocol *according to which* search, cleaning, and screening will proceed. "
        "Deposit it (Zenodo protocol DOI) before database searches if this is a new review. "
        "PROSPERO does not accept protocols for reviews whose searches have already been completed."
    )
    cfg = _screening_cfg()
    authors = extra.get("authors") or (
        "Lenka Miková (corresponding); Elena Scholz; Jiří Rous; Jan Komárek."
    )
    body = f"""# {title_kind} PRISMA-P protocol — soil moisture monitoring using unmanned aircraft systems

**Generated.** {stamp}  
**Source.** Review runner (`70_scripts/webapp/`) reading the live project on disk.  
**Canonical code.** {links.get('github_project') or 'https://github.com/LenkaMikova/UAS-review'}  
**Reusable scripts.** {links.get('github_tools') or 'https://github.com/LenkaMikova/PRISMAtools'}  
**Zenodo.** protocol {zenodo.get('protocol') or '—'}; dataset {zenodo.get('dataset') or '—'}; software {zenodo.get('software') or '—'}.

**Status.** {status}

Companion reporting checklist: PRISMA 2020 (`60_prisma/PRISMA_2020_checklist_filled.md`; Online Resource 4).

---

## Administrative information (PRISMA-P items 1–5)

### 1. Title

Systematic review of soil moisture monitoring using unmanned aircraft systems ({'retrospective' if retrospective else 'planned'} protocol).

### 2. Registration

None in PROSPERO. Protocol DOI (Zenodo): {zenodo.get('protocol') or '_add after upload_'}.

### 3. Authors

{authors}

Contact: mikoval@fzp.czu.cz

### 4. Amendments

Dated in this generated file and in Git / Zenodo version history. The Review runner writes a new file per export; it does not silently overwrite `PRISMA-P_retrospective_protocol.md` (the manuscript-facing copy).

### 5. Support

IGA grant 2026B0015, Faculty of Environmental Sciences, Czech University of Life Sciences Prague. Competing interests: none declared.

---

## Introduction (items 6–7)

### 6. Rationale

Soil moisture is a biophysical control on crop water use. Satellite and in-situ methods leave a scale gap at field level. Unmanned aircraft systems are used for high-resolution soil-moisture-related observations, alone or fused with satellite and ground data. This review maps methods (2019–2026) and audits how completely UAV campaigns report information needed to reproduce a flight.

### 7. Objectives

Identify and synthesise primary research on soil-moisture estimation or monitoring with remote sensing in agricultural settings, with emphasis on UAV-applicable workflows.

---

## Methods (items 8–17)

### 8. Eligibility criteria

**Inclusion**

- Topic: soil moisture estimation, monitoring, or mapping.
- Method: remote sensing (satellite, UAV/UAS/drone, or fusion with in-situ data).
- Setting: agricultural or closely related (cropland, arable land, farmland, bare soil, irrigation / water management).
- Years and language: as in the search strategy below.
- Document type: primary research (journal article, conference paper, or book chapter kept at audit).

**Bibliographic audit (`merge_and_classify.py`)**

{_exclusion_block(retrospective)}

**Screening exclusions**

- Records flagged as reviews (review / systematic review / meta-analysis in title–abstract–keywords or `M3`) are set aside, not synthesised as primary studies.
- Automated exclude: relevance score below the maybe threshold.

**Not used**

- Independent dual screening.
- A second full-text eligibility round that would drop the bulk of automated includes. Must-cite is a **priority subset**, not the remainder after full-text exclusion.

### 9. Information sources

Web of Science Core Collection (Clarivate) and Scopus (Elsevier). No trial registers, grey literature, or citation chasing unless added later and logged.

{_ris_block()}

### 10. Search strategy

{_search_block()}

### 11. Study records

**Data management.** Folder numbering `00_search` → `90_review`. Original RIS stay in `11_original/`; scripts read only `12_final/export_WoS.ris` and `export_Scopus.ris`. Merge writes `20_data_clean/` plus `21_audit/`. Screening writes `30_screening/`. Extraction templates: `40_extraction/41_input/`.

**Selection process**

{_screening_block(cfg)}

One-person verification of scores (the person who set the rules). Not dual screening.

### 12. Data items

Extraction templates from `extraction_templ.py`: bibliographic fields, platform, sensor, scaling, UAV flag, plus empty manual columns (study area, method, validation, Include_final, notes). Priority HIGH if `must_cite` is already true.

### 13. Outcomes and prioritization

Primary synthesis set is defined in the manuscript after extraction. Automated include / maybe / exclude and must-cite tiers are priority filters, not the final included set.

### 14. Risk of bias

No formal RoB tool at the automated stage. Reporting completeness uses the 25-item paper checklist (Online Resource 5) plus an optional soil-moisture module.

### 15. Data synthesis

Qualitative / structured mapping. No meta-analysis planned in the automated pipeline.

### 16–17. Meta-bias and confidence

Not applicable to the automated pipeline; address in the manuscript if a quantitative synthesis is added.

---

## Runner log

{_run_log_block()}

---

## How to cite this file

Cite the Zenodo protocol DOI when minted. Keep GitHub `UAS-review` as the live source; Zenodo is a versioned snapshot of a GitHub release. Generic script copies live in PRISMAtools — sync them after structural changes here, do not treat that repo as a second source of truth for *this* review.
"""
    return body.strip() + "\n"


def save_markdown(mode: str, extra: dict | None = None, destination: Path | None = None) -> dict:
    GENERATED.mkdir(parents=True, exist_ok=True)
    md = build_markdown(mode, extra)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    latest_name = f"PRISMA-P_{'executed' if mode == 'retrospective' else 'planned'}.md"
    stamped_name = f"PRISMA-P_{'executed' if mode == 'retrospective' else 'planned'}_{stamp}.md"
    latest = GENERATED / latest_name
    stamped = GENERATED / stamped_name
    latest.write_text(md, encoding="utf-8")
    stamped.write_text(md, encoding="utf-8")
    copied = None
    if destination:
        dest = Path(destination)
        dest.mkdir(parents=True, exist_ok=True)
        copied = dest / stamped_name
        copied.write_text(md, encoding="utf-8")
    return {
        "mode": mode,
        "latest": str(latest),
        "stamped": str(stamped),
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
