# ============================================
# WoS / Scopus Query Generator
# ============================================
# Generates structured search queries and saves them


import os
import json
from datetime import datetime


DEBUG = True


import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from project_paths import PROJECT_ROOT

project_root = str(PROJECT_ROOT)

output_dir = os.path.join(project_root, "00_search", "01_raw")
os.makedirs(output_dir, exist_ok=True)

json_file = os.path.join(output_dir, "search_strategies.json")
txt_file = os.path.join(output_dir, "Query_combinations.txt")


def get_user_input():

    print("\nEnter keyword groups (term1, term2 | field). Empty line = end.\n")

    groups = []
    exclude = []

    # --- include groups ---
    while True:
        line = input("Group: ")
        if not line.strip():
            break

        if "|" not in line:
            print("Format error: use: term1, term2 | field")
            continue

        terms_part, field = line.split("|")
        terms = [t.strip() for t in terms_part.split(",")]

        groups.append({
            "terms": terms,
            "field": field.strip().lower()
        })

    # --- exclude groups ---
    while True:
        line = input("Exclude (optional): ")
        if not line.strip():
            break

        if "|" not in line:
            print("Format error: use: term1, term2 | field")
            continue

        terms_part, field = line.split("|")
        terms = [t.strip() for t in terms_part.split(",")]

        exclude.append({
            "terms": terms,
            "field": field.strip().lower()
        })

    year_from = input("Year from: ")
    year_to = input("Year to: ")
    language = input("Language: ")

    return {
        "groups": groups,
        "exclude": exclude,
        "year_from": int(year_from) if year_from else None,
        "year_to": int(year_to) if year_to else None,
        "language": language if language else None
    }



def map_field_wos(field):
    return {
        "topic": "TS",
        "title": "TI",
        "abstract": "AB",
        "all": "TS"
    }.get(field, "TS")


def map_field_scopus(field):
    return {
        "topic": "TITLE-ABS-KEY",
        "title": "TITLE",
        "abstract": "ABS",
        "all": "TITLE-ABS-KEY"
    }.get(field, "TITLE-ABS-KEY")




def format_terms(terms):
    return "(" + " OR ".join([f'"{t}"' for t in terms]) + ")"


def build_wos_part(group):
    return f"{map_field_wos(group['field'])}={format_terms(group['terms'])}"


def build_scopus_part(group):
    return f"{map_field_scopus(group['field'])}{format_terms(group['terms'])}"


def build_queries(params):

    wos_parts = [build_wos_part(g) for g in params["groups"]]
    scopus_parts = [build_scopus_part(g) for g in params["groups"]]

    wos_query = " AND ".join(wos_parts)
    scopus_query = " AND ".join(scopus_parts)

    # --- exclusions ---
    for ex in params["exclude"]:
        wos_query += f" NOT {build_wos_part(ex)}"
        scopus_query += f" AND NOT {build_scopus_part(ex)}"

    # --- year ---
    if params["year_from"] and params["year_to"]:
        wos_query += f" AND PY={params['year_from']}-{params['year_to']}"
        scopus_query += (
            f" AND PUBYEAR > {params['year_from']-1} "
            f"AND PUBYEAR < {params['year_to']+1}"
        )

    # --- language ---
    if params["language"]:
        wos_query += f" AND LA={params['language'].upper()}"
        scopus_query += f" AND LANGUAGE({params['language'].lower()})"

    if DEBUG:
        print("[INFO] Query built")

    return wos_query, scopus_query



def save_outputs(params, wos, scopus):

    # --- JSON ---
    data = {
        "timestamp": datetime.now().isoformat(),
        "input": params,
        "queries": {
            "web_of_science": wos,
            "scopus": scopus
        }
    }

    with open(json_file, "a", encoding="utf-8") as f:
        json.dump(data, f)
        f.write("\n")

    # --- TXT ---
    with open(txt_file, "a", encoding="utf-8") as f:

        f.write("\n\n---\n\n")

        for group in params["groups"]:
            f.write(f"{', '.join(group['terms'])} | {group['field']}\n")

        for ex in params["exclude"]:
            f.write(f"NOT: {', '.join(ex['terms'])} | {ex['field']}\n")

        if params["year_from"]:
            f.write(f"year: {params['year_from']}-{params['year_to']}\n")

        if params["language"]:
            f.write(f"language: {params['language']}\n")

        f.write("\nWeb of Science:\n")
        f.write(wos + "\n\n")

        f.write("Scopus:\n")
        f.write(scopus + "\n")

    print("[INFO] Saved outputs:")
    print(f" - JSON: {json_file}")
    print(f" - TXT:  {txt_file}")


def freeze_final_query(params, wos, scopus):
    """Overwrite 00_search/02_final/final_query.txt; backup previous copy."""
    import shutil

    final_dir = os.path.join(project_root, "00_search", "02_final")
    os.makedirs(final_dir, exist_ok=True)
    dest = os.path.join(final_dir, "final_query.txt")
    if os.path.exists(dest):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = os.path.join(output_dir, f"final_query_backup_{stamp}.txt")
        shutil.copy2(dest, backup)
        print(f"[INFO] Previous frozen query: {backup}")

    lines = ["## frozen", ""]
    for group in params["groups"]:
        lines.append(f"{', '.join(group['terms'])} | {group['field']}")
    for ex in params.get("exclude") or []:
        lines.append(f"NOT: {', '.join(ex['terms'])} | {ex['field']}")
    if params.get("year_from"):
        lines.append(f"year: {params['year_from']}-{params['year_to']}")
    if params.get("language"):
        lines.append(f"language: {params['language']}")
    lines += ["", "Web of Science:", wos, "", "Scopus:", scopus, ""]
    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    params_path = os.path.join(final_dir, "final_query_params.json")
    with open(params_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "input": params,
                "queries": {"web_of_science": wos, "scopus": scopus},
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"[INFO] Frozen query: {dest}")
    return dest


def run_from_params(params, save=True, freeze=False):
    wos, scopus = build_queries(params)
    if save:
        save_outputs(params, wos, scopus)
    if freeze:
        freeze_final_query(params, wos, scopus)
    return wos, scopus


def run_query():

    params = get_user_input()

    wos, scopus = build_queries(params)

    print("\n=== RESULTS ===\n")
    print("Web of Science:\n", wos)
    print("\nScopus:\n", scopus)

    confirm = input("\nSave search strategy? (y/n): ")
    if confirm.lower() == "y":
        save_outputs(params, wos, scopus)



def main():

    print("\n=== QUERY GENERATOR ===")

    while True:
        run_query()

        again = input("\nAnother query? (y/n): ")
        if again.lower() != "y":
            break

    print("\n[INFO] Finished.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="WoS / Scopus query generator")
    parser.add_argument("--params", help="JSON file with groups, exclude, years, language")
    parser.add_argument("--save", action="store_true", help="Append to 00_search/01_raw")
    parser.add_argument("--freeze", action="store_true", help="Write 00_search/02_final/final_query.txt")
    args = parser.parse_args()

    if args.params:
        with open(args.params, encoding="utf-8") as f:
            payload = json.load(f)
        params = payload.get("input", payload)
        wos, scopus = run_from_params(params, save=args.save, freeze=args.freeze)
        print("\n=== RESULTS ===\n")
        print("Web of Science:\n", wos)
        print("\nScopus:\n", scopus)
    else:
        main()
