# Retrospective protocol for a systematic review of soil moisture monitoring using unmanned aircraft systems (2019–2026)

**Status.** This document was prepared **after** the searches were run (29 April 2026) and after screening and extraction. It is a retrospective reconstruction of the methods that were used, structured as PRISMA-P 2015 (Moher et al. 2015; Shamseer et al. 2015). It is **not** an a priori protocol and **was not registered** in PROSPERO (PROSPERO does not accept protocols for completed reviews).

**Companion reporting checklist.** PRISMA 2020 for the completed review is Online Resource 4 (`or-prisma-check`) and `60_prisma/PRISMA_2020_checklist_filled.md`.

**Zenodo.** This file is the main text of the protocol record (https://doi.org/10.5281/zenodo.24362475; Miková 2026). The executed log from the review runner is `60_prisma/protocol/generated/PRISMA-P_executed.md` (Generate does not overwrite this narrative).

---

## Administrative information (PRISMA-P items 1–5)

### 1. Title

Systematic review of soil moisture monitoring using unmanned aircraft systems (retrospective protocol).

### 2. Registration

None. No PROSPERO, OSF, or other registration number exists. This retrospective protocol is deposited on Zenodo (https://doi.org/10.5281/zenodo.24362475). Dataset and software are separate records, not a fourth protocol package.

### 3. Authors

| Role | Name | Affiliation |
|---|---|---|
| Corresponding; screening, extraction, pipeline | Lenka Miková | Czech University of Life Sciences Prague, Faculty of Environmental Sciences |
| Methods / co-author | Elena Scholz | Julius-Maximilians-Universität Würzburg |
| Platforms / sensors chapters | Jiří Rous | CZU Prague |
| Historical progress; co-author | Jan Komárek | CZU Prague |

Contact: mikoval@fzp.czu.cz

### 4. Amendments

Because the protocol is retrospective, it records the methods **as executed**, not as originally planned. Differences from a naïve PRISMA full-text screening story (in particular: no dual independent screening; no full-text exclusion of 925 records) are stated under items 8 and 11 below. Future amendments, if any, will be dated in this file and in the Zenodo version history.

### 5. Support

IGA grant, Faculty of Environmental Sciences, Czech University of Life Sciences Prague, grant 2026B0015. The funder’s role in design, screening, or interpretation is not specified. Competing interests: none declared.

---

## Introduction (items 6–7)

### 6. Rationale

Soil moisture (SM) is a biophysical control on crop water use and irrigation. Satellite and in-situ methods leave a scale gap at field level. Unmanned aircraft systems (UAS/UAV) are increasingly used for high-resolution SM-related observations, alone or fused with satellite and ground data. Existing reviews cover UAVs in agriculture or SM from satellites; they do not evaluate UAV acquisition, processing, and reporting specifically for SM. This review maps methods used in 2019–2026 and audits how completely UAV campaigns report the information needed to reproduce a flight.

### 7. Objectives

Primary objective: to systematically identify and synthesise primary research (2019–2026) on SM estimation or monitoring with remote sensing in agricultural settings, with emphasis on UAV-applicable workflows.

Specific questions:

- Which platforms and sensors were used, alone or in combination?
- How were UAV campaigns flown and processed, and what was reported?
- Which inputs, applications, and retrieval methods appear in the priority subset?
- Which reporting items are consistently missing (paper checklist, 25 items + SM module)?

---

## Methods (items 8–17)

### 8. Eligibility criteria

**Inclusion**

- Topic: soil moisture estimation, monitoring, or mapping.
- Method: remote sensing (satellite, UAV/UAS/drone, or fusion with in-situ data).
- Setting: agricultural or closely related (cropland, arable land, farmland, bare soil, irrigation / water management).
- Years: publication year 2019–2026.
- Language: English.
- Document type: primary research (journal article, full conference paper, or book chapter kept at audit and assessed later).

**Exclusion at bibliographic audit** (`merge_and_classify.py`)

- Duplicate DOI (keep first).
- Duplicate title + year among remaining `correct_record` rows.
- Books and e-books (`TY` BOOK, EBOOK).
- Records outside the original kept list after audit (`lock_extra`; executed n = 8).

**Not an exclusion.** Records without a DOI are **retained**, flagged `doi_missing`, and still go through title–year duplicate checks (executed n = 21 among records going to screening).

**Exclusion at screening**

- Records flagged as reviews (`review` / `systematic review` / `meta-analysis` in title–abstract–keywords or `M3`), set aside (n = 115). They are background, not the synthesis set.
- Automated `exclude`: relevance score &lt; 3.

**Not used**

- Independent dual screening.
- A second full-text eligibility round that dropped 925 of 973 retrieved reports. The 49 must-cite records are a **priority subset of automated include**, not the remainder after full-text exclusion.

### 9. Information sources

Web of Science Core Collection (Clarivate) and Scopus (Elsevier). Last search: **29 April 2026**. No trial registers, grey literature, citation chasing, or author contact for missing studies.

### 10. Search strategy

Equivalent Boolean queries were generated with `WoS_Scopus_query.py` and then frozen in `00_search/02_final/final_query.txt` (Online Resource 7). Five concept groups, all required (AND):

1. Target: `"soil moisture"`
2. Observation / platform: `"remote sensing"` OR UAV OR UAS OR `drone*` OR `satellite*`
3. Agricultural setting: agriculture, cropland, arable land, farmland, bare soil
4. Methods / scaling: precision agriculture, site-specific, irrigation, water management, downscaling, multi-scale, data fusion
5. Limits: PY 2019–2026; English

Fields: WoS `TS`; Scopus `TITLE-ABS-KEY`. Full strings: Online Resource 7 (`or-search`).

### 11. Study records

**Data management.** RIS exports were stored untouched in `10_data_raw/11_original/` and copied to `12_final/` as `export_WoS.ris` / `export_Scopus.ris`. Merge, classification, and screening were run with the Python scripts in `70_scripts/pipeline/` (also mirrored at github.com/LenkaMikova/PRISMAtools). Zotero (v. 9.0.6) held citation records for the selected subset.

**Selection process (as executed).**

1. Merge and classify (`merge_and_classify.py`): parse RIS, merge, label status, write `clean_records.xlsx` (`correct_record` only) and a full audit trail. Duplicates were listed for manual inspection (`21_audit/duplicates_*.xlsx`).
2. Screening (`screening_and_deep_classify.py`): for each non-review record, concatenate title, abstract, and keywords (lowercase) and assign:
   - thematic flags (platform, sensor, domain, methodology, scaling);
   - `uav_applicability` if the text contains `uav`, `drone`, or `uas`;
   - `uav_potential` if `platform` contains satellite (or MODIS/Landsat/Sentinel) **and** the text contains a high-resolution phrase, a scaling phrase, or a passive-optical term (`optical`, `multispectral`, `hyperspectral`);
   - relevance score 0–8: soil moisture +2, direct UAV +3, scaling phrase +2, agricultural domain +1. `uav_potential` does **not** add points;
   - decision: include ≥ 6, maybe 3–5, exclude &lt; 3.
3. Scores were then **checked by the same person who wrote the rules** (one-person verification, not dual screening).
4. Must-cite flag (same screening script, **not** `extraction_templ.py`):
   - strict / core: score ≥ 7 **and** direct UAV **and** a scaling phrase (executed n = 22, all score 8);
   - extended must-cite: the strict set plus records with score ≥ 6 that also satisfy the second coded branch (executed n = 27 additional records, all score 6, **all still direct UAV**, `uav_potential` true, no scaling phrase). In the executed corpus, **zero** must-cite records were satellite-only. Must-cite total = 49.
5. `extraction_templ.py` built extraction sheets. Priority HIGH = already `must_cite`. Full-text fields were filled manually for the HIGH subset. Synthesis tables use **46 unique studies**; three of the 49 records are a publisher correction (Hussain 2025), a book chapter (Surendran 2024), and a conference paper without an operational SM retrieval (Montzka 2020). UAV campaigns in Online Resource 13: 10.

**Data collection.** One author extracted study-level fields from full text into the HIGH sheet. A second extractor and a documented conflict rule were not used.

### 12. Data items

Automated (title/abstract/keywords): platform, sensor type/mode, application domain, methodology, scaling phrase, UAV flags, score, screening decision, must-cite flags.

Manual (full text, HIGH / 46 studies): inputs and layers, application setting, retrieval method and reported accuracy, UAV campaign parameters (platform, payload, altitude, overlap, GCPs, RMSE), and the 25 Layer 1 reporting items plus the SM module.

Outcomes of interest are **methodological** (what was measured, how, and what was reported), not a pooled SM accuracy.

### 13. Outcomes and prioritization

No single primary health or biophysical outcome. Prioritization for extraction: must-cite (HIGH), then remaining include records (templates exist; they were not the synthesis set).

### 14. Risk of bias in individual studies

Not assessed (no RoB tool, no GRADE).

### 15. Data synthesis

Qualitative, categorical synthesis (platforms, sensors, applications, methods). Counts and percentages only. **No meta-analysis**, because designs, sensors, depths, and accuracy metrics are heterogeneous.

Keyword co-occurrence (VOSviewer 1.6.20) was run on the 49 must-cite RIS file (full counting, keyword occurrence ≥ 5).

### 16. Meta-bias(es)

Not assessed (no small-study or selective-reporting analysis).

### 17. Confidence in cumulative evidence

Not assessed.

---

## Deviations from a standard PRISMA full-text flow (for item 4 / reporting)

| Typical PRISMA step | This review |
|---|---|
| Two independent screeners | One-person rule-based score + check |
| Title/abstract then full-text eligibility for all retrieved reports | Automated include/maybe/exclude; full text only for the 49 must-cite records |
| n included = n after full-text exclusions | 46 unique studies extracted from 49 automatically flagged records |
| Protocol registered before search | Retrospective protocol after search |

These are limitations of the review, not of the code. They must be stated in Methods and in Limitations of Review.

Figure 2 (Haddaway PRISMA2020 web app, https://estech.shinyapps.io/prisma_flowdiagram/): 1,636 identified (WoS 633; Scopus 1,003). Removed before screening: 479 duplicates and 11 other (3 books + 8 outside the original kept list). Screened 1,146 (including 115 reviews). Not taken to full text 1,097. Sought and assessed 49 must-cite (22 core; 27 extended). Included 46 studies / 46 reports.

---

## Data and code availability (three Zenodo records)

| Zenodo record | DOI | Content |
|---|---|---|
| Protocol | 10.5281/zenodo.24362475 | This file; PRISMA-P checklist; PRISMA 2020 checklist |
| Dataset | 10.5281/zenodo.24362075 | Frozen query; merge audit; screened Excel; RIS subsets; reports; a copy of Online Resources 1–19. **Not** copyrighted PDFs |
| Software | 10.5281/zenodo.24362240 | `70_scripts/` snapshot and `requirements.txt` |

Online Resources 1–19 in the journal are SI, not a fourth Zenodo deposit.

GitHub live repository: https://github.com/LenkaMikova/UAS-review

---

## References for this protocol

- Moher D, et al. (2015) Preferred reporting items for systematic review and meta-analysis protocols (PRISMA-P) 2015 statement. *Syst Rev* 4:1.
- Shamseer L, et al. (2015) PRISMA-P 2015 explanation and elaboration. *BMJ* 350:g7647.
- Page MJ, et al. (2021) The PRISMA 2020 statement. *BMJ* 372:n71.
