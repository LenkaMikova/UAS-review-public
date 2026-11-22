# Screening and Initial Classification

Outputs from `screening_and_deep_classify.py` (see `70_scripts/pipeline/screening_and_deep_classify_info.md`). Input after Audit Save: `20_data_clean/forward_records.xlsx` (`prefer_after_manual_check`). Locked counts below are the original 1 133 run until the next screening Replace.

## Structure

- **31_dataset/** — `screened_records.xlsx` (non-review records, all screening variables)
- **32_exports/** — bibliographic RIS subsets for Zotero (screening flags stay in the Excel):
  - `all_records.ris` — all screened non-review records (n = 1 018)
  - `include_records.ris` — `screening_decision == include` (n = 249)
  - `core_studies.ris` — `must_cite_strict` (n = 22)
  - `extended_studies.ris` — `must_cite` but not strict (n = 26)
  - `must_cite_records.ris` — **core ∪ extended** (n = 48). Do not merge this with `extended_studies.ris`
  - `must_cite_list.xlsx` — 48 / 45 lists (sheets `48_must_cite`, `45_unique_studies`, `HIGH_Scaling_none`) plus `must_cite_48.csv` and `must_cite_45.csv`. Column `Scaling_source`: **automaticky** (22) vs **ručně** (26 of 48; 23 of 45)
  - `HIGH_Scaling_none_with_abstracts.xlsx` — the 23 HIGH records with no keyword match. Tick **exactly one** category (`data fusion` / `downscaling` / `multi-scale` / **one source** / **ostatní**). *one source* = one platform/sensor **or a comparison of two sources that is not fusion**. *ostatní* = cannot be classified otherwise. The article figure still plots these as `none` until the body is updated. Do not re-run `_add_kategorie_ticks.py` after filling — it would wipe the ticks. Coding canvas (git copy): `90_review/99_aux/canvases/scaling-none-abstracts.canvas.tsx`
  - PDF folders (`must_cite/`, `review/`, `review_uav/`, `other/`) — downloaded full texts, not written by the screening script
- **33_reports/** — `screening_summary.txt`, `screening_summary.xlsx`, `keyword_statistics.txt`
- **34_reviews/** — `review_articles.xlsx`, `review_articles.ris`, optional `review_articles_uav.ris`
- **35_VOS-ris/** — the two files for Figure 4: `VOS_full.ris` (= all_records) and `VOS_must-cite.ris` (= must_cite_records). See that folder’s README.

## Relevance score (0–8)

| Component | Points |
|-----------|--------|
| soil moisture in text | +2 |
| direct UAV (UAV, drone, UAS) | +3 |
| scaling (downscaling, data fusion, multi-scale) | +2 |
| agricultural domain | +1 |

`uav_potential` (satellite methods with UAV potential) is tracked separately and does **not** add to the score.

## Screening decision

| Score | Decision |
|-------|----------|
| ≥ 6 | **include** |
| 3–5 | **maybe** |
| < 3 | **exclude** |

Strategy is **inclusive** (sensitivity over specificity); full-text review is required.

## Must-cite (two tiers)

- **Extended (`must_cite`):** score ≥ 6 and (direct UAV + scaling) or (potential UAV + scaling/passive sensing)
- **Strict / core (`must_cite_strict`):** score ≥ 7, direct UAV, and scaling → exported as `core_studies.ris`

## Variables added to each record

`platform`, `sensor_type`, `sensor_mode`, `application_domain`, `methodology`, `scaling`, `uav_applicability`, `uav_potential`, `uav_relevance`, `relevance_score`, `must_cite`, `must_cite_strict`, `screening_decision`, `is_review`

## Workflow role

- *include* and *maybe* → data extraction (`40_extraction/`)
- *exclude* → not carried forward
- review articles → `34_reviews/` only (background), not in extraction datasets
- final inclusion → manual, during full-text review (`Include_final` in extraction template)

The manuscript reads **this** `33_reports/screening_summary.txt`. Current counts: 115 reviews excluded → **1 018** screened → 249 / 724 / 45 (include / maybe / exclude) → 48 must-cite. Figure 2 uses these numbers but still tells a false full-text story (925 → 48); redraw: `60_prisma/PRISMA_diagram_zadani.md`.
