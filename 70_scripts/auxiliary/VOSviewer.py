# ============================================
# VOSviewer CSV Export (FIXED)
# ============================================

import pandas as pd
from collections import Counter
import itertools
import os

# ============================================
# CONFIGURATION
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

input_excel = os.path.join(
    project_root,
    "30_screening",
    "31_dataset",
    "screened_records.xlsx"
)

input_ris = os.path.join(
    project_root,
    "30_screening",
    "32_exports",
    "all_records.ris"
)

output_dir = os.path.join(project_root, "40_extraction", "43_vosviewer")
os.makedirs(output_dir, exist_ok=True)

nodes_file = os.path.join(output_dir, "vosviewer_nodes.csv")
links_file = os.path.join(output_dir, "vosviewer_links.csv")

# ============================================
# LOAD DATA
# ============================================
def load_data():

    if USE_EXCEL:
        df = pd.read_excel(input_excel)

        if FILTER_INCLUDE_ONLY:
            df = df[df["screening_decision"] == "include"]

        print(f"[INFO] Records: {len(df)}")

        records = []
        for _, row in df.iterrows():
            kws = str(row.get("KW", "")).lower().split(";")
            kws = [k.strip() for k in kws if k.strip()]
            records.append(kws)

        return records

    else:
        records = []
        current = {}

        with open(input_ris, encoding="utf-8") as f:
            for line in f:
                if line.startswith("TY"):
                    current = {}
                elif line.startswith("ER"):
                    kws = current.get("KW", [])
                    records.append([k.lower() for k in kws])
                else:
                    if "  - " in line:
                        tag, val = line.split("  - ", 1)
                        current.setdefault(tag, []).append(val.strip())

        print(f"[INFO] RIS records: {len(records)}")
        return records

# ============================================
# BUILD + FILTER NETWORK (FIXED)
# ============================================
def build_filtered_network(records):

    keyword_counter = Counter()

    # 1. count
    for kws in records:
        for k in set(kws):
            keyword_counter[k] += 1

    # 2. filter
    keywords = {
        k: v for k, v in keyword_counter.items()
        if v >= MIN_OCC
    }

    print(f"[INFO] Keywords >= {MIN_OCC}: {len(keywords)}")

    # 3. ONLY filtered keywords go into links
    pair_counter = Counter()

    for kws in records:

        filtered_kws = [k for k in set(kws) if k in keywords]

        for a, b in itertools.combinations(filtered_kws, 2):
            pair_counter[(a, b)] += 1

    return keywords, pair_counter

# ============================================
# FILTER
# ============================================
def filter_keywords(counter):
    return {k: v for k, v in counter.items() if v >= MIN_OCC}

# ============================================
# EXPORT CSV
# ============================================
def export_vosviewer(keywords, pairs):

    # =====================
    # NODES (MAP FILE)
    # =====================
    id_map = {}

    with open(nodes_file, "w", encoding="utf-8") as f:
        f.write("id\tlabel\n")

        for i, (k, v) in enumerate(
            sorted(keywords.items(), key=lambda x: -x[1]),
            start=1
        ):
            id_map[k] = i
            f.write(f"{i}\t{k}\n")

    print("MAX NODE ID:", max(id_map.values()))

    # =====================
    # LINKS (NETWORK FILE)
    # =====================
    max_link_id = 0

    with open(links_file, "w", encoding="utf-8") as f:

        for (a, b), w in pairs.items():

            if a in id_map and b in id_map:

                s = id_map[a]
                t = id_map[b]

                f.write(f"{s}\t{t}\t{w}\n")

                max_link_id = max(max_link_id, s, t)

    print("MAX LINK ID:", max_link_id)

    print(f"[INFO] Nodes saved: {nodes_file}")
    print(f"[INFO] Links saved: {links_file}")

# ============================================
# MAIN
# ============================================
def main():

    print("\n=== VOSVIEWER EXPORT ===")

    records = load_data()

    keywords, pair_counter = build_filtered_network(records)

    print(f"[INFO] Keywords >= {MIN_OCC}: {len(keywords)}")

    export_vosviewer(keywords, pair_counter)

    print("\nDONE")

# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    main()