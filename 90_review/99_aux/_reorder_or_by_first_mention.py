"""Rename or-NN-*.qmd and rewrite the include list to match first @or-* in review.qmd.

First mentions (printed body, not HTML comments):
  tbl-history caption: or-reviews, or-icons
  Existing reviews: or-fusion
  Methods lead: or-prisma-check
  fig-prismadig caption: or-processing, or-prisma-flow
  Data Selection: or-search
  Dataset Overview: or-keywords; or-inputs, or-applications, or-methods; or-screening
  Trends lead: or-uav
  Type of Platforms: or-platforms
  Type of Sensors: or-sensors
  Drone studies: or-uav-param, or-uav-param-core
  Conclusion: or-metadata, or-metadata-SM
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "92_appendix"
SRC = ROOT / "_online-resources.qmd"

ORDER = [
    "or-reviews",
    "or-icons",
    "or-fusion",
    "or-prisma-check",
    "or-processing",
    "or-prisma-flow",
    "or-search",
    "or-keywords",
    "or-inputs",
    "or-applications",
    "or-methods",
    "or-screening",
    "or-uav",
    "or-platforms",
    "or-sensors",
    "or-uav-param",
    "or-uav-param-core",
    "or-metadata",
    "or-metadata-SM",
]


def stem(n: int, or_id: str) -> str:
    return f"or-{n:02d}-{or_id.removeprefix('or-')}.qmd"


def main() -> None:
    current: dict[str, Path] = {}
    for path in ROOT.glob("or-[0-9][0-9]-*.qmd"):
        or_id = "or-" + path.name[6:].removesuffix(".qmd")
        current[or_id] = path
    missing = [i for i in ORDER if i not in current]
    extra = sorted(set(current) - set(ORDER))
    if missing or extra:
        raise SystemExit(f"id mismatch missing={missing} extra={extra}")

    temps: list[tuple[str, Path]] = []
    for or_id, path in current.items():
        tmp = ROOT / f"_tmp-{or_id}.qmd"
        path.rename(tmp)
        temps.append((or_id, tmp))

    for n, or_id in enumerate(ORDER, 1):
        src = ROOT / f"_tmp-{or_id}.qmd"
        dest = ROOT / stem(n, or_id)
        text = src.read_text(encoding="utf8")
        text = re.sub(
            r"<!-- Online Resource \d+",
            f"<!-- Online Resource {n}",
            text,
            count=1,
        )
        dest.write_text(text, encoding="utf8")
        src.unlink()
        print(f"  {n:>2}. {dest.name}")

    lines = [
        "<!-- GENERATED include list. Edit the `or-NN-*.qmd` files, not this file.",
        "     Order of includes = Online Resource number = first @or-* in review.qmd.",
        "     Rebuild the manuscript caption list with: python 90_review/_build_or_list.py",
        "==================================================================== -->",
        "",
    ]
    for n, or_id in enumerate(ORDER, 1):
        lines.append(f"{{{{< include {stem(n, or_id)} >}}}}")
        lines.append("")
    SRC.write_text("\n".join(lines), encoding="utf8")
    print(f"wrote {SRC.name} ({len(ORDER)} includes)")


if __name__ == "__main__":
    main()
