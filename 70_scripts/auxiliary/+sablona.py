# ============================================
# SCRIPT NAME
# ============================================
# Description:
# Short description of what the script does
# (e.g., screening, extraction, visualization)

# ============================================
# IMPORTS
# ============================================
import os
import pandas as pd

# ============================================
# CONFIGURATION
# ============================================
# General settings

DEBUG = True

# ============================================
# PATHS (INPUT / OUTPUT)
# ============================================
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from project_paths import PROJECT_ROOT

project_root = str(PROJECT_ROOT)

# -------- INPUTS --------
input_file = os.path.join(
    project_root,
    "path",
    "to",
    "input_file.xlsx"
)

# -------- OUTPUTS --------
output_root = os.path.join(project_root, "path", "to", "outputs")

output_file = os.path.join(output_root, "output_file.xlsx")
report_file = os.path.join(output_root, "report.txt")

# create folders
os.makedirs(output_root, exist_ok=True)

# ============================================
# LOAD DATA
# ============================================
def load_data(path):
    df = pd.read_excel(path)

    if DEBUG:
        print(f"[INFO] Loaded records: {len(df)}")

    return df

# ============================================
# DATA PROCESSING
# ============================================
def process_data(df):

    # --- example ---
    df = df.copy()

    # filtering
    df = df[df["column"].notna()]

    # transformation
    df["new_column"] = df["column"].astype(str).str.lower()

    if DEBUG:
        print(f"[INFO] After processing: {len(df)}")

    return df

# ============================================
# ANALYSIS / CORE LOGIC
# ============================================
def analyze_data(df):

    # --- example ---
    summary = {
        "total": len(df),
        "non_empty": df["column"].notna().sum()
    }

    if DEBUG:
        print("[INFO] Analysis completed")

    return df, summary

# ============================================
# SAVE OUTPUTS
# ============================================
def save_outputs(df, summary):

    # main output
    df.to_excel(output_file, index=False)

    # report
    with open(report_file, "w", encoding="utf-8") as f:
        for k, v in summary.items():
            f.write(f"{k}: {v}\n")

    print("[INFO] Outputs saved")
    print(f" - dataset: {output_file}")
    print(f" - report: {report_file}")

# ============================================
# MAIN RUN
# ============================================
def main():

    print("\n=== RUN START ===")

    # 1. load
    df = load_data(input_file)

    # 2. process
    df = process_data(df)

    # 3. analyze
    df, summary = analyze_data(df)

    # 4. save
    save_outputs(df, summary)

    print("=== RUN END ===\n")


# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    main()