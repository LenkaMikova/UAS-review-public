# Processed Bibliographic Data

This folder contains cleaned and classified bibliographic records used for screening and analysis. Processing was performed in Python 3.13 using pandas library.

## Structure

- clean_records.xlsx
  Filtered dataset containing records classified as valid (correct_record). This dataset was used for screening.

The status "correct_record" indicates records that:
- contain valid title and publication year
- are not books (`TY`: `BOOK`, `EBOOK` only — book **chapters** stay)
- are not duplicates based on DOI or title-year matching

Missing DOI is **not** an automatic exclusion. `missing_doi.xlsx` is the Assign DOI queue; after Audit Save, screening reads `forward_records.xlsx` (kept copies, including no-DOI when forwarded). Conference papers stay.

Books are excluded during audit (`non_article_type`) because this systematic review synthesizes primary research articles only. Other non-article publication types (e.g. conference papers, book chapters) are retained here and handled during screening.

- 21_audit/
  Complete dataset with classification results and diagnostic outputs:
  - all_records_with_status.xlsx → full dataset with status and exclusion reasons
  - duplicates_doi.xlsx → records with duplicate DOI
  - duplicates_title.xlsx → records with duplicate title and year
  - missing_doi.xlsx → records with missing DOI

## Description

Bibliographic records were processed using a custom Python script. Each record was classified based on metadata completeness, publication type, and duplication.

All records, including excluded ones, were preserved to ensure full transparency and reproducibility. The audit trail enables verification of all filtering and classification steps.

The manuscript reads **this** `21_audit/processing_report.txt`, not the optional copy in `60_prisma/`. Locked original run (`99_backup/original_run/`): 1 636 merged → 503 removed → **1 133** retained. After the next Audit, `removed` should be duplicates + books only (no missing-DOI drop). Figure 2 identification counts still use the lock until redraw (`60_prisma/PRISMA_diagram_zadani.md`). Dataset DOI: [10.5281/zenodo.24362075](https://doi.org/10.5281/zenodo.24362075).

Also in `21_audit/`: `processing_report.txt`, `prisma_counts.csv` (copied to `60_prisma/` only for drawing the diagram — Quarto does not read those copies).