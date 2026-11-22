# Tools for Systematic Review (WoS & Scopus)

Python scripts for the PRISMA pipeline. Shared path resolution: `project_paths.py` (project root = parent of `70_scripts/`).

## Layout

| Folder / file | Role |
|---------------|------|
| `runner/` | GUI (`run_review.bat`) — preferred. No separate Zenodo DOI; archived with this folder |
| `review_runner.py` | Text menu — same pipeline steps |
| `original_run.py` | `backup` / `compare` / `restore` against `99_backup/original_run/` |
| `requirements.txt` | `pandas`, `openpyxl`, `pyzotero` |
| `project_paths.py` | `PROJECT_ROOT` for all scripts |
| **`pipeline/`** | Core workflow (steps 1–4) |
| **`zotero/`** | Zotero API sync into extraction Excel |
| **`auxiliary/`** | Optional tools (VOSviewer, JSON export, template) |

### `pipeline/` — core workflow

| Script | Doc |
|--------|-----|
| `WoS_Scopus_query.py` | [WoS_Scopus_query_info.md](pipeline/WoS_Scopus_query_info.md) |
| `merge_and_classify.py` | [merge_and_clssify_info.md](pipeline/merge_and_clssify_info.md) |
| `screening_and_deep_classify.py` | [screening_and_deep_classify_info.md](pipeline/screening_and_deep_classify_info.md) |
| `extraction_templ.py` | [extraction_templ_info.md](pipeline/extraction_templ_info.md) |

### `zotero/`

| File | Role |
|------|------|
| `zotero_sync.py` | Fill `Zotero_key` + `Notes` in Excel |
| `zotero_config.example.json` | Copy → `zotero_config.json` (gitignored) |
| [zotero_sync_info.md](zotero/zotero_sync_info.md) | Setup and usage |

### `auxiliary/` — optional

| Script | Output |
|--------|--------|
| `VOSviewer.py` | `40_extraction/43_vosviewer/*.csv` |
| `ris_to_json.py` | `40_extraction/43_json/vosviewer_map.json` |
| `+sablona.py` | Script template for new tools |

## Quick start

**Review runner (recommended):** double-click `run_review.bat` in the project root, or `70_scripts/run_review.bat`. One step at a time; that step’s files are overwritten; the main product is a PRISMA-P protocol. Details: [runner/README.md](runner/README.md).

Text menu (same scripts):

```bash
cd 70_scripts
pip install -r requirements.txt
python review_runner.py
```

Or run a single step:

```bash
python pipeline/merge_and_classify.py
python zotero/zotero_sync.py
python original_run.py backup
python original_run.py compare
```

## Where the pipeline writes

| Step | Writes to | Read by the manuscript from |
|------|-----------|-----------------------------|
| 2 merge | `20_data_clean/21_audit/` | `_pipeline-stats.qmd` → Abstract, Study Selection, OR 5 |
| 3 screening | `30_screening/33_reports/`, `32_exports/`, `35_VOS-ris/` | `_pipeline-stats.qmd` → Abstract, Study Selection, OR 6–7 |
| 4 templates | `40_extraction/41_input/` | not in the article text |

Do not write icons or the PRISMA PNG from these scripts. Icons: `80_figures/81_icons/`. Figure 2: `60_prisma/` ([redraw assignment](../60_prisma/PRISMA_diagram_zadani.md)). Finished Word/HTML: `50_outputs/` after `90_review/_publish_outputs.py`.

## PRISMAtools (GitHub)

General-purpose copies of these scripts live in [PRISMAtools](https://github.com/LenkaMikova/PRISMAtools). After structural changes here, sync that repo if you use it across projects.

## License and archive

MIT — see [LICENSE](https://github.com/LenkaMikova/PRISMAtools/blob/main/LICENSE).
Software deposit: [10.5281/zenodo.24362240](https://doi.org/10.5281/zenodo.24362240) (`@MikovaCode2026`). GitHub is the live copy; Zenodo should point at a tag. All three live DOI: root `README.md`.
