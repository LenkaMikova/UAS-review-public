"""Check that every markdown image in review.qmd + appendix exists on disk."""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVIEW = HERE.parent
ROOT = REVIEW.parent
QMD = [REVIEW / "review.qmd", REVIEW / "92_appendix" / "_online-resources.qmd"]
IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")

bad = []
n = 0
stale = []
for qmd in QMD:
    text = qmd.read_text(encoding="utf-8")
    for m in IMG.finditer(text):
        n += 1
        rel = m.group(1)
        if "91_figures" in rel or "81_VOSviewer" in rel:
            stale.append((qmd.name, rel))
        path = (REVIEW / rel).resolve()
        if not path.exists():
            bad.append((qmd.name, rel, str(path)))

print(f"image refs: {n}")
if stale:
    print("STALE PATHS:")
    for row in stale:
        print(" ", row)
if bad:
    print("MISSING FILES:")
    for row in bad:
        print(" ", row)
    raise SystemExit(1)
print("all image files exist")
