# Manuscript outputs

This is where the **finished** review goes — the files you send to co-authors or
the journal. Pipeline reports do **not** belong here (`20_data_clean/21_audit/`,
`30_screening/33_reports/`, `60_prisma/`).

| File | What it is |
|------|------------|
| `review.docx` | Manuscript (Word) |
| `review.html` | Manuscript (HTML preview) |
| `review.pdf` | Manuscript (PDF), once you add a PDF format |
| `online-resources.docx` | Appendix, A4 landscape |
| `online-resources.html` | Appendix (HTML preview) |
| `online-resources.pdf` | Appendix for Springer SI (`quarto render online-resources.qmd --to pdf`) |

Quarto still writes next to the `.qmd` in `90_review/` — that is what `quarto preview`
needs. After a good render, copy the files here:

```bash
cd 90_review
python _publish_outputs.py
```

`90_review/*.html` and `*.docx` are gitignored so the repo does not store two
copies of the same 3–6 MB files.

Icons are not copied here — they are already inside the Word/HTML. Source icons:
`../80_figures/81_icons/`. Figure 1 and Figure 6: `../80_figures/83_others/`.
Figure 2: `../60_prisma/PRISMA_diagram.png`.
Figure 4: `../80_figures/82_VOSviewer/VOS_must-cite.png`.
Staging for Zenodo packs (from `python 90_review/99_aux/zenodo/_pack.py`) may
appear as `zenodo/0N_*/`. Do not put downloaded article PDFs here. Live DOI:
root `README.md`.

The files currently refreshed on 16 Oct 2026 are **HTML only**; Word copies
here may lag until the next `docx` render.
