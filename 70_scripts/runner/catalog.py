"""Step catalogue. Short titles for the UI; longer notes only for the Help section."""

from __future__ import annotations

STEPS = [
    {
        "id": "output",
        "title": "1  Setup",
        "headline": "Folder, review, protocol, databases, other sources, DOI",
        "what": (
            "Pick an empty folder. Every later step writes into it and creates its own subfolders "
            "(00_search, 10_data_raw, 20_data_clean, 30_screening, 40_extraction, 60_prisma). "
            "The form below is copied into the PRISMA-P protocol. "
            "Choose whether to write the protocol before searching (plan) or after the run (retrospective); Continue follows that path. "
            "DOIs are for the protocol, dataset and code you will publish for this run."
        ),
        "inputs": "Output folder plus protocol details (title, authors, databases, optional DOIs).",
        "outputs": "Chosen folder + run_settings.json; subfolders appear when you run each step.",
        "script": None,
        "folders": [],
    },
    {
        "id": "protocol_plan",
        "title": "2  Protocol (plan)",
        "headline": "PRISMA-P before the run",
        "what": "Writes a planned protocol from the current search terms and screening rules. Generate this before changing settings if you need a record of intent.",
        "inputs": "Frozen query (if any) and screening_config.json.",
        "outputs": "60_prisma/protocol/generated/PRISMA-P_planned.md",
        "script": "runner/protocol_export.py --mode prospective",
        "folders": ["60_prisma/protocol/generated"],
    },
    {
        "id": "search",
        "title": "3  Search",
        "headline": "Keyword groups and databases",
        "what": "AND between rows, OR inside a row. Format: term1, term2 | field (all, topic, title, abstract). Tick the databases you will search. Save query writes both the draft (01_raw) and the frozen string (02_final) in one step. Then export RIS and continue to step 4.",
        "inputs": "Keyword groups, years, language.",
        "outputs": "00_search/01_raw/ and, if frozen, 00_search/02_final/",
        "script": "pipeline/WoS_Scopus_query.py",
        "folders": ["00_search/01_raw", "00_search/02_final"],
    },
    {
        "id": "raw",
        "title": "4  RIS + merge",
        "headline": "Attach exports and merge them",
        "what": "Usually two or three databases. For each: name, download date, RIS file. Then merge — that combines the files, drops duplicates and books, and keeps records without a DOI. One original per database is kept in 11_original/ as `{YYYY-MM-DD} export_{database}.ris`. Scripts read 12_final/export_*.ris. An existing merge table is not replaced. Manual check of that table is on the next step (Audit).",
        "inputs": "One RIS export per database (database + date + file).",
        "outputs": "10_data_raw/ plus 20_data_clean/ after Merge.",
        "script": "pipeline/merge_and_classify.py",
        "folders": ["10_data_raw/11_original", "10_data_raw/12_final", "20_data_clean", "20_data_clean/21_audit", "20_data_clean/21_audit/checked"],
    },
    {
        "id": "clean",
        "title": "5  Audit",
        "headline": "What the merge did",
        "what": "Each row is one disjoint class from the merge (duplicates, books, kept). n is the script count. Open duplicates to compare the pair and mark which record stays. Then choose which records go to screening. Every choice is stored in record_decisions.json; the merge file is not replaced. Screening reads forward_records.xlsx when that file exists. Extra is only for removals that have no row in the lists. Save stores the class table and a copy of the technical log.",
        "inputs": "processing_report.txt and exclusion_log.json from Merge in step 4.",
        "outputs": "record_decisions.json, forward_records.xlsx, classification_review.json, audit_saved.txt (merge files unchanged).",
        "script": None,
        "see_script": "pipeline/merge_and_classify.py",
        "folders": ["20_data_clean/21_audit", "20_data_clean/21_audit/checked"],
    },
    {
        "id": "screen",
        "title": "6  Screening",
        "headline": "Terms, weights, thresholds, exports",
        "what": "Tick the keyword groups used in title, abstract and keywords, then set the scores. Reviews are set aside. Must-cite strict = core; extended = wider priority. UAV potential does not add points. Outputs are grouped (main table, reports, RIS, VOSviewer, reviews). Names come from screening_and_deep_classify.py and go into 30_screening/. Ticked files are written only if that name is not already there. After you have checked the table, Upload after manual check (a new file in checked/).",
        "inputs": "clean_records.xlsx (or the file after manual check from Audit, if present) and screening weights/terms.",
        "outputs": "30_screening/ (dataset, reports, optional RIS). Script files stay. File after manual check: 31_dataset/checked/.",
        "script": "pipeline/screening_and_deep_classify.py",
        "folders": [
            "30_screening/31_dataset",
            "30_screening/32_exports",
            "30_screening/33_reports",
            "30_screening/34_reviews",
            "30_screening/35_VOS-ris",
            "30_screening/31_dataset/checked",
        ],
    },
    {
        "id": "extract",
        "title": "7  Extraction",
        "headline": "Excel templates",
        "what": "Three tabs: Groups, PRISMA, Templates. Groups are Reviews / Include / Maybe / Exclude / Unclassified. Include = Must-cite (Core + Extended) + rest. Open a group for every field; untick a row that the automatic step got wrong and move it (logged to the protocol). Maybe is the middle score band, not Exclude. PRISMA shows numbers already loaded; type only empty boxes. Then run templates. HIGH = must_cite (Core ∪ Extended).",
        "inputs": "30_screening/31_dataset/screened_records.xlsx plus recodes and the full-text counts you type.",
        "outputs": "40_extraction/41_input/ (templates); 40_extraction/43_recode/extract_recodes.json + .txt; after_manual_check copies of screened/reviews. PRISMA_flow_how.md on start / Save PRISMA counts.",
        "script": "pipeline/extraction_templ.py",
        "folders": ["40_extraction/41_input", "40_extraction/42_reviews", "40_extraction/42_working", "40_extraction/41_input/batches", "40_extraction/43_recode", "30_screening/31_dataset/checked", "30_screening/34_reviews/checked", "60_prisma"],
    },
    {
        "id": "protocol_run",
        "title": "8  Protocol (run)",
        "headline": "PRISMA-P after the run",
        "what": "Main product of this app: a protocol of what was actually executed. From the first RIS upload the live file PRISMA-P_executed.md is rewritten (data_work.md lists each action and the exact records). Generate here writes a dated stamp from live reports (DOI retained; must-cite / unique studies / Figure 2 boxes). It does not overwrite the Zenodo/manuscript narrative `60_prisma/protocol/PRISMA-P_retrospective_protocol.md` — keep that file aligned with this export.",
        "inputs": "Outputs of steps 4–7, data_work.jsonl, and the run journal.",
        "outputs": "60_prisma/protocol/generated/PRISMA-P_executed.md plus data_work.md",
        "script": "runner/protocol_export.py --mode retrospective",
        "folders": ["60_prisma/protocol/generated"],
    },
]

DATABASE_CHOICES = [
    "WoS",
    "Scopus",
    "PubMed / MEDLINE",
    "Embase",
    "Dimensions",
    "IEEE Xplore",
    "CAB Abstracts",
    "AGRICOLA",
    "GeoRef",
    "Google Scholar",
]

REGISTRATION_CHOICES = ["None", "Zenodo", "PROSPERO", "OSF Registries", "INPLASY", "Other"]

SETUP_TABS = (
    ("folder", "Folder"),
    ("review", "Review"),
    ("protocol", "Protocol"),
    ("databases", "Databases"),
    ("sources", "Other sources"),
    ("doi", "DOI"),
    ("prisma", "PRISMA-P"),
    ("other", "Funding"),
)

SCREEN_TABS = (
    ("keywords", "Keywords"),
    ("download", "Download"),
)

AUDIT_TABS = (
    ("doi", "Duplicate DOI"),
    ("title", "Duplicate title"),
    ("both", "Keep both"),
    ("book", "Book"),
    ("nodoi", "No DOI"),
    ("kept", "Kept for screening"),
)

EXTRACT_TABS = (
    ("groups", "Groups"),
    ("prisma", "PRISMA"),
    ("templates", "Templates"),
)

EXTRACT_GROUP_LABELS = {
    "reviews": "Reviews",
    "include": "Include",
    "maybe": "Maybe",
    "exclude": "Exclude",
    "must_cite": "Must-cite",
    "core": "Core",
    "extended": "Extended",
    "include_rest": "Rest of Include",
    "unclassified": "Unclassified",
}

# Groups on Extraction (chip tabs). Unclassified is the holding tank after Not this group.

# Long WoS names collapse to the short label used in the UI.
DATABASE_ALIASES = {
    "wos": "WoS",
    "wos cc": "WoS",
    "web of science": "WoS",
    "web of science core collection": "WoS",
    "isi web of science": "WoS",
    "clarivate": "WoS",
}

CHECK_CHOICES = [
    "Automatic",
    "I checked the list",
    "Sample checked",
    "Not yet",
]

CHECK_ALIASES = {
    "Automatic (script)": "Automatic",
    "Automatic, then I checked": "Sample checked",
    "Manual (I checked the records)": "I checked the list",
    "Not checked": "Not yet",
}

CLASS_LABELS = {
    "correct_record": "Kept for screening",
    "duplicate_doi": "Duplicate DOI",
    "duplicate_title": "Duplicate title and year",
    "non_article_type": "Book",
    "incomplete_record": "Missing title or year",
    "doi_missing": "No DOI",
}

EXTRA_REASONS = [
    "Journal article kept over conference paper or book chapter (same work)",
    "Disputed DOI: more complete metadata kept",
    "Duplicate among records without DOI",
    "Conference abstract of a journal paper already kept",
    "Duplicate already counted in another database",
    "Not a primary research article",
    "Retracted",
    "Wrong record (parsing error)",
    "Other",
]

# RIS TY → short English label (same wording in Audit, report, protocol).
TY_LABELS = {
    "JOUR": "journal article",
    "CONF": "conference paper",
    "CPAPER": "conference paper",
    "INPR": "conference paper",
    "CHAP": "book chapter",
    "BOOK_CHAPTER": "book chapter",
    "BOOK": "book",
    "EBOOK": "e-book",
    "CONFERENCE_REVIEW": "conference review",
    "THES": "thesis",
    "RPRT": "report",
    "GEN": "other",
}


def publication_type_label(code) -> str:
    c = str(code or "").strip().upper()
    if not c or c in {"NAN", "NONE", "NA", "(BLANK)"}:
        return "unknown type"
    return TY_LABELS.get(c, c.replace("_", " ").lower())


def publication_type_counts(values) -> list[dict]:
    from collections import Counter

    c: Counter[str] = Counter()
    if values is None:
        return []
    for v in values:
        c[publication_type_label(v)] += 1
    return [{"label": k, "n": int(n)} for k, n in c.most_common()]


def format_type_counts(rows) -> str:
    return ", ".join(f"{r.get('n')} {r.get('label')}" for r in (rows or []) if r.get("n"))


def normalize_check(value: str) -> str:
    v = (value or "").strip()
    if v in CHECK_CHOICES:
        return v
    return CHECK_ALIASES.get(v, CHECK_CHOICES[0])


RESULT_CHOICES = ["removed", "kept"]

FORMAT_CHOICES = ("xlsx", "csv", "json", "ris")

TERM_GROUPS = (
    ("soil_moisture", "Soil moisture (SM score)"),
    ("obs_method", "Remote sensing"),
    ("uav", "UAV / drone (UAV score)"),
    ("satellite", "Satellite"),
    ("sensors", "Named sensors"),
    ("active", "Active (SAR / microwave)"),
    ("passive", "Passive optical"),
    ("domain", "Domain (domain score)"),
    ("methods", "Methods"),
    ("scaling", "Scaling (scaling score)"),
    ("high_res", "High / fine resolution"),
    ("review", "Review (set aside, no score)"),
)

PREVIEW_COLUMNS = (
    ("TY", "Type", 120),
    ("TI", "Title", 360),
    ("PY", "Year", 55),
    ("DO", "DOI", 150),
    ("Source", "Database", 90),
    ("AU", "Authors", 180),
)

# What screening_and_deep_classify.py can write. Stem is fixed; formats are chosen per item.
SCREEN_OUTPUT_GROUPS = (
    {
        "title": "Main table — needed for the next step",
        "folder": "30_screening/31_dataset/",
        "why": "The scored list of papers. Extraction (step 7) reads this. Name is fixed; pick the format.",
        "items": (
            {
                "key": "screened_xlsx",
                "stem": "screened_records",
                "why": "Every non-review record with score and include / maybe / exclude. xlsx is required — Extraction reads this file.",
                "formats": ("xlsx", "csv", "json"),
                "default": ("xlsx",),
                "required": ("xlsx",),
            },
        ),
    },
    {
        "title": "Reports — counts for the protocol",
        "folder": "30_screening/33_reports/",
        "why": "Numbers the executed protocol copies. Not the papers themselves.",
        "items": (
            {
                "key": "summary",
                "stem": "screening_summary",
                "why": "Counts (include, maybe, exclude, must-cite).",
                "formats": ("txt", "xlsx"),
                "default": ("txt",),
            },
            {
                "key": "keyword_txt",
                "stem": "keyword_statistics",
                "why": "How often the ticked screening words appeared.",
                "formats": ("txt",),
                "default": ("txt",),
            },
        ),
    },
    {
        "title": "RIS for a reference manager (Zotero, …)",
        "folder": "30_screening/32_exports/",
        "why": "Subsets of the scored records. These are not the original WoS/Scopus downloads from step 4.",
        "items": (
            {
                "key": "ris_all",
                "stem": "all_records",
                "why": "All non-review records (the screening set).",
                "formats": ("ris",),
                "default": (),
            },
            {
                "key": "ris_include",
                "stem": "include_records",
                "why": "Decision = include (score at or above the include threshold).",
                "formats": ("ris",),
                "default": (),
            },
            {
                "key": "ris_core",
                "stem": "core_studies",
                "why": "Must-cite strict (highest priority / core).",
                "formats": ("ris",),
                "default": (),
            },
            {
                "key": "ris_must_cite",
                "stem": "must_cite_records",
                "why": "All must-cite (strict + the wider branch).",
                "formats": ("ris",),
                "default": (),
            },
            {
                "key": "ris_extended_not_strict",
                "stem": "extended_studies",
                "why": "Must-cite but not strict. Off by default so it is not mixed with the core file.",
                "formats": ("ris",),
                "default": (),
            },
        ),
    },
    {
        "title": "VOSviewer maps",
        "folder": "30_screening/35_VOS-ris/",
        "why": "Two files meant to be opened in VOSviewer, not in Zotero.",
        "items": (
            {
                "key": "vos_pair",
                "stem": "VOS_full + VOS_must-cite",
                "why": "Full screened set and the must-cite subset.",
                "formats": ("ris",),
                "default": (),
            },
        ),
    },
    {
        "title": "Reviews set aside",
        "folder": "30_screening/34_reviews/",
        "why": "Records flagged as reviews are not scored with the others.",
        "items": (
            {
                "key": "reviews_xlsx_ris",
                "stem": "review_articles",
                "why": "All review articles found by the review terms. xlsx is required — Extraction reads this file.",
                "formats": ("xlsx", "ris"),
                "default": ("xlsx",),
                "required": ("xlsx",),
            },
            {
                "key": "reviews_uav_ris",
                "stem": "review_articles_uav",
                "why": "Only reviews that also mention UAV or UAV-potential.",
                "formats": ("ris",),
                "default": (),
            },
        ),
    },
)

SCREEN_FILE_KEYS = tuple(item["key"] for group in SCREEN_OUTPUT_GROUPS for item in group["items"])


def step_script(spec: dict) -> str:
    raw = spec.get("script") or spec.get("see_script") or ""
    return str(raw).split()[0] if raw else ""

FOLDER_PLAN = (
    "00_search/          search strings (step 3)\n"
    "10_data_raw/        RIS exports (step 4)\n"
    "20_data_clean/      merged records + audit (step 5)\n"
    "30_screening/       scores and RIS subsets (step 6)\n"
    "40_extraction/      Excel templates (step 7)\n"
    "60_prisma/          protocol + PRISMA flow PNG (steps 2, 7–8)"
)

DEFAULT_SETTINGS = {
    "title": "Systematic review of soil moisture monitoring using unmanned aircraft systems",
    "authors": "Lenka Miková (corresponding)\nElena Scholz\nJiří Rous\nJan Komárek",
    "contact": "mikoval@fzp.czu.cz",
    "support": "IGA grant 2026B0015, Faculty of Environmental Sciences, Czech University of Life Sciences Prague.",
    "registration_type": "Zenodo",
    "registration_id": "",
    "registration": "Zenodo",
    "protocol_mode": "plan",
    "databases": ["WoS", "Scopus"],
    "databases_other": "",
    "github": "",
    "doi_protocol": "",
    "doi_dataset": "",
    "doi_software": "",
    "rationale": (
        "Soil moisture (SM) is a biophysical control on crop water use and irrigation. "
        "Satellite and in-situ methods leave a scale gap at field level. "
        "Unmanned aircraft systems (UAS/UAV) are increasingly used for high-resolution SM-related observations, "
        "alone or fused with satellite and ground data. Existing reviews cover UAVs in agriculture or SM from satellites; "
        "they do not evaluate UAV acquisition, processing, and reporting specifically for SM. "
        "This review maps methods used in 2019–2026 and audits how completely UAV campaigns report the information needed to reproduce a flight."
    ),
    "objectives": (
        "Primary objective: to systematically identify and synthesise primary research (2019–2026) "
        "on SM estimation or monitoring with remote sensing in agricultural settings, with emphasis on UAV-applicable workflows.\n\n"
        "Specific questions:\n"
        "- Which platforms and sensors were used, alone or in combination?\n"
        "- How were UAV campaigns flown and processed, and what was reported?\n"
        "- Which inputs, applications, and retrieval methods appear in the priority subset?\n"
        "- Which reporting items are consistently missing (paper checklist, 25 items + SM module)?"
    ),
    "inclusion": (
        "Topic, methods and setting as defined by the search groups. "
        "Primary research (journal article, conference paper, or book chapter kept at audit). "
        "Years and language as set in Search."
    ),
    "prisma_register_n": "0",
    "prisma_registers": "",
    "prisma_website_n": "0",
    "prisma_organisation_n": "0",
    "prisma_citation_n": "0",
    "prisma_sought": "",
    "prisma_not_retrieved": "0",
    "prisma_not_retrieved_notes": "",
    "prisma_included_studies": "",
    "prisma_included_reports": "",
    "prisma_ft_excluded": "",
    "prisma_screen_excluded_notes": "",
}

DEFAULT_SEARCH = {
    "groups": [
        {"terms": ["soil moisture"], "field": "all"},
        {"terms": ["remote sensing", "UAV", "UAS", "drone*", "satellite*"], "field": "all"},
        {"terms": ["agriculture", "cropland", "arable land", "farmland", "bare soil"], "field": "all"},
        {
            "terms": [
                "precision agriculture",
                "site-specific",
                "irrigation",
                "water management",
                "downscaling",
                "multi-scale",
                "data fusion",
            ],
            "field": "all",
        },
    ],
    "exclude": [],
    "year_from": 2019,
    "year_to": 2026,
    "language": "English",
}

OUTPUT_LABELS = {
    "screened_xlsx": "screened_records.xlsx",
    "summary_txt": "screening_summary.txt",
    "summary_xlsx": "screening_summary.xlsx",
    "keyword_txt": "keyword_statistics.txt",
    "ris_all": "all_records.ris",
    "ris_include": "include_records.ris",
    "ris_core": "core_studies.ris",
    "ris_must_cite": "must_cite_records.ris",
    "ris_extended_not_strict": "extended_studies.ris",
    "vos_pair": "VOS pair",
    "reviews_xlsx_ris": "review_articles",
    "reviews_uav_ris": "review_articles_uav.ris",
    "csv": "CSV",
    "json": "JSON",
}

REPRODUCE = (
    "Work through the numbered steps in order. A later step unlocks only after the previous one is done. "
    "Use the same keyword groups, RIS files, and screening weights to obtain the same tables. "
    "A script output is kept. Where you check by hand, Upload after manual check (a new file marked "
    "after_manual_check). Do not replace the script file. "
    "The protocol in step 8 is the PRISMA record of the run."
)

AFTER_MANUAL_CHECK = "after_manual_check"

# Automated files that a re-run must not replace unless the box is ticked.
SCRIPT_OUTPUTS = {
    "raw": (
        ("20_data_clean", "clean_records.xlsx"),
        ("20_data_clean", "21_audit", "processing_report.txt"),
    ),
    "screen": (("30_screening", "31_dataset", "screened_records.xlsx"),),
    "extract": (
        ("40_extraction", "41_input", "extraction_input_refined.xlsx"),
        ("40_extraction", "41_input", "extraction_input_full.xlsx"),
    ),
}

# Only steps with a manual check: upload a corrected file, leave the script output.
MANUAL_CHECK_UPLOADS = {
    "screen": {
        "title": "Upload file after manual check (screening)",
        "folder": ("30_screening", "31_dataset", "checked"),
        "types": [("Excel", "*.xlsx")],
    },
    "extract": {
        "title": "Upload file after manual check (extraction)",
        "folder": ("40_extraction", "42_working"),
        "types": [("Excel", "*.xlsx")],
    },
}

STEP_NEED = {
    "output": "Choose a folder and save the review details.",
    "protocol_plan": "Generate the planned protocol.",
    "search": "Save the query (draft + freeze).",
    "raw": "Merge the RIS files.",
    "clean": "Save the audit after you have checked Keep both (if any pairs remain).",
    "screen": "Run screening. After you have checked the table, upload it (the script file stays).",
    "extract": "Check Groups (open a list to recode). On PRISMA, type only the empty boxes. Then run Templates.",
    "protocol_run": "Generate a dated executed protocol. The live copy is already written from the RIS upload onward.",
}
