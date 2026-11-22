"""Build the landscape reference document used by online-resources.qmd.

The appendix is almost entirely wide multi-column tables, so its DOCX is set to
A4 landscape with narrow margins. Word takes the page setup from the reference
document, so we take Pandoc's own default and only rewrite the section
properties. Re-run this if Pandoc is upgraded; nothing else depends on it.
"""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

OUT = Path(__file__).resolve().parent / "_reference-landscape.docx"

# A4 landscape in twentieths of a point, 1.5 cm margins.
PAGE = '<w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/>'
MARGINS = (
    '<w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850" '
    'w:header="708" w:footer="708" w:gutter="0"/>'
)

with tempfile.TemporaryDirectory() as tmp:
    src = Path(tmp) / "reference.docx"
    src.write_bytes(
        subprocess.run(
            ["quarto", "pandoc", "--print-default-data-file", "reference.docx"],
            capture_output=True,
            check=True,
            shell=True,
        ).stdout
    )

    with zipfile.ZipFile(src) as zin:
        names = zin.namelist()
        doc = zin.read("word/document.xml").decode("utf8")
        if "<w:sectPr" not in doc:
            raise SystemExit("no <w:sectPr> in the default reference document")
        # Pandoc's default ships a sectPr without any page setup, so insert one.
        # Inside sectPr the schema order is footnotePr, endnotePr, type, pgSz,
        # pgMar, ... — appending right before </w:sectPr> keeps that order.
        if "<w:pgSz" in doc:
            doc = re.sub(r"<w:pgSz[^/]*/>", PAGE, doc)
            doc = re.sub(r"<w:pgMar[^/]*/>", MARGINS, doc)
        else:
            doc = doc.replace("</w:sectPr>", f"{PAGE}{MARGINS}</w:sectPr>", 1)

        with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
            for name in names:
                data = doc.encode("utf8") if name == "word/document.xml" else zin.read(name)
                zout.writestr(name, data)

check = zipfile.ZipFile(OUT).read("word/document.xml").decode("utf8")
print(f"wrote {OUT.name} ({OUT.stat().st_size // 1024} kB)")
print("landscape:", 'w:orient="landscape"' in check)
