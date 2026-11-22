# ============================================
# Bib Processing (PRISMA)
# ============================================

import json
import pandas as pd
import os
from datetime import datetime


DEBUG = True

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from project_paths import PROJECT_ROOT

project_root = str(PROJECT_ROOT)

input_dir = os.path.join(project_root, "10_data_raw", "12_final")

output_clean_dir = os.path.join(project_root, "20_data_clean")
output_audit_dir = os.path.join(output_clean_dir, "21_audit")

os.makedirs(output_clean_dir, exist_ok=True)
os.makedirs(output_audit_dir, exist_ok=True)

# INPUT: all *.ris in 12_final/ (any number of databases)

# OUTPUT FILES — working tables are xlsx only; extra csv/ris are optional in the runner
file_clean_xlsx = os.path.join(output_clean_dir, "clean_records.xlsx")

file_master = os.path.join(output_audit_dir, "all_records_with_status.xlsx")
file_report = os.path.join(output_audit_dir, "processing_report.txt")
file_prisma = os.path.join(output_audit_dir, "prisma_counts.csv")


def normalize_ty(value):
    """Normalize RIS publication types, incl. Scopus 'label.ris.referenceType.*'."""
    if not isinstance(value, str):
        return value
    v = value.strip()
    prefix = "label.ris.referenceType."
    if v.startswith(prefix):
        v = v[len(prefix):].split(".")[0]
    return v.upper()


def parse_ris(file_path, source):

    records = []
    record = {}

    with open(file_path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()

            if line.startswith("TY  -"):
                record = {}
                record["TY"] = normalize_ty(line.split("  - ", 1)[1]) \
                    if "  - " in line else ""

            elif line.startswith("ER  -"):
                record["Source"] = source
                records.append(record)

            elif "  - " in line:
                tag, value = line.split("  - ", 1)
                record[tag] = record.get(tag, "") + (
                    "; " if tag in record else ""
                ) + value

    return pd.DataFrame(records)


def _doi_missing_mask(df):
    """True where DOI is absent or blank. Not an exclusion reason."""
    if "DO" not in df.columns:
        return pd.Series(True, index=df.index)
    s = df["DO"]
    blank = s.isna()
    as_text = s.astype(str).str.strip().str.lower()
    return blank | as_text.eq("") | as_text.isin(["nan", "none", "na"])


def classify_records(df):

    df = df.copy()

    df["status"] = "correct_record"
    df["exclusion_reason"] = ""
    df["doi_missing"] = _doi_missing_mask(df)

    # --- incomplete ---
    mask = df["TI"].isna() | df["PY"].isna()
    df.loc[mask, ["status", "exclusion_reason"]] = [
        "incomplete_record", "Missing title or year"
    ]

    # --- non-article (publication type): exclude books only ---
    if "TY" in df.columns:
        book_mask = df["TY"].isin(["BOOK", "EBOOK"])
        df.loc[book_mask, ["status", "exclusion_reason"]] = [
            "non_article_type",
            "Book (systematic review of primary research articles only)",
        ]

    # Missing DOI is flagged (doi_missing) but NOT removed. Title–year
    # duplicate detection still applies to these rows.

    # --- duplicate DOI (only when a DOI is present) ---
    if "DO" in df.columns:
        dup_mask = df.duplicated(subset=["DO"], keep="first")
        mask = dup_mask & ~df["doi_missing"]
        df.loc[mask, ["status", "exclusion_reason"]] = [
            "duplicate_doi", "Duplicate DOI"
        ]

    # --- duplicate title + year among rows still marked keepable ---
    dup_title = df.duplicated(subset=["TI", "PY"], keep="first")
    mask = dup_title & (df["status"] == "correct_record")
    df.loc[mask, ["status", "exclusion_reason"]] = [
        "duplicate_title", "Duplicate title and year"
    ]

    return df


def export_diagnostics(df):

    # --- duplicate DOI ---
    if "DO" in df.columns:
        dup = df[df["DO"].notna() &
                 df.duplicated(subset=["DO"], keep=False)]

        if not dup.empty:
            dup = dup.sort_values("DO")
            dup["dup_group"] = dup.groupby("DO").ngroup()

            dup.to_excel(
                os.path.join(output_audit_dir, "duplicates_doi.xlsx"),
                index=False
            )

    # --- duplicate TITLE ---
    dup_title = df[df.duplicated(["TI", "PY"], keep=False)]

    if not dup_title.empty:
        dup_title = dup_title.sort_values(["TI", "PY"])
        dup_title["dup_group"] = dup_title.groupby(["TI", "PY"]).ngroup()

        dup_title.to_excel(
            os.path.join(output_audit_dir, "duplicates_title.xlsx"),
            index=False
        )

    # --- missing DOI (retained; audit list only) ---
    if "doi_missing" in df.columns:
        missing = df[df["doi_missing"]]
    else:
        missing = df[df["DO"].isna()] if "DO" in df.columns else df.iloc[0:0]

    if not missing.empty:
        missing.to_excel(
            os.path.join(output_audit_dir, "missing_doi.xlsx"),
            index=False
        )

    print("[INFO] Diagnostics exported")


def export_ris(df, path):

    skip = {"Source", "status", "exclusion_reason", "doi_missing"}
    with open(path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            f.write("TY  - JOUR\n")

            for col, val in row.items():
                if pd.notna(val) and col not in skip:
                    f.write(f"{col}  - {val}\n")

            f.write("ER  - \n\n")


def _type_rows(df):
    if df is None or df.empty or "TY" not in df.columns:
        return []
    runner = Path(__file__).resolve().parents[1] / "runner"
    if str(runner) not in sys.path:
        sys.path.insert(0, str(runner))
    from catalog import publication_type_counts
    return publication_type_counts(df["TY"].tolist())


def save_exclusion_log(df_classified, df_clean):
    """Machine-readable reasons for PRISMA and the webapp protocol export."""
    import json

    removed = df_classified[df_classified["status"] != "correct_record"]
    rows = []
    for (status, reason), n in (
        removed.groupby(["status", "exclusion_reason"]).size().items()
    ):
        rows.append({
            "source": "script",
            "status": status,
            "reason": reason,
            "n": int(n),
            "kept": False,
        })
    n_missing_kept = int(
        (df_clean["doi_missing"] == True).sum()  # noqa: E712
        if "doi_missing" in df_clean.columns else 0
    )
    if n_missing_kept:
        rows.append({
            "source": "script",
            "status": "doi_missing",
            "reason": "DOI missing — retained (cannot exclude)",
            "n": n_missing_kept,
            "kept": True,
            "cannot_exclude": True,
        })
    missing_kept = (
        df_clean[df_clean["doi_missing"] == True]  # noqa: E712
        if "doi_missing" in df_clean.columns else df_clean.iloc[0:0]
    )
    payload = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "retained": int(len(df_clean)),
        "removed": int(len(df_classified) - len(df_clean)),
        "doi_missing_retained": n_missing_kept,
        "doi_missing_types": _type_rows(missing_kept),
        "kept_types": _type_rows(df_clean),
        "entries": rows,
    }
    path = os.path.join(output_audit_dir, "exclusion_log.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def save_report(df_classified, df_clean, sources):

    stats = df_classified["status"].value_counts()
    stats.to_csv(file_prisma)

    n_doi_merged = int(df_classified["doi_missing"].sum()) if "doi_missing" in df_classified.columns else 0
    n_doi_kept = int(df_clean["doi_missing"].sum()) if "doi_missing" in df_clean.columns else 0

    with open(file_report, "w", encoding="utf-8") as f:

        f.write("=== DATA PROCESSING REPORT ===\n\n")
        f.write(f"Date: {datetime.now()}\n\n")

        f.write("INPUT (only these files in 12_final):\n")
        for rec in sources:
            f.write(f"  {rec['database']}\n")
            f.write(f"    file: {rec['file']}\n")
            if rec.get("downloaded_at"):
                f.write(f"    downloaded: {rec['downloaded_at']}\n")
            f.write(f"    records: {rec['n']}\n")
        f.write(f"Merged (sum of files, before removing duplicates): {len(df_classified)}\n\n")

        f.write("CLASSIFICATION:\n")
        for k, v in stats.items():
            f.write(f"{k}: {v}\n")

        f.write("\nDOI:\n")
        f.write(f"missing among merged: {n_doi_merged}\n")
        f.write(f"missing among retained: {n_doi_kept}\n")
        missing_kept = (
            df_clean[df_clean["doi_missing"] == True]  # noqa: E712
            if "doi_missing" in df_clean.columns else df_clean.iloc[0:0]
        )
        for rec in _type_rows(missing_kept):
            f.write(f"  missing retained type | {rec['label']}: {rec['n']}\n")
        f.write("policy: records without DOI are retained and cannot be excluded for missing DOI\n")

        f.write("\nKEPT PUBLICATION TYPES (conference papers and book chapters stay; books removed):\n")
        kept_types = _type_rows(df_clean)
        if not kept_types:
            f.write("(none)\n")
        else:
            for rec in kept_types:
                f.write(f"  {rec['label']}: {rec['n']}\n")

        f.write("\nREMOVED BY REASON:\n")
        removed = df_classified[df_classified["status"] != "correct_record"]
        if removed.empty:
            f.write("(none)\n")
        else:
            for (status, reason), n in removed.groupby(
                ["status", "exclusion_reason"]
            ).size().items():
                f.write(f"{status} | {reason}: {n}\n")

        f.write("\nFINAL:\n")
        f.write(f"Retained: {len(df_clean)}\n")
        f.write(f"Removed: {len(df_classified) - len(df_clean)}\n")
        f.write("correct_record: " + str(len(df_clean)) + "\n")

    save_exclusion_log(df_classified, df_clean)
    print("[INFO] Report saved")




def main():

    print("\n=== PRISMA PROCESSING ===")

    from pathlib import Path as _Path

    input_path = _Path(input_dir)
    meta_path = input_path / "ris_meta.json"
    meta = {}
    if meta_path.exists():
        with open(meta_path, encoding="utf-8") as fh:
            meta = json.load(fh) or {}
    listed = list(meta.get("exports") or [])
    jobs = []
    if listed:
        for rec in listed:
            fp = input_path / (rec.get("file") or "")
            if fp.exists() and fp.suffix.lower() == ".ris":
                jobs.append((fp, rec))
    if not jobs:
        for fp in sorted(input_path.glob("*.ris"), key=lambda x: x.name.lower()):
            if fp.name.startswith("_"):
                continue
            jobs.append((fp, {
                "database": fp.stem.replace("export_", "").replace("_", " ").strip() or fp.stem,
                "file": fp.name,
            }))
    if not jobs:
        raise FileNotFoundError(
            f"No .ris files in {input_dir}. Upload at least one export in the runner (step 4)."
        )

    print("[INFO] Loading data...")

    frames = []
    sources = []
    for fp, rec in jobs:
        source = rec.get("database") or fp.stem
        df_one = parse_ris(str(fp), source)
        sources.append({
            "database": source,
            "file": fp.name,
            "downloaded_at": rec.get("downloaded_at") or "",
            "n": len(df_one),
        })
        frames.append(df_one)
        print(f"[INFO] {source}: {len(df_one)}  ({fp.name})")

    df_merged = pd.concat(frames, ignore_index=True)

    print(f"[INFO] Records loaded: {len(df_merged)}")

    # --- classification ---
    df_classified = classify_records(df_merged)

    sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "runner"))
    from record_audit import fill_blank_fields_from_duplicates
    df_classified = fill_blank_fields_from_duplicates(df_classified)

    # --- diagnostics ---
    export_diagnostics(df_classified)

    # --- clean dataset ---
    keepable = {"correct_record", "missing_doi"}
    df_clean = df_classified[df_classified["status"].isin(keepable)]

    # --- export ---
    df_classified.to_excel(file_master, index=False)

    df_clean.to_excel(file_clean_xlsx, index=False)

    # --- report ---
    save_report(df_classified, df_clean, sources)

    # --- summary ---
    print("\n=== SUMMARY ===")
    print(f"Total records: {len(df_merged)}")
    print(f"Clean records: {len(df_clean)}")

    print("\nOutputs:")
    print(f"- CLEAN: {output_clean_dir}")
    print(f"- AUDIT: {output_audit_dir}")




if __name__ == "__main__":
    main()
