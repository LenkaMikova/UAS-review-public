# VOSviewer RIS pair

Two files for Figure 4 (`fig-VOS-must` in `90_review/review.qmd`). Written by
`70_scripts/pipeline/screening_and_deep_classify.py` together with the Zotero
subsets in `32_exports/`.

Live counts: [`counts.txt`](counts.txt) (regenerated every screening run).

## Why this folder, not `32_exports/`

`32_exports/` is the pipeline split for Zotero: include, core, extended,
all screened records. VOSviewer needs **exactly two** files that match the
figure caption (full vs must-cite). Keeping them here avoids opening the
wrong half (e.g. `extended_studies.ris` = 26, not 48).

Maps / PNG stay in `80_figures/82_VOSviewer/`. This folder is only the RIS
input — do not copy the PNG maps here.

## The two files

| File | n | Same as | Load in VOSviewer as |
|---|---:|---|---|
| `VOS_full.ris` | 1 018 | `32_exports/all_records.ris` | left panel — all screened non-review records |
| `VOS_must-cite.ris` | 48 | `32_exports/must_cite_records.ris` = **core ∪ extended** | right panel — must-cite flag |

48 = 22 core (`core_studies.ris`) + 26 extended (`extended_studies.ris`).
That is **48 RIS records**, not the 45 unique studies in the extraction tables
(Hussain 2025 correction, Surendran 2024 chapter, Montzka 2020 conference stay
in the 48).

**Do not** concatenate `extended_studies.ris` with `must_cite_records.ris`.
The second file already contains the extended tier; you would double those
26 records.

## Thresholds (different on purpose)

| Map | Min. occurrences | Why |
|---|---:|---|
| Full (n = 1 018) | 50 | overview of the screened literature |
| Must-cite (n = 48) | 5 | 50 would leave almost no nodes |

Do not copy the “6 582 keywords” count from the full run onto the must-cite run.
VOSviewer recounts keywords from the file you loaded.

## If VOSviewer shows ~727 instead of 1 018

The old `all_records.ris` wrote **two** `TY` lines per record (`JOUR`, then the
real type). Tools that keep only `TY  - JOUR` saw **727** journal articles.
The re-export writes one `TY` (JOUR / CONF / BOOK_CHAPTER / …). Load
`VOS_full.ris` as-is; do not filter to journals. Keyword co-occurrence can still
skip the few records with no `KW` — see `counts.txt`.

## Related

- Pipeline flags: `30_screening/README.md`
- Figure PNGs: `80_figures/82_VOSviewer/`
