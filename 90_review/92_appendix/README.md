# Appendix source (Online Resources)

This folder is the **source** of the Online Resources. It is not rendered on its
own. `online-resources.qmd` (parent folder) includes the full file and
renders HTML, Word, and PDF; `review.qmd` includes the generated caption list.

| File | Role |
|------|------|
| `or-01-reviews.qmd` … `or-19-metadata-SM.qmd` | **One Online Resource per file.** Edit captions and tables here. |
| `_online-resources.qmd` | Include list only. Order of includes = OR number. |
| `_online-resources-list.qmd` | **Generated** captions only. Do not edit by hand. |
| `ASPRS_2024_Positional_Accuracy_Table.md` | Working notes for `or-uav-param` |
| `ASPRS_Methodological_Completeness_Subparameters.md` | Same |
| `UAV_ASPRS_2024_accuracy_matrix.xlsx` | Working matrix behind Table 7 / OR 16 |

After changing a caption:

```bash
cd 90_review
python _build_or_list.py
```

Image paths inside `or-NN-*.qmd` are relative to `90_review/`
(`../80_figures/81_icons/…`), not to this folder.

Current order = first `@or-*` in `review.qmd`: 1 reviews, 2 icons, 3 fusion,
4 PRISMA checklist, 5 processing, 6 PRISMA flow how-to, 7 search, 8 keywords,
**9–11 inputs / applications / methods (the 45 studies)**, 12 screening,
13 uav, 14 platforms, 15 sensors, 16 uav-param, 17 uav-param-core,
18 metadata (Layer 1, 25 items), 19 metadata-SM.
Map: `../99_aux/manuscript-structure.md`. Insert a new float at the position
of its first mention in the article, then rename `or-NN-*.qmd` to match.
The appendix is the **journal SI** (Online Resources / ESM). A **copy** goes in the Zenodo dataset zip ([10.5281/zenodo.24362075](https://doi.org/10.5281/zenodo.24362075), `@MikovaData2026`), not as a fourth record. OR 4 (PRISMA checklist) is also in the protocol record ([10.5281/zenodo.24362475](https://doi.org/10.5281/zenodo.24362475)).
