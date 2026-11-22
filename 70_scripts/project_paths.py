"""Paths for the review pipeline.

Scripts live under 70_scripts/. Data folders (00_search …) default to the
repository root. The Review runner can redirect data to another directory by
setting the environment variable REVIEW_DATA_ROOT before a script starts.
"""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parent
CODE_ROOT = SCRIPTS_ROOT.parent
ENV_DATA_ROOT = "REVIEW_DATA_ROOT"


def data_root() -> Path:
    raw = os.environ.get(ENV_DATA_ROOT, "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return CODE_ROOT


PROJECT_ROOT = data_root()

AFTER_MANUAL_CHECK = "after_manual_check"


def prefer_after_manual_check(script_file: Path | str) -> Path:
    """Use the file marked after manual check when it exists; never the other way around."""
    script_file = Path(script_file)
    if script_file.name.lower() == "clean_records.xlsx":
        decided = script_file.parent / "21_audit" / "forward_records.xlsx"
        if decided.exists():
            return decided
    folders = [script_file.parent / "checked"]
    if script_file.name.lower() == "clean_records.xlsx":
        folders.insert(0, script_file.parent / "21_audit" / "checked")
    stem, suffix = script_file.stem, script_file.suffix
    for folder in folders:
        current = folder / f"{stem}_{AFTER_MANUAL_CHECK}{suffix}"
        if current.exists():
            return current
    return script_file


def write_excel(df, path, *, index: bool = False, **kwargs) -> Path:
    """Write an xlsx via a local temp file. OneDrive/Excel locks on the dest often raise Errno 22."""
    import pandas as pd

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(suffix=".xlsx", prefix=path.stem + "_")
    os.close(fd)
    tmp = Path(tmp_name)
    last: Exception | None = None
    try:
        df.to_excel(tmp, index=index, **kwargs)
        last = _install_over(tmp, path)
        if last is None:
            return path
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
    raise OSError(
        f"Could not write {path}. Close the file in Excel if it is open, "
        f"wait until OneDrive finishes syncing, then run again. ({last})"
    ) from last


def write_excel_sheets(sheets: dict, path) -> Path:
    """Write several sheets. Same OneDrive-safe temp + replace as write_excel."""
    import pandas as pd

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(suffix=".xlsx", prefix=path.stem + "_")
    os.close(fd)
    tmp = Path(tmp_name)
    last: Exception | None = None
    try:
        with pd.ExcelWriter(tmp, engine="openpyxl") as writer:
            for name, frame in sheets.items():
                frame.to_excel(writer, sheet_name=str(name)[:31], index=False)
        last = _install_over(tmp, path)
        if last is None:
            return path
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
    raise OSError(
        f"Could not write {path}. Close the file in Excel if it is open, "
        f"wait until OneDrive finishes syncing, then run again. ({last})"
    ) from last


def _install_over(src: Path, dest: Path) -> Exception | None:
    import shutil

    last: Exception | None = None
    for attempt in range(8):
        try:
            if dest.exists():
                try:
                    dest.unlink()
                except OSError as e:
                    last = e
            shutil.copy2(src, dest)
            return None
        except OSError as e:
            last = e
            time.sleep(0.4 * (attempt + 1))
    return last
