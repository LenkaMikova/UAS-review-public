# Raw Bibliographic Data

This folder contains bibliographic records exported from Web of Science and Scopus.

## Structure

- 11_original/
  Original exports from databases with timestamps and original filenames.

- 12_final/
  Standardized copies were created by renaming files to:
  - export_Scopus.ris
  - export_WoS.ris

No content modifications were performed.

- WoS_searchHistory.xlsx
  Search history exported from Web of Science.

## Description

All records were exported in RIS format on 29 April 2026. The original files were preserved unchanged, while standardized copies were created for consistent processing.

Only the files in `12_final/` are input for `merge_and_classify.py`. The original exports stay in `11_original/` and are never overwritten.