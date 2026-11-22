# Manuscript structure

Living map of `../review.qmd` and `../92_appendix/_online-resources.qmd`.
Update this file whenever a table, figure, or Online Resource is added, removed, or moved.
Recount body/appendix rows with `python 90_review/99_aux/_count_table_studies.py`.

Cursor canvas (same content, interactive): open beside chat —
`canvases/manuscript-structure.canvas.tsx`. Git copy: `99_aux/canvases/`.

**Last synced:** 22 November 2026 (checklist před odesláním: PRISMA + časopis; osobní md v `99_temp/`)

| | |
|---|---|
| Body tables | 12 |
| Body figures | 6 (`fig-history`, `fig-prismadig`, `fig-workflow`, `fig-VOS-must`, `fig-distribution`, `fig-conclusion`) |
| Online Resources | 19 |
| Studies in OR 9–11 | 46 unique (must-cite flag = 49 records) |
| Hand-written numbers | none for Table/Figure/OR labels. Pipeline counts: `{r} stats_r['…']` from `_pipeline-stats.qmd` (`merged`, `removed`, `retained`, `duplicate_doi`, `duplicate_title`, `n_duplicates`, `missing_doi`, `books`, `lock_extra`, `other_exclusions`, `prisma_ta_excluded`, `reviews`, `non_review`, `include_n` / `maybe_n` / `exclude_n`, `must_cite`, `must_cite_strict`, `extended`, `n_studies`, `n_leftover`, `n_uav_campaigns`). Figure 2 PNG is the Haddaway web-app export; do not Make PNG in the runner. Figure 3 is still drawn. |

`or-studies` is **not used**. The 46 studies already have rows in OR 9–11 (`or-inputs`, `or-applications`, `or-methods`).

Figure 1 and Figure 6 live in `80_figures/83_others/` (`fig-history.png`, `fig-conclusion.png`). Icons stay in `81_icons/`. VOSviewer stays in `82_VOSviewer/`. PRISMA / workflow stay in `60_prisma/`.

Numbering follows first `@or-*` in `review.qmd`. Table 1 caption cites `@or-reviews` then `@or-icons` (OR 1–2). `@or-prisma-check` is OR 4 (Methods, before Figure 2). `@or-prisma-flow` is OR 6 (Figure 2 caption). Retrospective protocol: `60_prisma/protocol/`. Three Zenodo records (`99_aux/zenodo/`): protocol, dataset (screening/extraction + copy of OR), software. OR 1–19 = journal SI. Pre-submission: `99_aux/pre-submission-checklist.md`.

## 49 must-cite ≠ 46 unique studies

| | n |
|---|---:|
| Unique studies in OR 9–11 | 46 |
| Publisher correction to Hussain 2025 (same article, second RIS) | 1 |
| Surendran 2024 book chapter | 1 |
| Montzka 2020 conference (SARSense; no operational SM retrieval) | 1 |
| **must-cite flag** | **49** |

OR 2 is a **selected** subset of the 115 reviews identified at processing, not the complete set.

## What you write vs. what prints

| You write | You cite | Quarto prints |
|---|---|---|
| `{#tbl-sensors}` on a caption | `@tbl-sensors` | Table 5 |
| `{#fig-history}` on an image | `@fig-history` | Figure 1 |
| `::: {#or-sensors}` in the appendix | `@or-sensors` | Online Resource 15 |
| `::: {#or-uav-param}` in the appendix | `@or-uav-param` | Online Resource 16 |
| `::: {#or-metadata}` in the appendix | `@or-metadata` | Online Resource 18 |

The Online Resource number is the position of the `::: {#or-*}` div in
`_online-resources.qmd`. That order must match the order of first mention in
`review.qmd`.

## Chapters → tables → figures → Online Resources

**Rows (short)** = body table. **Rows (long)** = matching Online Resource.

| Chapter | Subsection | Body | Rows (short) | Appendix | Rows (long) | Source type |
|---|---|---|---:|---|---:|---|
| Introduction | Historical Progress | Table 1 `tbl-history`, Figure 1 `fig-history` | 5 | OR 1 `or-reviews`, OR 2 `or-icons` (Table 1 caption, that order) | — | category + **review** |
| Introduction | Existing reviews and Research Gap | — | — | OR 1 `or-reviews` (already cited) | 30 | **review** (29 published + this review) |
| Introduction | Existing reviews and Research Gap | Table 2 `tbl-review-category` | 3 | — | — | **review** |
| Introduction | Existing reviews and Research Gap | Table 3 `tbl-review-sm` | 3 | OR 3 `or-fusion` | 7 | **review** |
| Review Methodology | (chapter lead) | Figure 2 `fig-prismadig` | — | OR 4 `or-prisma-check`, OR 5 `or-processing`, OR 6 `or-prisma-flow` | — | pipeline + PRISMA 2020 checklist + how the diagram was produced |
| Review Methodology | Data Selection | — | — | OR 7 `or-search` | — | pipeline |
| Review Methodology | Data Workflow | Figure 3 `fig-workflow` | — | — | — | pipeline |
| Review Methodology | Dataset Overview | Figure 4 `fig-VOS-must`, Figure 5 `fig-distribution` | — | OR 8 `or-keywords`, OR 9–11 studies, OR 12 `or-screening` | 46 | pipeline + **must-cite** |
| Trends 2019–2026 | (chapter lead) | — | — | OR 13 `or-uav` (first mention, with OR 9–11) | 10 | **must-cite** UAV campaigns |
| Trends 2019–2026 | Type of Platforms | Table 4 `tbl-platforms` | 5 | OR 14 `or-platforms` | 5 | category; representative **must-cite** |
| Trends 2019–2026 | Type of Sensors | Table 5 `tbl-sensors` | 5 | OR 15 `or-sensors` | 5 | category; representative **must-cite** |
| Trends 2019–2026 | Drone studies | Table 6 `tbl-uav` | 4 | OR 13 `or-uav` (already cited) | 10 | **must-cite** UAV campaigns (10 of 46) |
| Trends 2019–2026 | Drone studies | Table 7 `tbl-uav-param` | 12 | OR 16 `or-uav-param` | 46 | **must-cite** ASPRS 2024 completeness |
| Trends 2019–2026 | Drone studies | Table 8 `tbl-uav-param-core` | 25 | OR 17 `or-uav-param-core` | 22 | **must-cite** Layer 1 items (25); OR table currently 22 of 46 studies |
| Trends 2019–2026 | Inputs | Table 9 `tbl-inputs` | 6 | OR 9 `or-inputs` | 46 | **must-cite** per-study |
| Trends 2019–2026 | Applications | Table 10 `tbl-applications` | 4 | OR 10 `or-applications` | 46 | **must-cite** per-study |
| Trends 2019–2026 | Methods | Table 11 `tbl-methods` | 4 | OR 11 `or-methods` | 46 | **must-cite** per-study |
| Trends 2019–2026 | Conclusions, Limitations and Perspectives | Table 12 `tbl-conclusion`, Figure 6 `fig-conclusion` | 4 | — | — | category (four periods) |
| Conclusion | (chapter) | — | — | OR 18 `or-metadata`, OR 19 `or-metadata-SM` | 25 + SM module | Layer 1 paper checklist (25) + SM application module |

Discussion now has draft paragraphs (Major Findings, Limitations, Future Directions, Operational Applicability). Abstract YAML is still *Insert abstract here*.

## Appendix order = numbering

| # | Label | Content |
|---|---|---|
| OR 1 | `or-reviews` | Selected existing review articles (30) |
| OR 2 | `or-icons` | Icon legend — both plates |
| OR 3 | `or-fusion` | Platform combinations and data fusion (7) |
| OR 4 | `or-prisma-check` | PRISMA 2020 checklist |
| OR 5 | `or-processing` | Record counts + merge / deduplication log |
| OR 6 | `or-prisma-flow` | How the PRISMA flow diagram was produced (Haddaway web app <https://estech.shinyapps.io/prisma_flowdiagram/>; `PRISMA_flow_how.md`) |
| OR 7 | `or-search` | Frozen search strings (WoS, Scopus) |
| OR 8 | `or-keywords` | Keyword frequency statistics |
| OR 9 | `or-inputs` | Input data per study (46) |
| OR 10 | `or-applications` | Application environments per study (46) |
| OR 11 | `or-methods` | Methods and accuracies per study (46) |
| OR 12 | `or-screening` | Automated screening summary |
| OR 13 | `or-uav` | Flight parameters of individual campaigns (10) |
| OR 14 | `or-platforms` | Platform categories (5) |
| OR 15 | `or-sensors` | Sensor modalities (5) |
| OR 16 | `or-uav-param` | ASPRS 2024 positional / photogrammetric completeness (46) |
| OR 17 | `or-uav-param-core` | Core / mandatory UAV + SM retrieval parameters (**22 rows now**; intended 46) |
| OR 18 | `or-metadata` | Paper reporting checklist, Layer 1 (25 UAV campaign items) |
| OR 19 | `or-metadata-SM` | Soil-moisture application module (Mandatory = paper; Q/F kept until cut) |

Each Online Resource is `92_appendix/or-NN-<id>.qmd`. `_online-resources.qmd` is the include list. `review.qmd` includes captions only (`_online-resources-list.qmd`). After editing a caption, run `python 90_review/_build_or_list.py`.

## Open items that affect this map

- Figure 2 is `PRISMA_diagram.png` (`fig-prismadig`), Haddaway web app, `@PRISMAfd2022`. Counts close (46/46). Do not overwrite with runner Make PNG (that still uses screened 1031 / other 3).
- Front matter in `review.qmd`: Highlights (4 bullets), Impact (2 sentences), Abstract as Purpose / Methods / Results / Conclusion (live `stats_r`). YAML abstract is the same skeleton without counts — Word may print it twice. Discussion / Conclusion still wait for new numbers.
- Online Resources render: html, docx, **pdf** (`quarto render online-resources.qmd --to pdf`).
- Figures/icons: Napkin/ChatGPT still in Fig. 1–3 and `81_icons/`; replace before submission (`99_aux/pre-submission-checklist.md` §7).
- Printed OR 18 is the 25-item Layer 1 checklist. Full OpenSkyLab matrix is in `99_aux/or-metadata-full.md`. Fillable HTML: `99_aux/opensky-sm-checklist.html`.
- Drone-studies: \(N \ge 30\) is not a paper failure unless a map accuracy class is claimed. Metadata lead: ASPRS is a geodetic citation; scoring is the 25 Layer 1 items.
- Cite keys `@ASPRS2024` and `@Dopper2022` (no umlaut) match `full_papers_review.bib`.
- All 116 printed cite keys in `review.qmd` + appendix match `full_papers_review.bib` (21 Oct 2026).
- `or-uav-param-core` (OR 17) currently lists 22 studies, not 46. Caption was repaired after a paste into the last table cell. `@Guo2026` is extended, so it stays out of OR 17.
- `@or-icons` is cited in the Table 1 caption.
- Methodology vs files: `99_temp/methodology-vs-pipeline.md` (local only). Retrospective protocol: `60_prisma/protocol/`. Three Zenodo records: protocol, dataset (plus copy of OR), software. Journal SI is separate (`99_aux/pre-submission-checklist.md`).
- `fig-distribution` still plots `none`. Coding sheet: `30_screening/32_exports/HIGH_Scaling_none_with_abstracts.xlsx`.
- `or-uav` (OR 13) is 10 campaigns. First mentioned in the Trends chapter lead, before `@or-platforms`.
- `workflow.png` (Figure 3) is dark. There is no `workflow2.png` on disk.
