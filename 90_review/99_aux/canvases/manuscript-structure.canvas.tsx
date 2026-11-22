import {
  Callout,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  Stack,
  Stat,
  Table,
  Text,
  useHostTheme,
} from "cursor/canvas";

type Node = {
  kind: "table" | "figure" | "or" | "text";
  num?: string;
  id?: string;
  meta?: string;
};

type Link = { body: Node; or: Node | null };
type Section = { sub: string; rows: Link[] };
type Chapter = { title: string; sections: Section[] };

const TEXT_ONLY: Node = { kind: "text" };

const CHAPTERS: Chapter[] = [
  {
    title: "Introduction",
    sections: [
      {
        sub: "Historical Progress",
        rows: [
          {
            body: { kind: "table", num: "Table 1", id: "tbl-history", meta: "5 ř. · category" },
            or: { kind: "or", num: "OR 1", id: "or-reviews", meta: "30 ř. · review (první v popisku)" },
          },
          {
            body: { kind: "table", num: "Table 1", id: "tbl-history", meta: "5 ř. · category" },
            or: { kind: "or", num: "OR 2", id: "or-icons", meta: "legenda" },
          },
          { body: { kind: "figure", num: "Figure 1", id: "fig-history" }, or: null },
        ],
      },
      {
        sub: "Existing reviews and Research Gap",
        rows: [
          {
            body: TEXT_ONLY,
            or: { kind: "or", num: "OR 1", id: "or-reviews", meta: "už citováno v Table 1" },
          },
          {
            body: {
              kind: "table",
              num: "Table 2",
              id: "tbl-review-category",
              meta: "3 ř. · review",
            },
            or: null,
          },
          {
            body: {
              kind: "table",
              num: "Table 3",
              id: "tbl-review-sm",
              meta: "3 ř. · review",
            },
            or: { kind: "or", num: "OR 3", id: "or-fusion", meta: "7 ř. · review" },
          },
        ],
      },
    ],
  },
  {
    title: "Review Methodology",
    sections: [
      {
        sub: "(chapter lead)",
        rows: [
          {
            body: { kind: "figure", num: "Figure 2", id: "fig-prismadig" },
            or: {
              kind: "or",
              num: "OR 5",
              id: "or-processing",
              meta: "pipeline",
            },
          },
          {
            body: TEXT_ONLY,
            or: {
              kind: "or",
              num: "OR 4",
              id: "or-prisma-check",
              meta: "PRISMA 2020 checklist",
            },
          },
          {
            body: TEXT_ONLY,
            or: {
              kind: "or",
              num: "OR 6",
              id: "or-prisma-flow",
              meta: "how the diagram was produced",
            },
          },
        ],
      },
      {
        sub: "Data Selection",
        rows: [{ body: TEXT_ONLY, or: { kind: "or", num: "OR 7", id: "or-search", meta: "pipeline" } }],
      },
      {
        sub: "Data Workflow",
        rows: [{ body: { kind: "figure", num: "Figure 3", id: "fig-workflow" }, or: null }],
      },
      {
        sub: "Dataset Overview",
        rows: [
          { body: { kind: "figure", num: "Figure 4", id: "fig-VOS-must" }, or: null },
          { body: { kind: "figure", num: "Figure 5", id: "fig-distribution" }, or: null },
          {
            body: TEXT_ONLY,
            or: { kind: "or", num: "OR 8", id: "or-keywords", meta: "pipeline" },
          },
          {
            body: TEXT_ONLY,
            or: {
              kind: "or",
              num: "OR 9–11",
              id: "or-inputs / applications / methods",
              meta: "46 ř. · must-cite",
            },
          },
          {
            body: TEXT_ONLY,
            or: { kind: "or", num: "OR 12", id: "or-screening", meta: "pipeline" },
          },
        ],
      },
    ],
  },
  {
    title: "Trends 2019–2026",
    sections: [
      {
        sub: "Type of Platforms",
        rows: [
          {
            body: {
              kind: "table",
              num: "Table 4",
              id: "tbl-platforms",
              meta: "5 ř. · category",
            },
            or: { kind: "or", num: "OR 14", id: "or-platforms", meta: "5 ř. · must-cite" },
          },
        ],
      },
      {
        sub: "Type of Sensors",
        rows: [
          {
            body: {
              kind: "table",
              num: "Table 5",
              id: "tbl-sensors",
              meta: "5 ř. · category",
            },
            or: { kind: "or", num: "OR 15", id: "or-sensors", meta: "5 ř. · must-cite" },
          },
        ],
      },
      {
        sub: "Type of Sensors → Drone studies",
        rows: [
          {
            body: { kind: "table", num: "Table 6", id: "tbl-uav", meta: "4 ř. · must-cite" },
            or: { kind: "or", num: "OR 13", id: "or-uav", meta: "10 ř. · must-cite UAV (první v Trends lead)" },
          },
        ],
      },
      {
        sub: "Type of Sensors → Drone studies (ASPRS)",
        rows: [
          {
            body: {
              kind: "table",
              num: "Table 7",
              id: "tbl-uav-param",
              meta: "12 ř. · must-cite",
            },
            or: { kind: "or", num: "OR 16", id: "or-uav-param", meta: "46 ř. · ASPRS 2024" },
          },
        ],
      },
      {
        sub: "Type of Sensors → Drone studies (core params)",
        rows: [
          {
            body: {
              kind: "table",
              num: "Table 8",
              id: "tbl-uav-param-core",
              meta: "25 ř. · Layer 1",
            },
            or: {
              kind: "or",
              num: "OR 17",
              id: "or-uav-param-core",
              meta: "22 ř. teď (cíl 46)",
            },
          },
        ],
      },
      {
        sub: "Applications and Methods → Inputs",
        rows: [
          {
            body: {
              kind: "table",
              num: "Table 9",
              id: "tbl-inputs",
              meta: "6 ř. · category",
            },
            or: { kind: "or", num: "OR 9", id: "or-inputs", meta: "46 ř. · must-cite" },
          },
        ],
      },
      {
        sub: "Applications and Methods → Applications",
        rows: [
          {
            body: {
              kind: "table",
              num: "Table 10",
              id: "tbl-applications",
              meta: "4 ř. · category",
            },
            or: {
              kind: "or",
              num: "OR 10",
              id: "or-applications",
              meta: "46 ř. · must-cite",
            },
          },
        ],
      },
      {
        sub: "Applications and Methods → Methods",
        rows: [
          {
            body: {
              kind: "table",
              num: "Table 11",
              id: "tbl-methods",
              meta: "4 ř. · category",
            },
            or: { kind: "or", num: "OR 11", id: "or-methods", meta: "46 ř. · must-cite" },
          },
        ],
      },
      {
        sub: "Conclusions, Limitations and Perspectives",
        rows: [
          {
            body: {
              kind: "table",
              num: "Table 12",
              id: "tbl-conclusion",
              meta: "4 ř. · periods",
            },
            or: null,
          },
          { body: { kind: "figure", num: "Figure 6", id: "fig-conclusion" }, or: null },
        ],
      },
    ],
  },
  {
    title: "Conclusion",
    sections: [
      {
        sub: "(chapter)",
        rows: [
          {
            body: TEXT_ONLY,
            or: { kind: "or", num: "OR 18", id: "or-metadata", meta: "Layer 1, 25 items" },
          },
          {
            body: TEXT_ONLY,
            or: { kind: "or", num: "OR 19", id: "or-metadata-SM", meta: "SM module" },
          },
        ],
      },
    ],
  },
];

const APPENDIX_ORDER: Array<[string, string, string]> = [
  ["OR 1", "or-reviews", "Vybrané existující review (30 ř.; ne všech 115)"],
  ["OR 2", "or-icons", "Legenda ikon — obě sady"],
  ["OR 3", "or-fusion", "Kombinace platforem a datová fúze (7 ř.)"],
  ["OR 4", "or-prisma-check", "PRISMA 2020 checklist"],
  ["OR 5", "or-processing", "Počty záznamů + log slučování"],
  ["OR 6", "or-prisma-flow", "Jak vznikl PRISMA flow diagram (Haddaway web app estech.shinyapps.io)"],
  ["OR 7", "or-search", "Rešeršní dotazy (WoS, Scopus)"],
  ["OR 8", "or-keywords", "Statistika klíčových slov"],
  ["OR 9", "or-inputs", "Vstupní data podle studií (46)"],
  ["OR 10", "or-applications", "Aplikační prostředí podle studií (46)"],
  ["OR 11", "or-methods", "Metody a přesnosti podle studií (46)"],
  ["OR 12", "or-screening", "Souhrn automatického screeningu"],
  ["OR 13", "or-uav", "Letové parametry kampaní (10 z 46)"],
  ["OR 14", "or-platforms", "Kategorie platforem (5 ř.)"],
  ["OR 15", "or-sensors", "Klasifikace senzorových modalit (5 ř.)"],
  ["OR 16", "or-uav-param", "ASPRS 2024 poziční / fotogrammetrická úplnost (46)"],
  ["OR 17", "or-uav-param-core", "Core / mandatory UAV + SM parametry (teď 22 z 46)"],
  ["OR 18", "or-metadata", "Paper checklist Layer 1 (25 položek)"],
  ["OR 19", "or-metadata-SM", "SM aplikační modul (Mandatory = paper)"],
];

const ICON_SET_LABEL = {
  methods: "platformy",
  land: "land use",
  cat: "kolečka kategorií",
  sensor: "obecné senzory",
} as const;

const ICON_USE: Array<[string, string, keyof typeof ICON_SET_LABEL]> = [
  ["Table 1 · tbl-history", "Platform Paradigm — po obdobích", "cat"],
  ["Table 2 · tbl-review-category", "Sensors used on UAV", "sensor"],
  ["Table 4 · tbl-platforms + or-platforms", "Platform Category", "methods"],
  ["Table 5 · tbl-sensors + or-sensors", "Sensor Category", "sensor"],
  ["Table 6 · tbl-uav + or-uav", "Primary Payload / Study", "sensor"],
  ["Table 9 · tbl-inputs + or-inputs", "Input Modality", "sensor"],
  ["Table 10 · tbl-applications + or-applications", "Target Application", "land"],
  ["or-reviews", "Investigated Platforms", "methods"],
  ["or-fusion", "Platform Combinations", "methods"],
];

function Chip({ node }: { node: Node }) {
  const theme = useHostTheme();

  if (node.kind === "text") {
    return (
      <Text size="small" tone="quaternary" italic>
        jen odkaz v textu
      </Text>
    );
  }

  const isOr = node.kind === "or";
  return (
    <span
      style={{
        display: "inline-flex",
        flexWrap: "wrap",
        alignItems: "baseline",
        gap: 8,
        border: `1px solid ${theme.stroke.tertiary}`,
        borderRadius: 6,
        padding: "3px 8px",
        background: isOr ? theme.fill.tertiary : "transparent",
      }}
    >
      <span
        style={{
          fontSize: 12,
          fontWeight: 590,
          color: isOr ? theme.accent.primary : theme.text.primary,
        }}
      >
        {node.num}
      </span>
      <span
        style={{
          fontFamily: "monospace",
          fontSize: 11,
          color: theme.text.quaternary,
        }}
      >
        {node.id}
      </span>
      {node.meta ? (
        <span style={{ fontSize: 11, color: theme.text.tertiary }}>{node.meta}</span>
      ) : null}
    </span>
  );
}

function LinkLine({ link }: { link: Link }) {
  const theme = useHostTheme();
  return (
    <Grid columns="minmax(0, 1fr) 28px minmax(0, 1fr)" gap={0} align="center">
      <span>
        <Chip node={link.body} />
      </span>
      <span
        style={{
          textAlign: "center",
          color: link.or ? theme.text.tertiary : "transparent",
          fontSize: 13,
        }}
      >
        →
      </span>
      <span>{link.or ? <Chip node={link.or} /> : null}</span>
    </Grid>
  );
}

function ChapterBlock({ chapter }: { chapter: Chapter }) {
  const theme = useHostTheme();
  return (
    <Stack gap={10}>
      <H3>{chapter.title}</H3>
      {chapter.sections.map((section) => (
        <div key={section.sub}>
          <Grid
            columns="minmax(0, 260px) minmax(0, 1fr)"
            gap={16}
            align="start"
            style={{
              borderTop: `1px solid ${theme.stroke.tertiary}`,
              paddingTop: 8,
              paddingBottom: 2,
            }}
          >
            <Text size="small" tone="secondary">
              {section.sub}
            </Text>
            <Stack gap={6}>
              {section.rows.map((row, i) => (
                <div key={`${section.sub}-${i}`}>
                  <LinkLine link={row} />
                </div>
              ))}
            </Stack>
          </Grid>
        </div>
      ))}
    </Stack>
  );
}

export default function ManuscriptStructure() {
  const theme = useHostTheme();

  return (
    <Stack gap={24} style={{ padding: 24, maxWidth: 1080 }}>
      <Stack gap={6}>
        <H1>Tabulky, obrázky a Online Resources</H1>
        <Text tone="secondary">
          Mapa manuskriptu <Text as="span" weight="semibold">review.qmd</Text> a
          přílohy <Text as="span" weight="semibold">92_appendix/or-NN-*.qmd</Text>
          {" · "}22. 11. 2026 (OR 4 + PRISMA-P = Figure 2; 46 studií = OR 9–11). Šipka znamená „krátká tabulka v textu → úplná verze
          v příloze“. GitHub kopie:{" "}
          <Text as="span" weight="semibold">90_review/99_aux/manuscript-structure.md</Text>.
        </Text>
      </Stack>

      <Grid columns={5} gap={16}>
        <Stat value="12" label="tabulek v těle" />
        <Stat value="6" label="obrázky v těle" />
        <Stat value="19" label="Online Resources" />
        <Stat value="46" label="studií v OR 9–11" />
        <Stat value="0" label="ručně psaných čísel" tone="success" />
      </Grid>

      <Callout tone="info" title="Číslování se generuje samo">
        Štítky tabulek, obrázků a OR se číslují z pořadí. Počty z pipeline
        (merged, retained, removed, other_exclusions, must-cite, n_studies, n_uav_campaigns) jdou z{" "}
        <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>stats_r</Text>
        {" "}v{" "}
        <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>_pipeline-stats.qmd</Text>
        . Figure 2 PNG je Haddaway web app (ne Make PNG). Figure 3 ještě kreslený. Prázdný{" "}
        <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>or-studies</Text>{" "}
        se nepoužívá: studie už jsou v OR 9–11.
      </Callout>

      <Callout tone="neutral" title="49 must-cite ≠ 46 unikátních studií">
        Pipeline flag = 49 záznamů (22 core + 27 extended). Syntéza v tabulkách
        = 46 studií + 1 publisher correction k Hussain 2025 + 1 knižní kapitola
        Surendran 2024 + 1 konference Montzka 2020 (SARSense). OR 2 je vybraná
        podmnožina 115 review, ne komplet.
      </Callout>

      <Stack gap={8}>
        <H2>Co píšeš vs. co se vysází</H2>
        <Table
          headers={["Do zdroje napíšeš", "V textu odkážeš", "Vysází se"]}
          rows={[
            ["{#tbl-sensors} u popisku", "@tbl-sensors", "Table 5"],
            ["{#fig-history} u obrázku", "@fig-history", "Figure 1"],
            ["::: {#or-sensors} v příloze", "@or-sensors", "Online Resource 15"],
          ]}
        />
        <Text size="small" tone="tertiary">
          Číslo Online Resource vychází z pořadí bloků v souboru přílohy. Proto platí
          jediné pravidlo: pořadí bloků v příloze musí odpovídat pořadí prvních zmínek
          v textu.
        </Text>
      </Stack>

      <Divider />

      <Stack gap={12}>
        <Stack gap={4}>
          <H2>Ikony v tabulkách</H2>
          <Text size="small" tone="tertiary">
            Dvě zdrojové sady: <Text as="span" weight="semibold">metody a platformy</Text>{" "}
            (setIcons2.png) a{" "}
            <Text as="span" weight="semibold">land use</Text> (setIcons1.png).
            Obě jsou vyobrazené v OR 2. Table 1 cituje nejdřív @or-reviews (OR 1), potom legendu.
          </Text>
          <Text size="small" tone="tertiary">
            Table 1 nese <Text as="span" weight="semibold">kolečka kategorií</Text>{" "}
            (<Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>in-situ</Text>,{" "}
            <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>sat</Text>,{" "}
            <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>drone</Text>,{" "}
            <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>ugv</Text>
            ). Sloupce se senzory používají obecné{" "}
            <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>sensor_*</Text>.
            Ikony <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>drone_*</Text>{" "}
            zůstávají v or-platforms.
          </Text>
        </Stack>

        <Callout tone="warning" title="V tabulkách jen markdown, nikdy <img>">
          Pandoc při exportu do DOCX zahazuje surové HTML. Správně je{" "}
          <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>
            ![](../80_figures/81_icons/drone_ms.png){"{width=40}"}
          </Text>
          . Šířka 60 v kategoriálních tabulkách, 40 v tabulkách po studiích, 45
          u koleček v Table 1.
        </Callout>

        <Grid columns="minmax(0, 1fr) minmax(0, 1fr)" gap={20} align="start">
          <Table
            headers={["Tabulka", "Sloupec s ikonami", "Sada"]}
            rows={ICON_USE.map(([where, column, set]) => [
              where,
              column,
              <span
                key={where}
                style={{
                  color: set === "methods" ? theme.text.secondary : theme.accent.primary,
                  fontWeight: set === "methods" ? 400 : 590,
                }}
              >
                {ICON_SET_LABEL[set]}
              </span>,
            ])}
            striped
          />
          <Stack gap={10}>
            <Card>
              <CardHeader>Bez ikon záměrně</CardHeader>
              <CardBody>
                <Text size="small">
                  Table 3 by na každém řádku nesla tytéž tři ikony platforem.
                  Table 7 (`tbl-uav-param`) a Table 10 (`tbl-methods`) jsou o
                  parametrech a algoritmech — pro ty sada ikon neexistuje.
                </Text>
              </CardBody>
            </Card>
            <Card>
              <CardHeader>Zalomení a pevné mezery</CardHeader>
              <CardBody>
                <Text size="small">
                  <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>
                    &lt;br&gt;
                  </Text>{" "}
                  v DOCX řeší{" "}
                  <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>
                    _filters/linebreaks.lua
                  </Text>
                  . Pevná mezera:{" "}
                  <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>
                    &amp;nbsp;
                  </Text>
                  .
                </Text>
              </CardBody>
            </Card>
          </Stack>
        </Grid>
      </Stack>

      <Divider />

      <Stack gap={20}>
        <Stack gap={4}>
          <H2>Propojení kapitol, tabulek a příloh</H2>
          <Text size="small" tone="tertiary">
            Vlevo to, co je v těle review; vpravo úplná verze v příloze. Řádkové
            počty jsou datové řádky (bez hlavičky).
          </Text>
        </Stack>
        {CHAPTERS.map((chapter) => (
          <div key={chapter.title}>
            <ChapterBlock chapter={chapter} />
          </div>
        ))}
      </Stack>

      <Divider />

      <Grid columns="minmax(0, 3fr) minmax(0, 2fr)" gap={20} align="start">
        <Stack gap={8}>
          <H2>Pořadí v příloze = číslování</H2>
          <Callout tone="info" title="Příloha existuje ve dvou podobách">
            <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>
              review.qmd
            </Text>{" "}
            vkládá jen seznam popisků (
            <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>
              _online-resources-list.qmd
            </Text>
            ). Tabulky jsou v{" "}
            <Text as="span" style={{ fontFamily: "monospace", fontSize: 11 }}>
              online-resources.qmd
            </Text>
            , A4 na šířku.
          </Callout>
          <Table
            headers={["#", "Štítek", "Obsah"]}
            rows={APPENDIX_ORDER.map(([num, id, desc]) => [
              <span key={num} style={{ color: theme.accent.primary, fontWeight: 590 }}>
                {num}
              </span>,
              <span key={id} style={{ fontFamily: "monospace", fontSize: 11 }}>
                {id}
              </span>,
              desc,
            ])}
            columnAlign={["left", "left", "left"]}
            striped
          />
        </Stack>

        <Stack gap={8}>
          <H2>K dořešení</H2>
          <Table
            headers={["Položka", "Stav"]}
            rows={[
              [
                "Figure 2 PRISMA",
                "Haddaway web app, @PRISMAfd2022, PNG 46/46. Runner Make PNG nepřepisovat (screened 1031 ≠ 1146).",
              ],
              [
                "Abstract / Discussion / Conclusion",
                "Highlights + Impact + structured Abstract v těle. YAML bez live counts (Word může vytisknout 2×). OR PDF format. Ikony/Fig. 1–3 ještě vyměnit (checklist §7).",
              ],
              [
                "OR 17 or-uav-param-core",
                "V příloze teď 22 studií, ne 46. Fenhe/@Guo2026 je extended, sem nepatří. @or-icons je v popisku Table 1 (OR 2).",
              ],
              [
                "Citeproc",
                "Všechny vytištěné citační klíče (116) jsou v bib (21 Oct 2026).",
              ],
              [
                "fig-distribution",
                "V těle jen nástřel a none. Kódování má pět voleb včetně one source; 22/26 je v HTML komentáři.",
              ],
              ["or-uav (OR 13)", "9 kampaní. V 99_aux/93_chapters/Sensors_JR je delší draft."],
              ["workflow.png", "Tmavý; workflow2.png na disku není."],
              [
                "Ikony",
                "or-inputs @Ye2024 bez ikony (pilotovaný letoun); or-applications @Tauro2022 topol = sad.",
              ],
              [
                "Statements",
                "Formal analysis: xxx; stray ]; Holtz ORCID prázdné. Protokol neregistrovaný.",
              ],
            ]}
            striped
          />
        </Stack>
      </Grid>
    </Stack>
  );
}
