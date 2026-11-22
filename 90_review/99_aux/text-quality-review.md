# Kontrola textu v review.qmd

Klik na odkaz otevře **přesně tu anglickou větu** (řádek v `review.qmd`).
Filtr v canvasu **Smazat** = jen to, co v textu ještě je.

Canvas: open beside chat — `canvases/text-quality-review.canvas.tsx`. Git copy: `99_aux/canvases/`.

**Last synced:** 22 November 2026 (OR 4 položky 5/16/17/24/27 + PRISMA-P šablona sladěné s Figure 2 a tělem; DOI retained).

Zdroje: Elena Scholz (e-mail + 10 bublin ve Wordu); inline komentáře v `review.qmd` (Lenka, Jiří, Jan); `99_temp/navrhy-upravy-spoluautori.md`; `99_temp/methodology-vs-pipeline.md`.

| | n |
|---|---:|
| `opraveno AI, schváleno` ještě v souboru | 21 |
| `opraveno AI, odmítnuto` | 1 (Historical — původní věta) |
| Komentář smazán, text nechán | 2 (Figure 5; dichotomie u Table 5) |
| AI v těle, ještě bez rozhodnutí | 0 |
| Zbývá předělat / dopsat | Discussion; Conclusion Core/Q/Full; Abstract |
| Smazat (ještě v textu) | 0 |
| Nechat | 11 |

## Už zapracováno (20. 11. večer)

Seznam Přijmout / Vrátit v canvasu **už není**. V `review.qmd` poznáte stav podle komentáře, dokud ho nesmažete.

- 21× `opraveno AI, schváleno` (včetně věty u Table 5, sloučeného ASPRS odstavce a metadata lead).
- Historical první věta **vrácena** (`odmítnuto`).
- Figure 5: komentář smazán; auto/ručně + čtyři definice zůstaly.
- Dichotomie: komentář smazán; věta *fall into two groups* zůstala.
- ASPRS v metadatech: geodetický odkaz, ne druhý checklist; skóre = 25 Layer 1 (`@tbl-uav-param-core`). *N* ≥ 30 jen u tvrzené mapové třídy. DOI/licence ≠ checklist článku.

## Verdikt

Tělo Elena/kluci (bez nových čísel) je uzavřené. Zbývá až po běhu runneru: Discussion (pořád kopíruje Table 12), Conclusion vs Aim (pořád Core/Q/Full + ASPRS Geodetic), Abstract. Figure 2–3 překreslení, Code Availability a Formal analysis `xxx` nejsou úprava vět.

## Smazat (ještě v textu)

Nic z Elena/kluci, co šlo bez nových čísel. Discussion (battery / VLOS / swarms) **nechat** do přepisu po běhu — teď kopíruje Table 12.

## Dopsat

| Sekce | Co | Co udělat |
|---|---|---|
| [Highlights](../review.qmd#L162) | 4 odrážky v těle (šablona PA) | Po runneru jen kdybyste chtěla počty. Ne 22/26. |
| [Impact](../review.qmd#L178) | 2 věty v těle | Můžete zkrátit na jednu. |
| [Abstract](../review.qmd#L186) | Purpose / Methods / Results / Conclusion v těle; YAML stejná kostra bez counts | **Až na konec** dopsat Results/Conclusion. Větu o satelitech vs UAV v Results nech (`methodologically important subset` — Elena chtěla vyhodit; to je podíl UAV, ne must-cite). |

## Předělat (zbývá po běhu)

Zapracované AI opravy už v canvasu jako seznam Přijmout / Vrátit nejsou.

| Sekce | Kdo | Co udělat |
|---|---|---|
| [Discussion — battery / VLOS / swarms](../review.qmd#L1591) | Kluci + TEXT QUALITY | Kapitolu nesmazat. Po nových číslech nahradit českými návrhy: Major Findings = audit 46 studií; Limitations = díry v reportech; Future = jedna sada, ne Table 12 podruhé. |
| [Conclusion — Core/Q/Full](../review.qmd#L1829) | METADATA | Sladit s Aim: 25položkový checklist + SM modul. Core/Q/Full a *ASPRS Geodetic* jsou schema datasetu, ne povinnost článku. |

## Nechat

- [Applications](../review.qmd#L1345) — Chakhar, Shokati, Dopper (jen dvě věty výše).
- [Drone studies](../review.qmd#L994) — TIR overlap, HS čas, GNSS-R/LiDAR; TIR z Trends Conclusions už tady.
- [Inputs vrstvy](../review.qmd#L1273) — NDVI / HS pásy / LST / VV/VH / CHM; gravimetrie pod tabulkou.
- [fig-distribution definice](../review.qmd#L806) — auto vs ručně + čtyři kategorie; komentář smazán. 22/26 do článku ne.
- [Dataset Overview příběh](../review.qmd#L627) — skóre 0–8 → include/maybe/exclude → must-cite 49 → extrakce 46. Leftover odstavce a „clear distinction“ už pryč. `@Guo2026` (Fenhe) je v OR 9–11.
- [Aim](../review.qmd#L425) — gap + 25-item checklist. Mimo rozsah už je (yield / disease).
- [Abstract — UAV vs satelit](../review.qmd#L196) — `methodologically important subset` nechat.
- [Platforms — fúze](../review.qmd#L904) — `does not aim` pryč; teď multi-source fusion.
- [Importance of Soil Moisture](../review.qmd#L226) — 1. půda, 2. SM se špatně měří.
- [Historical tři éry](../review.qmd#L280) — scatterometry → SMOS/SMAP → UAS.
- [Data Selection](../review.qmd#L515) — pět skupin, TI/AB/KW, 2019–2026. Kontrolu sem nevracet.

## Už smazáno — nehledej

| Sekce | Co tam bylo | Stav |
|---|---|---|
| [Type of Platforms — does not aim](../review.qmd#L904) | `does not aim to replace spaceborne platforms but rather` | Pryč. |
| [Methods — učebnicové věty](../review.qmd#L1460) | `highly flexible` / `overfitting` / `black-box nature` | Pryč. Energie/RTM schváleno. |
| [Chavez — HTML komentář](../review.qmd#L1216) | `<!-- The ability to vary flight characteristics… (@Chavez2020) -->` | Pryč. |
| [Po Table 3](../review.qmd#L409) | `Despite this clear trend toward multi-source integration…` | Pryč. |
| [Trends — úvod](../review.qmd#L866) | `most important biophysical…` a `gradual development` | Pryč. |
| [Type of Platforms — poslední odstavec](../review.qmd#L912) | `combinations platforms… choice of right sensor` | Pryč. |
| [Type of Sensors — PA 5.0](../review.qmd#L983) | `Precision Agriculture 5.0 is therefore shifting away…` | Pryč. |
| [Existing reviews](../review.qmd#L367) | `A significant number of review articles have been published…` | Pryč. |
| [Dataset Overview leftover](../review.qmd#L851) | Scaling-related / irrigation dominant / transferable satellite studies | Pryč. |
| [Dataset Overview](../review.qmd#L620) | `This classification allows a clear distinction…` | Pryč. |
| [Data Selection](../review.qmd#L527) | `@fig-prismadig shown a total of…` | Pryč. Počty jdou z `stats_r`. |

## Diagramy, DOI, odeslání (ne mazání vět v Trends)

- Figure 2 `{#fig-prismadig}` — Haddaway web app, `@PRISMAfd2022`, PNG 46/46. How-to OR 6. Make PNG v runneru nepoužívat. Figure 3 `{#fig-workflow}` ještě kreslený.
- Figure 1 Napkin + ikony `81_icons/`: vyměnit za licencovanou sadu / vlastní čáry / text, jinak SN prompt-only zakazuje.
- OR 4, PRISMA-P narrative, filled checklist a `60_prisma/README.md`: bez DOI se nevyřazuje; Generate zapisuje `PRISMA-P_executed.md` z živých reportů (šablona runneru je `protocol_export.py`, ne ruční Zenodo kopie).
- Code Availability: až řeknete; hned za Data Availability; runner nejmenovat; DOI `@MikovaCode2026`.
- Formal analysis: `xxx` před odesláním.
- Cílový časopis: Precision Agriculture (Springer 11119). AI obrázky: checklist §7.
- Scoring nespouštět. Pipeline nepřepočítávat.

## Pořadí teď

1. Runner v **této** složce (ne `Downloads\test`). Discussion / Conclusion / Abstract až po číslech (v canvasu pořád Přijmout u těch tří).
2. Merge Replace → Audit (zámek 1133 + No DOI + Keep both + Save) → Screening Replace.
3. `python 70_scripts/original_run.py compare` (nebo menu 8).
4. Až budou nová čísla: Discussion, Conclusion vs Aim, Figure 2–3.
5. Abstract a zkratky až nakonec.
