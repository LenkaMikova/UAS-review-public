"""Check Python and packages. Install only when the user asks."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path

MIN = (3, 10)
HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
REQ = SCRIPTS / "requirements.txt"
APP = HERE / "app.py"
REQUIRED = ("pandas", "openpyxl")
OPTIONAL_WHY = {"pyzotero": "Zotero sync"}


@dataclass
class Pkg:
    name: str
    spec: str
    version: str | None
    required: bool
    why: str

    @property
    def ok(self) -> bool:
        return bool(self.version)


def python_line() -> str:
    v = sys.version_info
    return f"{v.major}.{v.minor}.{v.micro}"


def python_ok() -> bool:
    v = sys.version_info
    return (v.major, v.minor) >= MIN


def has_tkinter() -> bool:
    try:
        import tkinter  # noqa: F401
        return True
    except ImportError:
        return False


def _req_rows() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if not REQ.exists():
        return [(name, "") for name in REQUIRED]
    for raw in REQ.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        name = re.split(r"[<>=!~]", line, 1)[0].strip()
        spec = line[len(name):].strip()
        if name:
            rows.append((name, spec))
    return rows


def probe() -> list[Pkg]:
    out: list[Pkg] = []
    for name, spec in _req_rows():
        try:
            ver = metadata.version(name)
        except metadata.PackageNotFoundError:
            ver = None
        out.append(
            Pkg(
                name=name,
                spec=spec,
                version=ver,
                required=name in REQUIRED,
                why=OPTIONAL_WHY.get(name, "pipeline"),
            )
        )
    return out


def missing(pkgs: list[Pkg] | None = None) -> list[Pkg]:
    return [p for p in (pkgs or probe()) if not p.ok]


def required_missing(pkgs: list[Pkg] | None = None) -> list[Pkg]:
    return [p for p in missing(pkgs) if p.required]


def install_packages() -> tuple[int, str]:
    cmd = [
        sys.executable, "-m", "pip", "install",
        "--disable-pip-version-check",
        "-r", str(REQ),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    text = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, text.strip() or "(no pip output)"


def show_window(parent=None) -> bool:
    """List packages and offer Install. Returns True when required packages are present."""
    import tkinter as tk
    from tkinter import ttk

    import ui

    pkgs = probe()
    result = {"ok": not required_missing(pkgs)}

    if parent is None:
        win = tk.Tk()
        ui.apply_theme(win)
        close_loop = True
    else:
        win = tk.Toplevel(parent)
        win.transient(parent)
        win.configure(bg=ui.BG)
        close_loop = False

    win.title("Python and packages")
    win.geometry("560x520")
    win.minsize(480, 420)

    tip = ui.Tip(win)
    win._ui_tip = tip  # noqa: SLF001

    ttk.Label(win, text="Python and packages", style="Head.TLabel").pack(anchor="w", padx=16, pady=(16, 4))
    py_lbl = ttk.Label(win, text="", style="TLabel")
    py_lbl.pack(anchor="w", padx=16)
    exe_lbl = ttk.Label(win, text=str(sys.executable), style="Muted.TLabel")
    exe_lbl.pack(anchor="w", padx=16, pady=(0, 8))
    note = ttk.Label(win, text="", style="Choice.TLabel", wraplength=520)
    note.pack(anchor="w", padx=16, pady=(0, 8))
    body = ui.text_widget(win, height=10, font=("Consolas", 10))
    body.pack(fill="both", expand=True, padx=16)
    log = ui.text_widget(win, height=6, font=("Consolas", 9))
    log.pack(fill="x", padx=16, pady=(8, 0))
    btns = ttk.Frame(win)
    btns.pack(fill="x", padx=16, pady=14)

    def set_log(text: str) -> None:
        log.delete("1.0", "end")
        log.insert("1.0", text)

    def finish(ok: bool) -> None:
        result["ok"] = ok
        win.destroy()
        if close_loop:
            win.quit()

    def render() -> None:
        nonlocal pkgs
        pkgs = probe()
        miss = missing(pkgs)
        need = required_missing(pkgs)
        py_ok = python_ok()
        tk_ok = has_tkinter()
        py_lbl.configure(
            text=(
                f"Python {python_line()}"
                + ("  — ready" if py_ok else f"  — need {MIN[0]}.{MIN[1]} or newer (this review used 3.11)")
            )
        )
        lines = []
        for p in pkgs:
            if p.ok:
                state = f"{p.version}  ready"
            elif p.required:
                state = "missing  (needed to run the pipeline)"
            else:
                state = f"missing  (optional: {p.why})"
            spec = f" {p.spec}" if p.spec else ""
            lines.append(f"{(p.name + spec):<22}  {state}")
        body.configure(state="normal")
        body.delete("1.0", "end")
        body.insert("1.0", "\n".join(lines) or "(no packages listed)")
        body.configure(state="disabled")
        if not py_ok:
            note.configure(text="This Python is too old. Install 3.10 or newer, then run again.")
        elif not tk_ok:
            note.configure(text="tkinter is missing. Reinstall Python and tick tcl/tk.")
        elif need:
            names = ", ".join(p.name for p in need)
            note.configure(text=f"Missing: {names}. Install packages, then continue.")
        elif miss:
            names = ", ".join(p.name for p in miss)
            note.configure(text=f"Optional missing: {names}. You can install them or continue.")
        else:
            note.configure(text="Everything needed is installed.")
        can_run = py_ok and tk_ok and not need
        install_btn.set_state("disabled" if not REQ.exists() else "normal")
        continue_btn.set_state("normal" if can_run else "disabled")
        result["ok"] = can_run

    def do_install() -> None:
        if not REQ.exists():
            set_log(f"Missing {REQ}")
            return
        install_btn.set_state("disabled")
        continue_btn.set_state("disabled")
        set_log("Downloading packages…")
        win.update_idletasks()
        code, text = install_packages()
        set_log(text)
        render()
        if code != 0:
            note.configure(text="Install failed. See the log below.")
            install_btn.set_state("normal")

    install_btn = ui.button(btns, "Install packages", do_install, kind="accent")
    install_btn.pack(side="left")
    continue_btn = ui.button(btns, "Continue", lambda: finish(True), kind="default")
    continue_btn.pack(side="right")
    if parent is not None:
        ui.button(btns, "Close", lambda: finish(result["ok"])).pack(side="right", padx=(0, 8))

    render()
    set_log("Install only runs when you click the button. Nothing is downloaded automatically.")
    win.protocol("WM_DELETE_WINDOW", lambda: finish(result["ok"]))
    if parent is None:
        win.mainloop()
    else:
        win.grab_set()
        win.wait_window()
    return bool(result["ok"]) and not required_missing()


def main() -> int:
    print(f"Python {python_line()}")
    print(f"Executable: {sys.executable}")
    if not python_ok():
        print(f"Need Python {MIN[0]}.{MIN[1]} or newer (this review used 3.11).")
        return 1
    if not has_tkinter():
        print("tkinter is missing. Reinstall Python and tick tcl/tk.")
        return 1
    pkgs = probe()
    for p in pkgs:
        print(f"{p.name}: {p.version or 'missing'}")
    if missing(pkgs):
        if not show_window():
            return 1
    print("Starting Review runner…")
    return subprocess.call([sys.executable, str(APP)])


if __name__ == "__main__":
    raise SystemExit(main())
