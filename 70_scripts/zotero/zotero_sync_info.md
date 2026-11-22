# Zotero → extraction sync

[Python script](zotero_sync.py) pulls **item keys** and **notes** from your Zotero library into extraction Excel files.

## Why not `.bib`?

| Export | Contains |
|--------|----------|
| **`.bib`** (standard) | Bibliographic metadata; citation key only with [Better BibTeX](https://retorque.re/zotero-better-bibtex/) |
| **`.bib`** | Does **not** include Zotero notes or item keys (unless custom BBT fields) |
| **`zotero_sync.py`** | `Zotero_key` + `Notes` via Zotero API, matched by DOI (fallback: title) |

Use **`.bib`** for `90_review/review.qmd` citations (`90_review/references.bib`).  
Use **`zotero_sync.py`** for linking extraction tables to Zotero work.

## Setup (once)

1. `pip install -r requirements.txt`
2. Copy `zotero/zotero_config.example.json` → `zotero/zotero_config.json`
3. Paste your [API key](https://www.zotero.org/settings/keys/new) into `api_key`
4. Leave `library_id` empty — the script fills it automatically from the API key  
   Or find it manually on **[zotero.org/settings/keys](https://www.zotero.org/settings/keys)** under **“Your userID for use in API calls”** (not under Account)
5. Set `library_type` to `"user"` for My Library (default)
6. Optional `collection_key`: collection URL contains `/collections/XXXX` — use `XXXX`

Check setup:

```bash
python zotero_sync.py --show-id
```

Zotero desktop does not need to be open (uses web API).

## Usage

```bash
python zotero_sync.py
```

Or from **review_runner.py** → option `5`.

Updates `Zotero_key` when empty; fills `Notes` when empty (or overwrite if you choose `y`).

## Workflow

1. Import RIS into Zotero, add notes and PDFs there  
2. Run `extraction_templ.py` → Excel templates  
3. Run `zotero_sync.py` → fill keys and notes from Zotero  
4. Continue editing in Excel or in Zotero (re-run sync after major Zotero updates)  
5. Export `.bib` from Zotero for Quarto citations (separate step)
