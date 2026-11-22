# PRISMA 2020 checklist (filled)

Working copy for submission. Copy into the official Word template
`62_official/PRISMA_2020_checklist.docx` before sending. Locations refer to
`90_review/review.qmd` and `90_review/online-resources.qmd`.

This review is a **qualitative systematic review without meta-analysis**.
Items 12, 14, 15, 19–22 that assume a statistical synthesis are **N/A**, with
that stated in Methods (Data Extraction and Data Analysis).

Abstract, Discussion, and Conclusion are still being written; rows marked
*draft* must be updated when those sections are finished.

| # | Item | Location | Status |
|---|------|----------|--------|
| **TITLE** | | | |
| 1 | Identify the report as a systematic review | Title: *Systematic Review of Soil Moisture monitoring using Unmanned Aircraft Systems* | Reported |
| **ABSTRACT** | | | |
| 2 | See the PRISMA 2020 for Abstracts checklist | Body section Abstract (Purpose / Methods / Results / Conclusion). YAML `abstract:` is still the placeholder *Insert abstract here* — that string currently prints in the Word header. Search date, eligibility, limitations, funding, and registration are not yet in the abstract. | Draft — finish last |
| **INTRODUCTION** | | | |
| 3 | Rationale | Importance of Soil Moisture; Existing reviews and Research Gap; @or-reviews | Reported |
| 4 | Objectives | Aim and Scope this Review | Reported |
| **METHODS** | | | |
| 5 | Eligibility criteria | Data Selection; Data Workflow. Inclusion: SM estimation/monitoring/mapping; RS (satellite or UAV); agricultural setting; 2019–2026; English; primary research (journal, conference paper, or book chapter kept at audit). Exclusion at audit: books and duplicates. Records without a DOI are retained. Reviews set aside. Automated exclude: score &lt; 3. Same wording as OR 4. | Reported |
| 6 | Information sources | WoS (Clarivate) and Scopus (Elsevier); search date **29 April 2026**. No trial registers, grey literature, or citation chasing. | Reported (databases only) |
| 7 | Search strategy | Five concept groups; full Boolean strings for both databases in @or-search (`00_search/02_final/final_query.txt`) | Reported |
| 8 | Selection process | Automated relevance score (0–8) on title/abstract/keywords, then **manual check of scores**. One-person rule-based screen, not independent dual screening (see note below). Disagreement rule is not described because a second screener was not used. | Reported as automated + manual check |
| 9 | Data collection process | Semi-automated templates + manual full-text of *include* and *maybe*. Who extracted, whether a second extractor checked a sample, and how conflicts were resolved are not stated. | Partial |
| 10 | Data items | Dimensions listed: platform, sensor, domain, method, scaling, UAV relevance. No table of all extracted fields in Methods. Per-study fields appear in @or-inputs, @or-applications, @or-methods, @or-uav. | Partial |
| 11 | Study risk of bias | Not assessed | Not reported |
| 12 | Effect measures | No meta-analysis | N/A |
| 13 | Synthesis methods | Descriptive counts and categorical aggregation; no pooling. Heterogeneity given as the reason for no meta-analysis. | Reported |
| 14 | Reporting bias assessment | Not done | N/A / not reported |
| 15 | Certainty assessment | Not done (no GRADE) | N/A / not reported |
| **RESULTS** | | | |
| 16 | Study selection | @fig-prismadig, @or-processing, @or-screening, OR 4. Figure 2 path: 1,636 identified → 479 duplicates + 11 other → 1,146 screened (incl. 115 reviews) → 1,097 not taken to full text → 49 sought/assessed must-cite (22 core; 27 extended) → 46 studies / 46 reports | Reported (live stats in OR 4) |
| 17 | Study characteristics | 46 unique studies in @or-inputs, @or-applications, @or-methods; 10 UAV campaigns in @or-uav. 3 of 49 must-cite records are not additional studies: Hussain 2025 correction, Surendran 2024 chapter, Montzka 2020 conference paper | Reported |
| 18 | Risk of bias in studies | — | Not reported |
| 19 | Results of individual studies | Accuracies (RMSE, R²) in @or-methods (45 studies), not in the body | Partial (appendix) |
| 20 | Results of syntheses | Trends chapter (platforms, sensors, applications, methods) — qualitative | Draft / in progress |
| 21 | Reporting biases | — | N/A / not reported |
| 22 | Certainty of evidence | — | N/A / not reported |
| **DISCUSSION** | | | |
| 23 | Discussion | Discussion subsections exist but are mostly empty; a draft conclusions block sits under Trends. Limitations of the *review* are under Conclusion. Finish after the middle of the paper. | Draft — left until the middle is done |
| **OTHER INFORMATION** | | | |
| 24 | Registration and protocol | **Not registered.** Retrospective PRISMA-P at Zenodo [@MikovaProtocol2026]. Same as Methods and OR 4. | Reported |
| 25 | Support | Funding: IGA FŽP CZU, grant 2026B0015. Stray `]` after the grant number. Role of the funder not stated. | Partial |
| 26 | Competing interests | “The authors have no relevant financial or non-financial interests to disclose.” | Reported |
| 27 | Availability of data, code and other materials | GitHub [UAS-review](https://github.com/LenkaMikova/UAS-review); [PRISMAtools](https://github.com/LenkaMikova/PRISMAtools). Three Zenodo records: protocol [@MikovaProtocol2026], dataset [@MikovaData2026], software [@MikovaCode2026]. OR 1–19 = journal SI, not a fourth deposit | Reported |

## PRISMA 2020 for Abstracts (item 2 unpacked)

| # | Item | In current Abstract? |
|---|------|----------------------|
| 1 | Identify as a systematic review | Yes (Methods sentence) |
| 2 | Objectives | Partial (Purpose) |
| 3 | Eligibility criteria | No |
| 4 | Information sources + date | Databases named; **date missing** |
| 5 | Risk of bias methods | No (N/A if none) |
| 6 | Synthesis methods | Automated screening mentioned; no MA |
| 7 | Included studies | Counts for include/maybe/exclude/must-cite |
| 8 | Synthesis of results | Qualitative gap statement |
| 9 | Limitations of evidence | No |
| 10 | Limitations of review | No |
| 11 | Interpretation | Conclusion sentence |
| 12 | Funding | No |
| 13 | Registration | No |

## Note on item 8 — dual screening vs this review

**Dual (independent) screening** means two people each decide include/exclude
on every record (or a large sample), blinded to each other; a third person or
consensus resolves disagreements. Cochrane and PRISMA expect that because a
single reader’s keyword habits systematically miss or over-include studies.

This review used a **rule-based score (0–8) on title/abstract/keywords, then a
manual check of those scores**. That is *not* dual screening. It is closer to
machine-assisted single-screener triage.

It is **not automatically worse**: the rule is transparent, repeatable, and the
low threshold kept uncertain records as *maybe* instead of dropping them. For a
methodological map of 1 018 records that is defensible.

It **is weaker on PRISMA item 8** than two independent human screeners, because
(1) the score cannot read nuance the way a second person can, (2) the person
who wrote the rules also checked them, and (3) there is no reported agreement
statistic (kappa / percent agreement).

What to do in the paper: keep the method, name it as a **deviation**, and say
that a second reviewer checked scores (or a sample) — if that is true. Do not
call it dual screening.

## Checklist file to submit

Paste the Location / Status columns into `62_official/PRISMA_2020_checklist.docx`.
Submit that DOCX as a journal supplementary file, not this Markdown.
