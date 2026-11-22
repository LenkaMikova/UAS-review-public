# Manuscript (Quarto / Elsevier)

Quarto project for the systematic review manuscript.

**What lives here vs. elsewhere**

| Here (`90_review/`) | Elsewhere |
|---|---|
| Source: `.qmd`, `full_papers_review.bib`, filters | Finished Word/HTML/PDF → `../50_outputs/` |
| Appendix source → `92_appendix/` | Icons + Figure 1 + VOSviewer → `../80_figures/` |
| Helpers / drafts / maps → `99_aux/` | PRISMA → `../60_prisma/`; pipeline counts → `../20_data_clean/`, `../30_screening/` |
| Cite keys `@MikovaProtocol2026`, `@MikovaData2026`, `@MikovaCode2026` | Zenodo DOI — table in the [root README](../README.md) |

All images used by the manuscript except PRISMA/workflow are in `../80_figures/`
(`81_icons/`, `82_VOSviewer/`). The two RIS files that feed the VOSviewer maps
are `../30_screening/35_VOS-ris/` (`VOS_full.ris`, `VOS_must-cite.ris`).

## Open in RStudio / Quarto

Open **`review.Rproj`** in this folder — the manuscript project root.

## Structure

| Path | Purpose |
|------|---------|
| `review.qmd` | Main manuscript: body text + short tables + the list of Online Resource captions. |
| `92_appendix/or-01-*.qmd` … `or-19-*.qmd` | **One Online Resource per file.** Included in order by `_online-resources.qmd`. |
| `92_appendix/_online-resources-list.qmd` | Captions only — **generated**, included by `review.qmd`. See "Where the appendix lives". |
| `online-resources.qmd` | Standalone render of the appendix (submitted as a separate file, A4 landscape). |
| `_pipeline-stats.qmd` | Shared Python setup that loads the pipeline numbers. Included by both documents. |
| **`99_aux/`** | Helpers only: living maps, **pipeline I/O table**, canvases (git copies), chapter drafts, unused figure scripts. Not rendered. See `99_aux/README.md`. |
| _make_sensor_icons.py | Regenerates the generic sensor icons from the drone payloads. |
| _publish_outputs.py | Copies the last render into ../50_outputs/ (the files you send). |
| `_make_landscape_reference.py`, `_reference-landscape.docx` | Page setup for the appendix DOCX. |
| `review.Rproj` | RStudio project |
| `full_papers_review.bib` | Active bibliography (Zotero export) |
| `elsevier-harvard.csl` | Citation style |
| `review.html`, `review.docx` | Last render — working copies, **gitignored**. Official copies: `../50_outputs/` |
| `online-resources.html`, `online-resources.docx`, `online-resources.pdf` | Same for the appendix (PDF = Springer SI) |
| `_filters/linebreaks.lua` | Makes `<br>` inside table cells work in DOCX as well as HTML |
| **`91_tables/`** | Draft or exported tables *(as needed)* |
| `_extensions/quarto-journals/elsevier/` | Elsevier Quarto format |
| `style-guide/` | Elsevier author documentation |
| `review_files/` | Render output assets (regenerated on `quarto render`) |

## Render

```bash
quarto render review.qmd --to html      # manuscript (captions of the resources only)
quarto render review.qmd --to docx
quarto render online-resources.qmd --to html
quarto render online-resources.qmd --to docx
quarto render online-resources.qmd --to pdf   # Springer SI (landscape A4)
python _verify_icons.py                 # check numbering + icons in HTML *and* DOCX
python _publish_outputs.py              # copy Word/HTML/PDF into ../50_outputs/
```

- Pipeline data is in the **parent** folder. `_pipeline-stats.qmd` finds it by walking
  up from the working directory until it sees `20_data_clean/`, so the render works
  from anywhere. Do not replace this with `QUARTO_PROJECT_ROOT`: there is no
  `_quarto.yml`, so Quarto sets that variable to `90_review/` and nothing is found.
- The counts are read **only** from where the pipeline scripts write them:

  | Report | Written by |
  |---|---|
  | `20_data_clean/21_audit/processing_report.txt` | `merge_and_classify.py` |
  | `30_screening/33_reports/screening_summary.txt` | `screening_and_deep_classify.py` |
  | `30_screening/33_reports/keyword_statistics.txt` | `screening_and_deep_classify.py` |
  | `00_search/02_final/final_query.txt` | `WoS_Scopus_query.py` (frozen search) |

  `60_prisma/` holds **hand-made copies** for the flow diagram (see its README).
  Never read those from the manuscript — that is how the Abstract ended up quoting
  April numbers (1136 retained) months after the pipeline produced 1133.
- A missing export or an unmatched pattern now **raises**, and the render fails with
  the offending file and pattern named. It used to default to `0`, which is how a
  whole zeroed Results section passed unnoticed. `_pipeline-stats.qmd` also checks
  that `reviews + non-review == retained`, so two reports from different pipeline
  runs cannot be quoted against each other.
- Paths to images inside `92_appendix/_online-resources.qmd` are relative to
  **this** folder (`../80_figures/81_icons/...`), not to `92_appendix/`.
- The Python chunks use the standard library only (no `pandas`, no `tabulate`),
  so the render also works in a minimal `reticulate` environment.

---

# Numbering rules — read this before adding a table or a resource

## Never write a number by hand

There is **no hard-coded number anywhere** in the manuscript. Tables, figures, and
Online Resources are all numbered by Quarto at render time, in order of appearance.
You always write a *label*, and Quarto turns it into "Table 4", "Figure 1", or
"Online Resource 9".

| You write | Quarto prints |
|---|---|
| `{#tbl-sensors}` on a caption, `@tbl-sensors` in text | Table 5 |
| `{#fig-history}` on an image, `@fig-history` in text | Figure 1 |
| `::: {#or-sensors}` in the appendix, `@or-sensors` in text | Online Resource 15 |

If you add, remove, or move something, **everything renumbers itself on the next
render.** Nothing to update by hand, nothing to get out of sync.

## Where the appendix lives

The manuscript must not carry the full appendix — it is submitted as its own file.
But Quarto only resolves `@or-...` against float divs in the **same** document, so
simply dropping the appendix from `review.qmd` turns every reference into
`?@or-icons`.

So the appendix exists in two shapes, both generated from one source:

| Document | Includes | Contains |
|---|---|---|
| `review.qmd` | `_online-resources-list.qmd` | the 19 caption-only divs — this is what gives the references their numbers |
| `online-resources.qmd` | `_online-resources.qmd` (includes `or-01-` … `or-19-`) | the resources themselves |

Both documents therefore number the resources identically. After editing a caption
in the matching `or-NN-*.qmd`, regenerate the list:

```bash
python _build_or_list.py
```

`_verify_icons.py` fails if the two drift apart, so a forgotten regeneration cannot
reach a render unnoticed.

## Non-breaking spaces

Write `&nbsp;`. Pandoc turns it into a real non-breaking space in **both** HTML and
DOCX, so `36&nbsp;000 m` never breaks across a line. A literal typed NBSP works too
but is invisible in the source, which makes it easy to destroy while editing.

## How Online Resource numbers are decided

The number of an Online Resource comes from **its position in
`92_appendix/_online-resources.qmd`** — first div is Online Resource 1, second is 2,
and so on.

Journals require resources to be numbered in the order they are first mentioned in
the text. So the single rule to follow is:

> **The order of the divs in `_online-resources.qmd` must match the order in which
> the resources are first mentioned in `review.qmd`.**

That order is currently first `@or-*` in `review.qmd` (see the map below). Rebuild files with `python 90_review/99_aux/_reorder_or_by_first_mention.py` then `_build_or_list.py`.

### Adding a new Online Resource

1. Decide where in the body text it will first be mentioned.
2. Insert the div at the matching position in `92_appendix/_online-resources.qmd`:

```markdown
::: {#or-mytopic}
| A | B |
|---|---|
| 1 | 2 |

Caption of the new resource.
:::
```

3. Cite it in the body as `@or-mytopic`.
4. Re-render. Everything after it shifts by one automatically.

The last paragraph inside the div is the caption. Footnotes such as
`\* Conference paper.` go **after** the closing `:::`, not inside it.

## Short table in the body ↔ full table in the appendix

The manuscript uses one consistent pattern: a **short, synthesized table in the body**
and, where needed, **one full table per topic in the appendix**. The naming mirrors
that pairing:

- body table → `#tbl-<topic>`
- matching appendix resource → `#or-<topic>`

So `@tbl-sensors` (body) and `@or-sensors` (appendix) are always the same topic. The
body caption must end with a pointer to the full version, e.g.
*"The complete classification … is given in @or-sensors."*

---

# Manuscript map (summary)

Canonical copies (update these, not only this README):

- [`99_aux/manuscript-structure.md`](99_aux/manuscript-structure.md) — chapters, tables, figures, Online Resources, row counts
- [`99_aux/text-quality-review.md`](99_aux/text-quality-review.md) — what to cut, move, keep, or still write

Keep this in sync with `review.qmd` and `92_appendix/_online-resources.qmd`.
Row counts are **data rows** (not the header). Recount with
`python 99_aux/_count_table_studies.py` after adding or deleting rows.

| | |
|---|---|
| Body tables | 12 |
| Body figures | 6 (`fig-history`, `fig-prismadig`, `fig-workflow`, `fig-VOS-must`, `fig-distribution`, `fig-conclusion`) |
| Online Resources | 19 |
| Hand-written numbers | none — always cite the label |

**Source type** in the tables below:

- **review** — existing review articles (background / research gap), not the
  primary synthesis set
- **must-cite** — primary studies flagged `must_cite` in the pipeline (48
  records: 22 core + 26 extended). Per-study appendix tables use this set
  (45 rows; two extra rows are reviews marked ‡)
- **category** — one row per class (platform, sensor, land cover, method),
  not one row per study; citations are representative
- **pipeline** — counts/logs, not literature rows

## Current chapter outline

| Chapter | Subsections (now) |
|---|---|
| Highlights | 3–5 bullets (Precision Agriculture template) — counts after runner |
| Impact | 1–2 sentences on fit to the journal |
| Abstract | Purpose / Methods / Results / Conclusion — **finish last** |
| Introduction | Importance of Soil Moisture; Historical Progress; Existing reviews and Research Gap; Aim and Scope this Review |
| Review Methodology | Data Selection; Data Workflow; Dataset Overview *(Characteristic of Selected Studies is gone)* |
| Trends 2019–2026 | Type of Platforms; Type of Sensors (+ Drone studies, incl. ASPRS + core-param tables); Applications and Methods; Conclusions, Limitations and Perspectives (`tbl-conclusion`, `fig-conclusion`) |
| Discussion | Major Findings; Current Limitations; Future Research Directions; Operational Applicability — **drafts in the body** |
| Conclusion | Opening + `@or-metadata` / `@or-metadata-SM`; Limitations of Review. Three-layer rewrite is in HTML comments only. |
| Acknowledgments | AI disclosure |
| Statements and Declarations | Funding, Competing Interests, CRediT, Data Availability |
| References | |
| Online Resources | Caption list only |

## Map: chapters → tables → figures → Online Resources

"OR" numbers are what the current render produces — cite the label, not the number.
**Rows (short)** = body table. **Rows (long)** = matching Online Resource.

| Chapter | Subsection | Body | Rows (short) | Appendix | Rows (long) | Source type |
|---|---|---|---:|---|---:|---|
| Introduction | Historical Progress | Table 1 `tbl-history`, Figure 1 `fig-history` | 5 | OR 1 `or-reviews`, OR 2 `or-icons` | — | category + **review** |
| Introduction | Existing reviews and Research Gap | — | — | OR 1 `or-reviews` (already cited) | 30 | **review** (29 published reviews + this review) |
| Introduction | Existing reviews and Research Gap | Table 2 `tbl-review-category` | 3 | — | — | **review** (7 unique reviews) |
| Introduction | Existing reviews and Research Gap | Table 3 `tbl-review-sm` | 3 | OR 3 `or-fusion` | 7 | **review** (representative existing reviews, 13 unique in OR 3) |
| Review Methodology | (chapter lead) | Figure 2 `fig-prismadig` | — | OR 4 `or-prisma-check`, OR 5 `or-processing`, OR 6 `or-prisma-flow` | — | pipeline |
| Review Methodology | Data Selection | — | — | OR 7 `or-search` | — | pipeline (search strings) |
| Review Methodology | Data Workflow | Figure 3 `fig-workflow` | — | — | — | pipeline |
| Review Methodology | Dataset Overview | Figure 4 `fig-VOS-must`, Figure 5 `fig-distribution` | — | OR 8 `or-keywords`, OR 9–11, OR 12 `or-screening` | 45 | pipeline + **must-cite** |
| Trends 2019–2026 | Type of Platforms | Table 4 `tbl-platforms` | 5 | OR 14 `or-platforms` | 5 | category; representative **must-cite** |
| Trends 2019–2026 | Type of Sensors | Table 5 `tbl-sensors` | 5 | OR 15 `or-sensors` | 5 | category; representative **must-cite** |
| Trends 2019–2026 | Drone studies | Table 6 `tbl-uav` | 4 | OR 13 `or-uav` | 9 | **must-cite** UAV campaigns (9 of the 45) |
| Trends 2019–2026 | Drone studies | Table 7 `tbl-uav-param` | 12 | OR 16 `or-uav-param` | 45 | **must-cite** ASPRS 2024 completeness |
| Trends 2019–2026 | Drone studies | Table 8 `tbl-uav-param-core` | 25 | OR 17 `or-uav-param-core` | 22 | **must-cite** Layer 1 (25 items); OR table 22 of 45 studies |
| Trends 2019–2026 | Inputs | Table 9 `tbl-inputs` | 6 | OR 9 `or-inputs` | 45 | **must-cite** per-study (same 45 as OR 10–11) |
| Trends 2019–2026 | Applications | Table 10 `tbl-applications` | 4 | OR 10 `or-applications` | 45 | **must-cite** per-study (same 45) |
| Trends 2019–2026 | Methods | Table 11 `tbl-methods` | 4 | OR 11 `or-methods` | 45 | **must-cite** per-study (same 45; RMSE/R²) |
| Trends 2019–2026 | Conclusions, Limitations and Perspectives | Table 12 `tbl-conclusion`, Figure 6 `fig-conclusion` | 4 | — | — | category (four periods) |
| Conclusion | (chapter) | — | — | OR 18 `or-metadata`, OR 19 `or-metadata-SM` | 25 + SM module | Layer 1 paper checklist + SM module |

The **45** rows in OR 9–11 are one synthesis corpus (not 45 × 3 studies).
Pipeline must-cite = **48 records**, not 48 unique papers:

| | n |
|---|---:|
| Unique studies in OR 9–11 | 45 |
| Publisher correction to Hussain 2025 (same article, second RIS record) | 1 |
| Surendran 2024 book chapter (*Remote Sensing in Precision Agriculture*) | 1 |
| Montzka 2020 conference (SARSense / ROSE-L rehearsal, no operational SM retrieval) | 1 |
| **must-cite flag** | **48** |

These two omitted items are not the three books removed at audit. `@Capolupo2026`
and `@Chavez2020` are inside the 45 and are marked ‡ as review/meta rows.
`@Dopper2022` is must-cite (Döpper in the RIS). OR 13 is a **9-row subset** of
UAV flights, not a second corpus.

Figure 5 (`fig-distribution`) is the same 48 HIGH records by year × `Scaling_type`.
**22** were tagged automatically (phrases *data fusion* / *downscaling* / *multi-scale*
in title, abstract, or keywords); **26** were assigned manually (`Scaling_source` in
`../40_extraction/41_input/extraction_input_refined.xlsx` and
`../30_screening/32_exports/must_cite_list.xlsx`). Current bars: 18 data fusion,
3 downscaling, 4 multi-scale, 23 none. Three of the 26 were recoded from the
abstract (Guo 2022, Senyurek 2022 → data fusion; He 2025 → multi-scale). Recode
the remaining 23 in `../30_screening/32_exports/HIGH_Scaling_none_with_abstracts.xlsx`
(one tick: data fusion / downscaling / multi-scale / **one source** / **ostatní**;
coding canvas git copy: `99_aux/canvases/scaling-none-abstracts.canvas.tsx`).
(one tick: data fusion / downscaling / multi-scale / **one source** / **ostatní**).
*one source* = one platform/sensor, **or a comparison of two sources that is not fusion**.
*ostatní* = cannot be classified otherwise. The figure still plots these as `none`. Counts sit in an HTML
comment in `review.qmd`, not in the printed body, until they are explicitly requested.

`or-studies` was dropped: the 45 studies are already in OR 9–11. Empty
placeholder would only duplicate them.

## Appendix order = numbering

The manuscript does not carry the full tables. `review.qmd` includes only the
caption list (`92_appendix/_online-resources-list.qmd`, generated by
`_build_or_list.py`). The tables themselves are in `online-resources.qmd`,
rendered A4 landscape. Both documents number the resources identically.

| # | Label | Content |
|---|---|---|
| OR 1 | `or-reviews` | Comparison of existing review articles |
| OR 2 | `or-icons` | Icon legend — both plates |
| OR 3 | `or-fusion` | Platform combinations and data fusion |
| OR 4 | `or-prisma-check` | PRISMA 2020 checklist |
| OR 5 | `or-processing` | Record counts + merge / deduplication log |
| OR 6 | `or-prisma-flow` | How the PRISMA flow diagram was produced (`PRISMA_flow_how.md`) |
| OR 7 | `or-search` | Frozen search strings (WoS, Scopus) |
| OR 8 | `or-keywords` | Keyword frequency statistics |
| OR 9 | `or-inputs` | Input data per study (45) |
| OR 10 | `or-applications` | Application environments per study (45) |
| OR 11 | `or-methods` | Methods and accuracies per study (45) |
| OR 12 | `or-screening` | Automated screening summary |
| OR 13 | `or-uav` | Flight parameters of individual campaigns (9) |
| OR 14 | `or-platforms` | Platform categories (5 rows) |
| OR 15 | `or-sensors` | Full classification of sensor modalities |
| OR 16 | `or-uav-param` | ASPRS 2024 positional / photogrammetric completeness (45) |
| OR 17 | `or-uav-param-core` | Core / mandatory UAV + SM retrieval parameters (22 of 45) |
| OR 18 | `or-metadata` | Paper reporting checklist, Layer 1 (25 UAV campaign items) |
| OR 19 | `or-metadata-SM` | Soil-moisture application module |

---

# Icons

Two icon plates are used as a visual key across the tables:

| Plate | File | Content |
|---|---|---|
| Methods & platforms | `../80_figures/81_icons/setIcons2.png` | in-situ probe, gravimetric, CRNS, UGV-CRNS, GPR, satellite, the six UAS payloads, UGV-HS |
| Land use | `../80_figures/81_icons/setIcons1.png` | bare soil, bare, arable, arable crops, orchards, vineyards, mixed agriculture, grasslands, forest, forage, regional/global |

Both plates are shown together in **`or-icons` (OR 2)**. Table 1 cites `@or-reviews`
first, then the icon legend, so reviews is Online Resource 1.

The single thumbnails live in `../80_figures/81_icons/` as PNG. Do not keep a
second copy under `90_review/`.

A further set is **derived** from the drone payloads, so a sensor column does not
imply a UAV:

| Set | Files | Made by | Why |
|---|---|---|---|
| Generic sensors | `sensor_ms`, `sensor_rgb`, `sensor_thermal`, `sensor_hs`, `sensor_microwave`, `sensor_lidar` | `_make_sensor_icons.py`, cut from the payloads of the `drone_*` icons | The same modality also flies on satellites and rides on ground vehicles |

The circular **category badges** (`in-situ`, `sat`, `drone`, `ugv`, `lab-sampl`) are
the same files used in Table 4 / `or-platforms`. Table 1 does not have a second
`cat_*` set.

The `drone_*` (platform + payload) icons stay in **`or-platforms`**, which is the
one table that is genuinely about platforms and their payloads.

## Two rules when placing an icon in a table

**1. Use markdown image syntax, never an `<img>` tag.**

```markdown
![](../80_figures/81_icons/drone_ms.png){width=40}     <!-- yes: HTML *and* Word     -->
<img src="../80_figures/81_icons/drone_ms.png" ... />  <!-- no: silently lost in Word -->
```

Pandoc's docx writer drops raw HTML, so `<img>` icons only ever showed up in the
HTML build.

**2. Keep the widths consistent.**

| Where | Width |
|---|---|
| Table 1 `tbl-history` (round badges, visually heavier than the line art) | `{width=45}` |
| Category tables (one row per class): Tables 2–8, `or-fusion`, `or-platforms`, `or-sensors` | `{width=60}` |
| Per-study tables: `or-reviews`, `or-uav`, `or-inputs` | `{width=40}` |
| Per-study land-use icons in `or-applications` | `{width=52}` — thin line art, illegible at 40 |

Icons go at the end of the cell they describe, after a `<br>`. `<br>` is turned into
a real line break in DOCX by `_filters/linebreaks.lua`; without that filter the Word
export glues the lines together.

## Which column carries the icons

| Table | Column | Icon set |
|---|---|---|
| Table 1 `tbl-history` | Platform Paradigm | **category badges** (`in-situ`, `sat`, `drone`, `ugv`) |
| Table 2 `tbl-review-category` | Sensors used on UAV | **generic sensors** |
| Table 4 `tbl-platforms`, `or-platforms` | Platform Category | platforms (incl. `drone_*` payloads) |
| Table 5 `tbl-sensors`, `or-sensors` | Sensor Category | **generic sensors** |
| Table 6 `tbl-uav`, `or-uav` | Primary Payload / Study | **generic sensors** |
| Table 9 `tbl-inputs`, `or-inputs` | Input Modality | **generic sensors** + `satellite` |
| Table 10 `tbl-applications`, `or-applications` | Target Application | **land use** |
| `or-reviews` | Investigated Platforms | platforms |
| `or-fusion` | Platform Combinations | platforms |

`tbl-review-sm` (Table 3) and `tbl-methods` (Table 11) carry no icons on purpose:
every row of Table 3 would get the same three platform icons, and Table 9 is about
algorithms, which the icon sets do not cover.

---

# Open items

- **Figure 2 PRISMA diagram** — numbers are current (503 / 1 133), but the
  *story* is wrong: 925 excluded after full-text → 48 included. 48 is
  must-cite. Redraw from [`../60_prisma/PRISMA_diagram_zadani.md`](../60_prisma/PRISMA_diagram_zadani.md).
- **PRISMA checklist** — working fill-in:
  [`../60_prisma/PRISMA_2020_checklist_filled.md`](../60_prisma/PRISMA_2020_checklist_filled.md).
  Still copy into the official Word template before submission.
- **Abstract** — YAML `abstract:` is still *Insert abstract here*. Discussion,
  Conclusion, and Trends-conclusions now have **draft prose** in the body.
  Three-layer metadata split is in HTML comments only (`<!-- METADATA`).
  Printed OR 18 is the 25-item Layer 1 checklist; the full OpenSkyLab matrix
  is in `99_aux/or-metadata-full.md`. Fillable page:
  `99_aux/opensky-sm-checklist.html`.
- Cite keys `@ASPRS2024` and `@Dopper2022` (no umlaut) are in `full_papers_review.bib`.
- All 116 printed cite keys in `review.qmd` + appendix match `full_papers_review.bib` (21 Oct 2026). `Huang2026` is in the bib.
- **`@or-icons`** is cited in the Table 1 caption (OR 2; `@or-reviews` is OR 1).
- **`or-uav-param-core` (OR 15)** currently has 22 study rows, not 45.
- **`or-studies` dropped.** The 45 extracted studies already have rows in
  `or-inputs` / `or-applications` / `or-methods`. A fourth copy would not add
  a field those tables lack. Numbering now runs OR 1–17.
- **`or-uav` (OR 13)** is 10 campaigns. Older chapter drafts are in `99_temp/93_chapters/` (local only).
- **`workflow.png`** (Figure 3) is dark. There is no `workflow2.png` on disk.
- Two icon mismatches: `or-inputs` `@Ye2024` (manned aircraft, no icon) and
  `or-applications` `@Tauro2022` (poplar SRC with the orchard icon).
- Placeholders still in Statements: `Formal analysis: xxx`; stray `]` after
  the grant number; Holtz ORCID/address empty.
- Protocol not registered — add one sentence in Methods (PRISMA item 24).
- Output size: `review.docx` ~3 MB, `online-resources.docx` ~6.5 MB (PNG
  thumbnails).
- Chapter drafts in `99_temp/93_chapters/` still use old labels; they are not rendered.
