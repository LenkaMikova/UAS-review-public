"""Copy the four Zenodo packages into 50_outputs/zenodo/.

Does not upload. Does not copy copyrighted paper PDFs or Zotero secrets.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "50_outputs" / "zenodo"


def copy(src: Path, dest: Path) -> None:
    if not src.exists():
        print(f"  skip missing {src.relative_to(ROOT)}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dest, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dest)
    print(f"  {src.relative_to(ROOT)} -> {dest.relative_to(ROOT)}")


def pack1() -> None:
    d = OUT / "01_protocol"
    copy(ROOT / "60_prisma" / "protocol" / "PRISMA-P_retrospective_protocol.md", d / "PRISMA-P_retrospective_protocol.md")
    copy(ROOT / "60_prisma" / "protocol" / "PRISMA-P_checklist.md", d / "PRISMA-P_checklist.md")
    copy(ROOT / "60_prisma" / "PRISMA_2020_checklist_filled.md", d / "PRISMA_2020_checklist_filled.md")
    copy(ROOT / "90_review" / "92_appendix" / "or-04-prisma-check.qmd", d / "or-04-prisma-check.qmd")


def pack2() -> None:
    d = OUT / "02_search-screening"
    copy(ROOT / "00_search" / "02_final" / "final_query.txt", d / "final_query.txt")
    audit = ROOT / "20_data_clean" / "21_audit"
    for name in (
        "processing_report.txt",
        "prisma_counts.csv",
        "duplicates_doi.xlsx",
        "duplicates_title.xlsx",
        "missing_doi.xlsx",
        "classification_review.json",
        "manual_exclusions.json",
        "audit_saved.txt",
        "record_decisions.json",
        "record_decisions.txt",
        "forward_records.xlsx",
        "all_records_with_status.xlsx",
    ):
        copy(audit / name, d / name)
    copy(audit / "checked", d / "audit_checked")
    copy(ROOT / "20_data_clean" / "clean_records.xlsx", d / "clean_records.xlsx")
    copy(ROOT / "30_screening" / "31_dataset" / "screened_records.xlsx", d / "screened_records.xlsx")
    copy(
        ROOT / "30_screening" / "31_dataset" / "checked",
        d / "screening_checked",
    )
    reports = ROOT / "30_screening" / "33_reports"
    for name in ("screening_summary.txt", "screening_summary.xlsx", "keyword_statistics.txt"):
        copy(reports / name, d / name)
    exports = ROOT / "30_screening" / "32_exports"
    for name in (
        "must_cite_list.xlsx",
        "must_cite_48.csv",
        "must_cite_45.csv",
        "all_records.ris",
        "include_records.ris",
        "core_studies.ris",
        "extended_studies.ris",
        "must_cite_records.ris",
        "HIGH_Scaling_none_with_abstracts.xlsx",
    ):
        copy(exports / name, d / name)
    vos = ROOT / "30_screening" / "35_VOS-ris"
    for name in ("VOS_full.ris", "VOS_must-cite.ris"):
        copy(vos / name, d / name)
    copy(
        ROOT / "40_extraction" / "41_input" / "extraction_input_refined.xlsx",
        d / "extraction_input_refined.xlsx",
    )
    copy(
        ROOT / "40_extraction" / "42_working" / "extraction_filled.xlsx",
        d / "extraction_filled.xlsx",
    )


def pack3() -> None:
    d = OUT / "03_online-resources"
    app = ROOT / "90_review" / "92_appendix"
    for path in sorted(app.glob("or-*.qmd")):
        copy(path, d / path.name)
    copy(ROOT / "90_review" / "99_aux" / "opensky-sm-checklist.html", d / "opensky-sm-checklist.html")
    for name in (
        "online-resources.html",
        "online-resources.docx",
        "online-resources.pdf",
    ):
        copy(ROOT / "90_review" / name, d / name)


def pack4() -> None:
    d = OUT / "04_software"
    src = ROOT / "70_scripts"
    dest = d / "70_scripts"
    if dest.exists():
        shutil.rmtree(dest)
    def ignore(directory: str, names: list[str]) -> list[str]:
        skip = {"__pycache__", ".gitignore", "zotero_config.json"}
        return [n for n in names if n in skip or n.endswith(".pyc")]
    shutil.copytree(src, dest, ignore=ignore)
    print(f"  70_scripts/ -> {dest.relative_to(ROOT)}")
    copy(ROOT / "90_review" / "99_aux" / "pipeline-io.md", d / "pipeline-io.md")
    copy(src / "requirements.txt", d / "requirements.txt")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    copy(ROOT / "90_review" / "99_aux" / "zenodo" / "README.md", OUT / "README.md")
    print("\n== 01 protocol ==")
    pack1()
    print("\n== 02 search-screening ==")
    pack2()
    print("\n== 03 online-resources ==")
    pack3()
    print("\n== 04 software ==")
    pack4()
    print(f"\nDone: {OUT}")


if __name__ == "__main__":
    main()
