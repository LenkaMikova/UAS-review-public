# Helpers (not part of the manuscript)

Working files that support writing `review.qmd` but are **not rendered** and are not submitted.

Personal drafts and co-author scratch notes are in **`99_temp/`** at the repo root (gitignored). Cursor opens live canvases only from the IDE folder `canvases/` (beside the chat). Git copies of those files live here under `canvases/` so GitHub has them too.

| Path | Role |
|------|------|
| `manuscript-structure.md` | Living map of tables, figures, Online Resources, row counts |
| `text-quality-review.md` | What to cut, move, keep, or still write |
| `pre-submission-checklist.md` | Precision Agriculture: PRISMA, journal duties, remaining points |
| `zenodo/` | Three Zenodo records. OR 1–19 = journal SI; dataset zip holds a copy, not a fourth DOI |
| `canvases/` | Git copies of Cursor canvases (structure, text quality, pre-submission, Scaling_type recode) |
| `pipeline-io.md` | Internal chain: input → script/action → output (including unchanged copies) |
| `or-metadata-full.md` | Layer 2 OpenSkyLab matrix (not printed OR 18) |
| `opensky-sm-checklist.html` | Fillable Layer 1 + SM module |
| `_count_table_studies.py` | Recounts data rows in body + appendix tables → `_table_counts.json` |
| `_check_icon_paths.py` | Checks that every `![](…)` in `review.qmd` and the appendix exists |
| `_audit_renamed_paths.py` | One-off leftover-path scan after folder renames |
| `_split_online_resources.py`, `_reorder_or_by_first_mention.py` | OR file maintenance |

Recount:

```bash
python 90_review/99_aux/_count_table_studies.py
```
