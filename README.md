# UAV soil-moisture systematic review — public files

Minimum set for reviewers: frozen search, screening and extraction tables, PRISMA protocol and flow, and the Python pipeline. The manuscript and figures are submitted to *Precision Agriculture*, not stored here.

| Persistent copies (Zenodo) | DOI |
|---|---|
| Dataset (search, screening, extraction) | [10.5281/zenodo.24362075](https://doi.org/10.5281/zenodo.24362075) |
| Retrospective PRISMA-P protocol | [10.5281/zenodo.24362475](https://doi.org/10.5281/zenodo.24362475) |
| Software (`70_scripts/`) | [10.5281/zenodo.24362240](https://doi.org/10.5281/zenodo.24362240) |

| Folder | Contents |
|---|---|
| `00_search/02_final/` | Frozen WoS and Scopus queries |
| `10_data_raw/12_final/` | RIS used by the merge script |
| `20_data_clean/` | Merge audit and forward list |
| `30_screening/` | Scores, must-cite lists, reports (no article PDFs) |
| `40_extraction/` | Extraction templates and working tables |
| `60_prisma/` | Flow diagram, PRISMA-P, executed protocol |
| `70_scripts/` | Pipeline and review runner |

This repository is a filtered mirror of a private working copy. Personal notes, manuscript source (`90_review/`), and figures (`80_figures/`) are not included.

Start the runner locally with `run_review.bat`.
