
import pandas as pd
import os
import json
import argparse


SAVE_UAV_REVIEWS = True


import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from project_paths import PROJECT_ROOT, prefer_after_manual_check, write_excel, write_excel_sheets

CFG_PATH = Path(__file__).with_name("screening_config.json")
_CFG = {}

project_root = str(PROJECT_ROOT)

input_file = str(
    prefer_after_manual_check(Path(project_root) / "20_data_clean" / "clean_records.xlsx")
)

output_dir = os.path.join(project_root, "30_screening")

dataset_dir = os.path.join(output_dir, "31_dataset")
exports_dir = os.path.join(output_dir, "32_exports")
reports_dir = os.path.join(output_dir, "33_reports")
review_dir = os.path.join(output_dir, "34_reviews")
vos_dir = os.path.join(output_dir, "35_VOS-ris")

for d in [dataset_dir, exports_dir, reports_dir, review_dir, vos_dir]:
    os.makedirs(d, exist_ok=True)

# Bibliographic RIS tags only. Screening flags stay in screened_records.xlsx.
RIS_TAGS = {
    "TY", "A1", "A2", "A3", "AU", "TI", "T1", "T2", "T3",
    "JO", "JF", "JA", "J1", "J2", "VL", "IS", "SP", "EP",
    "PY", "Y1", "DA", "KW", "DE", "ID", "AB", "N1", "N2",
    "DO", "UR", "L1", "L2", "SN", "PB", "CY", "LA", "M3",
    "C1", "C2", "C3", "C7", "AD", "DB", "AN", "CN", "CP",
    "ED", "ET", "NV", "OP", "PP", "RI", "SE", "ST", "SV",
    "TA", "TT",
}

# Keywords

OBS_METHOD = ["remote sensing"]
UAV_TERMS = ["uav", "drone", "uas"]
SAT_TERMS = ["satellite"]

SENSORS = ["modis", "landsat", "sentinel"]

ACTIVE = ["sar", "radar", "microwave"]
PASSIVE = ["optical", "multispectral", "hyperspectral"]

DOMAIN = ["cropland", "farmland", "arable", "bare soil", "agriculture"]
METHODS = ["irrigation", "precision agriculture", "water management"]
SCALING = ["downscaling", "data fusion", "multi-scale"]

HIGH_RES = ["high resolution", "fine resolution"]
REVIEW_TERMS = ["review", "systematic review", "meta-analysis"]
SOIL_MOISTURE = ["soil moisture"]


def _default_config():
    return {
        "weights": {
            "soil_moisture": 2,
            "uav_direct": 3,
            "scaling": 2,
            "agriculture": 1,
        },
        "thresholds": {"include_min": 6, "maybe_min": 3},
        "must_cite_strict": {
            "score_min": 7,
            "require_direct_uav": True,
            "require_scaling": True,
        },
        "must_cite_extended": {
            "score_min": 6,
            "branch_direct_and_scaling": True,
            "branch_potential_and_scaling_or_passive": True,
        },
        "terms": {
            "soil_moisture": SOIL_MOISTURE,
            "obs_method": OBS_METHOD,
            "uav": UAV_TERMS,
            "satellite": SAT_TERMS,
            "sensors": SENSORS,
            "active": ACTIVE,
            "passive": PASSIVE,
            "domain": DOMAIN,
            "methods": METHODS,
            "scaling": SCALING,
            "high_res": HIGH_RES,
            "review": REVIEW_TERMS,
        },
        "outputs": {
            "screened_xlsx": True,
            "summary_txt": True,
            "summary_xlsx": False,
            "keyword_txt": True,
            "ris_all": False,
            "ris_include": False,
            "ris_core": False,
            "ris_must_cite": False,
            "ris_extended_not_strict": False,
            "vos_pair": False,
            "reviews_xlsx_ris": True,
            "reviews_uav_ris": False,
            "csv": False,
            "json": False,
        },
        "output_formats": {
            "screened_xlsx": ["xlsx"],
            "summary": ["txt"],
            "keyword_txt": ["txt"],
            "ris_all": [],
            "ris_include": [],
            "ris_core": [],
            "ris_must_cite": [],
            "ris_extended_not_strict": [],
            "vos_pair": [],
            "reviews_xlsx_ris": ["xlsx"],
            "reviews_uav_ris": [],
        },
    }


def load_config(path=None):
    cfg = _default_config()
    src = Path(path) if path else CFG_PATH
    if src.exists():
        with open(src, encoding="utf-8") as f:
            user = json.load(f)
        for key, val in user.items():
            if isinstance(val, dict) and isinstance(cfg.get(key), dict):
                cfg[key].update(val)
            else:
                cfg[key] = val
    return cfg


def apply_config(cfg):
    global OBS_METHOD, UAV_TERMS, SAT_TERMS, SENSORS, ACTIVE, PASSIVE
    global DOMAIN, METHODS, SCALING, HIGH_RES, REVIEW_TERMS, SOIL_MOISTURE, _CFG
    _CFG = cfg
    t = cfg.get("terms") or {}
    OBS_METHOD = t.get("obs_method", OBS_METHOD)
    UAV_TERMS = t.get("uav", UAV_TERMS)
    SAT_TERMS = t.get("satellite", SAT_TERMS)
    SENSORS = t.get("sensors", SENSORS)
    ACTIVE = t.get("active", ACTIVE)
    PASSIVE = t.get("passive", PASSIVE)
    DOMAIN = t.get("domain", DOMAIN)
    METHODS = t.get("methods", METHODS)
    SCALING = t.get("scaling", SCALING)
    HIGH_RES = t.get("high_res", HIGH_RES)
    REVIEW_TERMS = t.get("review", REVIEW_TERMS)
    SOIL_MOISTURE = t.get("soil_moisture", SOIL_MOISTURE)


def contains_any(text, keywords):
    return any(k in text for k in keywords)


def analyze_row(row):

    text = " ".join([
        str(row.get("TI", "")),
        str(row.get("AB", "")),
        str(row.get("KW", ""))
    ]).lower()

    text = " ".join(text.split())
    result = {}

    # REVIEW
    result["is_review"] = (
        contains_any(text, REVIEW_TERMS) or
        "review" in str(row.get("M3", "")).lower()
    )

    # SENSOR
    sensors_found = [s for s in SENSORS if s in text]
    result["sensor_type"] = ", ".join(sensors_found)

    # PLATFORM
    platform = []
    if contains_any(text, UAV_TERMS):
        platform.append("UAV")
    if contains_any(text, SAT_TERMS) or sensors_found:
        platform.append("satellite")
    result["platform"] = ", ".join(sorted(set(platform)))

    # OBS METHOD
    result["observation_method"] = "RS" if (contains_any(text, OBS_METHOD) or sensors_found) else ""

    # SENSOR MODE
    sensor_mode = []
    if contains_any(text, ACTIVE):
        sensor_mode.append("active")
    if contains_any(text, PASSIVE):
        sensor_mode.append("passive")
    result["sensor_mode"] = ", ".join(sensor_mode)

    # DOMAIN / METHODS
    result["application_domain"] = ", ".join([d for d in DOMAIN if d in text])
    result["methodology"] = ", ".join([m for m in METHODS if m in text])
    result["scaling"] = ", ".join([s for s in SCALING if s in text])

    # UAV LOGIC
    uav_direct = contains_any(text, UAV_TERMS)

    uav_potential = (
        ("satellite" in result["platform"]) and
        (
            contains_any(text, HIGH_RES) or
            contains_any(text, SCALING) or
            contains_any(text, PASSIVE)
        )
    )

    result["uav_applicability"] = uav_direct
    result["uav_potential"] = uav_potential
    result["uav_relevance"] = (
        "direct" if uav_direct else
        "transferable" if uav_potential else
        "none"
    )  # transferable here = satellite potential, not the must-cite extended tier

    weights = (_CFG.get("weights") or {})
    thresholds = (_CFG.get("thresholds") or {})
    ext = (_CFG.get("must_cite_extended") or {})
    strict = (_CFG.get("must_cite_strict") or {})
    terms = (_CFG.get("terms") or {})

    # SCORE — each keyword group can carry its own weight
    score = 0
    alias = {"uav": "uav_direct", "domain": "agriculture"}
    for key, words in terms.items():
        if key == "review" or not words:
            continue
        raw = weights.get(key)
        if raw is None:
            raw = weights.get(alias.get(key, ""), 0)
        try:
            w = int(raw or 0)
        except (TypeError, ValueError):
            w = 0
        if w and contains_any(text, words):
            score += w
    if not terms:
        if contains_any(text, SOIL_MOISTURE):
            score += int(weights.get("soil_moisture", 2))
        if uav_direct:
            score += int(weights.get("uav_direct", 3))
        if contains_any(text, SCALING):
            score += int(weights.get("scaling", 2))
        if contains_any(text, DOMAIN):
            score += int(weights.get("agriculture", 1))

    result["relevance_score"] = score

    has_scaling = contains_any(text, SCALING)
    ext_min = int(ext.get("score_min", 6))
    branch_direct = bool(ext.get("branch_direct_and_scaling", True))
    branch_potential = bool(ext.get("branch_potential_and_scaling_or_passive", True))
    result["must_cite"] = (
        (branch_direct and score >= ext_min and uav_direct and has_scaling)
        or
        (
            branch_potential
            and score >= ext_min
            and uav_potential
            and (has_scaling or contains_any(text, PASSIVE))
        )
    )

    strict_min = int(strict.get("score_min", 7))
    result["must_cite_strict"] = (
        score >= strict_min
        and (uav_direct if strict.get("require_direct_uav", True) else True)
        and (has_scaling if strict.get("require_scaling", True) else True)
    )

    include_min = int(thresholds.get("include_min", 6))
    maybe_min = int(thresholds.get("maybe_min", 3))
    if score >= include_min:
        decision = "include"
    elif score >= maybe_min:
        decision = "maybe"
    else:
        decision = "exclude"

    result["screening_decision"] = decision

    return pd.Series(result)



def generate_summary(df, df_reviews, df_reviews_uav):

    path = os.path.join(reports_dir, "screening_summary.txt")

    total = len(df)

    include = (df["screening_decision"] == "include").sum()
    maybe = (df["screening_decision"] == "maybe").sum()
    exclude = (df["screening_decision"] == "exclude").sum()

    with open(path, "w", encoding="utf-8") as f:

        f.write("=== SCREENING SUMMARY (PRISMA READY) ===\n\n")

        f.write(f"Records (non-review): {total}\n")
        f.write(f"Review articles: {len(df_reviews)}\n")
        f.write(f"UAV-related reviews: {len(df_reviews_uav)}\n\n")

        f.write("SCREENING DECISIONS:\n")
        f.write(f"Include: {include} ({include/total*100:.1f}%)\n")
        f.write(f"Maybe: {maybe} ({maybe/total*100:.1f}%)\n")
        f.write(f"Exclude: {exclude} ({exclude/total*100:.1f}%)\n\n")

        n_must = int(df["must_cite"].sum())
        n_core = int(df["must_cite_strict"].sum())
        f.write("PRIORITIZATION:\n")
        f.write(f"Must-cite: {n_must}\n")
        f.write(f"Must-cite (core): {n_core}\n")
        f.write(f"Must-cite (extended): {n_must - n_core}\n")



def generate_summary_excel(df):

    path = os.path.join(reports_dir, "screening_summary.xlsx")
    total = len(df)
    decision = df["screening_decision"].value_counts().reindex(
        ["include", "maybe", "exclude"], fill_value=0
    ).reset_index()
    decision.columns = ["decision", "count"]
    decision["percentage"] = (decision["count"] / total) * 100
    write_excel_sheets(
        {
            "decisions": decision,
            "score": df["relevance_score"].value_counts().sort_index().rename_axis("score").reset_index(name="count"),
            "must_cite": df["must_cite"].value_counts().rename_axis("must_cite").reset_index(name="count"),
            "must_cite_strict": df["must_cite_strict"].value_counts().rename_axis("must_cite_strict").reset_index(name="count"),
        },
        path,
    )



def generate_keyword_statistics(df):

    path = os.path.join(reports_dir, "keyword_statistics.txt")

    with open(path, "w", encoding="utf-8") as f:

        f.write("=== KEYWORD & CATEGORY STATISTICS ===\n\n")
        f.write(f"Total records: {len(df)}\n\n")

        # PLATFORM
        f.write("PLATFORM:\n")
        f.write(f"UAV: {df['platform'].str.contains('uav', case=False).sum()}\n")
        f.write(f"Satellite: {df['platform'].str.contains('satellite', case=False).sum()}\n\n")

        # SCALING
        f.write("SCALING:\n")
        for s in SCALING:
            f.write(f"{s}: {df['scaling'].str.contains(s, case=False).sum()}\n")
        f.write("\n")

        # UAV APPLICABILITY
        f.write("UAV APPLICABILITY:\n")
        direct = df["uav_applicability"].sum()
        potential = df["uav_potential"].sum()
        combined = ((df["uav_applicability"]) | (df["uav_potential"])).sum()

        f.write(f"Direct UAV: {direct}\n")
        f.write(f"Potential UAV: {potential}\n")
        f.write(f"Combined: {combined}\n")
        f.write(f"Non-UAV: {len(df) - combined}\n")

        # SENSOR MODE
        f.write("\nSENSOR MODE:\n")
        f.write(f"Active: {df['sensor_mode'].str.contains('active', na=False).sum()}\n")
        f.write(f"Passive: {df['sensor_mode'].str.contains('passive', na=False).sum()}\n")

        # DOMAIN
        f.write("\nDOMAIN:\n")
        for d in DOMAIN:
            f.write(f"{d}: {df['application_domain'].str.contains(d, case=False, na=False).sum()}\n")



def _ris_empty(val):
    if pd.isna(val):
        return True
    text = str(val).strip()
    return text == "" or text.lower() == "nan"


def export_ris(df, path):
    """Write bibliographic RIS only. One TY per record (the real type, not a forced JOUR)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            ty = row["TY"] if "TY" in row.index and not _ris_empty(row["TY"]) else "JOUR"
            f.write(f"TY  - {ty}\n")
            for col, val in row.items():
                if col == "TY" or col not in RIS_TAGS or _ris_empty(val):
                    continue
                f.write(f"{col}  - {val}\n")
            f.write("ER  - \n\n")


def _has_keywords(series):
    kw = series.fillna("").astype(str).str.strip()
    return ~kw.eq("") & ~kw.str.lower().eq("nan")


def write_vos_counts(df_main):
    path = os.path.join(vos_dir, "counts.txt")
    kw = _has_keywords(df_main["KW"]) if "KW" in df_main.columns else pd.Series(False, index=df_main.index)
    must = df_main["must_cite"]
    strict = df_main["must_cite_strict"]
    extended = must & ~strict
    ty = df_main["TY"].fillna("JOUR").astype(str).str.upper() if "TY" in df_main.columns else pd.Series("JOUR", index=df_main.index)
    n_jour = int(ty.isin(["JOUR", "JO"]).sum())

    with open(path, "w", encoding="utf-8") as f:
        f.write("VOS RIS pair — written by screening_and_deep_classify.py\n\n")
        f.write(f"VOS_full.ris (all screened non-review): {len(df_main)}\n")
        f.write(f"  with keywords: {int(kw.sum())}\n")
        f.write(f"  without keywords: {int((~kw).sum())}\n")
        f.write(f"  TY journal (JOUR/JO): {n_jour}\n")
        f.write(f"  TY other (CONF, chapter, …): {len(df_main) - n_jour}\n")
        f.write(f"VOS_must-cite.ris (must_cite = core + extended): {int(must.sum())}\n")
        f.write(f"  core (must_cite_strict): {int(strict.sum())}\n")
        f.write(f"  extended (must_cite and not strict): {int(extended.sum())}\n")
        f.write(
            "\nDo not merge extended_studies.ris with must_cite_records.ris -- "
            "that doubles the extended tier.\n"
            "VOS_must-cite is core + extended in one file (48 records, not 45 unique studies).\n"
        )





def _want(key, default=True):
    return bool((_CFG.get("outputs") or {}).get(key, default))


_REQUIRED_FORMATS = {
    "screened_xlsx": ("xlsx",),
    "reviews_xlsx_ris": ("xlsx",),
}


def _item_formats(key, default=()):
    of = _CFG.get("output_formats") or {}
    if key in of:
        fmts = [str(x).lower() for x in (of.get(key) or [])]
    elif key == "summary":
        out = []
        if _want("summary_txt"):
            out.append("txt")
        if _want("summary_xlsx"):
            out.append("xlsx")
        fmts = out or list(default)
    elif _want(key, bool(default)):
        fmts = list(default)
    else:
        fmts = []
    for fmt in _REQUIRED_FORMATS.get(key, ()):
        if fmt not in fmts:
            fmts.append(fmt)
    return fmts


def _export_table(df, stem_path, formats=None):
    fmts = [x.lower() for x in (formats or [])]
    if "csv" in fmts or (not fmts and _want("csv", False)):
        df.to_csv(stem_path.with_suffix(".csv"), index=False, encoding="utf-8-sig")
    if "json" in fmts or (not fmts and _want("json", False)):
        df.to_json(stem_path.with_suffix(".json"), orient="records", force_ascii=False)


def main(config_path=None):

    apply_config(load_config(config_path))
    used_cfg_path = os.path.join(reports_dir, "screening_config_used.json")
    with open(used_cfg_path, "w", encoding="utf-8") as f:
        json.dump(_CFG, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Input: {input_file}")
    df = pd.read_excel(input_file)

    if "TY" in df.columns:
        book_mask = df["TY"].isin(["BOOK", "EBOOK"])
        if book_mask.any():
            dropped = int(book_mask.sum())
            df = df.loc[~book_mask].copy()
            print(
                f"[WARN] Dropped {dropped} book record(s) from screening input "
                "(should already be excluded in merge_and_classify.py)."
            )

    df_analysis = df.apply(analyze_row, axis=1)
    df_all = pd.concat([df, df_analysis], axis=1)

    df_reviews = df_all[df_all["is_review"]]
    df_main = df_all[~df_all["is_review"]]

    df_reviews_uav = df_reviews[
        (df_reviews["uav_applicability"]) |
        (df_reviews["uav_potential"])
    ]

    # SAVE
    dataset_path = os.path.join(dataset_dir, "screened_records.xlsx")
    screened_fmts = _item_formats("screened_xlsx", ("xlsx",))
    if "xlsx" in screened_fmts:
        write_excel(df_main, dataset_path, index=False)
    if screened_fmts:
        _export_table(df_main, Path(dataset_path), screened_fmts)

    review_fmts = _item_formats("reviews_xlsx_ris", ("xlsx", "ris"))
    if "xlsx" in review_fmts and not df_reviews.empty:
        write_excel(df_reviews, os.path.join(review_dir, "review_articles.xlsx"), index=False)

    # REPORTS
    summary_fmts = _item_formats("summary", ("txt", "xlsx"))
    if "txt" in summary_fmts:
        generate_summary(df_main, df_reviews, df_reviews_uav)
    if "xlsx" in summary_fmts:
        generate_summary_excel(df_main)
    if _item_formats("keyword_txt", ("txt",)):
        generate_keyword_statistics(df_main)

    # EXPORTS (Zotero subsets — bibliographic RIS only)
    if "ris" in _item_formats("ris_all", ("ris",)):
        export_ris(df_main, os.path.join(exports_dir, "all_records.ris"))
    if "ris" in _item_formats("ris_include", ("ris",)):
        export_ris(
            df_main[df_main["screening_decision"] == "include"],
            os.path.join(exports_dir, "include_records.ris"),
        )
    if "ris" in _item_formats("ris_core", ("ris",)):
        export_ris(
            df_main[df_main["must_cite_strict"]],
            os.path.join(exports_dir, "core_studies.ris"),
        )
    if "ris" in _item_formats("ris_extended_not_strict", ()):
        export_ris(
            df_main[(df_main["must_cite"]) & (~df_main["must_cite_strict"])],
            os.path.join(exports_dir, "extended_studies.ris"),
        )
    if "ris" in _item_formats("ris_must_cite", ("ris",)):
        export_ris(
            df_main[df_main["must_cite"]],
            os.path.join(exports_dir, "must_cite_records.ris"),
        )

    if "ris" in _item_formats("vos_pair", ("ris",)):
        export_ris(df_main, os.path.join(vos_dir, "VOS_full.ris"))
        export_ris(
            df_main[df_main["must_cite"]],
            os.path.join(vos_dir, "VOS_must-cite.ris"),
        )
        write_vos_counts(df_main)

    if "ris" in review_fmts:
        export_ris(df_reviews, os.path.join(review_dir, "review_articles.ris"))

    if "ris" in _item_formats("reviews_uav_ris", ()):
        export_ris(df_reviews_uav,
                   os.path.join(review_dir, "review_articles_uav.ris"))

    # INFO
    print("\n=== SUMMARY ===")
    print(f"Records (non-review): {len(df_main)}")
    print(f"Include: {(df_main['screening_decision']=='include').sum()}")
    print(f"Maybe: {(df_main['screening_decision']=='maybe').sum()}")
    print(f"Exclude: {(df_main['screening_decision']=='exclude').sum()}")

    n_must = int(df_main["must_cite"].sum())
    n_core = int(df_main["must_cite_strict"].sum())
    print("\n=== PRIORITY ===")
    print(f"Must-cite: {n_must}")
    print(f"Must-cite (core): {n_core}")
    print(f"Must-cite (extended): {n_must - n_core}")

    print("\n=== STRUCTURE ===")
    print(f"Core studies (strict): {n_core}")
    print(f"Extended (must_cite, not strict): {n_must - n_core}")
    print(f"Must-cite total: {n_must}")

    print("\n=== REVIEWS ===")
    print(f"All reviews: {len(df_reviews)}")
    print(f"UAV-related reviews: {len(df_reviews_uav)}")

    print("\nOutputs:")
    print(f"- dataset: {dataset_path}")
    print(f"- reviews: {review_dir}")
    print(f"- exports: {exports_dir}")
    print(f"- VOS RIS: {vos_dir}")
    print(f"- reports: {reports_dir}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rule-based screening")
    parser.add_argument("--config", default=None, help="JSON config (terms, weights, outputs)")
    args = parser.parse_args()
    main(args.config)
