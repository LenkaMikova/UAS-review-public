# Tři Zenodo celky (vlastní DOI)

Listopad 2026. **Tři records.** Online Resources 1–19 jdou **s článkem** (Springer SI / ESM). Dataset je screening + extrakce; do jeho zipu patří **kopie** vyrenderované přílohy, ne čtvrtý DOI. Related identifiers: zbylé dva DOI a článek (až vyjde). Přehled i v kořenovém [`README.md`](../../../README.md). Checklist odeslání: [`../pre-submission-checklist.md`](../pre-submission-checklist.md).

| Celek | Typ | Licence | DOI | Cite |
|---|---|---|---|---|
| 1 Protocol | Publication | CC BY 4.0 | [10.5281/zenodo.24362475](https://doi.org/10.5281/zenodo.24362475) | `@MikovaProtocol2026` |
| 2 Dataset (search/screening/extraction + kopie OR) | Dataset | CC BY 4.0 | [10.5281/zenodo.24362075](https://doi.org/10.5281/zenodo.24362075) | `@MikovaData2026` |
| 3 Software | Software | MIT | [10.5281/zenodo.24362240](https://doi.org/10.5281/zenodo.24362240) | `@MikovaCode2026` |

Runner **nemá** čtvrtý DOI — je uvnitř celku 3. GitHub `LenkaMikova/UAS-review` a `LenkaMikova/PRISMAtools` jsou live copy; na Zenodo mířit **tag/commit**.

Staging: spusťte `python 90_review/99_aux/zenodo/_pack.py` — zkopíruje soubory do `50_outputs/zenodo/0N_*/` (složka se může gitignorovat; zdroj zůstává v repositáři).

**Nedávat na Zenodo:** PDF stažených článků (`30_screening/32_exports/must_cite/` atd.), Zotero API klíče, `zotero_config.json`.

---

## Celek 1 — Protocol and checklists

**Název.** Retrospective PRISMA-P protocol and PRISMA 2020 checklist: systematic review of UAV soil-moisture monitoring (2019–2026)

**Typ.** Publication / Report (or “Working paper”)

**Soubory**

| Soubor | Odkud |
|---|---|
| `PRISMA-P_retrospective_protocol.md` | `60_prisma/protocol/` |
| `PRISMA-P_checklist.md` | `60_prisma/protocol/` |
| `PRISMA_2020_checklist_filled.md` | `60_prisma/` |
| `or-04-prisma-check.qmd` (stejný checklist jako OR 4) | `90_review/92_appendix/` |

**Keywords.** PRISMA-P; PRISMA 2020; systematic review protocol; soil moisture; UAV; retrospective protocol

**Poznámka v popisu.** *This protocol was prepared after the search (29 April 2026). It was not registered in PROSPERO.*

---

## Celek 2 — Dataset (search/screening + kopie přílohy)

**Název.** Systematic Review of Soil Moisture Monitoring Using Unmanned Aircraft Systems: Dataset of Included Studies and Extracted Variables (`@MikovaData2026`)

**Typ.** Dataset — tabulky, ze kterých vznikly OR 9–11, plus audit/screening/extrakce. Formátovaná příloha **není** tento record: u časopisu je SI (`ESM_*.pdf` + zip). Sem patří jen **kopie** toho PDF/zipu.

**Soubory — kopie Online Resources (ne kanonický ESM u časopisu)**

| Soubor | Role |
|---|---|
| `or-01-*.qmd` … `or-19-*.qmd` | zdroj přílohy (`90_review/92_appendix/`) |
| `online-resources.html` / `.docx` / `.pdf` | poslední render celé přílohy (SI u časopisu = PDF) |
| `opensky-sm-checklist.html` | fillable Layer 1 + SM modul (`90_review/99_aux/`) |

Pořadí OR = první `@or-*` v článku. OR 4 = PRISMA 2020 checklist (stejný text je i v celku 1). OR 6 = jak vznikl PRISMA flow diagram. 46 studií = OR 9–11.

**Soubory — search, audit, screening, extrakce**

| Soubor | Odkud |
|---|---|
| `final_query.txt` | `00_search/02_final/` |
| `processing_report.txt`, `prisma_counts.csv` | `20_data_clean/21_audit/` |
| `duplicates_doi.xlsx`, `duplicates_title.xlsx`, `missing_doi.xlsx` | `20_data_clean/21_audit/` |
| `classification_review.json`, `manual_exclusions.json`, `audit_saved.txt` | `20_data_clean/21_audit/` — **po Save v runneru**; důkaz ruční kontroly merge |
| `clean_records.xlsx` | `20_data_clean/` (1 133 retained) |
| `screened_records.xlsx` | `30_screening/31_dataset/` (1 018) |
| `screening_summary.txt` / `.xlsx`, `keyword_statistics.txt` | `30_screening/33_reports/` |
| `must_cite_list.xlsx`, `must_cite_48.csv`, `must_cite_45.csv` | `30_screening/32_exports/` |
| RIS: `all_records.ris`, `include_records.ris`, `core_studies.ris`, `extended_studies.ris`, `must_cite_records.ris` | `30_screening/32_exports/` |
| `VOS_full.ris`, `VOS_must-cite.ris` | `30_screening/35_VOS-ris/` |
| `extraction_input_refined.xlsx` | `40_extraction/41_input/` (HIGH = 48; po ručním recode scaling) |
| `HIGH_Scaling_none_with_abstracts.xlsx` | `30_screening/32_exports/` — pracovní list ručního *none* |
| `extraction_filled.xlsx` (pokud existuje) | `40_extraction/42_working/` — full-text extrakce 45 studií |

Surové WoS/Scopus RIS (`10_data_raw/11_original/`) jen pokud licence databáze dovolí redistribuci abstraktů. Jinak stačí frozen query + vaše odvozené tabulky.

---

## Celek 3 — Software

**Název.** PRISMAtools pipeline used in a systematic review of UAV soil-moisture monitoring

**Typ.** Software

**Soubory**

| Soubor | Odkud |
|---|---|
| celá složka `70_scripts/` bez `__pycache__` a bez `zotero_config.json` | pipeline **i runner** (`run_review.bat`, `70_scripts/runner/`) — jeden DOI, ne zvlášť na GUI |
| `requirements.txt` | závislosti |
| `pipeline-io.md` | `90_review/99_aux/` (řetěz vstup–výstup) |

Related identifier: GitHub `LenkaMikova/UAS-review` a `LenkaMikova/PRISMAtools`. Na Zenodo dejte **tag/commit**, ať DOI míří na zmrazenou verzi, ne na moving main.

Runner je jen rozhraní ke stejným skriptům. V článku ho nejmenovat jako samostatný produkt a nedávat mu čtvrtý DOI. Pole `doi_software` v Setup = DOI tohoto celku.

---

## Co nahrát, když článek říká „manually verified“

Nahrává se **soubor po kontrole vedle výstupu skriptu**, ne přepsáním automatického souboru. V runneru jen u Audit / Screening / Extraction: **Upload after manual check** (`*_after_manual_check.xlsx` v `checked/` nebo `42_working/`). Save u auditu ukládá rozhodnutí; výstup merge se tím nemění. Tick **Replace existing script files** jen pro nový automatický běh.

| Věta v Methods | Soubor, který má být na Zenodo (celek 2) |
|---|---|
| Dataset cleaned … then checked manually (merge / duplicity) | skript: `clean_records.xlsx`, `all_records_with_status.xlsx`, `processing_report.txt`; ruční: `record_decisions.json`, `forward_records.xlsx`, `classification_review.json`, `audit_saved.txt` |
| Scores were manually verified | skript: `screened_records.xlsx`; ruční: `31_dataset/checked/screened_records_after_manual_check.xlsx` |
| Scaling *none* assigned manually | `must_cite_list.xlsx` (`Scaling_source`) a `HIGH_Scaling_none_with_abstracts.xlsx` |
| Full-text extraction of 45 studies | šablona: `extraction_input_refined.xlsx`; vyplněno: `42_working/extraction_filled_after_manual_check.xlsx` |

Automatické logy (`processing_report.txt`, `screening_summary.txt`) dokládají skript, ne ruční rozhodnutí.

---

## Po nahrání

1. Cite keys v `full_papers_review.bib` už jsou (`MikovaProtocol2026`, `MikovaData2026`, `MikovaCode2026`). Methods cituje protokol a kód + dataset.
2. Cite keys v `or-04-prisma-check.qmd` a v `PRISMA-P_retrospective_protocol.md` už míří na tři Zenodo DOI. Po dalším Generate zkontrolovat `PRISMA-P_executed.md` (DOI retained; 46/49).
3. Data Availability: tři DOI; GitHub jako live copy.
4. Related identifiers na Zenodo: package 1 *cites* 2 a 3; 2–3 *is supplement to* 1; všechny *is supplement to* článek, až bude DOI článku.
