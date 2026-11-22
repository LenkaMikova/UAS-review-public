# Bibliographic Data Processing for Systematic Review (PRISMA)

[Python script](https://github.com/LenkaMikova/PRISMAtools/blob/main/merge_and_classify.py) for merging, cleaning, and classifying bibliographic records exported from Web of Science and Scopus.

---

## Purpose

This script supports systematic literature reviews conducted in accordance with PRISMA guidelines by ensuring:

- transparent and traceable data processing  
- reproducible workflow  
- full audit trail of all records (included and excluded)  

---

## Project layout

The script resolves paths relative to the **parent folder of the script directory** (e.g. if the script lives in `70_scripts/`, the project root is the review folder one level up).

Expected structure:

| Path | Role |
|------|------|
| `10_data_raw/12_final/export_Scopus.ris` | Scopus export |
| `10_data_raw/12_final/export_WoS.ris` | Web of Science export |
| `20_data_clean/` | Clean datasets |
| `20_data_clean/21_audit/` | Audit trail and PRISMA counts |

Place the script in a subfolder of your review project (e.g. `tools/` or `70_scripts/`), not in the repository root alone.

---

## Input Data

- `export_Scopus.ris`  
- `export_WoS.ris`  

Exported directly from Web of Science and Scopus (RIS format).

---

## Processing Workflow

1. **RIS parsing** — converts RIS files into tabular format  
2. **Dataset merging** — combines both databases  
3. **Record classification** — status labels by metadata quality and type  
4. **Duplicate detection** — DOI matching and title–year matching  
5. **Data validation** — incomplete or inconsistent records flagged  
6. **Dataset filtering** — clean dataset with `correct_record` only  
7. **Reporting** — diagnostic files and PRISMA-ready summaries  

---

## Output Files

### Main datasets

- `20_data_clean/clean_records.xlsx` / `.csv` — records with status `correct_record` (input for screening)  
- `20_data_clean/clean_records.ris` — import into Zotero or other reference managers  
- `20_data_clean/21_audit/all_records_with_status.xlsx` — full dataset with status and exclusion reasons  

### Diagnostics (manual validation)

- `20_data_clean/21_audit/duplicates_doi.xlsx`  
- `20_data_clean/21_audit/duplicates_title.xlsx`  
- `20_data_clean/21_audit/missing_doi.xlsx`  

### Reporting

- `20_data_clean/21_audit/processing_report.txt` — input counts, classification, retained/removed  
- `20_data_clean/21_audit/prisma_counts.csv` — counts by status (for PRISMA diagram)  

---

## Record Classification

Each record receives `status` and `exclusion_reason`.

| Status | Meaning |
|--------|---------|
| `correct_record` | Valid record retained for screening |
| `duplicate_doi` | Duplicate based on DOI |
| `duplicate_title` | Duplicate based on title + year |
| `missing_doi` | DOI not available (retained if otherwise valid) |
| `incomplete_record` | Missing key metadata (e.g. title or year) |
| `non_article_type` | Non-research publication (books) |

Books (`TY`: `BOOK`, `EBOOK`) are excluded at this stage with reason *Book (systematic review of primary research articles only)*, so they never enter `clean_records.xlsx`. Other publication types (e.g. conference papers, book chapters) are retained here and handled during screening.
| `outside_scope` | Optional manual classification |

---

## PRISMA Compliance

- All records preserved (no silent deletion)  
- Exclusion reasons documented  
- Reproducible, auditable workflow  
- Structured outputs for PRISMA reporting  

---

## Requirements

- Python 3.8+  
- pandas  
- openpyxl  

```bash
pip install pandas openpyxl
```
