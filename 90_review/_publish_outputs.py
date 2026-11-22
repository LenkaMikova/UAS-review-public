"""Copy the last Quarto render into 50_outputs/.

Quarto writes next to the .qmd (needed for `quarto preview`). The files you
send — Word, HTML, and later PDF — live in 50_outputs/, so 90_review/ stays
the source folder.
"""
from pathlib import Path
import shutil

REVIEW = Path(__file__).resolve().parent
OUT = REVIEW.parent / "50_outputs"
OUT.mkdir(exist_ok=True)

COPIED = []
for name in (
    "review.docx",
    "review.html",
    "online-resources.docx",
    "online-resources.html",
    "review.pdf",
    "online-resources.pdf",
):
    src = REVIEW / name
    if src.exists():
        shutil.copy2(src, OUT / name)
        COPIED.append(name)

if not COPIED:
    raise SystemExit("no rendered files found in 90_review/ — run quarto render first")
print("50_outputs/ <- " + ", ".join(COPIED))
