"""Audit leftover old folder names and resolve live include/image paths."""
from __future__ import annotations

import re
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
skip_dirs = {".git", "review_files", ".Rproj.user", "node_modules", "50_outputs", "99_temp", "99_backup"}
skip_files = {"review-MIKOVAL-PC-01.qmd"}
exts = {".md", ".qmd", ".py", ".mdc", ".tsx"}
inc = re.compile(r"\{\{<\s*include\s+([^ >]+)")
img = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")

print("=== old names in live sources ===")
for p in repo.rglob("*"):
    if not p.is_file() or p.suffix.lower() not in exts:
        continue
    if any(s in p.parts for s in skip_dirs):
        continue
    if p.name in skip_files:
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    hits = [k for k in ("91_figures", "94_appendix", "92_tables", "81_VOSviewer", "90_review/93_chapters") if k in t]
    if hits:
        print(p.relative_to(repo), hits)

print("\n=== includes and images from 90_review qmd ===")
review = repo / "90_review"
for qmd in (review / "review.qmd", review / "online-resources.qmd"):
    t = qmd.read_text(encoding="utf-8")
    for m in inc.finditer(t):
        rel = m.group(1)
        ok = (qmd.parent / rel).exists()
        print(("OK " if ok else "MISS"), qmd.name, "include", rel)
    missing = 0
    n = 0
    for m in img.finditer(t):
        n += 1
        rel = m.group(1)
        if not (qmd.parent / rel).exists():
            missing += 1
            print("MISS img", qmd.name, rel)
    print(qmd.name, "images", n, "missing", missing)

print("\n=== key files exist ===")
for rel in (
    "90_review/92_appendix/_online-resources.qmd",
    "90_review/92_appendix/_online-resources-list.qmd",
    "80_figures/81_icons/drone.png",
    "80_figures/82_VOSviewer/VOS_must-cite.png",
    "90_review/91_tables/README.md",
    "90_review/99_aux/93_chapters/Sensors_JR",
    "90_review/99_aux/_count_table_studies.py",
):
    p = repo / rel
    print(("OK " if p.exists() else "MISS"), rel)
