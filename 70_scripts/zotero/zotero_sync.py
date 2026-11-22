# ============================================
# Zotero → extraction Excel sync
# Fills Zotero_key and Notes from your Zotero library (match by DOI).
# ============================================

import json
import os
import re
import sys
import urllib.error
import urllib.request

import pandas as pd

# ============================================
# PATHS
# ============================================
import sys
from pathlib import Path

script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir.parent))
from project_paths import PROJECT_ROOT

project_root = str(PROJECT_ROOT)
config_path = script_dir / "zotero_config.json"
input_dir = os.path.join(project_root, "40_extraction", "41_input")
working_dir = os.path.join(project_root, "40_extraction", "42_working")

FILES = {
    "1": ("extraction_input_full.xlsx", input_dir),
    "2": ("extraction_input_refined.xlsx", input_dir),
    "3": ("extraction_filled.xlsx", working_dir),
}

# ============================================
# HELPERS
# ============================================
def normalize_doi(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    s = str(value).strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if s.startswith(prefix):
            s = s[len(prefix) :]
    return s.strip()


def strip_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def resolve_user_id_from_api_key(api_key: str) -> str:
    """Look up numeric user ID from API key (Zotero /keys endpoint)."""
    url = f"https://api.zotero.org/keys/{api_key}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Could not resolve user ID from API key (HTTP {e.code}).")
        print("Check api_key at https://www.zotero.org/settings/keys")
        sys.exit(1)
    user_id = data.get("userID") or data.get("userId")
    if not user_id:
        print("[ERROR] Unexpected response from Zotero API (no userID).")
        sys.exit(1)
    return str(user_id)


def load_config() -> dict:
    if not os.path.isfile(config_path):
        print(f"[ERROR] Missing {config_path}")
        print("Copy zotero_config.example.json to zotero_config.json and fill in api_key.")
        print("Create key: https://www.zotero.org/settings/keys/new")
        sys.exit(1)
    with open(config_path, encoding="utf-8-sig") as f:
        cfg = json.load(f)

    if not cfg.get("api_key") or "YOUR_" in str(cfg.get("api_key", "")):
        print("[ERROR] Set api_key in zotero_config.json")
        sys.exit(1)

    lib_id = str(cfg.get("library_id", "")).strip()
    if not lib_id or "YOUR_" in lib_id:
        user_id = resolve_user_id_from_api_key(cfg["api_key"])
        cfg["library_id"] = user_id
        cfg.setdefault("library_type", "user")
        print(f"[INFO] library_id resolved automatically: {user_id}")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
            f.write("\n")
        print(f"[INFO] Saved to {config_path}")

    cfg.setdefault("library_type", "user")
    return cfg


def fetch_zotero_index(cfg: dict) -> dict:
    try:
        from pyzotero import zotero
    except ImportError:
        print("[ERROR] Install pyzotero: python -m pip install pyzotero")
        sys.exit(1)

    zot = zotero.Zotero(cfg["library_id"], cfg.get("library_type", "user"), cfg["api_key"])

    if cfg.get("collection_key"):
        items = zot.everything(zot.collection_items(cfg["collection_key"]))
    else:
        items = zot.everything(zot.items(itemType="-attachment"))

    index = {}
    for item in items:
        data = item.get("data", {})
        if data.get("itemType") in ("note", "attachment"):
            continue

        key = item.get("key", "")
        doi = normalize_doi(data.get("DOI", ""))
        title = (data.get("title") or "").strip().lower()

        notes = []
        try:
            for child in zot.children(key):
                cdata = child.get("data", {})
                if cdata.get("itemType") == "note" and cdata.get("note"):
                    notes.append(strip_html(cdata["note"]))
        except Exception:
            pass

        entry = {
            "zotero_key": key,
            "notes": "\n---\n".join(notes) if notes else "",
            "title": title,
        }

        if doi:
            index[f"doi:{doi}"] = entry
        if title:
            index[f"title:{title}"] = entry

    print(f"[INFO] Zotero items indexed: {len(items)}")
    return index


def match_row(row, index: dict) -> dict | None:
    doi = normalize_doi(row.get("DOI", ""))
    if doi and f"doi:{doi}" in index:
        return index[f"doi:{doi}"]

    title = str(row.get("Title", row.get("TI", ""))).strip().lower()
    if title and f"title:{title}" in index:
        return index[f"title:{title}"]

    return None


def sync_file(path: str, index: dict, overwrite_notes: bool = False) -> None:
    if not os.path.isfile(path):
        print(f"[SKIP] Not found: {path}")
        return

    df = pd.read_excel(path)

    if "Zotero_key" not in df.columns:
        df["Zotero_key"] = ""
    if "Notes" not in df.columns:
        df["Notes"] = ""

    matched = 0
    keys_filled = 0
    notes_filled = 0

    for i, row in df.iterrows():
        hit = match_row(row, index)
        if not hit:
            continue
        matched += 1

        if not str(row.get("Zotero_key", "")).strip():
            df.at[i, "Zotero_key"] = hit["zotero_key"]
            keys_filled += 1

        if hit["notes"] and (overwrite_notes or not str(row.get("Notes", "")).strip()):
            df.at[i, "Notes"] = hit["notes"]
            notes_filled += 1

    df.to_excel(path, index=False)
    print(f"[OK] {os.path.basename(path)}: matched={matched}, keys+={keys_filled}, notes+={notes_filled}")


def show_ids_only() -> None:
    """Print user ID from API key and exit (for setup)."""
    cfg = load_config()
    print(f"\nlibrary_id (user ID): {cfg['library_id']}")
    print(f"library_type:         {cfg.get('library_type', 'user')}")
    print("\nUser ID is also shown on: https://www.zotero.org/settings/keys")
    print("(section: Your userID for use in API calls)\n")


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--show-id", "--id"):
        show_ids_only()
        return

    print("\n=== ZOTERO TO EXTRACTION SYNC ===\n")
    print("Source: Zotero API (notes are NOT included in standard .bib export).\n")
    print("Which file to update?")
    for k, (name, folder) in FILES.items():
        print(f"  {k}  {name}  ({folder})")
    print("  4  all files in 41_input")
    print("  0  cancel")

    choice = input("\nChoice: ").strip()

    if choice == "0":
        return

    overwrite = input("Overwrite existing Notes? (y/N): ").strip().lower() == "y"

    cfg = load_config()
    index = fetch_zotero_index(cfg)

    os.makedirs(working_dir, exist_ok=True)

    if choice == "4":
        for _, (name, folder) in FILES.items():
            if folder == input_dir:
                sync_file(os.path.join(folder, name), index, overwrite)
    elif choice in FILES:
        name, folder = FILES[choice]
        sync_file(os.path.join(folder, name), index, overwrite)
    else:
        print("[ERROR] Invalid choice.")


if __name__ == "__main__":
    main()
