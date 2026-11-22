# Checklist před odesláním

Precision Agriculture (Springer, ISSN journal 11119). Canvas vedle chatu:
`canvases/pre-submission-checklist.canvas.tsx`. Git kopie: `99_aux/canvases/`.

**Last synced:** 22 November 2026 (PRISMA artefakty sedí s Figure 2; checklist má PRISMA + časopis + zbývající body; `99_temp/` jen lokálně).

Zdroje pokynů (neměnit z hlavy):

- váš soubor [`SpringerNature.pdf`](../../../SpringerNature.pdf) (šablona časopisu, 5 stran)
- [Submission guidelines](https://www.springer.com/journal/11119/submission-guidelines)
- [SN AI manuscript preparation](https://www.springernature.com/gp/policies/editorial-policies/ai-manuscript-preparation)

Stav: **hotovo** = už v projektu sedí. **otevřené** = ještě není. Klik v canvasu jen označuje, že jste to odškrtla — tělo článku se tím nemění.

---

## 1. Online Resources ≠ dataset

Dohoda: OR 1–19 jdou **s článkem** (Springer *Supplementary Information*). Dataset, protokol a kód zůstávají **tři** Zenodo records. Do zipu datasetu jde **kopie** vyrenderované přílohy, ne čtvrtý DOI.

Časopis k SI (web, sekce *Supplementary Information*):

| Pravidlo | Co to znamená u nás |
|---|---|
| Citujte jako „Online Resource N“ | Už v `review.qmd` (`@or-*`). |
| U každého souboru: title, journal, autoři, affiliation + e-mail corresponding | Na první stranu PDF / do záhlaví. Teď chybí. |
| Text a prezentace jako **PDF** (docx/ppt nejsou vhodné) | Formát je v `online-resources.qmd`. Render: `quarto render online-resources.qmd --to pdf`. |
| Tabulky k interaktivnímu použití jako csv/xlsx | Dlouhé OR tabulky v PDF; strojová data na Zenodo. |
| Více souborů smí do **zip** nebo gz | Zip `ESM.zip` s `ESM_1.pdf` … nebo jeden PDF + zip stejných souborů. |
| Soubory pojmenovat `ESM_3.pdf` | Ne `online-resources.docx`. |
| V rukopisu caption ke každému SI | Seznam na konci `review.qmd` (include `_online-resources-list.qmd`). |
| SI se publikuje **jak přijde** (bez sazby redakce) | PDF musí být čitelné, čísla OR 1–19 shodná s textem. |
| Datasety do SI jen výjimečně; preferuje se repository | Screening/extrakce = `@MikovaData2026`, ne čtvrtý ESM record. |

**Samostatně a v zipu** (to, na čem jsme se shodli):

1. U časopisu: PDF Online Resources (jeden soubor *nebo* `ESM_1.pdf` … `ESM_19.pdf`) **a** stejné soubory v `ESM.zip`.
2. Na Zenodo v datasetu: **kopie** toho PDF/zipu vedle xlsx/csv/RIS.
3. `_pack.py` pořád skládá čtvrtou složku `03_online-resources` — sloučit do datasetu, až budete balit.

---

## 2. Co nahrát do Editorial Manageru

| Soubor | Formát | Stav |
|---|---|---|
| Rukopis | `.docx` (Word; LaTeX by taky šel) | `50_outputs/review.docx` — přerenderovat až budou čísla |
| Editable source | `.qmd` časopis nechce; chce Word | Word je kanonický upload |
| Obrázky | zvlášť, pokud systém žádá | Fig 2–3 ještě překreslit |
| SI | PDF + zip, názvy `ESM_*` | otevřené |
| Cover / title page | corresponding e-mail, ORCID | v YAML je; zkontrolovat ve Wordu |
| Author contribution + Competing interests | **i v rozhraní** odeslání, nejen v textu | otevřené až při uploadu |

---

## 3. Šablona časopisu (`SpringerNature.pdf`)

Web i šablona se občas rozcházejí. Držet **šablonu** u Highlights/Impact; u abstraktu Purpose / Methods / Results / Conclusion (web). Šablonové Context / Aims pokrývá Purpose; Implications je v Impact.

| Položka | Požadavek | Stav v `review.qmd` |
|---|---|---|
| Highlights / Keypoints | 3–5 odrážek | **v těle** (4 odrážky). Čísla až po runneru. |
| Impact | 1–2 věty, jak práce sedí do definice časopisu | **v těle**. Finální věty můžete zkrátit. |
| Abstract | web: 150–250 slov, Purpose / Methods / Results / Conclusion | **v těle** jako **Purpose / Methods / Results / Conclusion**. YAML má tutéž kostru bez live counts. Počty a Conclusion až po runneru. |
| Keywords | 4–6 | 6 — hotovo |
| Sections numbered | **ne** (PRAG) | Quarto `number-sections: false` u docx |
| Max. 3 úrovně nadpisů | | zkontrolovat ve Wordu |
| Tabulky + obrázky v těle | šablona: cca 7–9 fig. + 2–3 tab., součet ~11; zbytek do SI | teď **12 tab. + 6 fig.** — rozhodnout, co ještě přestěhovat |
| Barva | online ano; tisk B/W — barvy musí jít číst i šedě | Fig. 2 červený rámeček; Fig. 5 |
| Čas minulý v Methods a Results | | po běhu runneru |
| Bez royal *we* | | projít před odesláním |

---

## 4. Tělo a čísla (než se renderuje finální Word)

Pořadí z text-quality: runner v **této** složce → nová čísla → Discussion / Conclusion / Abstract.

| Položka | Stav |
|---|---|
| Scoring nespouštět, dokud není lock 1133 | lock je (`original_selection.xlsx` / `99_backup/original_run/`) |
| Runner: Merge → Audit Save → Screening | otevřené |
| `original_run.py compare` | otevřené |
| Discussion (battery / VLOS / swarms = kopie Table 12) | otevřené |
| Conclusion vs Aim (pořád Core/Q/Full + ASPRS Geodetic) | otevřené |
| Abstract — dopsat Results/Conclusion po číslech | kostra je v těle |
| Figure 2–3 překreslit **bez** ChatGPT/Napkin | otevřené (viz §8) |
| Formal analysis `xxx` | otevřené |
| OR 4 položky 24/27 Zenodo | hotovo (tři records, `@MikovaProtocol2026` / Data / Code) |

---

## 5. Statements, data, kód, AI

| Položka | Požadavek časopisu | Stav |
|---|---|---|
| Competing Interests | v textu i v odesílacím formuláři | text hotov |
| Funding | IGA 2026B0015 | text hotov |
| Author Contributions | CRediT; do formuláře znovu | Formal analysis = `xxx` |
| Data Availability | povinné; datasety raději repository | teď jen GitHub — doplnit tři DOI |
| Code | šablona: kód jako supplemental **nebo** repository | `@MikovaCode2026`; Code Availability odstavec **až řeknete** (Elena: hned za Data Availability) |
| LLM | dokumentovat v **Methods** (ne jen acknowledgment). Copy-edit se nemusí hlásit; u vás je Cursor/Gemini/ChatGPT víc než copy-edit | přesun/doplnění do Methods otevřené |
| Generativní obrázky | viz §8 | otevřené |

---

## 6. Zenodo (tři records, ne čtyři)

| Record | DOI | Role |
|---|---|---|
| Protocol | 10.5281/zenodo.24362475 | PRISMA-P |
| Dataset | 10.5281/zenodo.24362075 | screening, extrakce, RIS + **kopie** OR PDF/zip |
| Software | 10.5281/zenodo.24362240 | `70_scripts/` včetně runneru |

Ještě: related identifiers mezi třemi DOI; tag na GitHubu, na který Zenodo míří; Data Availability přepsat z GitHub-only; do zipu datasetu dát ESM kopii.

---

## 7. Obrázky a ikony (SN: ne prompt-only)

Caption *Generated using NapkinAI/ChatGPT* **nestačí**. Prompt bez ověřitelného podkladu časopis nebere. Ikony v tabulkách smíte mít — musí být z licencované sady, vlastní kresby, nebo pryč.

| Úkol | Co | Jak zlegalizovat |
|---|---|---|
| Ikony v tabulkách + OR 1 | `80_figures/81_icons/` (Napkin) | CC0/MIT sada (Lucide, Tabler, Phosphor, FA Free) **nebo** čáry v Inkscape/PowerPoint **nebo** jen text (UAS, SAT). Licence + datum do caption OR 1. |
| Figure 1 `fig-history` | Napkin infografika | Jednoduchá autorská časová osa, nebo nechat jen Table 1 |
| Figure 2 `fig-prismadig` | Haddaway web app | PNG 46/46 v `60_prisma/PRISMA_diagram.png`; caption `@PRISMAfd2022`. Runner Make PNG nepřepisovat. |
| Figure 3 `fig-workflow` | Napkin workflow | PowerPoint/draw.io z vašich kroků pipeline |
| Figure 4 VOSviewer, Figure 5 z dat | ne generativní | nechat |
| Caption po výměně | *Generated using …* | smazat; u licencované sady uvést název + licenci |

Rozhodnutí (knihovna / vlastní čáry / bez ikon) ještě není. Do těla se nesahá, dokud ho neřeknete.

---

## 8. PRISMA 2020 — artefakty vs. reporting v článku

Soubory, které PRISMA chce, **máte**. Nesedí ještě všude *věty v rukopisu* (abstract, Data Availability, role fundera). Časopis PRISMA 2020 nepředepisuje jako povinnou šablonu, ale recenze se k ní hlásí v Methods a v OR 4.

| Položka | Kde to má být | Stav |
|---|---|---|
| 1 Title *systematic review* | Title | **hotovo** |
| 2 Abstract (PRISMA for Abstracts) | Purpose / Methods / Results / Conclusion | **otevřené** — chybí eligibility, datum search, n studií, registrace/ne, funding, limity review |
| 3–4 Rationale, objectives | Introduction | **hotovo** |
| 5 Eligibility | Data Selection / Workflow; OR 4 | **hotovo** (bez DOI se nevyřazuje) |
| 6 Information sources + datum | Methods; 29 April 2026 | **hotovo** |
| 7 Full search | OR 7 | **hotovo** |
| 8 Selection process | Methods: rule-based + one-person check | **hotovo** v Methods; v Limitations ještě výslovně *not dual screening* |
| 9 Data collection | one extractor | **částečně** — kdo extrahoval je v OR 4; v těle slabší |
| 10 Data items | OR 9–11, 13, 16–17 | **hotovo** |
| 11, 14, 15, 18, 21, 22 RoB / GRADE / reporting bias | Methods + OR 4 = not assessed / N/A | **hotovo** (žádná MA) |
| 12–13, 19–20 Synthesis | qualitative Trends; no pooling | **hotovo** jako mapa; Discussion ještě draft |
| 16 Study selection + flow | Figure 2 + OR 4 položka 16 + OR 5–6 | **hotovo** (1636 → 1146 screened → 49 → 46/46) |
| 17 Study characteristics | OR 9–11 (46); OR 13 (10 UAV) | **hotovo** |
| 23 Discussion + limitations of *the review* | Limitations of Review | **částečně** — draft; chybí single-screener / no a priori protocol |
| 24 Registration + protocol | Methods; Zenodo `@MikovaProtocol2026` | **hotovo** (neregistrováno; retrospektivní PRISMA-P) |
| 25 Support; role of funder | Funding | **otevřené** — grant je; role fundera není |
| 26 Competing interests | Statements | **hotovo** v textu; znovu do formuláře EM |
| 27 Data, code, materials | Data Availability + Methods | **částečně** — Methods cituje tři Zenodo; Data Availability pořád jen GitHub; Code Availability odstavec chybí |

**Máte jako soubory (nic dalšího z PRISMA balíku neschází):**

- PRISMA 2020 checklist = OR 4 (`or-04-prisma-check.qmd`) + pracovní kopie `60_prisma/PRISMA_2020_checklist_filled.md`
- PRISMA-P narativ = `60_prisma/protocol/PRISMA-P_retrospective_protocol.md` + P checklist
- executed log = `60_prisma/protocol/generated/PRISMA-P_executed.md` (Generate v runneru)
- Figure 2 PNG z Haddaway web app + how-to OR 6
- oficiální Word/PDF šablony v `60_prisma/62_official/` — do nich zkopírovat OR 4 před uploadem, pokud to EM chce jako samostatný soubor

**Make PNG v runneru nepoužívat.** Figure 2 je z https://estech.shinyapps.io/prisma_flowdiagram/.

---

## 9. Povinnosti časopisu (Precision Agriculture, single-blind)

Z [submission guidelines](https://www.springer.com/journal/11119/submission-guidelines) a šablony `SpringerNature.pdf`. Recenze je *single blind* (nemusíte anonymizovat rukopis).

| Povinnost | Kde | Stav |
|---|---|---|
| Editable source `.docx` (ne jen qmd) | Editorial Manager | **otevřené** — přerenderovat `50_outputs/review.docx` |
| Title page: corresponding e-mail, affiliations | YAML / Word | **zkontrolovat ve Wordu** |
| Highlights 3–5 | tělo | **v těle** (4); počty volitelně |
| Impact 1–2 věty vs definice časopisu | tělo | **v těle**; můžete zkrátit |
| Abstract 150–250 (web) / Purpose–Methods–Results–Conclusion | tělo | **kostra je**; Results/Conclusion dopsat |
| Keywords 4–6 | YAML | **hotovo** (6) |
| Author contribution **i v rozhraní** EM | nejen v textu | **otevřené** až při uploadu; Formal analysis = `xxx` |
| Competing interests **i v rozhraní** EM | | **otevřené** až při uploadu |
| Data Availability statement s odkazem/DOI | Statements | **otevřené** — doplnit tři Zenodo DOI (dataset citovat v referencích) |
| Research data: repository místo SI | Zenodo dataset | **DOI existují**; statement a related identifiers ještě |
| SI jako PDF, názvy `ESM_*`, cover (title, journal, autoři, e-mail) | OR 1–19 | **otevřené** |
| LLM v **Methods** (SN AI policy); copy-edit se nemusí | teď jen Acknowledgments | **otevřené** |
| Generativní obrázky: ne prompt-only | Fig 1, 3, ikony | **otevřené** |
| Šablona: ~11 tab+fig v těle | teď 12 tab. + 6 fig. | **rozhodnout**, co ještě do SI |
| Barvy čitelné i v šedé (tisk B/W) | Fig 2, 5 | **otevřené** |
| Methods a Results v minulém čase | | projít před odesláním |

---

## 10. Další body, které ještě musíte vyřešit (ne PRISMA soubor)

| Bod | Proč | Stav |
|---|---|---|
| Discussion (battery / VLOS / swarms) | teď kopíruje Table 12 | **otevřené** |
| Conclusion vs Aim | pořád Core/Q/Full + ASPRS Geodetic | **otevřené** |
| Abstract Results/Conclusion | až po finálních číslech; čísla už jsou | **otevřené** |
| Code Availability za Data Availability | Elena; `@MikovaCode2026`; runner nejmenovat v Methods | **až řeknete** |
| Formal analysis `xxx` | CRediT | **otevřené** |
| Related identifiers mezi třemi Zenodo + GitHub tag | freeze, na který DOI míří | **otevřené** |
| `_pack.py` čtvrtá složka OR | sloučit kopii SI do dataset zipu | **otevřené** |
| Figure 3 workflow bez Napkin | SN AI | **otevřené** |
| Figure 2 | web app, 46/46 | **hotovo** (PNG nepřepisovat) |
| Veřejný GitHub `UAS-review-public` | zrcadlo bez `99_temp/` | skript `70_scripts/sync_public.py`; hook + Action |
| Scoring / merge znovu nespouštět | lock + aktuální 1146/49/46 | **nechat** |

Osobní koncepty (`navrhy-upravy-spoluautori.md`, staré kapitoly, zadání OR 8, kopie z jiných PC) jsou v **`99_temp/`** — jen na tomto počítači, ne na GitHubu.

---

## 11. Odkazy na pokyny

- Časopis: <https://www.springer.com/journal/11119/submission-guidelines>
- Šablona (lokálně): `2026 Review_TempHumidity/SpringerNature.pdf`
- SN AI: <https://www.springernature.com/gp/policies/editorial-policies/ai-manuscript-preparation>
- PRISMA 2020: Page et al. 2021; flow: Haddaway web app `@PRISMAfd2022`
- Zenodo balení: `99_aux/zenodo/README.md`
- Veřejné zrcadlo: `70_scripts/sync_public.py` → `https://github.com/LenkaMikova/UAS-review-public`
