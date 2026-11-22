# Pipeline I/O (internal)

One table of **input → action → output** for this review. Folder READMEs stay local
(“what is in this folder”). This file is the chain.

**Copy?** = the file is the same records (or a renamed/convenience copy), not a
new analysis. Do not treat two copies as two datasets.

Canonical live sources: `90_review/review.qmd`, `90_review/full_papers_review.bib`,
`90_review/92_appendix/_online-resources.qmd`. Finished files to send: `50_outputs/`.

Recount tables: `python 90_review/99_aux/_count_table_studies.py`.

---

## Chain

| Step | Input | Copy / unchanged? | Action | Output | Used next as |
|------|--------|-------------------|--------|--------|--------------|
| 0 Search | Keywords typed in the script | — | `70_scripts/pipeline/WoS_Scopus_query.py` | `00_search/01_raw/Query_combinations.txt`, `search_strategies.json` | Log only |
| 0 Frozen query | Chosen query from the log | **You copy by hand** into `02_final/` (content frozen, not rewritten by the script) | Manual | `00_search/02_final/final_query.txt` | Methods; OR 7 `or-search`; run in WoS / Scopus |
| 1 Database export | WoS / Scopus RIS | Originals stay untouched | Download | `10_data_raw/11_original/*.ris` (timestamped) | Archive |
| 1 Rename for scripts | Files in `11_original/` | **Yes — rename only**, same bytes | Copy + rename | `10_data_raw/12_final/export_WoS.ris`, `export_Scopus.ris` | Merge |
| 2 Merge & classify | `12_final/export_WoS.ris` + `export_Scopus.ris` | No | `pipeline/merge_and_classify.py` | **Main:** `20_data_clean/clean_records.xlsx` (also `.csv`, `.ris`). **Audit:** `21_audit/all_records_with_status.xlsx`, `duplicates_*.xlsx`, `missing_doi.xlsx`, `processing_report.txt`, `prisma_counts.csv` | Screening; manuscript counts |
| 2 Optional PRISMA copies | `21_audit/processing_report.txt`, `prisma_counts.csv`, duplicate tables | **Yes — convenience copies** (do not edit these; edit the audit originals) | Manual copy | `60_prisma/processing_report.txt`, `prisma_counts.csv`, `61_diagnostics/` | Drawing Figure 2 only |
| 3 Screening | `20_data_clean/clean_records.xlsx` | No | `pipeline/screening_and_deep_classify.py` | **Main:** `30_screening/31_dataset/screened_records.xlsx`. **Reports:** `33_reports/screening_summary.txt` / `.xlsx`, `keyword_statistics.txt`. **Reviews out:** `34_reviews/` | Extraction; manuscript counts; OR 6–7 |
| 3 RIS for Zotero | Screened Excel | Derived subsets (not copies of each other) | Same screening script | `32_exports/all_records.ris` (1 018), `include_records.ris` (249), `core_studies.ris` (22), `extended_studies.ris` (26), `must_cite_records.ris` (48 = core ∪ extended) | Zotero import. **Do not** merge `must_cite_records` with `extended_studies` |
| 3 Must-cite lists | Same 48 / 45 | Lists, not a new screening | Same script + later recode sheet | `32_exports/must_cite_list.xlsx` (`48_must_cite`, `45_unique_studies`, `HIGH_Scaling_none`), `must_cite_48.csv`, `must_cite_45.csv`. Column `Scaling_source` | Figure 5 / recode |
| 3 Recode sheet | HIGH records with `Scaling_type` empty / `none` | Working sheet | Tick **one** category (do **not** re-run `_add_kategorie_ticks.py`) | `32_exports/HIGH_Scaling_none_with_abstracts.xlsx` | Copy chosen label into `Scaling_type` on the extraction Excel |
| 3 VOS RIS pair | Same as `all_records.ris` and `must_cite_records.ris` | **Yes — dedicated copies**, same records, different folder so VOSviewer is not fed the wrong half | Same screening script | `35_VOS-ris/VOS_full.ris` (1 018), `VOS_must-cite.ris` (48) | Load in VOSviewer |
| 3 PDFs | Downloaded papers | Manual archive | You | `32_exports/must_cite/`, `review/`, `review_uav/`, `other/` | Full-text reading; not a pipeline output |
| 4 Extraction templates | `31_dataset/screened_records.xlsx` | `Scaling_type` copied from screening `scaling` when a phrase matched | `pipeline/extraction_templ.py` | `40_extraction/41_input/extraction_input_full.xlsx` (include + maybe, n = 249 + 724 = **973**), `extraction_input_refined.xlsx` (include 249; HIGH = 48), `41_input/batches/` | Manual fill |
| 4 Reviews copy | `34_reviews/` | **Yes — copy** if still present | Same template script | `40_extraction/42_reviews/review_articles.xlsx` | Not in the 45-study tables |
| 4 Working fill | `extraction_input_refined.xlsx` | **You copy**, then edit | Manual + `zotero/zotero_sync.py` (keys, notes) | `42_working/extraction_filled.xlsx` *(you create)* | Full-text decisions |
| 4 Final extract | Working Excel | After `Include_final` | Manual | `43_final/extraction_final.xlsx` *(you create; folder does not exist yet)* | Synthesis tables |
| 4 Optional VOS CSV/JSON | Screened Excel or RIS | Optional side products | `auxiliary/VOSviewer.py`, `ris_to_json.py` | `43_vosviewer/*.csv`; `43_json/` *(folder only if you run the JSON script)* | Not Figure 4 (Figure 4 is a VOSviewer PNG) |
| 5 VOSviewer maps | `35_VOS-ris/VOS_full.ris` + `VOS_must-cite.ris` | Maps are new images; RIS are the copies from step 3 | VOSviewer (desktop) | `80_figures/82_VOSviewer/` — live Figure 4 = `VOS_must-cite.png` (`fig-VOS-must`) | `review.qmd` |
| 5 Icons | Artwork / drone payloads | Generic `sensor_*` are **crops** of `drone_*` | `90_review/_make_sensor_icons.py` | `80_figures/81_icons/` | Tables |
| 5 Other figures | Hand-made / Gemini plates | New images | Manual | `80_figures/83_others/fig-history.png` (Figure 1), `fig-conclusion.png` (Figure 6) | `review.qmd` |
| 5 PRISMA figure | Counts in `21_audit/` + `33_reports/` + typed Extraction boxes | PNG via Haddaway **PRISMA2020** (`Rscript PRISMA_flow.R`) | Runner on start / Save PRISMA counts | `60_prisma/PRISMA_diagram.png` (`fig-prismadig`); how-to `PRISMA_flow_how.md` = OR 6 | Figure 2 |
| 5 Workflow figure | — | — | Hand-made | `60_prisma/workflow.png` (`fig-workflow`) | Figure 3 |
| 6 Bibliography | Zotero collection | Export (not a pipeline script) | Zotero → Better BibTeX | `90_review/full_papers_review.bib` | Quarto citations. **Not** `ref.bib` / `references.bib` (those files are gone) |
| 6 Manuscript source | Pipeline reports + figures + bib | Live counts from `21_audit/` and `33_reports/` via `_pipeline-stats.qmd` | Edit `review.qmd`; appendix in `92_appendix/` | `90_review/review.qmd`, `online-resources.qmd` | Render |
| 6 Appendix list | `92_appendix/_online-resources.qmd` | **Generated** captions only | `python 90_review/_build_or_list.py` | `92_appendix/_online-resources-list.qmd` | Included by `review.qmd` |
| 7 Render | Quarto project in `90_review/` | Working copies next to the `.qmd` (gitignored) | `quarto render review.qmd` / `online-resources.qmd` | `90_review/review.docx` / `.html`, `online-resources.docx` / `.html` / `.pdf` | Publish |
| 7 Files to send | Last good render | **Yes — copies** of the same Word/HTML/PDF | `python 90_review/_publish_outputs.py` | `50_outputs/` | Co-authors / journal |

---

## Do not confuse these pairs

| This | Is not | Why |
|------|--------|-----|
| `must_cite_records.ris` (48) | Unique studies in OR 9–11 (45) | Hussain correction + Surendran chapter + Montzka conference stay in the 48 |
| `must_cite_records.ris` | `core_studies.ris` + a second merge with extended | Extended is **already inside** the 48 |
| `VOS_full.ris` | `include_records.ris` | Full = all 1 018 screened non-reviews, not the 249 include |
| Figure 4 PNG | `40_extraction/43_vosviewer/*.csv` | Article uses the VOSviewer screenshot in `80_figures/82_VOSviewer/` |
| `60_prisma/processing_report.txt` | The numbers Quarto prints | Manuscript reads **`20_data_clean/21_audit/`** and **`30_screening/33_reports/`** |
| `50_outputs/` | Manuscript source | Source is `90_review/`; outputs are copies after publish |
| `90_review/99_aux/` | Rendered article | Helpers only |

---

## Typical rerun (same order as `review_runner.py`)

1. New RIS → rename into `10_data_raw/12_final/` (content unchanged).
2. `python pipeline/merge_and_classify.py`
3. `python pipeline/screening_and_deep_classify.py`
4. Import chosen RIS into Zotero.
5. `python pipeline/extraction_templ.py`
6. `python zotero/zotero_sync.py`
7. Fill `42_working/extraction_filled.xlsx`; recode Scaling on the HIGH sheet if needed.
8. Rebuild VOSviewer PNGs from `35_VOS-ris/` if the 1 018 / 48 set changed.
9. `cd 90_review` → `quarto render review.qmd` → `quarto render online-resources.qmd` → `python _publish_outputs.py`

Menu: `cd 70_scripts` → `python review_runner.py`.
