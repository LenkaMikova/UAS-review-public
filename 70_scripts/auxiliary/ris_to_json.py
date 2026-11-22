# ============================================
# VOSviewer JSON Builder
# ============================================

# ============================================
# IMPORTS
# ============================================
import pandas as pd
from collections import Counter
import itertools
import json
import os

# ============================================
# CONFIG
# ============================================
USE_EXCEL = True
MIN_OCC = 5
FILTER_INCLUDE_ONLY = True

# ============================================
# PATHS
# ============================================
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from project_paths import PROJECT_ROOT

project_root = str(PROJECT_ROOT)

input_ris = os.path.join(
    project_root,
    "30_screening",
    "32_exports",
    "all_records.ris"
)

input_excel = os.path.join(
    project_root,
    "30_screening",
    "31_dataset",
    "screened_records.xlsx"
)

output_root = os.path.join(project_root, "40_extraction")
json_dir = os.path.join(output_root, "43_json")
os.makedirs(json_dir, exist_ok=True)

output_json = os.path.join(json_dir, "vosviewer_map.json")

# ============================================
# LOAD DATA
# ============================================
def load_from_excel():

    df = pd.read_excel(input_excel)

    if FILTER_INCLUDE_ONLY:
        df = df[df["screening_decision"] == "include"]

    print(f"[INFO] Excel records: {len(df)}")

    records = []
    for _, row in df.iterrows():
        raw = str(row.get("KW", ""))
        kws = [k.strip().lower() for k in raw.split(";") if k.strip()]
        records.append({"KW": kws})

    return records


def load_from_ris():

    records = []
    current = {}

    with open(input_ris, encoding="utf-8") as f:
        for line in f:
            if line.startswith("TY"):
                current = {}
            elif line.startswith("ER"):
                records.append(current)
            else:
                if "  - " in line:
                    tag, val = line.split("  - ", 1)
                    current.setdefault(tag, []).append(val.strip())

    print(f"[INFO] RIS records: {len(records)}")
    return records


def load_data():
    if USE_EXCEL:
        print("[INFO] Loading from Excel...")
        return load_from_excel()
    else:
        print("[INFO] Loading from RIS...")
        return load_from_ris()

# ============================================
# EXTRACT KEYWORDS
# ============================================
def extract_keywords(records):

    all_keywords = []

    for r in records:
        kws = r.get("KW", [])

        if isinstance(kws, list):
            cleaned = [k.lower().strip() for k in kws if k]
        else:
            cleaned = []

        if cleaned:
            all_keywords.append(list(set(cleaned)))

    print(f"[INFO] Records with keywords: {len(all_keywords)}")
    return all_keywords

# ============================================
# BUILD NETWORK
# ============================================
def build_network(all_keywords):

    pair_counter = Counter()
    keyword_counter = Counter()

    for kws in all_keywords:

        for k in kws:
            keyword_counter[k] += 1

        for a, b in itertools.combinations(kws, 2):
            pair_counter[tuple(sorted((a, b)))] += 1

    print(f"[INFO] Unique keywords: {len(keyword_counter)}")

    return keyword_counter, pair_counter

# ============================================
# FILTER
# ============================================
def filter_keywords(keyword_counter):

    keywords = {
        k: c for k, c in keyword_counter.items()
        if c >= MIN_OCC
    }

    print(f"[INFO] Keywords after threshold ({MIN_OCC}+): {len(keywords)}")
    return keywords

# ============================================
# BUILD JSON (VOSviewer format)
# ============================================
def build_json(keywords, pair_counter):

    id_map = {}
    items = []

    # nodes
    for i, (k, c) in enumerate(
        sorted(keywords.items(), key=lambda x: -x[1]),
        start=1
    ):
        id_map[k] = i

        items.append({
            "id": i,
            "label": k,
            "x": 0,
            "y": 0,
            "cluster": 1,
            "weights": {
                "Occurrences": c
            }
        })

    # links
    links = []
    for (a, b), w in pair_counter.items():
        if a in id_map and b in id_map:
            links.append({
                "source_id": id_map[a],
                "target_id": id_map[b],
                "strength": w
            })

    print(f"[INFO] Links created: {len(links)}")

    return {
        "network": {
            "items": items,
            "links": links
        }
    }

# ============================================
# EXPORT
# ============================================
def save_json(data):

    # validation
    try:
        json.dumps(data)
    except Exception as e:
        print("[ERROR] JSON validation failed:", e)
        return

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("[INFO] JSON saved")

# ============================================
# MAIN
# ============================================
def main():

    print("\n=== VOSVIEWER JSON GENERATION ===")

    records = load_data()
    all_keywords = extract_keywords(records)

    keyword_counter, pair_counter = build_network(all_keywords)
    keywords = filter_keywords(keyword_counter)

    output = build_json(keywords, pair_counter)

    save_json(output)

    print("\n=== SUMMARY ===")
    print(f"Nodes: {len(output['network']['items'])}")
    print(f"Links: {len(output['network']['links'])}")
    print(f"Output: {output_json}")

# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    main()