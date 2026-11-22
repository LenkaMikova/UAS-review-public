# Figures

All manuscript images except the PRISMA diagram live **here**. Do not keep a second copy under `90_review/`.

| What | Where | Used as |
|------|--------|---------|
| Icons (table thumbnails + plates) | `81_icons/` | tables in `review.qmd` and the appendix |
| Other body figures | `83_others/` | Figure 1 `fig-history.png`, Figure 6 `fig-conclusion.png` |
| VOSviewer maps | `82_VOSviewer/` | Figure 4 (`fig-VOS-must`) |
| PRISMA flow + workflow | `60_prisma/` | Figure 2, Figure 3 |

From the Quarto project (`90_review/`) the paths are `../80_figures/81_icons/…`,
`../80_figures/82_VOSviewer/…`, and `../80_figures/83_others/…`.

## `81_icons/`

PNG thumbnails and the two icon plates (`setIcons1.png`, `setIcons2.png`). Generic `sensor_*` icons are cropped from the drone payloads by `90_review/_make_sensor_icons.py`.

## `82_VOSviewer/`

| Path | Use |
|------|-----|
| `VOS_must-cite.png` | **Figure 4** in `review.qmd` (`{#fig-VOS-must}`) |
| `full/`, `include/`, `must-cite/`, `core/`, `extended/` | VOSviewer network files (`.net`, `.clu`, `.vec`, map/net txt) and the three views (network / overlay / density) |

RIS input for a new map: **`30_screening/35_VOS-ris/`** (`VOS_full.ris` n = 1 018 vs `VOS_must-cite.ris` n = 48). Do not put PNG copies next to those RIS files.

## `83_others/`

Body figures that are not icons and not VOSviewer: `fig-history.png` (Figure 1),
`fig-conclusion.png` (Figure 6).

New icons go in `81_icons/`. Figure 2 redraw: `60_prisma/PRISMA_diagram_zadani.md`.
