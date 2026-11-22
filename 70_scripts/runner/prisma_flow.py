"""PRISMA 2020 flow inputs for the Haddaway PRISMA2020 R package (PNG).

Not GSscraper. Pipeline counts plus the boxes the scripts do not know
(retrieval, full-text reasons, registers, other sources).
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

CSV_COLUMNS = (
    "data",
    "node",
    "box",
    "description",
    "boxtext",
    "tooltips",
    "url",
    "n",
)


def _int(value, default: int | None = None) -> int | None:
    text = str(value or "").strip()
    if text == "":
        return default
    return int(text.replace(" ", "").replace(",", ""))


def _or_table_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.startswith("|")]
    data = [
        ln for ln in lines[2:]
        if not re.match(r"^\|\s*:?-+:?[\s\|:-]*\|$", ln)
    ]
    return len(data) or None


def _parse_reasons(text: str) -> list[dict]:
    rows = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if "," in line:
            reason, n = line.rsplit(",", 1)
            n = n.strip()
            if re.fullmatch(r"\d+", n):
                rows.append({"reason": reason.strip(), "n": int(n)})
                continue
        rows.append({"reason": line, "n": None})
    return rows


def _merge_counts(root: Path) -> dict:
    out = {
        "wos": None,
        "scopus": None,
        "merged": None,
        "duplicate_doi": 0,
        "duplicate_title": 0,
        "books": 0,
        "missing_doi": 0,
        "script_retained": None,
    }
    reports = [
        root / "20_data_clean" / "21_audit" / "processing_report.txt",
        root / "60_prisma" / "processing_report.txt",
    ]
    text = ""
    for report in reports:
        if report.exists():
            text = report.read_text(encoding="utf-8")
            break

    def grab(pattern: str, blob: str = text):
        m = re.search(pattern, blob, re.MULTILINE | re.IGNORECASE)
        return int(m.group(1)) if m else None

    if text:
        # Old report: "WoS: 633". New report: a database heading then "records: 633".
        out["wos"] = grab(r"^(?:WoS|Web of Science)\s*:\s*(\d+)\s*$")
        out["scopus"] = grab(r"^Scopus\s*:\s*(\d+)\s*$")
        if out["wos"] is None:
            m = re.search(
                r"(?im)^\s*(?:WoS|Web of Science)\s*$(?:\n\s+\S.*)*?\n\s+records:\s*(\d+)\s*$",
                text,
            )
            if m:
                out["wos"] = int(m.group(1))
        if out["scopus"] is None:
            m = re.search(
                r"(?im)^\s*Scopus\s*$(?:\n\s+\S.*)*?\n\s+records:\s*(\d+)\s*$",
                text,
            )
            if m:
                out["scopus"] = int(m.group(1))
        out["merged"] = grab(
            r"^(?:Total merged records|Merged)(?:\s*\(.*\))?:\s*(\d+)\s*$"
        )
        out["duplicate_doi"] = grab(r"^duplicate_doi:\s*(\d+)\s*$") or 0
        out["duplicate_title"] = grab(r"^duplicate_title:\s*(\d+)\s*$") or 0
        out["books"] = grab(r"^non_article_type:\s*(\d+)\s*$") or 0
        out["missing_doi"] = (
            grab(r"^missing_doi:\s*(\d+)\s*$")
            or grab(r"^missing among retained:\s*(\d+)\s*$")
            or 0
        )
        out["script_retained"] = grab(r"^correct_record:\s*(\d+)\s*$") or grab(
            r"^Retained:\s*(\d+)\s*$"
        )
    meta_path = root / "10_data_raw" / "12_final" / "ris_meta.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {}
        for rec in meta.get("exports") or []:
            name = str(rec.get("database") or "").strip().lower()
            n = rec.get("n_records")
            if n is None:
                continue
            if name in {"wos", "web of science"} and out["wos"] is None:
                out["wos"] = int(n)
            if name == "scopus" and out["scopus"] is None:
                out["scopus"] = int(n)
    saved = root / "60_prisma" / "prisma_flow_inputs.json"
    if saved.exists() and (out["wos"] is None or out["scopus"] is None):
        try:
            ident = (json.loads(saved.read_text(encoding="utf-8")).get("identification") or {})
        except json.JSONDecodeError:
            ident = {}
        if out["wos"] is None and ident.get("wos") is not None:
            out["wos"] = int(ident["wos"])
        if out["scopus"] is None and ident.get("scopus") is not None:
            out["scopus"] = int(ident["scopus"])
        if out["merged"] is None and ident.get("database_results") is not None:
            out["merged"] = int(ident["database_results"])
    decisions = root / "20_data_clean" / "21_audit" / "record_decisions.json"
    if decisions.exists():
        data = json.loads(decisions.read_text(encoding="utf-8"))
        if data.get("n_forward"):
            out["retained"] = int(data["n_forward"])
    if "retained" not in out:
        out["retained"] = out["script_retained"]
    return out


def assemble(settings: dict, overview: dict, root: Path) -> dict:
    merge = _merge_counts(root)
    n_screen = int(overview.get("n_screen") or 0)
    n_inc = int(overview.get("n_include") or 0)
    n_may = int(overview.get("n_maybe") or 0)
    n_exc = int(overview.get("n_exclude") or 0)
    n_must = int(overview.get("n_must_cite") or 0)
    n_rest = int(overview.get("n_include_rest") or 0)
    n_rev = int(overview.get("n_reviews") or 0)

    sought = _int(settings.get("prisma_sought"), n_must)
    not_retrieved = _int(settings.get("prisma_not_retrieved"), 0) or 0
    assessed = max((sought or 0) - not_retrieved, 0)
    included_studies = _int(settings.get("prisma_included_studies"))
    included_reports = _int(settings.get("prisma_included_reports"))
    if included_studies is None:
        included_studies = _or_table_rows(
            root / "90_review" / "92_appendix" / "or-09-inputs.qmd"
        )
    if included_reports is None:
        included_reports = included_studies
    reasons = _parse_reasons(settings.get("prisma_ft_excluded") or "")
    if not reasons and n_must and included_studies and n_must > included_studies:
        leftover = n_must - included_studies
        if leftover == 3:
            reasons = [
                {"reason": "publisher correction", "n": 1},
                {"reason": "book chapter", "n": 1},
                {"reason": "conference paper without operational SM retrieval", "n": 1},
            ]
        else:
            reasons = [
                {
                    "reason": "not a unique extracted study (correction, chapter, or conference paper)",
                    "n": leftover,
                }
            ]
    reasons_n = sum(r["n"] or 0 for r in reasons)

    register_n = _int(settings.get("prisma_register_n"), 0) or 0
    website_n = _int(settings.get("prisma_website_n"), 0) or 0
    org_n = _int(settings.get("prisma_organisation_n"), 0) or 0
    cite_n = _int(settings.get("prisma_citation_n"), 0) or 0
    other_n = website_n + org_n + cite_n

    duplicates = (merge.get("duplicate_doi") or 0) + (merge.get("duplicate_title") or 0)
    books = merge.get("books") or 0
    wos = merge.get("wos")
    scopus = merge.get("scopus")
    identified = merge.get("merged")
    if wos is not None and scopus is not None:
        identified = (wos or 0) + (scopus or 0)
    retained = int(merge.get("retained") or 0)
    script_kept = int(merge.get("script_retained") or retained or 0)
    lock_extra = max(0, script_kept - retained) if retained else 0
    other_excl = books + lock_extra
    screened = retained or n_screen

    auto_split = sought == n_must and n_must <= n_inc
    not_to_ft = max(screened - (sought or 0), 0)
    split = {
        "exclude": n_exc,
        "maybe": n_may,
        "include_not_sought": n_rest if auto_split else None,
        "auto": auto_split,
        "total": not_to_ft,
    }

    db_detail = []
    if wos is not None:
        db_detail.append(f"WoS, {wos}")
    if scopus is not None:
        db_detail.append(f"Scopus, {scopus}")

    ft_reason_text = "; ".join(
        f"{r['reason']}, {r['n']}" if r["n"] is not None else r["reason"] for r in reasons
    ) or "0"

    warnings = []
    if sought and sought > screened:
        warnings.append("Sought for retrieval is larger than records screened.")
    if included_reports is not None and included_reports > assessed:
        warnings.append("Included reports exceed reports assessed.")
    if reasons_n and included_reports is not None and reasons_n + included_reports != assessed:
        warnings.append(
            f"Full-text exclusions ({reasons_n}) + included reports "
            f"({included_reports}) != assessed ({assessed})."
        )
    if not auto_split:
        warnings.append(
            "Sought is not the must-cite count. Extra full texts came from maybe "
            "or from include leftover, so write that split in the title–abstract notes."
        )
    if included_studies is None or included_reports is None:
        warnings.append("Included studies and/or reports are still empty.")
    missing_reasons = [r["reason"] for r in reasons if r["n"] is None]
    if missing_reasons:
        warnings.append("Full-text reason without a count: " + "; ".join(missing_reasons))

    return {
        "package": "PRISMA2020",
        "cite": "Haddaway NR, Page MJ, Pritchard CC, McGuinness LA (2022) Campbell Systematic Reviews 18:e1230.",
        "not": "GSscraper (Google Scholar scraper) is not used.",
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "previous": False,
        "other": other_n > 0,
        "identification": {
            "wos": wos,
            "scopus": scopus,
            "database_results": identified,
            "database_specific": "; ".join(db_detail),
            "register_results": register_n,
            "registers": (settings.get("prisma_registers") or "").strip(),
            "website_results": website_n,
            "organisation_results": org_n,
            "citations_results": cite_n,
            "duplicates": duplicates,
            "excluded_automatic": 0,
            "excluded_other": other_excl,
            "missing_doi_not_removed": merge.get("missing_doi") or 0,
            "retained": retained or merge.get("retained"),
            "reviews_set_aside": n_rev,
            "lock_extra": lock_extra,
        },
        "screening": {
            "records_screened": screened,
            "records_excluded": not_to_ft,
            "split": split,
            "notes": (settings.get("prisma_screen_excluded_notes") or "").strip(),
        },
        "retrieval": {
            "sought": sought,
            "sought_source": "typed" if str(settings.get("prisma_sought") or "").strip() else "must_cite",
            "not_retrieved": not_retrieved,
            "not_retrieved_notes": (settings.get("prisma_not_retrieved_notes") or "").strip(),
            "assessed": assessed,
        },
        "included": {
            "studies": included_studies,
            "reports": included_reports,
            "ft_excluded": reasons,
            "ft_excluded_n": reasons_n,
            "ft_excluded_box": ft_reason_text,
        },
        "warnings": warnings,
        "typed_fields": {
            "prisma_sought": settings.get("prisma_sought") or "",
            "prisma_not_retrieved": settings.get("prisma_not_retrieved") or "0",
            "prisma_not_retrieved_notes": settings.get("prisma_not_retrieved_notes") or "",
            "prisma_included_studies": settings.get("prisma_included_studies") or "",
            "prisma_included_reports": settings.get("prisma_included_reports") or "",
            "prisma_ft_excluded": settings.get("prisma_ft_excluded") or "",
            "prisma_screen_excluded_notes": settings.get("prisma_screen_excluded_notes") or "",
            "prisma_register_n": settings.get("prisma_register_n") or "0",
            "prisma_registers": settings.get("prisma_registers") or "",
            "prisma_website_n": settings.get("prisma_website_n") or "0",
            "prisma_organisation_n": settings.get("prisma_organisation_n") or "0",
            "prisma_citation_n": settings.get("prisma_citation_n") or "0",
        },
    }


def _csv_rows(payload: dict) -> list[dict]:
    ident = payload["identification"]
    scr = payload["screening"]
    ret = payload["retrieval"]
    inc = payload["included"]
    empty = {c: "" for c in CSV_COLUMNS}

    def row(data, n, *, node="", box="", description="", boxtext=""):
        item = dict(empty)
        item.update(
            {
                "data": data,
                "node": node,
                "box": box,
                "description": description,
                "boxtext": boxtext or description,
                "tooltips": description,
                "url": "",
                "n": n if n is not None else 0,
            }
        )
        return item

    n0 = 0
    return [
        row("database_results", ident.get("database_results") or 0, node="node7", box="box2",
            description="Records identified from: Databases", boxtext="Databases"),
        row("database_specific_results", ident.get("database_specific") or "",
            description="Records identified from: specific databases", boxtext="Specific Databases"),
        row("register_results", ident.get("register_results") or 0,
            description="Records identified from: Registers", boxtext="Registers"),
        row("website_results", ident.get("website_results") or 0, node="node17", box="box11",
            description="Records identified from: Websites", boxtext="Websites"),
        row("organisation_results", ident.get("organisation_results") or 0,
            description="Records identified from: Organisations", boxtext="Organisations"),
        row("citations_results", ident.get("citations_results") or 0,
            description="Records identified from: Citation searching", boxtext="Citation searching"),
        row("duplicates", ident.get("duplicates") or 0, node="node8", box="box3",
            description="Duplicate records", boxtext="Duplicate records"),
        row("excluded_automatic", ident.get("excluded_automatic") or 0,
            description="Records marked as ineligible by automation tools"),
        row("excluded_other", ident.get("excluded_other") or 0,
            description="Records removed for other reasons"),
        row("records_screened", scr.get("records_screened") or 0, node="node9", box="box4",
            description="Records screened", boxtext="Records screened"),
        row("records_excluded", scr.get("records_excluded") or 0, node="node10", box="box5",
            description="Records excluded", boxtext="Records excluded"),
        row("dbr_sought_reports", ret.get("sought") or 0, node="node11", box="box6",
            description="Reports sought for retrieval"),
        row("dbr_notretrieved_reports", ret.get("not_retrieved") or 0, node="node12", box="box7",
            description="Reports not retrieved"),
        row("dbr_assessed", ret.get("assessed") or 0, node="node13", box="box8",
            description="Reports assessed for eligibility"),
        row("dbr_excluded", inc.get("ft_excluded_box") or "0", node="node14", box="box9",
            description="Reports excluded"),
        row("new_studies", inc.get("studies") if inc.get("studies") is not None else n0,
            node="node15", box="box10", description="New studies included in review"),
        row("new_reports", inc.get("reports") if inc.get("reports") is not None else n0,
            description="Reports of new included studies"),
        row("previous_studies", 0, node="node5", box="box1",
            description="Studies included in previous version of review"),
        row("previous_reports", 0, description="Reports of studies included in previous version of review"),
    ]


def _r_script(payload: dict) -> str:
    prev = "TRUE" if payload.get("previous") else "FALSE"
    other = "TRUE" if payload.get("other") else "FALSE"
    return f"""# PRISMA 2020 flow diagram — generated by the review runner.
# Package: PRISMA2020 (Haddaway et al. 2022). Not GSscraper.
# Usage: Rscript PRISMA_flow.R
# Output: PRISMA_diagram.png in this folder.

if (!requireNamespace("PRISMA2020", quietly = TRUE)) {{
  stop("Install the CRAN package PRISMA2020, then run this script again.")
}}
library(PRISMA2020)

data <- PRISMA_data(read.csv("PRISMA2020_data.csv", stringsAsFactors = FALSE))
plot <- PRISMA_flowdiagram(
  data,
  interactive = FALSE,
  previous = {prev},
  other = {other}
)
PRISMA_save(plot, filename = "PRISMA_diagram", filetype = "PNG")
"""


def _how_md(payload: dict) -> str:
    split = payload["screening"]["split"]
    ident = payload["identification"]
    ret = payload["retrieval"]
    inc = payload["included"]
    warns = payload.get("warnings") or []
    warn_block = "\n".join(f"- {w}" for w in warns) or "- none"
    reviews_n = ident.get("reviews_set_aside")
    split_line = (
        f"reviews {reviews_n}; exclude {split['exclude']}; maybe {split['maybe']}; "
        f"include not sought {split['include_not_sought']}"
        if split.get("auto")
        else "typed notes only (sought ≠ must-cite)"
    )
    return f"""Figure 2 was produced with the Haddaway **PRISMA2020** web application (<https://estech.shinyapps.io/prisma_flowdiagram/>; Haddaway et al. 2022, *Campbell Systematic Reviews* 18:e1230). The review runner writes this note and a CSV/R template from the same counts. Do not replace `PRISMA_diagram.png` with `Rscript` unless the boxes match the web export.

Identification and title–abstract counts come from the merge report and from `n_forward` after audit. Review articles are inside Records screened and inside Records excluded. Retrieval and full-text boxes are typed in the runner (Extraction). Blank “sought for retrieval” defaults to the must-cite count. Missing DOI is **not** counted as removed (`missing_doi_not_removed` = {ident.get("missing_doi_not_removed")}). Other exclusions are books plus records outside the original kept list (`lock_extra`).

When sought equals must-cite, records not taken to full text are the screening remainder (exclude + maybe + include leftover). Extra full texts raise sought; those records left maybe or include leftover, and the new split is typed in the title–abstract notes.

| Box | Value |
|---|---|
| Databases | {ident.get("database_specific")} |
| Duplicates | {ident.get("duplicates")} |
| Other removals | {ident.get("excluded_other")} |
| Screened | {payload["screening"].get("records_screened")} |
| Not taken to full text | {payload["screening"].get("records_excluded")} ({split_line}) |
| Sought | {ret.get("sought")} ({ret.get("sought_source")}) |
| Not retrieved | {ret.get("not_retrieved")} |
| Assessed | {ret.get("assessed")} |
| Full-text exclusions | {inc.get("ft_excluded_box")} |
| Included studies / reports | {inc.get("studies")} / {inc.get("reports")} |

Warnings:

{warn_block}

Cite: {payload.get("cite")}
"""


def save(settings: dict, overview: dict, root: Path) -> dict:
    folder = root / "60_prisma"
    folder.mkdir(parents=True, exist_ok=True)
    payload = assemble(settings, overview, root)
    (folder / "prisma_flow_inputs.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    csv_path = folder / "PRISMA2020_data.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(_csv_rows(payload))
    (folder / "PRISMA_flow.R").write_text(_r_script(payload), encoding="utf-8")
    (folder / "PRISMA_flow_how.md").write_text(_how_md(payload), encoding="utf-8")
    return {
        "folder": folder,
        "payload": payload,
        "files": [
            "prisma_flow_inputs.json",
            "PRISMA2020_data.csv",
            "PRISMA_flow.R",
            "PRISMA_flow_how.md",
        ],
    }


def render_png(root: Path) -> dict:
    folder = root / "60_prisma"
    script = folder / "PRISMA_flow.R"
    rscript = shutil.which("Rscript")
    if not rscript:
        return {"ok": False, "log": "Rscript not on PATH. Install R, then PRISMA2020."}
    if not script.exists():
        return {"ok": False, "log": "Save the PRISMA counts first (writes PRISMA_flow.R)."}
    proc = subprocess.run(
        [rscript, str(script.name)],
        cwd=folder,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    png = folder / "PRISMA_diagram.png"
    log = (proc.stdout or "") + (proc.stderr or "")
    ok = proc.returncode == 0 and png.exists()
    return {"ok": ok, "log": log.strip() or ("PNG written" if ok else "R finished without PNG.")}


def overview_from_reports(root: Path) -> dict:
    path = root / "30_screening" / "33_reports" / "screening_summary.txt"
    text = path.read_text(encoding="utf-8") if path.exists() else ""

    def grab(pattern: str) -> int:
        m = re.search(pattern, text, re.MULTILINE)
        return int(m.group(1)) if m else 0

    n_inc = grab(r"^Include: (\d+)")
    n_must = grab(r"^Must-cite: (\d+)")
    return {
        "n_screen": grab(r"^Records \(non-review\): (\d+)"),
        "n_include": n_inc,
        "n_maybe": grab(r"^Maybe: (\d+)"),
        "n_exclude": grab(r"^Exclude: (\d+)"),
        "n_must_cite": n_must,
        "n_include_rest": max(n_inc - n_must, 0),
        "n_reviews": grab(r"^Review articles: (\d+)"),
    }


def protocol_block(root: Path, settings: dict | None = None) -> str:
    if settings is None:
        saved = root / "run_settings.json"
        settings = json.loads(saved.read_text(encoding="utf-8")) if saved.exists() else {}
    try:
        data = assemble(settings, overview_from_reports(root), root)
    except Exception:
        path = root / "60_prisma" / "prisma_flow_inputs.json"
        if not path.exists():
            return (
                "PRISMA flow extras (retrieval, full-text exclusions) have not been written yet. "
                "They are written when the runner starts, and again from Extraction."
            )
        data = json.loads(path.read_text(encoding="utf-8"))
    ret = data.get("retrieval") or {}
    inc = data.get("included") or {}
    scr = data.get("screening") or {}
    return (
        "PRISMA 2020 flow counts (`60_prisma/prisma_flow_inputs.json`). "
        "Figure 2 PNG is from the PRISMA2020 web app, not from Rscript:\n\n"
        f"- records screened: {scr.get('records_screened')}; not taken to full text: {scr.get('records_excluded')}\n"
        f"- reports sought: {ret.get('sought')}; not retrieved: {ret.get('not_retrieved')}; assessed: {ret.get('assessed')}\n"
        f"- included studies / reports: {inc.get('studies')} / {inc.get('reports')}\n"
        f"- full-text exclusions: {inc.get('ft_excluded_box')}\n"
    )
