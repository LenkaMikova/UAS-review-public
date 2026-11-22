import {
  Button,
  Callout,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Grid,
  H1,
  H2,
  Link,
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

type Status = "pending" | "in_progress" | "completed";
type Filter = "open" | "all";
type Group =
  | "prisma"
  | "journal"
  | "esm"
  | "upload"
  | "template"
  | "figures"
  | "body"
  | "declarations"
  | "zenodo"
  | "remaining";

type Item = {
  id: string;
  group: Group;
  content: string;
  initial: Status;
};

const ITEMS: Item[] = [
  {
    id: "prisma-files",
    group: "prisma",
    content:
      "PRISMA soubory: OR 4, PRISMA-P, executed log, Figure 2 (46/46) — máte, nic dalšího neschází",
    initial: "completed",
  },
  {
    id: "prisma-abstract",
    group: "prisma",
    content:
      "PRISMA Abstract: dopsat eligibility, datum search, n=46, neregistrováno, funding, limity",
    initial: "pending",
  },
  {
    id: "prisma-limitations",
    group: "prisma",
    content:
      "Limitations of Review: výslovně one-person screening, ne dual; no a priori protocol",
    initial: "pending",
  },
  {
    id: "prisma-funder",
    group: "prisma",
    content: "Položka 25: role fundera u IGA 2026B0015",
    initial: "pending",
  },
  {
    id: "cite-or",
    group: "esm",
    content: "V textu citovat Online Resource N (@or-*) — už je",
    initial: "completed",
  },
  {
    id: "captions",
    group: "esm",
    content: "Caption ke každému OR v rukopisu — seznam na konci review.qmd",
    initial: "completed",
  },
  {
    id: "pdf",
    group: "esm",
    content:
      "Vyrenderovat online-resources.pdf (formát už je; quarto render --to pdf)",
    initial: "pending",
  },
  {
    id: "cover",
    group: "esm",
    content:
      "Na každý ESM soubor: title, Precision Agriculture, autoři, affiliation + e-mail corresponding",
    initial: "pending",
  },
  {
    id: "names",
    group: "esm",
    content: "Soubory ESM_1.pdf … (ne online-resources.docx)",
    initial: "pending",
  },
  {
    id: "zip-journal",
    group: "esm",
    content: "Stejné soubory samostatně a v ESM.zip pro Editorial Manager",
    initial: "pending",
  },
  {
    id: "zip-zenodo",
    group: "esm",
    content: "Kopie toho PDF/zipu do zipu datasetu @MikovaData2026 (ne čtvrtý DOI)",
    initial: "pending",
  },
  {
    id: "word",
    group: "upload",
    content: "Finální review.docx po nových číslech (Word, ne jen qmd)",
    initial: "pending",
  },
  {
    id: "em-forms",
    group: "upload",
    content:
      "Author contribution + Competing interests znovu do formuláře odeslání",
    initial: "pending",
  },
  {
    id: "highlights",
    group: "template",
    content:
      "Highlights: 4 odrážky už v těle — po runneru jen kdybyste chtěla počty",
    initial: "in_progress",
  },
  {
    id: "impact",
    group: "template",
    content: "Impact: 2 věty už v těle — můžete zkrátit",
    initial: "in_progress",
  },
  {
    id: "abstract",
    group: "template",
    content:
      "Abstract Purpose/Methods/Results/Conclusion v těle — Results/Conclusion dopsat po číslech",
    initial: "in_progress",
  },
  {
    id: "keywords",
    group: "template",
    content: "Keywords 4–6 — v YAML je 6",
    initial: "completed",
  },
  {
    id: "body-count",
    group: "template",
    content:
      "Šablona: ~11 tabulek+obrázků v těle; teď 12 tab. + 6 fig. — co ještě do SI",
    initial: "pending",
  },
  {
    id: "bw",
    group: "template",
    content: "Barvy čitelné i v šedé (tisk B/W) — Fig. 2 červený rámeček, Fig. 5",
    initial: "pending",
  },
  {
    id: "runner",
    group: "body",
    content: "Runner v této složce: Merge → Audit Save → Screening; compare",
    initial: "pending",
  },
  {
    id: "discussion",
    group: "body",
    content: "Discussion po číslech (teď kopíruje Table 12)",
    initial: "pending",
  },
  {
    id: "conclusion",
    group: "body",
    content: "Conclusion vs Aim (pryč Core/Q/Full + ASPRS Geodetic jako povinnost článku)",
    initial: "pending",
  },
  {
    id: "icons-replace",
    group: "figures",
    content:
      "Ikony v tabulkách + OR 1: CC0/MIT sada, vlastní čáry, nebo jen text (Napkin prompt-only nelze)",
    initial: "pending",
  },
  {
    id: "fig1-redraw",
    group: "figures",
    content: "Figure 1 bez Napkin — autorská časová osa, nebo jen Table 1",
    initial: "pending",
  },
  {
    id: "fig2-redraw",
    group: "figures",
    content:
      "Figure 2 Haddaway web app, 46/46 — hotovo; Make PNG v runneru nepoužívat",
    initial: "completed",
  },
  {
    id: "fig3-redraw",
    group: "figures",
    content: "Figure 3 v PowerPoint/draw.io z kroků pipeline (ne Napkin)",
    initial: "pending",
  },
  {
    id: "fig-caption-ai",
    group: "figures",
    content:
      "Po výměně smazat Generated using NapkinAI/ChatGPT; u sady uvést licenci",
    initial: "pending",
  },
  {
    id: "or18",
    group: "body",
    content: "OR 4 položky 24/27: tři Zenodo cite keys — hotovo",
    initial: "completed",
  },
  {
    id: "journal-docx",
    group: "journal",
    content: "Časopis: editable Word do EM (ne jen qmd); single-blind, anonymizovat nemusíte",
    initial: "pending",
  },
  {
    id: "journal-em",
    group: "journal",
    content: "Časopis: Author contribution + Competing interests znovu do formuláře EM",
    initial: "pending",
  },
  {
    id: "journal-data",
    group: "journal",
    content: "Časopis: Data Availability s DOI datasetu (nestačí GitHub)",
    initial: "pending",
  },
  {
    id: "public-mirror",
    group: "remaining",
    content: "UAS-review-public: zrcadlo bez 99_temp (sync_public.py + hook)",
    initial: "in_progress",
  },
  {
    id: "credit",
    group: "declarations",
    content: "Formal analysis: xxx",
    initial: "pending",
  },
  {
    id: "data-av",
    group: "declarations",
    content: "Data Availability: tři Zenodo DOI, GitHub = live copy (teď jen GitHub)",
    initial: "pending",
  },
  {
    id: "code-av",
    group: "declarations",
    content: "Code Availability za Data Availability (@MikovaCode2026) — až řeknete",
    initial: "pending",
  },
  {
    id: "llm-methods",
    group: "declarations",
    content: "LLM použití do Methods (Springer); acknowledgment nestačí",
    initial: "pending",
  },
  {
    id: "related",
    group: "zenodo",
    content: "Related identifiers mezi třemi DOI; GitHub tag, na který Zenodo míří",
    initial: "pending",
  },
  {
    id: "pack",
    group: "zenodo",
    content: "_pack.py pořád skládá 03_online-resources jako čtvrtou složku — sloučit do datasetu",
    initial: "pending",
  },
];

const GROUPS: { id: Group; title: string }[] = [
  { id: "prisma", title: "PRISMA 2020" },
  { id: "journal", title: "Povinnosti časopisu" },
  { id: "esm", title: "Online Resources (SI u článku + kopie v zipu)" },
  { id: "upload", title: "Soubory do Editorial Manageru" },
  { id: "template", title: "Šablona Precision Agriculture" },
  { id: "figures", title: "Obrázky a ikony" },
  { id: "body", title: "Tělo a čísla" },
  { id: "declarations", title: "Statements, data, AI" },
  { id: "zenodo", title: "Tři Zenodo records" },
  { id: "remaining", title: "Další body" },
];

export default function PreSubmissionChecklist() {
  const dispatch = useCanvasAction();
  const [filter, setFilter] = useCanvasState<Filter>("filter", "open");
  const [override, setOverride] = useCanvasState<Record<string, Status>>(
    "status",
    {},
  );

  function statusOf(item: Item): Status {
    return override[item.id] ?? item.initial;
  }

  const done = ITEMS.filter((item) => statusOf(item) === "completed").length;
  const open = ITEMS.filter((item) => statusOf(item) !== "completed").length;

  function toggle(id: string) {
    const item = ITEMS.find((row) => row.id === id);
    if (!item) return;
    const next: Status =
      statusOf(item) === "completed" ? "pending" : "completed";
    setOverride((prev) => ({ ...prev, [id]: next }));
  }

  return (
    <Stack gap={24} style={{ maxWidth: 920, padding: 24 }}>
      <Stack gap={8}>
        <H1>Před odesláním — Precision Agriculture</H1>
        <Text tone="secondary">
          Springer journal 11119. Odškrtnutí v canvasu nemění článek. Markdown:{" "}
          <Text weight="semibold">90_review/99_aux/pre-submission-checklist.md</Text>
        </Text>
        <Row gap={8} wrap>
          <Button
            variant="secondary"
            onClick={() =>
              dispatch({
                type: "openFile",
                path: "90_review/99_aux/pre-submission-checklist.md",
              })
            }
          >
            Otevřít markdown
          </Button>
          <Button
            variant="ghost"
            onClick={() =>
              dispatch({
                type: "openFile",
                path: "c:\\Users\\lenka\\OneDrive - CZU v Praze\\DSP FŽP\\04 articles\\2026 Review_TempHumidity\\SpringerNature.pdf",
              })
            }
          >
            Šablona PDF
          </Button>
        </Row>
        <Text size="small" tone="tertiary">
          Pokyny:{" "}
          <Link href="https://www.springer.com/journal/11119/submission-guidelines">
            submission guidelines
          </Link>
          {" · "}
          <Link href="https://www.springernature.com/gp/policies/editorial-policies/ai-manuscript-preparation">
            SN AI policy
          </Link>
        </Text>
      </Stack>

      <Grid columns={3} gap={12}>
        <Stat value={String(open)} label="Otevřené" tone="warning" />
        <Stat value={String(done)} label="Hotovo" tone="success" />
        <Stat value="3" label="Zenodo DOI" />
      </Grid>

      <Callout tone="neutral" title="PRISMA soubory máte">
        Checklist OR 4, retrospektivní PRISMA-P, executed log a Figure 2
        (46/46) sedí. Chybí reporting v abstractu, Data Availability DOI,
        role fundera a výslovný single-screener v Limitations — ne další
        PRISMA soubor.
      </Callout>

      <Callout tone="info" title="Online Resources nejsou dataset">
        U časopisu: PDF + ESM.zip (samostatné soubory). Na Zenodo: screening a
        extrakce; do zipu datasetu jen kopie té přílohy. Runner nemá čtvrtý DOI.
      </Callout>

      <Stack gap={8}>
        <H2>Co časopis chce u SI</H2>
        <Table
          headers={["Pravidlo", "U nás"]}
          rows={[
            ["Citace Online Resource N", "Už v review.qmd"],
            ["Text jako PDF, ne docx", "Zatím docx/html"],
            ["ESM_3.pdf … + zip dovoleno", "Ještě nesbaleno"],
            [
              "Na každém souboru title, journal, autoři, e-mail",
              "Chybí cover",
            ],
            [
              "Datasety spíš repository než SI",
              "Zenodo dataset, ne čtvrtý record",
            ],
            ["Publikuje se jak přijde", "PDF musí být finální sazba"],
          ]}
        />
      </Stack>

      <Callout tone="warning" title="Tři věci, které časopis vrátí">
        Highlights a Impact v šabloně nejsou. Abstract je pořád koncept.
        NapkinAI/ChatGPT ikony bez ověřitelného zdroje SN 2026 zakazuje
        (opaque). 12 tabulek + 6 obrázků v těle je nad ~11 ze šablony — zbytek
        už je v OR, ale tělo je pořád husté.
      </Callout>

      <Divider />

      <Row gap={8} align="center">
        <Text weight="semibold">Seznam</Text>
        <Pill active={filter === "open"} onClick={() => setFilter("open")}>
          Jen otevřené
        </Pill>
        <Pill active={filter === "all"} onClick={() => setFilter("all")}>
          Vše
        </Pill>
        <Text size="small" tone="tertiary">
          Klik na řádek = hotovo / zpět
        </Text>
      </Row>

      {GROUPS.map((group) => {
        const rows = ITEMS.filter((item) => item.group === group.id).filter(
          (item) =>
            filter === "all" || statusOf(item) !== "completed",
        );
        if (rows.length === 0) return null;
        return (
          <Stack key={group.id} gap={8}>
            <H2>{group.title}</H2>
            <TodoListCard
              defaultExpanded
              todos={rows.map((item) => ({
                id: item.id,
                content: item.content,
                status: statusOf(item),
              }))}
              onTodoClick={(todo) => toggle(todo.id)}
            />
          </Stack>
        );
      })}

      <Card>
        <CardHeader>Až bude SI hotové</CardHeader>
        <CardBody>
          <Stack gap={6}>
            <Text>
              1. Render <Text weight="semibold">online-resources</Text> do PDF
              s čísly OR 1–19 shodnými se seznamem v článku.
            </Text>
            <Text>
              2. První strana: title, Precision Agriculture, autoři, corresponding
              e-mail.
            </Text>
            <Text>
              3. Uložit jako <Text weight="semibold">ESM_1.pdf</Text> (jeden
              soubor stačí, když jsou všechny OR uvnitř) <Text italic>nebo</Text>{" "}
              ESM_1.pdf … ESM_18.pdf.
            </Text>
            <Text>
              4. Stejné soubory do <Text weight="semibold">ESM.zip</Text> pro
              časopis a kopie do zipu datasetu.
            </Text>
          </Stack>
        </CardBody>
      </Card>
    </Stack>
  );
}
