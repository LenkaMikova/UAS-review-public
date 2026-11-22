Figure 2 was produced with the Haddaway **PRISMA2020** web application (<https://estech.shinyapps.io/prisma_flowdiagram/>; Haddaway et al. 2022, *Campbell Systematic Reviews* 18:e1230). The review runner writes this note and a CSV/R template from the same counts. Do not replace `PRISMA_diagram.png` with `Rscript` unless the boxes match the web export.

Identification and title–abstract counts come from the merge report and from `n_forward` after audit. Review articles are inside Records screened and inside Records excluded. Retrieval and full-text boxes are typed in the runner (Extraction). Blank “sought for retrieval” defaults to the must-cite count. Missing DOI is **not** counted as removed (`missing_doi_not_removed` = 21). Other exclusions are books plus records outside the original kept list (`lock_extra`).

When sought equals must-cite, records not taken to full text are the screening remainder (exclude + maybe + include leftover). Extra full texts raise sought; those records left maybe or include leftover, and the new split is typed in the title–abstract notes.

| Box | Value |
|---|---|
| Databases | WoS, 633; Scopus, 1003 |
| Duplicates | 479 |
| Other removals | 11 |
| Screened | 1146 |
| Not taken to full text | 1097 (reviews 115; exclude 50; maybe 723; include not sought 209) |
| Sought | 49 (typed) |
| Not retrieved | 0 |
| Assessed | 49 |
| Full-text exclusions | publisher correction, 1; book chapter, 1; conference paper without operational SM retrieval, 1 |
| Included studies / reports | 46 / 46 |

Warnings:

- none

Cite: Haddaway NR, Page MJ, Pritchard CC, McGuinness LA (2022) Campbell Systematic Reviews 18:e1230.
