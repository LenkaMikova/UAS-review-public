"""Check that the icon work landed in both the HTML and the DOCX build."""
from pathlib import Path
from collections import Counter
import html as htmllib
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
APPX = ROOT / "92_appendix"
ok = True

# review.qmd carries only the caption list, so it holds far fewer icons and
# line breaks than the standalone appendix.
EXPECTED = {
    "review": {"icons": 40, "breaks": 10},
    "online-resources": {"icons": 200, "breaks": 100},
}


def report(label, good, detail=""):
    global ok
    ok = ok and good
    print(f"  [{'ok ' if good else 'FAIL'}] {label}" + (f"  {detail}" if detail else ""))


for name, expect in EXPECTED.items():
    print(f"\n=== {name} ===")

    # ---------------- HTML ----------------
    raw = (ROOT / f"{name}.html").read_text(encoding="utf8")
    text = htmllib.unescape(re.sub(r"<[^>]+>", " ", raw)).replace("\xa0", " ")

    nums = sorted({int(m) for m in re.findall(r"Online Resource\s+(\d+)", text)})
    report("Online Resource numbering is 1..N with no gaps",
           nums == list(range(1, max(nums) + 1)) if nums else False, f"{nums}")

    caps = re.findall(r"Online Resource\s+(\d+):?\s*([A-Z][^.]{0,60})", text)
    first = [c for c in caps if c[0] == "1"]
    report("Online Resource 1 is the selected reviews table",
           any("selected" in c[1].lower() or "Comparative" in c[1] or "existing review" in c[1].lower() for c in first),
           f"{first[:2]}")
    second = [c for c in caps if c[0] == "2"]
    report("Online Resource 2 is the icon legend",
           any("Icon legend" in c[1] for c in second),
           f"{second[:2]}")

    report("no unresolved cross-references", "?or-" not in raw and "?@" not in raw)
    report(
        "legacy or-prisma float is gone (or-prisma-check = OR 4 is allowed)",
        "or-prisma\"" not in raw and "{#or-prisma}" not in raw,
    )

    srcs = [s for s in re.findall(r'<img[^>]+src="([^"]+)"', raw)
            if not s.startswith("data:")]
    missing = sorted({s for s in srcs if not (ROOT / s).resolve().exists()})
    report("every referenced image file exists", not missing, f"missing={missing}")

    icons = Counter(Path(s).stem for s in srcs if "81_icons" in s.replace("\\", "/"))
    report("icons rendered in HTML", sum(icons.values()) >= expect["icons"],
           f"{sum(icons.values())} placements, {len(icons)} distinct")

    # ---------------- DOCX ----------------
    z = zipfile.ZipFile(ROOT / f"{name}.docx")
    doc = z.read("word/document.xml").decode("utf8")
    media = [n for n in z.namelist() if "media" in n]
    drawings = doc.count("<w:drawing>")

    report("images embedded in DOCX", len(media) > 20,
           f"{len(media)} unique files, {drawings} placements, "
           f"{sum(z.getinfo(n).file_size for n in media) // 1024} kB")
    report("no SVG left in DOCX", not any(n.endswith(".svg") for n in media))
    breaks = len(re.findall(r"<w:br\s*/>", doc))
    report("<br> becomes a real line break in DOCX",
           breaks >= expect["breaks"], f"{breaks} breaks")
    report("&nbsp; survives as a non-breaking space in DOCX",
           "\u00a0" in doc, f"{doc.count(chr(0xa0))} found")

    dtxt = re.sub(r"<[^>]+>", "", doc)
    dnums = sorted({int(m) for m in re.findall(r"Online Resource\s*(\d+)", dtxt)})
    report("DOCX Online Resource numbering matches HTML", dnums == nums, f"{dnums}")


# ---------------- structure ----------------
print("\n=== structure ===")

review_html = (ROOT / "review.html").read_text(encoding="utf8")
appx_html = (ROOT / "online-resources.html").read_text(encoding="utf8")

# The manuscript must reference the resources, not reproduce them.
report("manuscript carries captions only, not the appendix tables",
       "Operational flight parameters" in review_html
       and "Flight altitude" not in review_html)

pages = re.findall(r'<w:pgSz[^>]*>',
                   zipfile.ZipFile(ROOT / "online-resources.docx")
                   .read("word/document.xml").decode("utf8"))
report("appendix DOCX is landscape",
       any('w:orient="landscape"' in p for p in pages), f"{pages}")

# The caption list is generated; regenerating must be a no-op.
before = (APPX / "_online-resources-list.qmd").read_bytes()
subprocess.run([sys.executable, str(ROOT / "_build_or_list.py")],
               capture_output=True, check=True)
report("caption list is in sync with the full appendix",
       (APPX / "_online-resources-list.qmd").read_bytes() == before)

# ---------------- pipeline numbers ----------------
print("\n=== pipeline numbers ===")
body = htmllib.unescape(re.sub(r"<[^>]+>", " ", review_html))
abstract = re.search(r"A total of ([\d ,]+) records were retained", body)
report("abstract shows real counts, not zeros",
       bool(abstract) and abstract.group(1).strip() not in ("0", ""),
       f"retained={abstract.group(1).strip() if abstract else 'not found'}")
report("appendix embeds the pipeline exports",
       "not found." not in htmllib.unescape(re.sub(r"<[^>]+>", " ", appx_html)))

print("\nRESULT:", "all checks passed" if ok else "SOME CHECKS FAILED")
