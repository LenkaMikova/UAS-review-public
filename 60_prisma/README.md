# PRISMA reporting

Materials for the PRISMA 2020 flow diagram and checklist, plus convenience copies of pipeline counts.

**Figure 2 is `PRISMA_diagram.png`** (`fig-prismadig`), exported from the Haddaway PRISMA2020 web app (<https://estech.shinyapps.io/prisma_flowdiagram/>). Identification/screening
counts should match the pipeline (1 636 − 479 − 11 = 1 146 screened; 49 must-cite; 46 included studies).
`PRISMA_diagram_short.png` is gone from this folder. Redraw notes:
[`PRISMA_diagram_zadani.md`](PRISMA_diagram_zadani.md).

**Checklist:** working fill-in
[`PRISMA_2020_checklist_filled.md`](PRISMA_2020_checklist_filled.md);
printed copy is Online Resource 4 (`or-prisma-check`). Copy into
`62_official/PRISMA_2020_checklist.docx` if the journal wants the official Word
template.

**Protocol (retrospective):** [`protocol/PRISMA-P_retrospective_protocol.md`](protocol/PRISMA-P_retrospective_protocol.md)
and [`protocol/PRISMA-P_checklist.md`](protocol/PRISMA-P_checklist.md). Prepared
after the search; not registered in PROSPERO. Zenodo package 1:
[10.5281/zenodo.24362475](https://doi.org/10.5281/zenodo.24362475)
(`@MikovaProtocol2026`). All deposits: root `README.md`.

## Structure

| Path | Contents |
|------|----------|
| `PRISMA_diagram.png` | **Figure 2** in the manuscript (`fig-prismadig`) |
| `prisma_flow_inputs.json` | Audit trail: pipeline counts + typed retrieval/exclusions (runner Extraction) |
| `PRISMA2020_data.csv` | Template for the Haddaway **PRISMA2020** R package (not GSscraper) |
| `PRISMA_flow.R` | Writes PNG (`Rscript PRISMA_flow.R`) |
| `PRISMA_flow_how.md` | How the diagram was produced — **Online Resource 6** (`or-prisma-flow`). Written when the runner starts |
| `PRISMA_2020_checklist_filled.md` | Filled checklist mapped to the manuscript |
| `61_diagnostics/` | Copies of duplicate / missing-DOI tables from `20_data_clean/21_audit/` |
| `62_official/` | Official PRISMA 2020 templates (empty checklist PDF/DOCX, flow-diagram DOCX) |
| `processing_report.txt` | Optional copy from `20_data_clean/21_audit/` |
| `prisma_counts.csv` | Optional copy — status counts for the flow diagram |
| `workflow.png` | Figure 3 in the manuscript (dark) |

The diagrams sit here, not in `80_figures/`, because they are a reporting artefact
tied to the pipeline counts, not an icon.

## Current counts

<!-- Figure 2–3 překreslit po novém auditu. Zámek original_run = 1 133
     retained (starý běh ještě vyřadil 22 missing DOI). Nový merge
     missing DOI nevyřazuje — Assign DOI / Save → forward_records.
     Po auditu přepsat Removed z processing_report / stats_r
     (duplicity + knihy, ne missing DOI). -->

| Box | n (Figure 2 / live pipeline) |
|---|---|
| WoS / Scopus / total | 633 / 1 003 / 1 636 |
| Removed before screening | 490 (479 duplicates + 11 other: 3 books + 8 outside the original kept list). Missing DOI is **not** removed |
| After audit (`n_forward`) | **1 146** |
| Review articles (inside screened) | 115 |
| Records screened | 1 146 |
| Not taken to full text | 1 097 |
| Include / Maybe / Exclude (non-review) | from `screening_summary.txt` |
| Must-cite (core + extended) | 49 (22 + 27) |
| Included studies / reports | 46 / 46 |

Do not put “925 excluded after full-text → 48 included” on Figure 2.

## Workflow

1. Run `merge_and_classify.py` → primary reports stay in `20_data_clean/21_audit/`.
2. Copy `processing_report.txt` and `prisma_counts.csv` here when preparing the diagram.
3. Redraw `PRISMA_diagram.png` from those counts **and the honest story**, then re-render.
4. Official templates in `62_official/` are a separate Word fill-in, not the PNG used in Quarto.


