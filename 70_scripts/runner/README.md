# Review runner

Reusable PRISMA workflow. Defaults match the UAV soil-moisture review; every field can be changed for other data.

```
run_review.bat
```

1. Choose an **output folder**. The directory tree is created step by step (`00_search`, `10_data_raw`, …).
2. Edit title, authors, search terms, screening weights, and **output DOIs**. This review: protocol [10.5281/zenodo.24362475](https://doi.org/10.5281/zenodo.24362475), dataset [10.5281/zenodo.24362075](https://doi.org/10.5281/zenodo.24362075), software [10.5281/zenodo.24362240](https://doi.org/10.5281/zenodo.24362240). No fifth DOI for the GUI.
3. Run only the step that is open. Script outputs stay. On Audit, Screening and Extraction: **Upload after manual check** stores a new file marked `after_manual_check`. Tick **Replace existing script files** only for a new automated run.
4. Generate the protocol (plan before the run; dated executed copy after). From the first RIS upload the live executed protocol is rewritten: `60_prisma/protocol/generated/PRISMA-P_executed.md` and `data_work.md`. Every later step (merge, audit, screening, manual check, extraction recode, PRISMA counts) appends what happened and the exact records. Generate on step 8 writes a dated stamp.
5. On start the runner writes `60_prisma/PRISMA_flow_how.md` (plus CSV + R) from current pipeline counts. **Extraction** has three tabs: **Groups** (Reviews / Include / Maybe / Exclude / Unclassified; Include = Must-cite (Core + Extended) + rest), **PRISMA** (numbers already loaded from the run; type only empty boxes), **Templates**. Open a group for every field; untick a row that does not belong and move it. Recodes go to the protocol. Extra full texts: raise **sought** and note whether they came from maybe or from include leftover. **Save PRISMA counts** updates JSON/CSV/how-to. Do **not** Make PNG if Figure 2 was exported from the Haddaway web app. Registers are on Setup → Other sources. The how-file is Online Resource 6. Generate on step 8 writes `PRISMA-P_executed.md` from live reports; it does not overwrite `PRISMA-P_retrospective_protocol.md`.

Before a re-run of **this** review, snapshot the live outputs (`99_backup/original_run/`) and after each step diff them:

```
python 70_scripts/original_run.py backup
python 70_scripts/original_run.py compare
```

`compare` lists counts and the specific articles that were added, removed, or reclassified. PDF full texts are not in the backup; scripts do not overwrite those folders. Restore: `python 70_scripts/original_run.py restore`. Details: `99_backup/README.md`.

`run_review.bat` checks the Python version (3.10+). If a package from `70_scripts/requirements.txt` is missing (`pandas`, `openpyxl`, `pyzotero`), a window lists what is missing and **Install packages** runs the download — nothing is installed unless you click that button. The same window is under the download icon in the runner. `tkinter` comes with Windows Python if tcl/tk was ticked at install.
