import {
  Button,
  Callout,
  Card,
  CardBody,
  CardHeader,
  Code,
  CollapsibleSection,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  TodoListCard,
  useCanvasAction,
  useCanvasState,
} from "cursor/canvas";

type Kind = "broken" | "cut" | "rewrite" | "hole" | "keep";
type Status = "open" | "done";
type Filter = "now" | "cut" | "rewrite" | "hole" | "keep" | "done" | "all";
type Verdict = "pending" | "accept" | "reject";

type AiEdit = {
  id: string;
  who: string;
  section: string;
  line: number;
  original: string;
  next: string;
};

type PendingComment = {
  id: string;
  who: string;
  section: string;
  line: number;
  endLine: number;
  proposal: string;
};

type Finding = {
  id: string;
  section: string;
  line: number;
  endLine: number;
  kind: Kind;
  status: Status;
  who: string;
  sentence: string;
  doThis: string;
};

const FINDINGS: Finding[] = [
  {
    id: "fig-dist-break",
    section: "Dataset Overview — Figure 5 rozbité",
    line: 807,
    endLine: 832,
    kind: "broken",
    status: "done",
    who: "tělo",
    sentence:
      "campaign or a ground network)… **Data fusion** denotes studie  +  That remainder includes none … UAVs that combine observations",
    doThis:
      "Smazat fragment za KONTROLA UKONCENA ZDE. Obnovit dva odstavce: auto vs ručně, pak čtyři definice. Teď je první slepený. 22/26 do těla ne.",
  },
  {
    id: "skeleton-bullets",
    section: "Trends Conclusions — odrážky",
    line: 1592,
    endLine: 1592,
    kind: "cut",
    status: "done",
    who: "kluci",
    sentence: "- Open landscape and Heterogeneity  /  - Microclimate changes",
    doThis:
      "Smazat. Kostra, ne věty. TIR už je v Drone studies.",
  },
  {
    id: "discussion-copy",
    section: "Discussion — battery / VLOS / swarms",
    line: 1591,
    endLine: 1718,
    kind: "cut",
    status: "open",
    who: "TEXT QUALITY + kluci",
    sentence:
      "UAS are being used with increasing frequency… limited battery capacity… autonomous UAV swarms",
    doThis:
      "Kapitolu nesmazat. Nahradit českými návrhy v komentářích: Major Findings = audit 46 studií; Limitations = díry v reportech; Future = jedna sada, ne Table 12 podruhé.",
  },
  {
    id: "methods-energy",
    section: "Methods — chybí TSEB / PROSAIL",
    line: 1462,
    endLine: 1473,
    kind: "hole",
    status: "done",
    who: "TEXT QUALITY + kluci",
    sentence:
      "Methods for estimating SMC range from empirical… (@tbl-methods).",
    doThis:
      "Dopiš jeden odstavec za tu větu. Český nástřel je v komentáři: Tauro/Chandel/Basurto-Lozada (energie) a Dopper/Chakhar/Shokati (RTM), R² 0.40–0.84.",
  },
  {
    id: "implications",
    section: "Limitations — Implications",
    line: 1878,
    endLine: 1896,
    kind: "hole",
    status: "done",
    who: "kluci",
    sentence: "Finally, relevance scoring… Additionally, the classification of potential UAV applicability…",
    doThis:
      "Dopiš 2–3 věty Implications za Limitations (checklist pro autory). Finally a Additionally nespojovat — UAV-potential sloučit do First.",
  },
  {
    id: "abstract",
    section: "Abstract",
    line: 186,
    endLine: 250,
    kind: "hole",
    status: "open",
    who: "Elena",
    sentence:
      "Highlights + Impact + Purpose/Methods/Results/Conclusion jsou v těle. Results/Conclusion dopsat po číslech.",
    doThis:
      "Až na konec. Větu o satelitech vs UAV v Results nech. Zkratky: UAV a PRISMA už rozepsané; v těle znovu.",
  },
  {
    id: "dataset-grammar",
    section: "Dataset Overview — gramatika",
    line: 626,
    endLine: 632,
    kind: "rewrite",
    status: "done",
    who: "Elena + kluci",
    sentence: "The relevance score (0-8) was assigned each record based in the title…",
    doThis:
      "was assigned to each record based on. Workflow: The same script than assigned → then. Minulý čas nechat. Názvy skriptů už pryč.",
  },
  {
    id: "vos",
    section: "VOSviewer — surová čísla",
    line: 724,
    endLine: 728,
    kind: "rewrite",
    status: "done",
    who: "kluci",
    sentence: "There were 275 links, and the total link strength reached 1,074.",
    doThis:
      "Jedna věta: 26 keywords (occurrence ≥ 5) formed four clusters; link strength = summed co-occurrence across 48 must-cite records. Nastavení VOSviewer nechat. 48 ≠ 45.",
  },
  {
    id: "48-vs-45",
    section: "48 vs 45 + zemědělství",
    line: 834,
    endLine: 848,
    kind: "rewrite",
    status: "done",
    who: "kluci",
    sentence:
      "The majority of the must-cite studies focused on agricultural applications… remaining 3 records are not additional studies",
    doThis:
      "Hussain / Surendran / Montzka nahoru hned po Figure 5. OR 8–10 citovat jednou. Tři věty zemědělství / satelit / UAV sloučit.",
  },
  {
    id: "trends-heading",
    section: "Trends — dvojí nadpis",
    line: 858,
    endLine: 862,
    kind: "rewrite",
    status: "done",
    who: "Elena + kluci",
    sentence:
      "Trends of Soil Moisture Content in 2019-2026 (Developments in Soil Moisture Estimation in 2019-2026)",
    doThis: "Nechat jednu variantu: Developments in Soil Moisture Estimation, 2019–2026.",
  },
  {
    id: "history-lead",
    section: "Historical Progress — první věta",
    line: 271,
    endLine: 277,
    kind: "rewrite",
    status: "done",
    who: "Elena",
    sentence:
      "The evolution of SM monitoring (@tbl-history, @fig-history) reflects a progression from point-scale measurements and coarse-resolution observations to multi-source observation and retrieval frameworks",
    doThis:
      "Odmítnuto 20. 11. večer — vrácena původní věta. Komentář: opraveno AI, odmítnuto. Tři éry pod tabulkou neřezat.",
  },
  {
    id: "github-and",
    section: "Methods úvod — GitHub",
    line: 477,
    endLine: 478,
    kind: "rewrite",
    status: "done",
    who: "Elena",
    sentence: "Development versions are maintained on GitHub (UAS-review and PRISMAtools).",
    doThis: "Hotovo — and už v těle je. Code Availability až řeknete; runner nejmenovat.",
  },
  {
    id: "sensors-hs",
    section: "Type of Sensors — HS buňka + dichotomie",
    line: 931,
    endLine: 942,
    kind: "rewrite",
    status: "done",
    who: "kluci",
    sentence:
      "Passive optical scanning in hundreds of narrow continuous bands… detailed information… deeper soil horizons",
    doThis:
      "Hotovo. Věta k Table 5: two groups (proxies vs dielectric/hydrogen). detailed → proxy. CRNS 10–50 cm v Geophysical.",
  },
  {
    id: "applications-sentences",
    section: "Applications — Chakhar / Dopper",
    line: 1409,
    endLine: 1434,
    kind: "rewrite",
    status: "done",
    who: "kluci",
    sentence:
      "volume scattering within the vegetation layer dominates… Specifically, @Dopper2022 demonstrated…",
    doThis:
      "Cibuli rozpůlit. Dopper u thatch jednou (Ye2024 druhá citace). Shokati / Chakhar / Dopper neřezat.",
  },
  {
    id: "lidar-typo",
    section: "Inputs — Hight / ans",
    line: 1316,
    endLine: 1330,
    kind: "rewrite",
    status: "done",
    who: "TEXT QUALITY",
    sentence: "LiDAR is used as CHM (Canopy Hight Model) ans DSM… High penetration capability…",
    doThis:
      "Height; and. V Table 9 Microwave: utility = dielektrikum / backscatter, ne penetrace oblaků.",
  },
  {
    id: "asprs-table7",
    section: "Drone studies — ASPRS / Table 7",
    line: 1122,
    endLine: 1230,
    kind: "rewrite",
    status: "done",
    who: "METADATA + kluci",
    sentence:
      "2. Sensor specification … Checkpoint Sample Size (ASPRS N >= 30) 0.0%",
    doThis:
      "Hotovo v odstavci pod Table 8: N≥30 jen u mapové třídy; díry bez %; DOI/licence ≠ paper. Nad tím už není these two frameworks.",
  },
  {
    id: "asprs-vs-own",
    section: "ASPRS vs vlastní 25-item checklist",
    line: 1190,
    endLine: 1230,
    kind: "rewrite",
    status: "done",
    who: "METADATA + Lenka",
    sentence:
      "We cite that standard as a geodetic reference, not as a second reporting checklist. Reporting was evaluated against 25 Layer 1 items…",
    doThis:
      "Hotovo v metadatech. Conclusion pořád Core/Q/Full + ASPRS Geodetic (wait-conclusion).",
  },
  {
    id: "three-endings",
    section: "Trends Conclusions vs Discussion vs Conclusion",
    line: 1475,
    endLine: 1849,
    kind: "rewrite",
    status: "open",
    who: "kluci + TEXT QUALITY",
    sentence:
      "Conclusions, Limitations and Perspectives  +  Core / Quantitative / Full in Conclusion",
    doThis:
      "Nadpis už je Synthesis. Zbývá Conclusion vs Aim (Core/Q/Full) a přepis Discussion po nových číslech.",
  },
  {
    id: "ack-typos",
    section: "Acknowledgments",
    line: 1903,
    endLine: 1938,
    kind: "rewrite",
    status: "done",
    who: "Elena",
    sentence: "final manucript review… check the manuscript for compilance",
    doThis:
      "manucript → manuscript; compilance → compliance. Až budete Sensors/Drone studies editovat: acknowledgment vs Pangram 100 % AI.",
  },
  {
    id: "does-not-aim",
    section: "Type of Platforms — does not aim",
    line: 904,
    endLine: 911,
    kind: "cut",
    status: "done",
    who: "kluci",
    sentence: "Current research does not aim to replace spaceborne platforms but rather…",
    doThis: "Už pryč. Teď: Current research relies on multi-source data fusion.",
  },
  {
    id: "methods-textbook",
    section: "Methods — učebnicové věty",
    line: 1420,
    endLine: 1421,
    kind: "cut",
    status: "done",
    who: "TEXT QUALITY",
    sentence: "highly flexible… overfitting… black-box nature",
    doThis: "Už pryč. Energie/RTM je v Dopsat.",
  },
  {
    id: "chavez",
    section: "Chavez — HTML komentář",
    line: 1216,
    endLine: 1216,
    kind: "cut",
    status: "done",
    who: "TEXT QUALITY",
    sentence: "<!-- The ability to vary flight characteristics… (@Chavez2020) -->",
    doThis: "Už pryč.",
  },
  {
    id: "despite",
    section: "Po Table 3 — most k Aim",
    line: 409,
    endLine: 411,
    kind: "cut",
    status: "done",
    who: "Elena + kluci",
    sentence: "Despite this clear trend toward multi-source integration…",
    doThis: "Už pryč. Kapitola končí Table 3.",
  },
  {
    id: "trends-intro",
    section: "Trends — první dvě věty",
    line: 866,
    endLine: 868,
    kind: "cut",
    status: "done",
    who: "Elena + TEXT QUALITY",
    sentence: "most important biophysical… gradual development of platforms and sensors",
    doThis: "Už pryč. Kapitola začíná The short tables in this chapter…",
  },
  {
    id: "platforms-para",
    section: "Type of Platforms — poslední odstavec",
    line: 912,
    endLine: 915,
    kind: "cut",
    status: "done",
    who: "Elena + kluci",
    sentence: "However, the use of a combinations platforms…",
    doThis: "Už pryč.",
  },
  {
    id: "pa50",
    section: "Type of Sensors — Precision Agriculture 5.0",
    line: 983,
    endLine: 989,
    kind: "cut",
    status: "done",
    who: "kluci",
    sentence: "Precision Agriculture 5.0 is therefore shifting away…",
    doThis: "Už pryč. Teď: Several of the reviewed studies fuse data from multiple sensors.",
  },
  {
    id: "significant-number",
    section: "Existing reviews",
    line: 367,
    endLine: 367,
    kind: "cut",
    status: "done",
    who: "TEXT QUALITY",
    sentence: "A significant number of review articles have been published…",
    doThis: "Už pryč.",
  },
  {
    id: "leftover",
    section: "Dataset Overview — leftover odstavce",
    line: 851,
    endLine: 852,
    kind: "cut",
    status: "done",
    who: "kluci + TEXT QUALITY",
    sentence: "Scaling-related… irrigation dominant… transferable satellite studies",
    doThis: "Už pryč.",
  },
  {
    id: "clear-distinction",
    section: "Dataset Overview — clear distinction",
    line: 620,
    endLine: 623,
    kind: "cut",
    status: "done",
    who: "kluci",
    sentence: "This classification allows a clear distinction…",
    doThis: "Už pryč.",
  },
  {
    id: "fig-shown",
    section: "Data Selection — shown a total",
    line: 527,
    endLine: 529,
    kind: "cut",
    status: "done",
    who: "TEXT QUALITY",
    sentence: "@fig-prismadig shown a total of…",
    doThis: "Už pryč. Počty z stats_r.",
  },
  {
    id: "tir-move",
    section: "TIR přesunuto do Drone studies",
    line: 1044,
    endLine: 1082,
    kind: "keep",
    status: "done",
    who: "TEXT QUALITY",
    sentence: "UAV-based TIR… microbolometers… NRCT… mixed-pixel effects",
    doThis: "Hotovo. V Trends Conclusions je komentář PŘESUNUTO.",
  },
  {
    id: "twins",
    section: "Table 3 — Digital Twins",
    line: 403,
    endLine: 403,
    kind: "keep",
    status: "done",
    who: "TEXT QUALITY",
    sentence: "Digital twins appear in reviews as an emerging framing",
    doThis: "Hotovo. Ne operational irrigation.",
  },
  {
    id: "inputs-rewrite",
    section: "Inputs — vrstvy",
    line: 1273,
    endLine: 1290,
    kind: "keep",
    status: "done",
    who: "TEXT QUALITY",
    sentence: "MS and RGB data enter as NDVI, EVI or NDRE… Hyperspectral retrievals use narrow water-absorption bands",
    doThis: "Hotovo. Hight/ans schváleno.",
  },
  {
    id: "abstract-subset",
    section: "Abstract — UAV vs satelit",
    line: 200,
    endLine: 202,
    kind: "keep",
    status: "open",
    who: "Elena chtěla vyhodit; nechat",
    sentence:
      "Satellite-based studies dominated the full dataset, while UAV-related studies represented a smaller but methodologically important subset.",
    doThis:
      "Nechat. Must-cite už je priority subset after scoring. Tahle věta je podíl UAV vs satelit.",
  },
  {
    id: "applications",
    section: "Applications",
    line: 1345,
    endLine: 1396,
    kind: "keep",
    status: "open",
    who: "TEXT QUALITY",
    sentence: "Chakhar (IEM+WCM), Shokati (holá půda), Dopper (thatch / PROSAIL).",
    doThis: "Nejlepší část těla — neřezat. Jen dvě věty v Předělat.",
  },
  {
    id: "drones",
    section: "Drone studies",
    line: 994,
    endLine: 1082,
    kind: "keep",
    status: "open",
    who: "TEXT QUALITY",
    sentence: "TIR overlap, HS integrační čas, GNSS-R/LiDAR. TIR z Trends Conclusions už tady.",
    doThis: "Neřezat. ASPRS / Table 7 je v Předělat.",
  },
  {
    id: "dataset",
    section: "Dataset Overview — příběh",
    line: 627,
    endLine: 675,
    kind: "keep",
    status: "open",
    who: "Elena + TEXT QUALITY",
    sentence: "Skóre 0–8 → include/maybe/exclude → must-cite 49 → extrakce 46.",
    doThis: "Příběh neřezat. Gramatika a 49 vs 46 jsou v Předělat. @Guo2026 (Fenhe) je v OR 9–11.",
  },
  {
    id: "distribution",
    section: "fig-distribution — definice",
    line: 802,
    endLine: 819,
    kind: "keep",
    status: "open",
    who: "TEXT QUALITY",
    sentence: "V těle automaticky vs ručně + čtyři definice. 22/26 je v komentáři.",
    doThis: "Hotovo — komentář smazán, odstavce nechat. 22/26 do článku ne.",
  },
  {
    id: "aim",
    section: "Aim and Scope",
    line: 425,
    endLine: 453,
    kind: "keep",
    status: "open",
    who: "kluci",
    sentence: "25-item reporting checklist and an SM-specific module… yield prediction or disease detection are outside the scope.",
    doThis: "Nesmazávej. Conclusion s tím sladit (teď říká Core/Q/Full).",
  },
  {
    id: "importance",
    section: "Importance of Soil Moisture",
    line: 226,
    endLine: 246,
    kind: "keep",
    status: "open",
    who: "kluci",
    sentence: "Odstavec 1: půda je důležitá. Odstavec 2: SM je složité měřit.",
    doThis: "Nesmazávej kapitolu.",
  },
  {
    id: "history-eras",
    section: "Historical Progress — tři éry",
    line: 280,
    endLine: 329,
    kind: "keep",
    status: "open",
    who: "TEXT QUALITY",
    sentence: "Tři éry pod tabulkou: scatterometry → SMOS/SMAP → UAS.",
    doThis: "Neřezat. Jen první větu zjednodušit (Předělat).",
  },
  {
    id: "data-selection",
    section: "Data Selection",
    line: 515,
    endLine: 531,
    kind: "keep",
    status: "open",
    who: "Elena",
    sentence: "Five thematic groups… title, abstract, and keywords… 2019–2026",
    doThis: "Kontrolu sem nevracet. Značka KONTROLA UKONCENA ZDE je až za Figure 5.",
  },
];

const AI_EDITS: AiEdit[] = [
  { id: "ai-hist", who: "Elena", section: "Historical — první věta", line: 271, original: "The evolution of SM monitoring … multi-platform data fusion", next: "@tbl-history and @fig-history periodize SM monitoring from in-situ and scatterometer observations to multi-platform fusion" },
  { id: "ai-fig3", who: "Elena", section: "Figure 3 caption", line: 594, original: "jen Processing, classification, and screening workflow", next: "stejná legenda auto/ručně jako u Figure 2" },
  { id: "ai-gram", who: "Elena + kluci", section: "Dataset Overview — gramatika", line: 626, original: "was assigned each record based in … Keywords weights", next: "was assigned to each record based on … Keyword weights" },
  { id: "ai-trends", who: "Elena + kluci", section: "Nadpis Trends", line: 859, original: "Trends of Soil Moisture Content… (Developments…)", next: "Developments in Soil Moisture Estimation, 2019–2026" },
  { id: "ai-ack", who: "Elena", section: "Acknowledgments", line: 1931, original: "manucript; compilance", next: "manuscript; compliance" },
  { id: "ai-than", who: "kluci", section: "Workflow — than", line: 569, original: "The same script than assigned", next: "The same script then assigned" },
  { id: "ai-vos", who: "kluci", section: "VOSviewer", line: 724, original: "275 links … total link strength 1,074", next: "26 keywords (occurrence ≥ 5) formed four clusters; link strength is the summed co-occurrence weight across the 48 must-cite records" },
  { id: "ai-fig5", who: "kluci", section: "Figure 5 + 48 vs 45", line: 807, original: "fragment campaign or a ground network; slepené none/fusion; 48 vs 45 až dole", next: "dva odstavce (auto vs ručně; čtyři definice); 48 vs 45 hned pod Figure 5; OR 8–10 jednou" },
  { id: "ai-hs", who: "kluci", section: "HS buňka Table 5", line: 939, original: "scanning in hundreds of narrow continuous bands; Limits data reduction", next: "imaging in tens to hundreds of contiguous narrow bands; Limits collinearity / SNR / calibration" },
  { id: "ai-geo", who: "kluci", section: "Geophysical Table 5", line: 941, original: "deeper soil horizons", next: "GPR root-zone profile; CRNS ~10–50 cm, hectare footprint" },
  { id: "ai-dich", who: "kluci", section: "Sensors — dichotomie", line: 950, original: "fundamental physical dichotomy + detailed information", next: "The sensors in @tbl-sensors fall into two groups: vegetation/surface proxies vs dielectric permittivity or hydrogen" },
  { id: "ai-gpr", who: "kluci", section: "GPR odstavec", line: 982, original: "vertical soil profiles", next: "root-zone profiles" },
  { id: "ai-rgb", who: "kluci", section: "Drone studies", line: 1047, original: "For optical and multispectral mapping", next: "For RGB and multispectral mapping" },
  { id: "ai-t7", who: "kluci", section: "Table 7 číslování", line: 1138, original: "začíná 2. Sensor specification", next: "věta: group 1 je v Table 8" },
  { id: "ai-asprs", who: "kluci", section: "ASPRS odstavec", line: 1239, original: "None … met N≥30; 12 metadata categories", next: "N≥30 jen když se tvrdí mapová třída; v textu červené položky; 25 Layer 1" },
  { id: "ai-lidar", who: "kluci", section: "LiDAR", line: 1316, original: "Hight / ans", next: "Height / and" },
  { id: "ai-mw", who: "kluci", section: "Table 9 Microwave", line: 1330, original: "High penetration capability through clouds…", next: "Dielectric constant and VV/VH backscatter as the SM-sensitive input" },
  { id: "ai-app", who: "kluci", section: "Applications úvod", line: 1378, original: "vary significantly across different agricultural land cover types", next: "vary across land-cover types" },
  { id: "ai-chak", who: "kluci", section: "Chakhar cibule", line: 1409, original: "jedna dlouhá věta barley → onion / volume scattering", next: "rané fáze; pak hustá cibule, C-pásmo půdu nevidí" },
  { id: "ai-dop", who: "kluci", section: "Dopper thatch", line: 1429, original: "Dopper dvakrát + Ye u thatch", next: "Ye u thatch; PROSAIL jen Dopper" },
  { id: "ai-rtm", who: "kluci", section: "Methods energie/RTM", line: 1462, original: "pod tabulkou jen jedna věta", next: "TSEB/SEBAL/METRIC (Tauro, Chandel, Basurto-Lozada); PROSAIL/WCM/MARMIT; R² 0.40–0.84" },
  { id: "ai-syn", who: "kluci", section: "Nadpis Trends conclusions", line: 1491, original: "Conclusions, Limitations and Perspectives", next: "Synthesis of 2019–2026 developments" },
  { id: "ai-lim", who: "kluci", section: "Limitations + Implications", line: 1878, original: "Finally … Additionally (UAV-potential zvlášť); Implications chyběly", next: "UAV-potential v First; odstavec Implications (checklist, ne agenda)" },
];

const WAITING: PendingComment[] = [
  {
    id: "wait-discussion",
    who: "kluci + TEXT QUALITY",
    section: "Discussion — battery / VLOS / swarms",
    line: 1591,
    endLine: 1718,
    proposal:
      "Kapitolu nesmazat. Po číslech nahradit českými návrhy: Major Findings = audit 46 studií; Limitations = díry v reportech; Future = jedna sada, ne Table 12 podruhé.",
  },
  {
    id: "wait-conclusion",
    who: "METADATA",
    section: "Conclusion — Core/Q/Full",
    line: 1829,
    endLine: 1849,
    proposal:
      "Sladit s Aim: 25položkový checklist + SM modul. Core/Q/Full a ASPRS Geodetic jsou schema datasetu, ne povinnost článku.",
  },
  {
    id: "wait-abstract",
    who: "Elena",
    section: "Abstract",
    line: 186,
    endLine: 250,
    proposal:
      "Až na konec. Větu o satelitech vs UAV v Results nechat. Kostra Purpose/Methods/Results/Conclusion už je v těle.",
  },
];

/** Snapshot from canvas verdicts at apply time (20. 11. 2026 večer). Live Přijmout/Odmítnout can still change remaining pending rows. */
const APPLIED: Record<string, Verdict> = {
  "ai-hist": "reject",
  "ai-fig3": "accept",
  "ai-gram": "accept",
  "ai-trends": "accept",
  "ai-ack": "accept",
  "ai-than": "accept",
  "ai-vos": "accept",
  "ai-fig5": "accept",
  "ai-hs": "accept",
  "ai-dich": "accept",
  "ai-geo": "accept",
  "ai-gpr": "accept",
  "ai-rgb": "accept",
  "ai-t7": "accept",
  "ai-asprs": "accept",
  "ai-lidar": "accept",
  "ai-mw": "accept",
  "ai-app": "accept",
  "ai-chak": "accept",
  "ai-dop": "accept",
  "ai-rtm": "accept",
  "ai-syn": "accept",
  "ai-lim": "accept",
  "wait-asprs-own": "accept",
};

function appliedOf(id: string): Verdict {
  return APPLIED[id] ?? "pending";
}

const KIND_LABEL: Record<Kind, string> = {
  broken: "Rozbité",
  cut: "Smazat",
  rewrite: "Předělat",
  hole: "Dopsat",
  keep: "Nechat",
};

const KIND_TONE: Record<Kind, "danger" | "warning" | "success" | "info" | "neutral"> = {
  broken: "danger",
  cut: "danger",
  rewrite: "warning",
  hole: "info",
  keep: "success",
};

const FILTERS: { id: Filter; label: string }[] = [
  { id: "now", label: "Zbývá" },
  { id: "cut", label: "Smazat / rozbité" },
  { id: "rewrite", label: "Předělat" },
  { id: "hole", label: "Dopsat" },
  { id: "keep", label: "Nechat" },
  { id: "done", label: "Už smazáno" },
  { id: "all", label: "Vše" },
];

function verdictOf(decisions: Record<string, Verdict>, id: string): Verdict {
  return decisions[id] ?? "pending";
}

function VerdictButtons({
  id,
  decisions,
  setDecisions,
}: {
  id: string;
  decisions: Record<string, Verdict>;
  setDecisions: (value: Record<string, Verdict> | ((prev: Record<string, Verdict>) => Record<string, Verdict>)) => void;
}) {
  const v = verdictOf(decisions, id);
  const set = (next: Verdict) =>
    setDecisions((prev) => ({ ...prev, [id]: next }));
  return (
    <Row gap={6} wrap>
      <Pill active={v === "accept"} onClick={() => set("accept")}>
        Přijmout
      </Pill>
      <Pill active={v === "reject"} onClick={() => set("reject")}>
        Odmítnout
      </Pill>
      <Pill active={v === "pending"} onClick={() => set("pending")}>
        Ještě ne
      </Pill>
    </Row>
  );
}

function JumpToReview({
  label,
  line,
  endLine,
}: {
  label: string;
  line: number;
  endLine: number;
}) {
  const dispatch = useCanvasAction();
  return (
    <Button
      variant="ghost"
      onClick={() =>
        dispatch({
          type: "openFile",
          path: "90_review/review.qmd",
          selection: {
            startLineNumber: line,
            startColumn: 1,
            endLineNumber: endLine,
            endColumn: 120,
          },
        })
      }
    >
      {label}
    </Button>
  );
}

function openFinding(
  dispatch: (action: {
    type: "openFile";
    path: string;
    selection: {
      startLineNumber: number;
      startColumn: number;
      endLineNumber: number;
      endColumn: number;
    };
  }) => void,
  f: Finding,
) {
  dispatch({
    type: "openFile",
    path: "90_review/review.qmd",
    selection: {
      startLineNumber: f.line,
      startColumn: 1,
      endLineNumber: f.endLine,
      endColumn: 120,
    },
  });
}

export default function TextQualityReview() {
  const [filter, setFilter] = useCanvasState<Filter>("filter", "now");
  const [decisions, setDecisions] = useCanvasState<Record<string, Verdict>>(
    "verdicts",
    {},
  );
  const dispatch = useCanvasAction();
  const openAi = AI_EDITS.filter((e) => appliedOf(e.id) === "pending");
  const openWaiting = WAITING.filter((e) => appliedOf(e.id) === "pending");
  const nDone = [...AI_EDITS, ...WAITING].filter(
    (e) => appliedOf(e.id) !== "pending",
  ).length;
  const nPending = [...openAi, ...openWaiting].filter(
    (e) => verdictOf(decisions, e.id) === "pending",
  ).length;

  const openCuts = FINDINGS.filter((f) => f.kind === "cut" && f.status === "open");
  const doneCuts = FINDINGS.filter((f) => f.kind === "cut" && f.status === "done");
  const rewrites = FINDINGS.filter((f) => f.kind === "rewrite" && f.status === "open");
  const holes = FINDINGS.filter((f) => f.kind === "hole" && f.status === "open");
  const keeps = FINDINGS.filter((f) => f.kind === "keep" && f.status === "open");

  const remaining = FINDINGS.filter(
    (f) => f.status === "open" && f.kind !== "keep",
  );

  const rows = FINDINGS.filter((f) => {
    if (filter === "all") return true;
    if (filter === "done") return f.status === "done";
    if (filter === "now") return f.status === "open" && f.kind !== "keep";
    if (filter === "cut") return f.status === "open" && (f.kind === "cut" || f.kind === "broken");
    if (filter === "keep") return f.kind === "keep" && f.status === "open";
    return f.kind === filter && f.status === "open";
  });

  const order = [
    FINDINGS.find((f) => f.id === "discussion-copy"),
    FINDINGS.find((f) => f.id === "three-endings"),
    FINDINGS.find((f) => f.id === "abstract"),
  ].filter((f): f is Finding => Boolean(f));

  return (
    <Stack gap={20}>
      <Stack gap={6}>
        <H1>Text quality — 20. 11. 2026 večer</H1>
        <Text tone="secondary">
          Elena/kluci v těle uzavřeno (21× schváleno v komentáři, Historical
          vráceno, Figure 5 a dichotomie bez komentáře). ASPRS v metadatech
          = geodetický odkaz, skóre = 25 Layer 1. Highlights/Impact v
          těle. Zbývá Discussion, Conclusion vs Aim, dopsat Abstract —
          až po číslech.
        </Text>
      </Stack>

      <Grid columns={3} gap={12}>
        <Stat value={nDone} label="Už zapracováno" tone="success" />
        <Stat value={nPending} label="Ještě nerozhodnuto" tone="warning" />
        <Stat value={remaining.length} label="Zbývá v těle" />
      </Grid>

      <Callout tone="neutral" title="Už zapracováno">
        V review.qmd: 21× opraveno AI, schváleno; 1× odmítnuto
        (Historical). Figure 5 a dichotomie: komentář smazán, text
        zůstal. Až zbývající komentáře smažete, podle značky poznáte, co
        v textu zůstalo.
      </Callout>

      {openAi.length > 0 ? (
        <Stack gap={8}>
          <H2>V těle — ještě bez rozhodnutí</H2>
          <Table
            headers={["Kdo", "Sekce", "Původní", "Nové", "Rozhodnutí"]}
            columnAlign={["left", "left", "left", "left", "left"]}
            striped
            stickyHeader
            rowTone={openAi.map((e) => {
              const v = verdictOf(decisions, e.id);
              if (v === "accept") return "success";
              if (v === "reject") return "danger";
              return "warning";
            })}
            rows={openAi.map((e) => [
              e.who,
              <span key={e.id}>
                <JumpToReview
                  label={e.section}
                  line={e.line}
                  endLine={e.line + 8}
                />
              </span>,
              <Code key={e.id + "-o"}>{e.original}</Code>,
              e.next,
              <span key={e.id + "-v"}>
                <VerdictButtons
                  id={e.id}
                  decisions={decisions}
                  setDecisions={setDecisions}
                />
              </span>,
            ])}
          />
        </Stack>
      ) : null}

      {openWaiting.length > 0 ? (
        <Stack gap={8}>
          <H2>Ještě není v těle</H2>
          <Table
            headers={["Kdo", "Sekce", "Návrh", "Rozhodnutí"]}
            columnAlign={["left", "left", "left", "left"]}
            striped
            stickyHeader
            rowTone={openWaiting.map((e) => {
              const v = verdictOf(decisions, e.id);
              if (v === "accept") return "success";
              if (v === "reject") return "danger";
              return "warning";
            })}
            rows={openWaiting.map((e) => [
              e.who,
              <span key={e.id}>
                <JumpToReview
                  label={e.section}
                  line={e.line}
                  endLine={e.endLine}
                />
              </span>,
              e.proposal,
              <span key={e.id + "-v"}>
                <VerdictButtons
                  id={e.id}
                  decisions={decisions}
                  setDecisions={setDecisions}
                />
              </span>,
            ])}
          />
        </Stack>
      ) : null}

      <Card>
        <CardHeader>Po běhu — klik skočí na místo</CardHeader>
        <CardBody>
          <TodoListCard
            todos={order.map((f, i) => ({
              id: f.id,
              content: `${i + 1}. ${f.section}: ${f.doThis}`,
              status: "pending" as const,
            }))}
            defaultExpanded
            onTodoClick={(todo) => {
              const f = order.find((x) => x.id === todo.id);
              if (f) openFinding(dispatch, f);
            }}
          />
        </CardBody>
      </Card>

      <H2>Zbývá v těle</H2>
      <Text tone="secondary" size="small">
        {remaining.length} položek. Filtr Zbývá = vše otevřené kromě Nechat.
        České návrhy v HTML komentářích nejsou článek — do těla až po vašem
        překladu.
      </Text>
      <Row gap={8} wrap>
        {FILTERS.map((f) => (
          <span key={f.id}>
            <Pill active={filter === f.id} onClick={() => setFilter(f.id)}>
              {f.label}
            </Pill>
          </span>
        ))}
      </Row>

      {rows.length > 0 ? (
        <Table
          headers={["Sekce", "Typ", "Kdo", "Anglická věta", "Co udělat"]}
          columnAlign={["left", "left", "left", "left", "left"]}
          striped
          stickyHeader
          rowTone={rows.map((r) =>
            r.status === "done" ? "success" : KIND_TONE[r.kind],
          )}
          rows={rows.map((r) => [
            <span key={r.id}>
              <JumpToReview label={r.section} line={r.line} endLine={r.endLine} />
            </span>,
            r.status === "done" ? "Už pryč" : KIND_LABEL[r.kind],
            r.who,
            <Code key={r.id + "-q"}>{r.sentence}</Code>,
            r.doThis,
          ])}
        />
      ) : null}

      <Divider />

      <H2>Nechat — nesahej teď</H2>
      <Grid columns={2} gap={16}>
        {keeps.map((k) => (
          <Stack key={k.id} gap={4}>
            <H3>{k.section}</H3>
            <Text>{k.doThis}</Text>
          </Stack>
        ))}
      </Grid>

      <CollapsibleSection title="Už smazáno" count={doneCuts.length}>
        <Table
          headers={["Sekce", "Co tam bylo"]}
          columnAlign={["left", "left"]}
          striped
          rows={doneCuts.map((r) => [
            <span key={r.id}>
              <JumpToReview label={r.section} line={r.line} endLine={r.endLine} />
            </span>,
            r.sentence,
          ])}
        />
      </CollapsibleSection>

      <Callout tone="neutral" title="Diagramy, DOI, odeslání">
        Figure 2: Haddaway web app; 46/46. How-to OR 6. OR 4, PRISMA-P a
        Generate executed log sladěné (DOI retained; tři Zenodo). Code
        Availability až řeknete. Formal analysis xxx. Scoring nespouštět.
        Make PNG v runneru nepoužívat.
      </Callout>
    </Stack>
  );
}
