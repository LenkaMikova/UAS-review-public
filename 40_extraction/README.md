# Data Extraction

This folder contains materials related to the data extraction stage of the systematic review.

## Structure

- **41_input/**
  - `extraction_input_full.xlsx` — *include* + *maybe* records (973 = 249 + 724)
  - `extraction_input_refined.xlsx` — *include* only, prioritized (`Priority == HIGH` = 48 must-cite). Columns `Scaling_type` and `Scaling_source`
  - `batches/batch_N.xlsx` — subsets (~50 records) for manual work

- **42_working/**
  - `extraction_filled.xlsx` *(you create)* — copy from refined template, fill during full-text review

- **42_reviews/**
  - Copy of review-article records (if present)

- **43_vosviewer/** — CSV exports from `VOSviewer.py` (optional; Figure 4 itself is `80_figures/82_VOSviewer/VOS_must-cite.png`)

- **43_json/** *(created by script if run)*
  - `vosviewer_map.json` — from `ris_to_json.py`

- **43_final/** *(you create when done — not on disk yet)*
  - `extraction_final.xlsx` — final dataset after full-text inclusion

## Scaling_type (HIGH / must-cite)

Copied from screening `scaling` when the title, abstract, or keywords contained `downscaling`, `data fusion`, or `multi-scale`.

| | n (of 48 HIGH) |
|---|---:|
| **automaticky** (`Scaling_source`) | 22 |
| **ručně** | 26 |
| of which still `none` | 23 |
| recoded from abstract | 3 (Guo 2022, Senyurek 2022 → data fusion; He 2025 → multi-scale) |

Current `Scaling_type` bars in Figure 5: 18 data fusion, 3 downscaling, 4 multi-scale, 23 none.

- Column `Scaling_source` sits next to `Scaling_type` in `extraction_input_refined.xlsx` and in `30_screening/32_exports/must_cite_list.xlsx`
- Recode the remaining 23 in `30_screening/32_exports/HIGH_Scaling_none_with_abstracts.xlsx` (one tick: data fusion / downscaling / multi-scale / **one source** / **ostatní**). *one source* = one platform/sensor **or a comparison of two sources that is not fusion**. Copy the chosen label into `Scaling_type` here; keep `Scaling_source` = ručně. Figure 5 still uses `none` until the article body is updated.
- Printable 48 / 45 lists: `30_screening/32_exports/must_cite_list.xlsx`

## Description

Data extraction uses a semi-automated workflow: Python templates from `screened_records.xlsx`, manual full-text review, Zotero sync for keys and notes.

## Workflow

1. Input: `30_screening/31_dataset/screened_records.xlsx`
2. Run `extraction_templ.py` → templates in `41_input/`
3. Import RIS into Zotero; run `zotero_sync.py` → `42_working/extraction_filled.xlsx`
4. After full-text review → `43_final/extraction_final.xlsx` *(create the folder when needed)*
5. Export Zotero → `90_review/full_papers_review.bib` for Quarto

## Local tools

From `70_scripts/`:

```bash
python review_runner.py
python extraction_templ.py
python zotero_sync.py
```

See `70_scripts/pipeline/extraction_templ_info.md` and `42_working/README.md`.
