"""Review runner — same procedure, other data. Defaults are editable."""

from __future__ import annotations

import calendar as calmod
import csv
import json
import os
import sys
import urllib.parse
import webbrowser
import tkinter as tk
from datetime import date, datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))

import actions
import ensure_env
import record_audit
from catalog import (
    CHECK_CHOICES,
    CLASS_LABELS,
    MANUAL_CHECK_UPLOADS,
    DATABASE_CHOICES,
    DEFAULT_SEARCH,
    DEFAULT_SETTINGS,
    EXTRA_REASONS,
    FOLDER_PLAN,
    FORMAT_CHOICES,
    REGISTRATION_CHOICES,
    REPRODUCE,
    SCREEN_OUTPUT_GROUPS,
    SCREEN_TABS,
    STEP_NEED,
    AUDIT_TABS,
    EXTRACT_TABS,
    EXTRACT_GROUP_LABELS,
    SETUP_TABS,
    STEPS,
    TERM_GROUPS,
    format_type_counts,
    normalize_check,
    step_script,
)
from project_paths import data_root
import protocol_export
import ui
from ui import (
    ACCENT,
    ACCENT_FG,
    BG,
    BORDER,
    BRAND,
    BTN,
    CARD,
    FG,
    FONT,
    FONT_HEAD,
    FONT_ICON,
    FONT_SMALL,
    FONT_TITLE,
    MUTED,
    PANEL,
    UI,
    apply_theme,
    brand_icon_image,
    Scrollable,
    text_widget,
)

FONT_LOG = ("Consolas", 10)


def set_text(widget: tk.Text, value: str) -> None:
    widget.delete("1.0", "end")
    widget.insert("1.0", value or "")


def get_text(widget: tk.Text) -> str:
    return widget.get("1.0", "end").strip()


class RunnerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Review runner")
        self.geometry("1120x760")
        self.minsize(960, 640)
        apply_theme(self)
        self._win_icon = brand_icon_image()
        self.iconphoto(True, self._win_icon)
        self.folder = tk.StringVar(value="")
        self.step_id = "output"
        self.nav_btns: dict[str, object] = {}
        self.frames: dict[str, ttk.Frame] = {}
        self.fields: dict[str, object] = {}
        self.db_vars: dict[str, tk.BooleanVar] = {}
        self.reg_type = tk.StringVar(value="None")
        self.protocol_mode = tk.StringVar(value="plan")
        self._before_continue: dict[str, object] = {}
        self._refresh_manual_check: dict[str, object] = {}
        self._setup_tab = "folder"
        self._setup_panes: dict[str, ttk.Frame] = {}
        self._setup_tab_btns: dict[str, object] = {}
        self._setup_seen: set[str] = set()
        self._setup_actions: ttk.Frame | None = None
        self._screen_tab = "keywords"
        self._screen_panes: dict[str, ttk.Frame] = {}
        self._screen_tab_btns: dict[str, object] = {}
        self._screen_actions: ttk.Frame | None = None
        self._audit_tab_btns: dict[str, object] = {}
        self._audit_data: dict = {}
        self._extract_tab = "groups"
        self._extract_panes: dict[str, ttk.Frame] = {}
        self._extract_tab_btns: dict[str, object] = {}
        self._extract_trees: dict[str, object] = {}
        self._extract_rowkeys: dict[str, dict[str, str]] = {}
        self._extract_preview_wins: dict[str, object] = {}
        self._extract_seen: set[str] = set()
        self._extract_summary: ttk.Label | None = None
        self._extract_split: ttk.Label | None = None
        self._extract_note: ttk.Label | None = None
        self._extract_listing = None
        self._extract_count_lbls: dict[str, ttk.Label] = {}
        self._extract_include_box: ttk.LabelFrame | None = None
        self._extract_must_box: ttk.LabelFrame | None = None
        self._extract_must_lbl: ttk.Label | None = None
        self._extract_in_group: dict[str, dict[str, bool]] = {}
        self._extract_tree_cols: dict[str, list[str]] = {}
        self._extract_move_dest: dict[str, tk.StringVar] = {}
        self._extract_move_core: dict[str, tk.BooleanVar] = {}
        self._extract_move_ext: dict[str, tk.BooleanVar] = {}
        self._prisma_auto_vals: dict[str, ttk.Label] = {}
        self._prisma_sought_hint: ttk.Label | None = None
        self._extract_dest = None
        self._extract_core = None
        self._extract_extended = None
        self._extract_flags_row: ttk.Frame | None = None
        self._ui_tip = ui.Tip(self)
        self._build()
        self.show("output")
        self.after(50, self._write_prisma_flow_on_start)

    def _build(self) -> None:
        left = ttk.Frame(self, width=280)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        names = ttk.Frame(left)
        names.pack(anchor="w", fill="x", padx=12, pady=(18, 12))
        tk.Label(
            names, text="Review runner", bg=BG, fg=BRAND, font=FONT_TITLE, anchor="w",
        ).pack(anchor="w")
        for spec in STEPS:
            btn = ui.button(
                left, spec["title"], lambda i=spec["id"]: self._open_step(i),
                kind="nav", width=256, height=34, align="left", padx=12,
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_btns[spec["id"]] = btn
        tools = ttk.Frame(left)
        tools.pack(fill="x", padx=10, pady=(16, 8))
        self._icon_btn(tools, "settings", lambda: self._open_step("output"), "Settings").pack(side="left", padx=(0, 6))
        self._icon_btn(tools, "packages", self._packages_window, "Python and packages").pack(side="left", padx=(0, 6))
        self._icon_btn(tools, "help", lambda: self._open_step("help"), "Help").pack(side="left")

        right = ttk.Frame(self)
        right.pack(side="right", fill="both", expand=True)
        self.nav_bar = ttk.Frame(right)
        self.nav_bar.pack(fill="x", padx=16, pady=(14, 4))
        self.back_btn = ui.button(self.nav_bar, "← Back", self._go_back)
        self.back_btn.pack(side="left")
        self.step_progress = ttk.Label(self.nav_bar, text="", style="Muted.TLabel")
        self.step_progress.pack(side="left", expand=True, padx=12)
        self.next_btn = ui.button(self.nav_bar, "Continue →", self._go_next, kind="accent")
        self.next_btn.pack(side="right")
        self.caption_row = ttk.Frame(right)
        self.caption_row.pack(fill="x", padx=16, pady=(4, 2))
        self.caption = ttk.Label(self.caption_row, text="", style="Head.TLabel")
        self.caption.pack(side="left")
        self.py_name = tk.Label(
            self.caption_row, text="", bg=BG, fg=MUTED, cursor="hand2",
            font=(UI, 11), takefocus=0,
        )
        self.py_name.pack(side="left", padx=(10, 0))
        cap_tools = ttk.Frame(self.caption_row)
        cap_tools.pack(side="right")
        self._icon_btn(cap_tools, "refresh", self._reload_view, "Refresh").pack(side="left")
        self.choice_note = ttk.Label(right, text="", style="Choice.TLabel")
        self.choice_note.pack(anchor="w", padx=16, pady=(0, 6))
        scroll_row = ttk.Frame(right)
        scroll_row.pack(fill="both", expand=True, padx=16)
        self._scroller = Scrollable(scroll_row)
        self._scroller.pack(fill="both", expand=True)
        self.body = self._scroller.inner
        self.status = ttk.Label(right, text="Output folder: (not set)", style="Muted.TLabel")
        self.status.pack(fill="x", padx=16, pady=(4, 2))
        self.log = text_widget(right, height=3, font=FONT_LOG)
        self.log.pack(fill="x", padx=16, pady=(0, 10))
        self._make_frames()

    def log_msg(self, text: str) -> None:
        self.log.insert("end", text.rstrip() + "\n")
        self.log.see("end")
        self.update_idletasks()

    def _need_folder(self) -> bool:
        if actions.has_data_root():
            return True
        messagebox.showinfo("Output folder", "Choose an output folder in step 1.")
        self.show("output")
        self._show_setup_tab("folder")
        return False

    def _guard_script_outputs(self, step: str, replace_var: tk.BooleanVar | None) -> bool:
        existing = actions.existing_script_outputs(step)
        if not existing:
            return True
        if replace_var is not None and replace_var.get():
            return True
        names = "\n".join(f"  {n}" for n in existing)
        if step in MANUAL_CHECK_UPLOADS:
            extra = (
                "To keep a corrected copy, use Upload after manual check on this step "
                "(a new file marked after_manual_check). Tick “Replace existing script files” "
                "only for a new automated run."
            )
        elif step == "raw":
            extra = (
                "After you have checked the merge tables, go to Audit and tick which records stay. "
                "Tick “Replace existing script files” only for a new automated merge."
            )
        else:
            extra = "Tick “Replace existing script files” only for a new automated run."
        messagebox.showinfo(
            "Keep the script output",
            "These files were written by the script and will not be replaced:\n"
            f"{names}\n\n{extra}",
        )
        return False

    def _manual_check_row(self, parent: ttk.Frame, step: str) -> None:
        spec = MANUAL_CHECK_UPLOADS[step]
        box = ttk.Frame(parent)
        box.pack(anchor="w", fill="x", pady=(12, 4))
        ttk.Label(box, text="After manual check", style="Head.TLabel").pack(anchor="w")
        self._hint(
            box,
            "Upload the spreadsheet you corrected. It is stored as a new file marked "
            "after_manual_check. The script output is not replaced.",
        )
        row = ttk.Frame(box)
        row.pack(anchor="w", pady=4)
        status = ttk.Label(row, text="", style="Muted.TLabel")

        def refresh_status() -> None:
            rec = actions.latest_manual_check(step)
            if rec:
                status.configure(text=f"After manual check: {rec['saved_as']}")
            else:
                status.configure(text="No file after manual check yet.")

        def go() -> None:
            if not self._need_folder():
                return
            path = filedialog.askopenfilename(
                title=spec["title"],
                filetypes=list(spec["types"]) + [("All files", "*.*")],
            )
            if not path:
                return
            dest = actions.save_checked_copy(step, Path(path))
            self.log_msg(f"After manual check (script output unchanged): {dest}")
            messagebox.showinfo(
                "After manual check",
                f"Marked as after manual check:\n{dest}\n\nThe script output was not replaced.",
            )
            refresh_status()
            self._refresh_tree()

        ui.button(row, "Upload after manual check", go).pack(side="left")
        status.pack(side="left", padx=12)
        self._refresh_manual_check[step] = refresh_status
        refresh_status()

    def show(self, step_id: str) -> None:
        self.step_id = step_id
        spec = next((s for s in STEPS if s["id"] == step_id), None)
        if step_id == "help":
            self.caption.configure(text="Help")
            self._set_script_link("")
        else:
            self.caption.configure(text=spec["headline"])
            self._set_script_link(step_script(spec or {}))
        for sid, frame in self.frames.items():
            if sid == step_id:
                frame.pack(fill="x", anchor="n")
            else:
                frame.pack_forget()
        self._scroller.reset()
        done = {s["id"]: actions.step_complete(s["id"]) for s in STEPS}
        if step_id == "help":
            self._set_choice("")
        elif done.get(step_id):
            self._set_choice("This step is done. Continue when you are ready.")
        else:
            self._set_choice(STEP_NEED.get(step_id, ""))
        self._sync_nav(done)
        self.after_idle(lambda sid=step_id: self._finish_show(sid))

    def _finish_show(self, step_id: str) -> None:
        if self.step_id != step_id:
            return
        if step_id != "help" and actions.has_data_root():
            created = actions.ensure_step_dirs(step_id)
            if created:
                self.log_msg("Created: " + ", ".join(created))
        fn = getattr(self, f"_refresh_{step_id}", None)
        if callable(fn):
            fn()
        mc = self._refresh_manual_check.get(step_id)
        if callable(mc):
            mc()
        self.body.update_idletasks()
        self._scroller._inner_cfg()

    def _set_choice(self, text: str) -> None:
        self.choice_note.configure(text=text)

    def _show_setup_tab(self, tab_id: str) -> None:
        if not self._setup_panes:
            return
        self._setup_tab = tab_id
        self._setup_seen.add(tab_id)
        last = SETUP_TABS[-1][0]
        for key, frame in self._setup_panes.items():
            if key == tab_id:
                frame.pack(fill="x")
            else:
                frame.pack_forget()
        for key, btn in self._setup_tab_btns.items():
            btn.set_kind("chip_on" if key == tab_id else "chip")
        if self._setup_actions is not None:
            if tab_id == last:
                self._setup_actions.pack(anchor="w", pady=(12, 0))
            else:
                self._setup_actions.pack_forget()
        if tab_id == "folder" and hasattr(self, "_refresh_tree"):
            self._refresh_tree()
        self._sync_nav()
        self.body.update_idletasks()
        self._scroller.reset()
        self._scroller._inner_cfg()

    def _show_screen_tab(self, tab_id: str) -> None:
        if not self._screen_panes:
            return
        self._screen_tab = tab_id
        for key, frame in self._screen_panes.items():
            if key == tab_id:
                frame.pack(fill="x")
            else:
                frame.pack_forget()
        for key, btn in self._screen_tab_btns.items():
            btn.set_kind("chip_on" if key == tab_id else "chip")
        if self._screen_actions is not None:
            self._screen_actions.pack(anchor="w", pady=(12, 0))
        self._sync_nav()
        self.body.update_idletasks()
        self._scroller.reset()
        self._scroller._inner_cfg()

    def _show_extract_tab(self, tab_id: str) -> None:
        if not self._extract_panes:
            return
        self._extract_tab = tab_id
        self._extract_seen.add(tab_id)
        for key, frame in self._extract_panes.items():
            if key == tab_id:
                frame.pack(fill="x")
            else:
                frame.pack_forget()
        for key, btn in self._extract_tab_btns.items():
            btn.set_kind("chip_on" if key == tab_id else "chip")
        self._sync_nav()
        self.body.update_idletasks()
        self._scroller.reset()
        self._scroller._inner_cfg()

    def _set_script_link(self, rel: str) -> None:
        parts = (rel or "").split()
        rel = parts[0] if parts else ""
        self.py_name.unbind("<Button-1>")
        if not rel:
            self.py_name.configure(text="")
            return
        self.py_name.configure(text=Path(rel).name)
        self.py_name.bind("<Button-1>", lambda _e, r=rel: self._script_window(r))

    def _script_window(self, rel: str) -> None:
        path = actions.script_file(rel)
        win = tk.Toplevel(self)
        win.title(path.name)
        win.configure(bg=BG)
        win.geometry("920x560")
        fr = ttk.Frame(win)
        fr.pack(fill="both", expand=True, padx=12, pady=10)
        ttk.Label(fr, text=path.name, style="Head.TLabel").pack(anchor="w")
        link = tk.Label(
            fr, text=str(path), bg=BG, fg=ACCENT, cursor="hand2",
            font=(UI, 12, "italic"), justify="left", wraplength=860, takefocus=0,
        )
        link.pack(anchor="w", pady=(0, 4))
        self._hint(fr, "Python file used on this step. Click the path or Open file to see it in your editor.")
        box = text_widget(fr, height=24, font=FONT_LOG)
        box.pack(fill="both", expand=True, pady=6)
        if path.exists():
            set_text(box, path.read_text(encoding="utf-8", errors="replace"))
        else:
            set_text(box, f"(file not found: {path})")
        box.configure(state="disabled")

        def open_file() -> None:
            if path.exists():
                actions.open_path(path)
            else:
                messagebox.showinfo("Script", f"File not found:\n{path}")

        def open_folder() -> None:
            folder = path.parent if path.parent.exists() else path
            if folder.exists():
                actions.open_path(folder)

        link.bind("<Button-1>", lambda _e: open_file())
        btns = ttk.Frame(fr)
        btns.pack(fill="x", pady=(4, 0))
        self._icon_btn(btns, "edit", open_file, "Edit file").pack(side="left")
        ui.button(btns, "Open folder", open_folder).pack(side="left", padx=6)
        ui.button(btns, "Close", win.destroy).pack(side="right")

    def _mark_done(self, btn, text: str) -> None:
        if btn is not None:
            btn.configure(text=text, style="Done.TButton")
        self._set_choice(text)
        self._sync_nav()

    def _allowed(self, step_id: str, done: dict | None = None) -> bool:
        if step_id == "help":
            return True
        path = self._path_ids()

        def complete(sid: str) -> bool:
            if done is not None:
                return bool(done.get(sid))
            return actions.step_complete(sid)

        if step_id not in path:
            return step_id in {s["id"] for s in STEPS} and complete(step_id)
        for sid in path:
            if sid == step_id:
                return True
            if not complete(sid):
                return False
        return True

    def _open_step(self, step_id: str) -> None:
        if self._allowed(step_id):
            self.show(step_id)
            return
        path = self._path_ids()
        blocked = next((s for s in path if not actions.step_complete(s)), path[0] if path else "output")
        spec = next((s for s in STEPS if s["id"] == blocked), None)
        need = STEP_NEED.get(blocked, "Finish the previous step first.")
        title = spec["title"] if spec else blocked
        messagebox.showinfo("One step at a time", f"Complete {title} first.\n{need}")
        self.show(blocked)

    def _step_label(self, step_id: str) -> str:
        spec = next(s for s in STEPS if s["id"] == step_id)
        return spec["title"]

    def _path_ids(self) -> list[str]:
        ids = [s["id"] for s in STEPS]
        if self.protocol_mode.get() == "after":
            return [i for i in ids if i != "protocol_plan"]
        return ids

    def _neighbors(self) -> tuple[str | None, str | None]:
        ids = self._path_ids()
        sid = self.step_id
        if sid not in ids:
            ids = [s["id"] for s in STEPS]
        if sid not in ids:
            return None, None
        i = ids.index(sid)
        prev = ids[i - 1] if i > 0 else None
        nxt = ids[i + 1] if i + 1 < len(ids) else None
        return prev, nxt

    def _sync_nav(self, done: dict | None = None) -> None:
        path = self._path_ids()
        done = done or {s["id"]: actions.step_complete(s["id"]) for s in STEPS}
        if self.step_id in path:
            n = path.index(self.step_id) + 1
            self.step_progress.configure(text=f"Step {n} of {len(path)}")
        elif self.step_id == "help":
            self.step_progress.configure(text="Help")
        else:
            self.step_progress.configure(text="")
        for spec in STEPS:
            sid = spec["id"]
            btn = self.nav_btns.get(sid)
            if btn is None:
                continue
            is_done = bool(done.get(sid))
            skipped = sid not in path
            if sid == self.step_id:
                style = "NavOn.TButton"
                label = f"✓  {spec['title']}" if is_done else spec["title"]
            elif skipped:
                style = "NavLocked.TButton"
                label = spec["title"]
            elif is_done:
                style = "NavDone.TButton"
                label = f"✓  {spec['title']}"
            elif self._allowed(sid, done):
                style = "Nav.TButton"
                label = spec["title"]
            else:
                style = "NavLocked.TButton"
                label = spec["title"]
            btn.configure(text=label, style=style)
        if self.step_id == "help":
            self.back_btn.configure(text="← Back", state="disabled")
            self.next_btn.configure(text="Continue →", state="disabled")
            return
        prev_id, next_id = self._neighbors()
        back_text, _ok = self._inner_back()
        if back_text:
            self.back_btn.configure(text=f"← {back_text}", state="normal")
        elif prev_id:
            self.back_btn.configure(text=f"← {self._step_label(prev_id)}", state="normal")
        else:
            self.back_btn.configure(text="← Back", state="disabled")
        fwd_text = self._inner_next_label()
        if fwd_text:
            self.next_btn.configure(text=f"{fwd_text} →", state="normal", style="Accent.TButton")
        elif next_id:
            ready = done.get(self.step_id) or self.step_id in self._before_continue
            self.next_btn.configure(
                text=f"{self._step_label(next_id)} →",
                state="normal",
                style="Accent.TButton" if ready else "TButton",
            )
        else:
            self.next_btn.configure(text="Done", state="disabled")

    def _tab_ids(self, tabs) -> list[str]:
        return [k for k, _ in tabs]

    def _inner_back(self) -> tuple[str, bool]:
        if self.step_id == "output":
            ids = self._tab_ids(SETUP_TABS)
            if self._setup_tab in ids:
                i = ids.index(self._setup_tab)
                if i > 0:
                    return SETUP_TABS[i - 1][1], True
        if self.step_id == "screen":
            ids = self._tab_ids(SCREEN_TABS)
            if self._screen_tab in ids:
                i = ids.index(self._screen_tab)
                if i > 0:
                    return SCREEN_TABS[i - 1][1], True
        if self.step_id == "extract":
            ids = self._tab_ids(EXTRACT_TABS)
            if self._extract_tab in ids:
                i = ids.index(self._extract_tab)
                if i > 0:
                    return EXTRACT_TABS[i - 1][1], True
        return "", False

    def _inner_next_label(self) -> str:
        if self.step_id == "output":
            ids = self._tab_ids(SETUP_TABS)
            if self._setup_tab in ids:
                i = ids.index(self._setup_tab)
                if i + 1 < len(ids):
                    return SETUP_TABS[i + 1][1]
        if self.step_id == "screen":
            ids = self._tab_ids(SCREEN_TABS)
            if self._screen_tab in ids:
                i = ids.index(self._screen_tab)
                if i + 1 < len(ids):
                    return SCREEN_TABS[i + 1][1]
        if self.step_id == "extract":
            ids = self._tab_ids(EXTRACT_TABS)
            if self._extract_tab in ids:
                i = ids.index(self._extract_tab)
                if i + 1 < len(ids):
                    return EXTRACT_TABS[i + 1][1]
        return ""

    def _go_back(self) -> None:
        if self.step_id == "output":
            ids = self._tab_ids(SETUP_TABS)
            if self._setup_tab in ids:
                i = ids.index(self._setup_tab)
                if i > 0:
                    self._show_setup_tab(ids[i - 1])
                    return
        if self.step_id == "screen":
            ids = self._tab_ids(SCREEN_TABS)
            if self._screen_tab in ids:
                i = ids.index(self._screen_tab)
                if i > 0:
                    self._show_screen_tab(ids[i - 1])
                    return
        if self.step_id == "extract":
            ids = self._tab_ids(EXTRACT_TABS)
            if self._extract_tab in ids:
                i = ids.index(self._extract_tab)
                if i > 0:
                    self._show_extract_tab(ids[i - 1])
                    return
        prev_id, _ = self._neighbors()
        if prev_id:
            self.show(prev_id)

    def _go_next(self) -> None:
        if self.step_id == "output":
            ids = self._tab_ids(SETUP_TABS)
            if self._setup_tab in ids:
                i = ids.index(self._setup_tab)
                if i + 1 < len(ids):
                    self._show_setup_tab(ids[i + 1])
                    return
            if not set(ids) <= self._setup_seen:
                missing = next(k for k in ids if k not in self._setup_seen)
                self._show_setup_tab(missing)
                messagebox.showinfo(
                    "Setup",
                    "Open every Setup tab (Folder through Funding) before the next step.",
                )
                return
        if self.step_id == "screen":
            ids = self._tab_ids(SCREEN_TABS)
            if self._screen_tab in ids:
                i = ids.index(self._screen_tab)
                if i + 1 < len(ids):
                    self._show_screen_tab(ids[i + 1])
                    return
        if self.step_id == "extract":
            ids = self._tab_ids(EXTRACT_TABS)
            if self._extract_tab in ids:
                i = ids.index(self._extract_tab)
                if i + 1 < len(ids):
                    self._show_extract_tab(ids[i + 1])
                    return
            if not set(ids) <= self._extract_seen:
                missing = next(k for k in ids if k not in self._extract_seen)
                self._show_extract_tab(missing)
                messagebox.showinfo(
                    "Extraction",
                    "Open every Extraction tab (Groups, PRISMA, Templates) before the next step.",
                )
                return
        fn = self._before_continue.get(self.step_id)
        if callable(fn) and fn() is False:
            return
        if self.step_id != "help" and not actions.step_complete(self.step_id):
            messagebox.showinfo("This step", STEP_NEED.get(self.step_id, "Finish this step before continuing."))
            return
        _, next_id = self._neighbors()
        if next_id:
            self.show(next_id)

    def _make_frames(self) -> None:
        makers = {
            "output": self._frame_output,
            "protocol_plan": lambda p: self._frame_protocol(p, "prospective"),
            "search": self._frame_search,
            "raw": self._frame_raw,
            "clean": self._frame_clean,
            "screen": self._frame_screen,
            "extract": self._frame_extract,
            "protocol_run": lambda p: self._frame_protocol(p, "retrospective"),
            "help": self._frame_help,
        }
        for spec in STEPS:
            fr = ttk.Frame(self.body)
            makers[spec["id"]](fr)
            self.frames[spec["id"]] = fr
        help_fr = ttk.Frame(self.body)
        makers["help"](help_fr)
        self.frames["help"] = help_fr

    def _set_folder(self, path: str) -> None:
        root = actions.set_data_root(Path(path))
        self.folder.set(str(root))
        self.status.configure(text=f"Output folder: {root}")
        if not actions.settings_path().exists():
            actions.save_settings(DEFAULT_SETTINGS)
        self._load_fields()
        self._refresh_tree()
        self.log_msg(f"Output → {root}")
        self._write_prisma_flow_on_start()

    def _pick_folder(self) -> None:
        path = filedialog.askdirectory(title="Output folder")
        if path:
            self._set_folder(path)

    def _write_prisma_flow_on_start(self) -> None:
        try:
            result = actions.save_prisma_flow()
        except Exception as exc:
            self.log_msg(f"PRISMA flow not written: {exc}")
            return
        files = ", ".join(result["files"])
        self.log_msg(f"PRISMA flow: {files} in 60_prisma/")
        for warn in result["payload"].get("warnings") or []:
            self.log_msg("PRISMA: " + warn)

    def _open_folder(self) -> None:
        if not self._need_folder():
            return
        os.startfile(data_root())

    def _collect_settings(self) -> dict:
        data = {}
        for key, widget in self.fields.items():
            if isinstance(widget, tk.Text):
                data[key] = get_text(widget)
            else:
                data[key] = widget.get().strip()
        dbs = [name for name, var in self.db_vars.items() if var.get()]
        other = data.get("databases_other") or ""
        data["databases"] = dbs
        data["registration_type"] = self.reg_type.get()
        data["protocol_mode"] = self.protocol_mode.get()
        rid = data.get("registration_id") or ""
        if data["registration_type"] == "None":
            data["registration"] = "None. Not registered in PROSPERO or another protocol registry."
        elif rid:
            data["registration"] = f"{data['registration_type']}: {rid}"
        else:
            data["registration"] = data["registration_type"]
        if other:
            data["databases"] = dbs + [other]
        return data

    def _load_fields(self) -> None:
        data = actions.load_settings()
        dbs = data.get("databases") or []
        if isinstance(dbs, str):
            dbs = [x.strip() for x in dbs.replace(";", ",").split(",") if x.strip()]
        chosen = {actions.canonical_database(x) for x in dbs}
        for name, var in self.db_vars.items():
            var.set(name in dbs or actions.canonical_database(name) in chosen)
        extra = [
            x for x in dbs
            if x not in DATABASE_CHOICES and actions.canonical_database(x) not in {actions.canonical_database(c) for c in DATABASE_CHOICES}
        ]
        if extra and "databases_other" in self.fields:
            self.fields["databases_other"].delete(0, "end")
            self.fields["databases_other"].insert(0, "; ".join(extra))
        self.reg_type.set(data.get("registration_type") or "None")
        self.protocol_mode.set(data.get("protocol_mode") or "plan")
        self._sync_nav()
        for key, widget in self.fields.items():
            if key == "databases_other" and extra:
                continue
            val = data.get(key, "")
            if isinstance(val, list):
                val = "\n".join(val)
            if isinstance(widget, tk.Text):
                set_text(widget, val)
            else:
                widget.delete(0, "end")
                widget.insert(0, val or "")

    def _save_settings(self) -> None:
        if not self._need_folder():
            return
        path = actions.save_settings(self._collect_settings())
        self.log_msg(f"Saved settings → {path.name}")

    def _hint(self, parent, text: str) -> None:
        ttk.Label(parent, text=text, style="Muted.TLabel", wraplength=740).pack(anchor="w")

    def _icon_btn(self, parent, kind: str, command, tip: str | None = None):
        return ui.icon_button(parent, kind, command, tip)

    def _full_record_tree(
        self,
        parent,
        columns: list[str],
        *,
        with_keep: bool = True,
        keep_heading: str = "Keep",
        selectmode: str = "extended",
    ) -> ttk.Treeview:
        wrap = ttk.Frame(parent)
        wrap.pack(fill="both", expand=True)
        wrap.grid_rowconfigure(0, weight=1)
        wrap.grid_columnconfigure(0, weight=1)
        cols = (["keep", *columns] if with_keep else list(columns))
        tree = ttk.Treeview(wrap, columns=cols, show="headings", selectmode=selectmode)
        ybar = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        xbar = ttk.Scrollbar(wrap, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        if with_keep:
            tree.heading("keep", text=keep_heading)
            tree.column("keep", width=78, minwidth=64, stretch=False, anchor="center")
        wide = {"TI", "Title", "AB", "KW", "N1", "N2", "note"}
        for col in columns:
            w = 320 if col in wide else (170 if col in {"AU", "DO", "T2", "note"} else 88)
            tree.heading(col, text="Note" if col == "note" else col)
            tree.column(col, width=w, minwidth=56, stretch=False, anchor="w")
        tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        tree.tag_configure("on", foreground=FG)
        tree.tag_configure("off", foreground=MUTED)
        self._bind_tree_copy(tree)
        return tree

    def _clipboard_copy(self, text: str, widget=None) -> None:
        w = widget or self
        text = text or ""
        w.clipboard_clear()
        w.clipboard_append(text)
        w.update_idletasks()

    @staticmethod
    def _tree_col(tree, *names: str) -> str | None:
        cols = set(tree["columns"])
        for name in names:
            if name in cols:
                return name
        return None

    def _tree_row_tsv(self, tree, iids: list[str]) -> str:
        cols = list(tree["columns"])
        headers = [str(tree.heading(c).get("text") or c) for c in cols]
        lines = ["\t".join(headers)]
        for iid in iids:
            vals = [str(v).replace("\t", " ").replace("\n", " ") for v in tree.item(iid, "values")]
            if len(vals) < len(cols):
                vals += [""] * (len(cols) - len(vals))
            lines.append("\t".join(vals[: len(cols)]))
        return "\n".join(lines)

    def _bind_tree_copy(self, tree) -> None:
        ctx: dict[str, str | None] = {"iid": None, "col": None}

        def locate(x, y) -> tuple[str | None, str | None]:
            if tree.identify_region(x, y) != "cell":
                return tree.identify_row(y) or None, None
            names = list(tree["columns"])
            try:
                idx = int(str(tree.identify_column(x)).replace("#", "")) - 1
                col = names[idx]
            except (ValueError, IndexError):
                col = None
            return tree.identify_row(y) or None, col

        def selected() -> list[str]:
            iids = list(tree.selection())
            if not iids and ctx.get("iid"):
                iids = [ctx["iid"]]
            return [i for i in iids if i]

        def copy_rows(_e=None):
            iids = selected()
            if not iids:
                return "break"
            self._clipboard_copy(self._tree_row_tsv(tree, iids), tree)
            return "break"

        def copy_cell(_e=None):
            iid, col = ctx.get("iid"), ctx.get("col")
            if not iid:
                iids = selected()
                iid = iids[0] if iids else None
            if not iid:
                return "break"
            if not col:
                col = self._tree_col(tree, "TI", "Title", "title") or list(tree["columns"])[0]
            self._clipboard_copy(tree.set(iid, col) or "", tree)
            return "break"

        def copy_named(*names: str):
            def _do(_e=None):
                col = self._tree_col(tree, *names)
                iids = selected()
                if not col or not iids:
                    return "break"
                parts = [tree.set(i, col) or "" for i in iids]
                self._clipboard_copy("\n".join(p for p in parts if p) or "\n".join(parts), tree)
                return "break"
            return _do

        def copy_search(_e=None):
            iids = selected()
            if not iids:
                return "break"
            py = self._tree_col(tree, "PY", "Year", "year")
            ti = self._tree_col(tree, "TI", "Title", "title")
            au = self._tree_col(tree, "AU", "authors")
            t2 = self._tree_col(tree, "T2", "JO")
            lines = []
            for iid in iids:
                bits = []
                if py:
                    bits.append(tree.set(iid, py) or "")
                if ti:
                    bits.append(tree.set(iid, ti) or "")
                if au:
                    bits.append(tree.set(iid, au) or "")
                if t2:
                    bits.append(tree.set(iid, t2) or "")
                lines.append(" ".join(b for b in bits if b))
            self._clipboard_copy("\n".join(lines), tree)
            return "break"

        menu = tk.Menu(tree, tearoff=0)
        menu.add_command(label="Copy row", command=copy_rows, accelerator="Ctrl+C")
        menu.add_command(label="Copy cell", command=copy_cell)
        menu.add_command(label="Copy title", command=copy_named("TI", "Title", "title"))
        menu.add_command(label="Copy year", command=copy_named("PY", "Year", "year"))
        menu.add_command(label="Copy authors", command=copy_named("AU", "authors"))
        menu.add_command(label="Copy T2", command=copy_named("T2", "JO"))
        menu.add_command(label="Copy DOI", command=copy_named("DO", "DOI", "doi"))
        menu.add_command(label="Copy for search", command=copy_search)

        def on_right(e):
            iid, col = locate(e.x, e.y)
            ctx["iid"], ctx["col"] = iid, col
            if iid and iid not in tree.selection():
                tree.selection_set(iid)
                tree.focus(iid)
            try:
                menu.tk_popup(e.x_root, e.y_root)
            finally:
                menu.grab_release()
            return "break"

        tree.bind("<Control-c>", copy_rows)
        tree.bind("<Control-C>", copy_rows)
        tree.bind("<Control-Insert>", copy_rows)
        tree.bind("<Button-3>", on_right)
        self._bind_tree_sort(tree)

    @staticmethod
    def _tree_sort_key(val) -> tuple:
        text = str(val or "").strip()
        if text in {record_audit.KEEP_OFF, "☐", "no", "false"}:
            return (0, 0.0)
        if text in {record_audit.KEEP_ON, "☑", "yes", "true"}:
            return (0, 1.0)
        if not text or text.lower() in {"nan", "none", "nat"}:
            return (2, "")
        compact = text.replace(" ", "").replace(",", ".")
        try:
            return (0, float(compact))
        except ValueError:
            pass
        return (1, text.casefold())

    def _bind_tree_sort(self, tree) -> None:
        labels = {col: str(tree.heading(col).get("text") or col) for col in tree["columns"]}
        state = {"col": None, "desc": False}

        def apply_sort() -> None:
            col = state["col"]
            if not col or col not in tree["columns"]:
                return
            rows = list(tree.get_children(""))
            rows.sort(key=lambda iid: self._tree_sort_key(tree.set(iid, col)), reverse=state["desc"])
            for i, iid in enumerate(rows):
                tree.move(iid, "", i)
            for name in tree["columns"]:
                mark = ""
                if name == col:
                    mark = " ↑" if not state["desc"] else " ↓"
                tree.heading(name, text=labels[name] + mark)

        def sort_by(col: str) -> None:
            if state["col"] == col:
                state["desc"] = not state["desc"]
            else:
                state["col"] = col
                state["desc"] = False
            apply_sort()

        for col in tree["columns"]:
            tree.heading(col, command=lambda c=col: sort_by(c))
        tree._sort_apply = apply_sort

    def _bind_tree_cell_edit(self, tree, *, editable: set[str], by_iid: dict) -> None:
        state: dict = {"entry": None}

        def finish(commit: bool) -> None:
            entry = state.get("entry")
            if entry is None:
                return
            iid, col = state.get("iid"), state.get("col")
            text = entry.get().strip() if commit else None
            try:
                entry.destroy()
            except tk.TclError:
                pass
            state["entry"] = None
            if not commit or iid is None or col is None:
                return
            if col == "DO":
                text = record_audit._norm_doi(text) or text
            tree.set(iid, col, text)
            rec = by_iid.get(iid)
            if rec is not None:
                rec[col] = text

        def start(e) -> str | None:
            if tree.identify_region(e.x, e.y) != "cell":
                return None
            names = list(tree["columns"])
            try:
                idx = int(str(tree.identify_column(e.x)).replace("#", "")) - 1
                col = names[idx]
            except (ValueError, IndexError):
                return None
            if col not in editable:
                return None
            iid = tree.identify_row(e.y)
            if not iid:
                return None
            finish(True)
            bbox = tree.bbox(iid, col)
            if not bbox:
                return None
            x, y, w, h = bbox
            entry = ttk.Entry(tree)
            entry.place(x=x, y=y, width=max(w, 80), height=h)
            entry.insert(0, tree.set(iid, col) or "")
            entry.select_range(0, "end")
            entry.focus_set()
            state.update(entry=entry, iid=iid, col=col)
            entry.bind("<Return>", lambda _e: finish(True))
            entry.bind("<Escape>", lambda _e: finish(False))
            entry.bind("<FocusOut>", lambda _e: finish(True))
            return "break"

        tree.bind("<Double-1>", start)

    def _open_doi_lookup(self, title: str, year: str = "", authors: str = "", t2: str = "") -> None:
        q = " ".join(x for x in (title, year, authors, t2) if x).strip()
        if not q:
            messagebox.showinfo("Look up DOI", "Select a row with a title first.")
            return
        webbrowser.open("https://search.crossref.org/search/works?q=" + urllib.parse.quote(q))

    DOI_LOOKUP_CSV_FIELDS = (
        ("row_ix", "row_ix"),
        ("PY", "year"),
        ("TI", "title"),
        ("AU", "authors"),
        ("T2", "T2"),
        ("JO", "journal"),
        ("DO", "DOI"),
        ("Source", "source"),
        ("TY", "TY"),
    )

    def _doi_lookup_csv_default(self) -> Path:
        folder = actions.p("20_data_clean", "21_audit") if actions.has_data_root() else Path.home()
        folder.mkdir(parents=True, exist_ok=True)
        return folder / "missing_doi_lookup.csv"

    def _export_doi_lookup_csv(self, tree, by_iid: dict, iid_order: list[str], parent=None) -> None:
        iids = list(tree.get_children())
        if tree.selection():
            iids = list(tree.selection())
        if not iids:
            iids = list(iid_order)
        if not iids:
            messagebox.showinfo("Export CSV", "No rows to export.", parent=parent)
            return
        dest = filedialog.asksaveasfilename(
            parent=parent,
            title="Export for DOI lookup",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("All files", "*.*")],
            initialfile=self._doi_lookup_csv_default().name,
            initialdir=str(self._doi_lookup_csv_default().parent),
        )
        if not dest:
            return
        fields = self.DOI_LOOKUP_CSV_FIELDS
        with open(dest, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([header for _key, header in fields])
            for iid in iids:
                rec = by_iid.get(iid) or {}
                row = []
                for key, _header in fields:
                    if key == "row_ix":
                        row.append(iid)
                        continue
                    if tree.exists(iid) and key in tree["columns"]:
                        row.append(tree.set(iid, key) or "")
                    else:
                        row.append(rec.get(key) or "")
                writer.writerow(row)
        self.log_msg(f"Exported {len(iids)} row(s) for DOI lookup → {Path(dest).name}")

    def _import_doi_lookup_csv(self, tree, by_iid: dict, parent=None) -> None:
        src = filedialog.askopenfilename(
            parent=parent,
            title="Import DOI CSV",
            filetypes=[("CSV", "*.csv"), ("All files", "*.*")],
            initialdir=str(self._doi_lookup_csv_default().parent),
        )
        if not src:
            return
        with open(src, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            messagebox.showinfo("Import DOI CSV", "The file has no data rows.", parent=parent)
            return
        n = 0
        for rec in rows:
            iid = str(rec.get("row_ix") or "").strip()
            doi = (rec.get("DOI") or rec.get("DO") or rec.get("doi") or "").strip()
            if not iid or iid not in by_iid:
                continue
            text = record_audit._norm_doi(doi) or doi
            if not text:
                continue
            if "DO" in tree["columns"] and tree.exists(iid):
                tree.set(iid, "DO", text)
            by_iid[iid]["DO"] = text
            n += 1
        if n == 0:
            messagebox.showinfo(
                "Import DOI CSV",
                "No DOI could be matched. Keep the row_ix column from the export and fill DOI.",
                parent=parent,
            )
            return
        self.log_msg(f"Imported DOI for {n} row(s) from {Path(src).name}. Save to keep them.")

    def _ask_doi(self, parent, *, title: str, year: str, authors: str, current: str, t2: str = "") -> str | None:
        win = tk.Toplevel(parent)
        win.title("Set DOI")
        win.configure(bg=BG)
        win.transient(parent)
        win.geometry("560x220")
        fr = ttk.Frame(win)
        fr.pack(fill="both", expand=True, padx=16, pady=12)
        ttk.Label(fr, text=(title or "(no title)")[:180], wraplength=520).pack(anchor="w")
        meta = " · ".join(x for x in (year, authors[:80] if authors else "") if x)
        if meta:
            ttk.Label(fr, text=meta, style="Muted.TLabel").pack(anchor="w", pady=(2, 8))
        ttk.Label(fr, text="DOI").pack(anchor="w")
        var = tk.StringVar(value=current or "")
        ent = ttk.Entry(fr, textvariable=var)
        ent.pack(fill="x", pady=(2, 8))
        ent.focus_set()
        result: dict[str, str | None] = {"doi": None}

        def ok(_e=None) -> None:
            result["doi"] = var.get().strip()
            win.destroy()

        def cancel() -> None:
            result["doi"] = None
            win.destroy()

        btns = ttk.Frame(fr)
        btns.pack(fill="x", pady=(8, 0))
        ui.button(btns, "Look up in Crossref", lambda: self._open_doi_lookup(title, year, authors, t2)).pack(side="left")
        ui.button(btns, "Save DOI", ok, kind="accent").pack(side="right")
        ui.button(btns, "Cancel", cancel).pack(side="right", padx=(0, 8))
        win.bind("<Return>", ok)
        win.wait_window()
        return result["doi"]

    def _reload_view(self) -> None:
        if hasattr(self, "_refresh_tree"):
            self._refresh_tree()
        fn = getattr(self, f"_refresh_{self.step_id}", None)
        if callable(fn):
            fn()
        mc = self._refresh_manual_check.get(self.step_id)
        if callable(mc):
            mc()
        self._sync_nav()
        self.log_msg("View refreshed.")

    def _format_bar(self, parent, *, include_ris: bool = True, include_xlsx: bool = True) -> dict[str, tk.BooleanVar]:
        keys = []
        vars_: dict[str, tk.BooleanVar] = {}
        for key in FORMAT_CHOICES:
            if key == "ris" and not include_ris:
                continue
            if key == "xlsx" and not include_xlsx:
                continue
            vars_[key] = tk.BooleanVar(value=False)
            keys.append(key)
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=8)
        summary = ttk.Label(row, text="", style="Muted.TLabel")

        def update_summary() -> None:
            picked = [k.upper() for k, v in vars_.items() if v.get()]
            summary.configure(text=" · ".join(picked) if picked else "No extra format selected")

        def open_win() -> None:
            self._export_dialog(vars_, keys)
            update_summary()

        ui.button(row, "Export", open_win, kind="ghost").pack(side="left")
        summary.pack(side="left", padx=12)
        update_summary()
        return vars_

    def _export_dialog(self, vars_: dict[str, tk.BooleanVar], keys: list[str]) -> None:
        win = tk.Toplevel(self)
        win.title("Export")
        win.configure(bg=BG)
        win.geometry("440x260")
        win.transient(self)
        fr = ttk.Frame(win)
        fr.pack(fill="both", expand=True, padx=18, pady=16)
        ttk.Label(fr, text="Export", style="Head.TLabel").pack(anchor="w")
        self._hint(
            fr,
            "Mark the extra formats to write. The working file stays as xlsx. "
            "Selected formats are highlighted.",
        )
        chips = ttk.Frame(fr)
        chips.pack(anchor="w", pady=16)

        def make_chip(key: str) -> None:
            btn = ui.button(
                chips,
                key.upper(),
                kind="chip_on" if vars_[key].get() else "chip",
                height=36,
            )

            def toggle(b=btn, k=key) -> None:
                vars_[k].set(not vars_[k].get())
                b.set_kind("chip_on" if vars_[k].get() else "chip")

            btn.set_command(toggle)
            btn.pack(side="left", padx=(0, 8))

        for key in keys:
            make_chip(key)
        ui.button(fr, "OK", win.destroy, kind="accent").pack(anchor="e", pady=(12, 0))
        win.grab_set()
        self.wait_window(win)

    def _apply_formats(self, folder: Path, vars_: dict[str, tk.BooleanVar], recursive: bool = False) -> None:
        extra = [k for k, v in vars_.items() if k in {"csv", "json"} and v.get()]
        if extra:
            for written in actions.extra_formats(folder, extra, recursive=recursive):
                self.log_msg(written)

    def _preview_window(self, status: str, title: str) -> None:
        if not self._need_folder():
            return
        data = actions.preview_table(status)
        win = tk.Toplevel(self)
        win.title(f"Preview — {title}")
        win.configure(bg=BG)
        win.geometry("980x480")
        fr = ttk.Frame(win)
        fr.pack(fill="both", expand=True, padx=12, pady=10)
        ttk.Label(fr, text=title, style="Head.TLabel").pack(anchor="w")
        if data.get("error"):
            self._hint(fr, data["error"])
            ui.button(fr, "Close", win.destroy).pack(anchor="e", pady=8)
            return
        extra = f"  ·  first {len(data['rows'])} shown" if data.get("truncated") else ""
        self._hint(fr, f"{data.get('file')}  ·  {data.get('n')} rows{extra}. Excel is not opened.")
        table_row = ttk.Frame(fr)
        table_row.pack(fill="both", expand=True, pady=6)
        cols = [f"c{i}" for i in range(len(data.get("headings") or []))]
        tree = ttk.Treeview(table_row, columns=cols, show="headings", selectmode="browse")
        ybar = ttk.Scrollbar(table_row, orient="vertical", command=tree.yview)
        xbar = ttk.Scrollbar(table_row, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        table_row.grid_rowconfigure(0, weight=1)
        table_row.grid_columnconfigure(0, weight=1)
        tree.tag_configure("odd", background=PANEL, foreground=FG)
        tree.tag_configure("even", background="#151b22", foreground=FG)
        for i, (head, width) in enumerate(zip(data.get("headings") or [], data.get("widths") or [])):
            tree.heading(cols[i], text=head, anchor="w")
            tree.column(cols[i], width=width, minwidth=50, stretch=(head == "Title"), anchor="w")
        for i, row in enumerate(data.get("rows") or []):
            tree.insert("", "end", values=row, tags=("even" if i % 2 else "odd",))
        self._bind_tree_copy(tree)
        ui.button(fr, "Close", win.destroy).pack(anchor="e")

    def _duplicate_window(self, kind: str) -> None:
        if not self._need_folder():
            return
        groups = actions.duplicate_groups(kind)
        if not groups:
            messagebox.showinfo("Duplicates", "No duplicate groups in the merge file.")
            return
        data = actions.load_record_decisions()
        title = "DOI duplicates" if kind == "doi" else "Title + year duplicates"
        win = tk.Toplevel(self)
        win.title(f"Compare — {title}")
        win.configure(bg=BG)
        win.geometry("1100x640")
        outer = ttk.Frame(win)
        outer.pack(fill="both", expand=True, padx=12, pady=10)
        ttk.Label(outer, text=title, style="Head.TLabel").pack(anchor="w")
        self._hint(
            outer,
            "The script kept the first record in each pair. Mark which one goes forward. "
            "The merge file is not replaced; your choice is stored as a record decision.",
        )
        body = ttk.Frame(outer)
        body.pack(fill="both", expand=True, pady=8)
        left = ttk.Frame(body)
        left.pack(side="left", fill="y")
        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))
        listbox = tk.Listbox(
            left, width=42, height=22, bg=PANEL, fg=FG, selectbackground=ACCENT,
            font=FONT, relief="flat", highlightthickness=0,
        )
        listbox.pack(fill="y", expand=True)
        state = {"i": 0, "data": data, "choice": tk.StringVar(value="")}
        cards = ttk.Frame(right)
        cards.pack(fill="both", expand=True)
        status = ttk.Label(right, text="", style="Muted.TLabel")
        status.pack(anchor="w", pady=(6, 0))

        def saved_for(group: dict) -> dict | None:
            return ((state["data"].get("duplicates") or {}).get(kind) or {}).get(group["key"])

        def fill_list() -> None:
            state["busy"] = True
            listbox.delete(0, "end")
            for i, g in enumerate(groups):
                rec = saved_for(g)
                mark = "·"
                if rec:
                    mark = "✓" if rec.get("action") == "keep_one" and rec.get("keep") == [g["script_keep"]] else "≠"
                    if rec.get("action") == "keep_both":
                        mark = "2"
                listbox.insert("end", f"{mark}  {i + 1}/{len(groups)}  {g['label'][:70]}")
            listbox.selection_clear(0, "end")
            listbox.selection_set(state["i"])
            listbox.see(state["i"])
            state["busy"] = False

        def show(i: int) -> None:
            state["i"] = max(0, min(i, len(groups) - 1))
            group = groups[state["i"]]
            for child in cards.winfo_children():
                child.destroy()
            rec = saved_for(group)
            if rec and rec.get("action") == "keep_both":
                state["choice"].set("both")
            elif rec and rec.get("keep"):
                state["choice"].set(str(rec["keep"][0]))
            else:
                state["choice"].set(str(group["script_keep"]))
            ttk.Label(
                cards,
                text=f"Group {state['i'] + 1} of {len(groups)}  ·  script kept row {group['script_keep']}",
                style="Head.TLabel",
            ).pack(anchor="w", pady=(0, 6))
            for m in group["members"]:
                box = ttk.Frame(cards)
                box.pack(fill="x", pady=4, ipady=4)
                script = "  (script keep)" if m["row_ix"] == group["script_keep"] else ""
                ttk.Radiobutton(
                    box,
                    text=f"Keep this record{script}",
                    value=str(m["row_ix"]),
                    variable=state["choice"],
                ).pack(anchor="w")
                meta = "  ·  ".join(
                    x for x in (
                        m.get("Source") or "",
                        m.get("TY_label") or m.get("TY") or "",
                        m.get("PY") or "",
                        m.get("status") or "",
                    ) if x
                )
                ttk.Label(box, text=meta, style="Muted.TLabel").pack(anchor="w")
                ttk.Label(box, text=m.get("TI") or "(no title)", wraplength=620).pack(anchor="w")
                au = m.get("AU") or ""
                if au:
                    ttk.Label(box, text=au[:200], style="Muted.TLabel", wraplength=620).pack(anchor="w")
                doi = m.get("DO") or ""
                jour = m.get("T2") or ""
                extra = "   ".join(x for x in ((f"DOI {doi}" if doi else ""), jour) if x)
                if extra:
                    ttk.Label(box, text=extra, style="Muted.TLabel", wraplength=620).pack(anchor="w")
            ttk.Radiobutton(
                cards, text="Not duplicates — keep both", value="both", variable=state["choice"],
            ).pack(anchor="w", pady=(8, 0))
            rec = saved_for(group)
            if rec:
                status.configure(text=f"Saved: {rec.get('action')}  keep={rec.get('keep')}")
            else:
                status.configure(text="Not saved yet — script keep is pre-selected.")
            fill_list()

        def apply_current(action: str | None = None) -> None:
            group = groups[state["i"]]
            val = state["choice"].get()
            if val == "both":
                keep = [int(m["row_ix"]) for m in group["members"]]
                action = "keep_both"
            else:
                keep = [int(val)] if val else [int(group["script_keep"])]
                action = action or "keep_one"
            state["data"] = actions.set_duplicate_choice(state["data"], group, action, keep)

        def keep_and_next() -> None:
            apply_current()
            if state["i"] + 1 < len(groups):
                show(state["i"] + 1)
            else:
                fill_list()
                status.configure(text="Last group. Save when you are done.")

        def accept_rest() -> None:
            apply_current()
            n_left = sum(1 for g in groups if g["key"] not in ((state["data"].get("duplicates") or {}).get(kind) or {}))
            if n_left and not messagebox.askyesno(
                "Accept script",
                f"Write the script keep for the remaining {n_left} groups that you have not marked?",
            ):
                return
            state["data"] = actions.confirm_script_duplicates(kind, state["data"])
            fill_list()
            status.configure(text="Remaining groups set to the script keep. Save to write the file.")

        def save() -> None:
            apply_current()
            dest = actions.save_record_decisions(state["data"])
            n_fw = actions.record_decision_summary().get("n_forward")
            self.log_msg(f"Record decisions saved: {dest} → {n_fw} go to screening")
            messagebox.showinfo(
                "Record decisions",
                f"Saved.\n{dest}\n\nRecords that go to screening: {n_fw}\n"
                "The merge file was not replaced.",
            )
            if hasattr(self, "_refresh_clean"):
                self._refresh_clean()
            self._refresh_tree()

        def on_list(_e) -> None:
            if state.get("busy") or not listbox.curselection():
                return
            j = int(listbox.curselection()[0])
            if j == state["i"]:
                return
            apply_current()
            show(j)

        listbox.bind("<<ListboxSelect>>", on_list)
        btns = ttk.Frame(outer)
        btns.pack(fill="x", pady=(8, 0))
        ui.button(btns, "Keep selected and next", keep_and_next, kind="accent").pack(side="left")
        ui.button(btns, "← Prev", lambda: show(state["i"] - 1)).pack(side="left", padx=6)
        ui.button(btns, "Next →", lambda: show(state["i"] + 1)).pack(side="left")
        ui.button(btns, "Accept script for remaining", accept_rest).pack(side="left", padx=12)
        ui.button(btns, "Save decisions", save).pack(side="left")
        ui.button(btns, "Close", win.destroy).pack(side="right")
        show(0)

    def _forward_window(self) -> None:
        if not self._need_folder():
            return
        payload = actions.records_for_picker()
        if payload.get("error"):
            messagebox.showinfo("Records", payload["error"])
            return
        data = actions.load_record_decisions()
        win = tk.Toplevel(self)
        win.title("Records that go to screening")
        win.configure(bg=BG)
        win.geometry("1100x640")
        fr = ttk.Frame(win)
        fr.pack(fill="both", expand=True, padx=12, pady=10)
        ttk.Label(fr, text="Choose which records go forward", style="Head.TLabel").pack(anchor="w")
        self._hint(
            fr,
            "Untick a row to stop it going to screening. Give a reason. "
            "The merge table is not replaced; this list becomes forward_records.xlsx.",
        )
        top = ttk.Frame(fr)
        top.pack(fill="x", pady=6)
        q = tk.StringVar(value="")
        ttk.Label(top, text="Find").pack(side="left")
        ttk.Entry(top, textvariable=q, width=36).pack(side="left", padx=6)
        only = tk.StringVar(value="forward")
        ttk.Combobox(
            top, textvariable=only, values=("forward", "dropped", "all"), width=10, state="readonly",
        ).pack(side="left", padx=6)
        counts = ttk.Label(top, text="", style="Muted.TLabel")
        counts.pack(side="left", padx=12)
        table_row = ttk.Frame(fr)
        table_row.pack(fill="both", expand=True, pady=6)
        cols = ("go", "src", "ty", "py", "ti", "doi")
        tree = ttk.Treeview(table_row, columns=cols, show="headings", selectmode="browse")
        ybar = ttk.Scrollbar(table_row, orient="vertical", command=tree.yview)
        xbar = ttk.Scrollbar(table_row, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        table_row.grid_rowconfigure(0, weight=1)
        table_row.grid_columnconfigure(0, weight=1)
        for key, head, width in (
            ("go", "Go", 50),
            ("src", "Database", 80),
            ("ty", "Type", 110),
            ("py", "Year", 50),
            ("ti", "Title", 420),
            ("doi", "DOI", 180),
        ):
            tree.heading(key, text=head, anchor="w")
            tree.column(key, width=width, minwidth=40, stretch=(key == "ti"), anchor="w")
        tree.tag_configure("odd", background=PANEL, foreground=FG)
        tree.tag_configure("even", background="#151b22", foreground=FG)
        tree.tag_configure("drop", foreground="#c9897a")
        self._bind_tree_copy(tree)
        by_id = {int(r["row_ix"]): dict(r) for r in payload.get("rows") or []}
        excluded = {int(e["row_ix"]): e for e in data.get("exclude") or [] if e.get("row_ix") is not None}

        def is_forward(row_ix: int) -> bool:
            row = by_id.get(row_ix) or {}
            if row_ix in excluded:
                return False
            return bool(row.get("forward"))

        def refill(*_a) -> None:
            tree.delete(*tree.get_children())
            needle = q.get().strip().lower()
            mode = only.get()
            n_yes = 0
            shown = 0
            for i, row in enumerate(payload.get("rows") or []):
                ix = int(row["row_ix"])
                going = is_forward(ix)
                if going:
                    n_yes += 1
                if mode == "forward" and not going:
                    continue
                if mode == "dropped" and going:
                    continue
                blob = " ".join(str(row.get(k) or "") for k in ("TI", "AU", "DO", "Source", "PY")).lower()
                if needle and needle not in blob:
                    continue
                tag = "drop" if not going else ("even" if shown % 2 else "odd")
                tree.insert(
                    "",
                    "end",
                    iid=str(ix),
                    values=(
                        "yes" if going else "no",
                        row.get("Source") or "",
                        row.get("TY_label") or row.get("TY") or "",
                        row.get("PY") or "",
                        (row.get("TI") or "")[:200],
                        row.get("DO") or "",
                    ),
                    tags=(tag,),
                )
                shown += 1
            counts.configure(text=f"{n_yes} go forward  ·  {len(excluded)} extra drops  ·  showing {shown}")

        reason = tk.StringVar(value=EXTRA_REASONS[0])
        note = tk.StringVar(value="")
        action = ttk.Frame(fr)
        action.pack(fill="x", pady=(4, 0))
        ttk.Label(action, text="Reason if it does not go forward").pack(side="left")
        ttk.Combobox(action, textvariable=reason, values=EXTRA_REASONS, width=48).pack(side="left", padx=6)
        ttk.Entry(action, textvariable=note, width=28).pack(side="left", padx=4)

        def selected_ix() -> int | None:
            cur = tree.selection()
            if not cur:
                return None
            return int(cur[0])

        def drop_selected() -> None:
            ix = selected_ix()
            if ix is None:
                return
            row = by_id.get(ix) or {}
            excluded[ix] = {"row_ix": ix, "reason": reason.get(), "TI": row.get("TI") or "", "note": note.get()}
            refill()

        def restore_selected() -> None:
            ix = selected_ix()
            if ix is None:
                return
            excluded.pop(ix, None)
            refill()

        def save() -> None:
            fresh = actions.load_record_decisions()
            fresh["exclude"] = []
            for ix, rec in excluded.items():
                actions.set_record_exclude(fresh, ix, rec.get("reason") or reason.get(), rec.get("TI") or "", rec.get("note") or "")
            dest = actions.save_record_decisions(fresh)
            self.log_msg(f"Record decisions saved: {dest}")
            messagebox.showinfo(
                "Records",
                f"Saved.\n{actions.record_decision_summary().get('n_forward')} records go to screening.\n"
                "The merge file was not replaced.",
            )
            if hasattr(self, "_refresh_clean"):
                self._refresh_clean()
            self._refresh_tree()
            win.destroy()

        self._icon_btn(action, "delete", drop_selected, "Do not go forward").pack(side="left", padx=8)
        ui.button(action, "Keep / restore", restore_selected).pack(side="left")
        ui.button(action, "Save list", save, kind="accent").pack(side="right")
        ui.button(action, "Close", win.destroy).pack(side="right", padx=6)
        q.trace_add("write", refill)
        only.trace_add("write", refill)
        tree.bind("<Double-1>", lambda _e: drop_selected())
        refill()

    def _entry_field(self, parent, key: str, label: str, hint: str) -> ttk.Entry:
        ttk.Label(parent, text=label).pack(anchor="w", pady=(8, 0))
        self._hint(parent, hint)
        ent = ttk.Entry(parent)
        ent.pack(fill="x", pady=(2, 0))
        self.fields[key] = ent
        return ent

    def _text_field(self, parent, key: str, label: str, hint: str, height: int = 3) -> tk.Text:
        ttk.Label(parent, text=label).pack(anchor="w", pady=(8, 0))
        self._hint(parent, hint)
        box = text_widget(parent, height=height)
        box.pack(fill="x", pady=(2, 0))
        self.fields[key] = box
        return box

    # --- 1 setup ---
    def _frame_output(self, p: ttk.Frame) -> None:
        tabs = ttk.Frame(p)
        tabs.pack(fill="x", pady=(0, 8))
        host = ttk.Frame(p)
        host.pack(fill="x")
        panes: dict[str, ttk.Frame] = {}
        for key, _label in SETUP_TABS:
            panes[key] = ttk.Frame(host)
        self._setup_panes = panes
        self._setup_tab_btns = {}
        for key, label in SETUP_TABS:
            btn = ui.button(
                tabs, label, lambda k=key: self._show_setup_tab(k),
                kind="chip", height=32, padx=12,
            )
            btn.pack(side="left", padx=(0, 6), pady=2)
            self._setup_tab_btns[key] = btn

        folder = panes["folder"]
        ttk.Label(folder, text="Where files go", style="Head.TLabel").pack(anchor="w")
        self._hint(
            folder,
            "Choose a folder for this run. The runner does not write into a hidden place: "
            "everything lands in this folder. A numbered tree is created as you go through the steps "
            "(not all at once).",
        )
        row = ttk.Frame(folder)
        row.pack(fill="x", pady=6)
        row.grid_columnconfigure(0, weight=1)
        ttk.Entry(row, textvariable=self.folder).grid(row=0, column=0, sticky="ew")
        self._icon_btn(row, "folder", self._pick_folder, "Choose folder").grid(row=0, column=1, padx=(8, 4), sticky="e")
        self._icon_btn(row, "folder_open", self._open_folder, "Open folder").grid(row=0, column=2, sticky="e")
        ttk.Label(folder, text="Folders that will appear here", style="Muted.TLabel").pack(anchor="w", pady=(8, 2))
        plan = text_widget(folder, height=7)
        plan.pack(fill="x")
        set_text(plan, FOLDER_PLAN)
        plan.configure(state="disabled")
        tree_head = ttk.Frame(folder)
        tree_head.pack(fill="x", pady=(8, 2))
        ttk.Label(tree_head, text="Already created in this folder", style="Muted.TLabel").pack(side="left")
        self._icon_btn(tree_head, "refresh", lambda: self._refresh_tree(), "Refresh").pack(side="left", padx=6)
        tree = text_widget(folder, height=8)
        tree.pack(fill="x")

        review = panes["review"]
        ttk.Label(review, text="This review (goes into the protocol)", style="Head.TLabel").pack(anchor="w")
        self._entry_field(
            review, "title", "Review title",
            "Full title of the systematic review, as it should appear on the protocol (PRISMA-P item 1).",
        )
        self._text_field(
            review, "authors", "Authors — one name per line",
            "Example: Lenka Miková (corresponding). Roles in parentheses are optional. Do not use commas to separate people.",
            height=4,
        )
        self._entry_field(
            review, "contact", "Corresponding e-mail",
            "E-mail of the corresponding author (PRISMA-P item 3). Not a Zotero or GitHub login.",
        )

        protocol = panes["protocol"]
        ttk.Label(protocol, text="Protocol registration", style="Head.TLabel").pack(anchor="w")
        reg_row = ttk.Frame(protocol)
        reg_row.pack(fill="x", pady=4)
        ttk.Combobox(
            reg_row, textvariable=self.reg_type, values=REGISTRATION_CHOICES, state="readonly", width=22,
        ).pack(side="left")
        ttk.Label(reg_row, text="ID or DOI (optional)").pack(side="left", padx=(12, 4))
        self.fields["registration_id"] = ttk.Entry(reg_row, width=36)
        self.fields["registration_id"].pack(side="left", fill="x", expand=True)
        self._hint(protocol, "Examples: PROSPERO CRD4202… · Zenodo 10.5281/zenodo.… — provider alone is enough.")
        ttk.Label(protocol, text="Where to go after Setup", style="Head.TLabel").pack(anchor="w", pady=(16, 0))
        self._hint(
            protocol,
            "Plan first if you will register the protocol before searching. "
            "After the run if you document a search that already happened (retrospective PRISMA-P).",
        )
        ttk.Radiobutton(
            protocol,
            text="Plan protocol first (before searching)",
            variable=self.protocol_mode,
            value="plan",
            command=self._sync_nav,
        ).pack(anchor="w", pady=(4, 0))
        ttk.Radiobutton(
            protocol,
            text="Protocol after the run (retrospective)",
            variable=self.protocol_mode,
            value="after",
            command=self._sync_nav,
        ).pack(anchor="w")

        databases = panes["databases"]
        ttk.Label(databases, text="Bibliographic databases", style="Head.TLabel").pack(anchor="w")
        self._hint(
            databases,
            "Tick every bibliographic database you searched (WoS, Scopus, …). "
            "Registers, websites, organisations and citation searching are the next tab.",
        )
        db_box = ttk.Frame(databases)
        db_box.pack(fill="x", pady=4)
        for i, name in enumerate(DATABASE_CHOICES):
            var = tk.BooleanVar(value=name in (DEFAULT_SETTINGS.get("databases") or []))
            ttk.Checkbutton(db_box, text=name, variable=var).grid(row=i // 2, column=i % 2, sticky="w", padx=4, pady=1)
            self.db_vars[name] = var
        self._entry_field(databases, "databases_other", "Other database(s)", "Optional. Separate extra names with a semicolon.")

        sources = panes["sources"]
        ttk.Label(sources, text="Other sources (not databases)", style="Head.TLabel").pack(anchor="w")
        self._hint(
            sources,
            "PRISMA 2020 Identification — registers, websites, organisations, citation searching. "
            "Leave at 0 if you did not use them. These counts are not in the merge report; "
            "they go into the flow diagram from Setup.",
        )
        self._entry_field(
            sources, "prisma_register_n", "Records from registers (n)",
            "Clinical trial or protocol registers. 0 if none.",
        )
        self._entry_field(
            sources, "prisma_registers", "Register names (optional)",
            "e.g. PROSPERO; ClinicalTrials.gov. Empty if n is 0.",
        )
        self._entry_field(
            sources, "prisma_website_n", "Records from websites (n)", "0 if none.",
        )
        self._entry_field(
            sources, "prisma_organisation_n", "Records from organisations (n)", "0 if none.",
        )
        self._entry_field(
            sources, "prisma_citation_n", "Records from citation searching (n)",
            "Snowballing / cited-reference search. 0 if none.",
        )

        doi = panes["doi"]
        ttk.Label(doi, text="DOIs of this run’s outputs (optional until minted)", style="Head.TLabel").pack(anchor="w")
        self._hint(doi, "Zenodo or other DOIs for the three products of this run. Leave blank until you have them.")
        self._entry_field(doi, "doi_protocol", "DOI — protocol", "https://doi.org/10.5281/zenodo.…")
        self._entry_field(doi, "doi_dataset", "DOI — dataset", "Search results, screening tables.")
        self._entry_field(doi, "doi_software", "DOI — software", "Scripts / this runner as used.")

        prisma = panes["prisma"]
        ttk.Label(prisma, text="Text copied into the protocol", style="Head.TLabel").pack(anchor="w")
        self._text_field(
            prisma, "rationale", "Rationale (PRISMA-P item 6)",
            "Why the review is needed. Two to four sentences. Empty is allowed; then the protocol will say it was not specified.",
            height=5,
        )
        self._text_field(
            prisma, "objectives", "Objectives (PRISMA-P item 7)",
            "The question(s) the review answers. Example: Which platforms and sensors were used for … ?",
            height=5,
        )
        self._text_field(
            prisma, "inclusion", "Inclusion rules (PRISMA-P item 8)",
            "Which records are eligible. The default is a generic starting point — rewrite it for your topic.",
            height=5,
        )

        other = panes["other"]
        ttk.Label(other, text="Other details", style="Head.TLabel").pack(anchor="w")
        self._text_field(
            other, "support", "Funding / support — one source per line",
            "PRISMA-P item 5. Each line is one grant or funder. Write None if there was no support. Not the software licence.",
            height=4,
        )
        self._entry_field(
            other, "github", "Code repository URL (optional)",
            "Public GitHub/GitLab of the scripts used for this review. Leave empty if you have not published the code yet.",
        )

        path_btns = ttk.Frame(p)
        self._setup_actions = path_btns
        save_btn = ui.button(path_btns, "Save these details")
        plan_btn = ui.button(path_btns, f"{self._step_label('protocol_plan')} →", kind="accent")
        after_btn = ui.button(path_btns, f"{self._step_label('search')} →")

        def setup_ready() -> bool:
            missing = [label for key, label in SETUP_TABS if key not in self._setup_seen]
            if missing:
                self._show_setup_tab(next(k for k, _l in SETUP_TABS if k not in self._setup_seen))
                messagebox.showinfo(
                    "Setup",
                    "Open every Setup tab before leaving this step:\n" + ", ".join(l for _k, l in SETUP_TABS) + ".",
                )
                return False
            return True

        def save_ok() -> bool:
            if not setup_ready():
                return False
            if not self._need_folder():
                return False
            self._save_settings()
            self._mark_done(save_btn, "Saved ✓")
            return True

        def go_plan() -> None:
            self.protocol_mode.set("plan")
            if save_ok():
                self._mark_done(plan_btn, "Saved ✓")
                self.show("protocol_plan")

        def go_after() -> None:
            self.protocol_mode.set("after")
            if save_ok():
                self._mark_done(after_btn, "Saved ✓")
                self.show("search")

        save_btn.configure(command=save_ok)
        plan_btn.configure(command=go_plan)
        after_btn.configure(command=go_after)
        save_btn.pack(side="left", padx=(0, 6))
        plan_btn.pack(side="left", padx=(0, 6))
        after_btn.pack(side="left")
        self._before_continue["output"] = save_ok

        def refresh_tree() -> None:
            if actions.has_data_root():
                set_text(tree, actions.list_tree() or "(folder is still empty — subfolders appear after each step)")
            else:
                set_text(tree, "(choose a folder above)")

        self._refresh_tree = refresh_tree
        self._refresh_output = refresh_tree
        self._show_setup_tab("folder")

    # --- protocol ---
    def _frame_protocol(self, p: ttk.Frame, mode: str) -> None:
        preview = text_widget(p, height=16)
        preview.pack(fill="both", expand=True, pady=(0, 8))

        def generate() -> None:
            if not self._need_folder():
                return
            self._save_settings()
            actions.ensure_step_dirs("protocol_plan" if mode == "prospective" else "protocol_run")
            info = protocol_export.save_markdown(mode)
            set_text(preview, info["markdown"])
            actions.journal(mode, "protocol", True, info["latest"])
            self.log_msg(f"Protocol → {info['latest']}")
            self._refresh_tree()
            self._mark_done(gen_btn, "Generated ✓")

        gen_btn = ui.button(p, "Generate protocol", generate, kind="accent")
        gen_btn.pack(anchor="w")

    # --- search ---
    def _pick_date(self, var: tk.StringVar) -> None:
        win = tk.Toplevel(self)
        win.title("Date")
        win.configure(bg=BG)
        win.transient(self)
        try:
            cur = datetime.strptime(var.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            cur = date.today()
        yv, mv = tk.IntVar(value=cur.year), tk.IntVar(value=cur.month)
        head = ttk.Frame(win)
        month_lbl = ttk.Label(head, text="", style="Head.TLabel")
        grid = ttk.Frame(win)

        def relabel() -> None:
            month_lbl.configure(text=calmod.month_name[mv.get()])

        def redraw() -> None:
            for child in grid.winfo_children():
                child.destroy()
            for i, name in enumerate("Mo Tu We Th Fr Sa Su".split()):
                ttk.Label(grid, text=name, style="Muted.TLabel").grid(row=0, column=i, padx=2)
            year = int(yv.get())
            month = int(mv.get())
            for r, week in enumerate(calmod.monthcalendar(year, month), start=1):
                for c, day in enumerate(week):
                    if day == 0:
                        continue
                    d = date(year, month, day)
                    ui.button(
                        grid, str(day),
                        lambda dd=d: (var.set(dd.isoformat()), win.destroy()),
                        width=36, height=32, padx=0,
                    ).grid(row=r, column=c, padx=2, pady=2)

        def prev() -> None:
            if mv.get() == 1:
                mv.set(12)
                yv.set(yv.get() - 1)
            else:
                mv.set(mv.get() - 1)
            relabel()
            redraw()

        def nxt() -> None:
            if mv.get() == 12:
                mv.set(1)
                yv.set(yv.get() + 1)
            else:
                mv.set(mv.get() + 1)
            relabel()
            redraw()

        def on_year() -> None:
            try:
                y = int(yv.get())
            except (tk.TclError, ValueError):
                return
            if y < 1990 or y > 2100:
                return
            relabel()
            redraw()

        head.pack(pady=8, padx=10)
        ui.button(head, "<", prev, width=36, height=32, padx=0).pack(side="left")
        month_lbl.pack(side="left", padx=8)
        year_box = ttk.Spinbox(head, from_=1990, to=2100, textvariable=yv, width=6, command=on_year)
        year_box.pack(side="left", padx=4)
        year_box.bind("<Return>", lambda _e: on_year())
        ui.button(head, ">", nxt, width=36, height=32, padx=0).pack(side="left")
        grid.pack(padx=8, pady=8)
        relabel()
        redraw()

    def _frame_search(self, p: ttk.Frame) -> None:
        ttk.Label(p, text="Keyword groups").pack(anchor="w")
        self._hint(p, "One group per line. AND between lines, OR inside a line.  term1, term2 | field   (all, topic, title, abstract)")
        groups = text_widget(p, height=7)
        groups.pack(fill="x", pady=4)
        params = actions.load_search_params(DEFAULT_SEARCH)
        lines = [f"{', '.join(g['terms'])} | {g.get('field', 'all')}" for g in params.get("groups") or []]
        set_text(groups, "\n".join(lines))
        row = ttk.Frame(p)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="Years").pack(side="left")
        y0 = ttk.Entry(row, width=8)
        y0.insert(0, str(params.get("year_from") or ""))
        y0.pack(side="left", padx=4)
        ttk.Label(row, text="-").pack(side="left")
        y1 = ttk.Entry(row, width=8)
        y1.insert(0, str(params.get("year_to") or ""))
        y1.pack(side="left", padx=4)
        ttk.Label(row, text="Language").pack(side="left", padx=(12, 0))
        lang = ttk.Entry(row, width=12)
        lang.insert(0, params.get("language") or "English")
        lang.pack(side="left", padx=4)
        ttk.Label(p, text="NOT groups (optional)").pack(anchor="w", pady=(8, 0))
        exclude = text_widget(p, height=2)
        exclude.pack(fill="x", pady=2)

        ttk.Label(p, text="Databases to search").pack(anchor="w", pady=(10, 2))
        db_frame = ttk.Frame(p)
        db_frame.pack(fill="x")
        search_db = {}
        saved = actions.load_settings() if actions.has_data_root() else DEFAULT_SETTINGS
        selected = saved.get("databases") or DEFAULT_SETTINGS.get("databases") or []
        if isinstance(selected, str):
            selected = [x.strip() for x in selected.replace(";", ",").split(",") if x.strip()]
        chosen = {actions.canonical_database(x) for x in selected}
        for i, name in enumerate(DATABASE_CHOICES):
            var = tk.BooleanVar(value=name in selected or actions.canonical_database(name) in chosen)
            ttk.Checkbutton(db_frame, text=name, variable=var).grid(row=i // 2, column=i % 2, sticky="w", padx=4)
            search_db[name] = var
        other_db = ttk.Entry(p)
        other_db.pack(fill="x", pady=4)
        extra = [
            x for x in selected
            if x not in DATABASE_CHOICES and actions.canonical_database(x) not in {actions.canonical_database(c) for c in DATABASE_CHOICES}
        ]
        if extra:
            other_db.insert(0, "; ".join(extra))
        self._hint(p, "Other database names, separated by semicolon.")

        def parse() -> dict:
            def rows(widget):
                out = []
                for line in get_text(widget).splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    if "|" not in line:
                        raise ValueError(f"Use: term1, term2 | field\n{line}")
                    terms_part, field = line.split("|", 1)
                    terms = [t.strip() for t in terms_part.split(",") if t.strip()]
                    out.append({"terms": terms, "field": field.strip().lower() or "all"})
                return out
            gs = rows(groups)
            if not gs:
                raise ValueError("Add at least one keyword group.")
            return {
                "groups": gs,
                "exclude": rows(exclude),
                "year_from": int(y0.get()) if y0.get().strip() else None,
                "year_to": int(y1.get()) if y1.get().strip() else None,
                "language": lang.get().strip() or None,
            }

        def selected_dbs() -> list[str]:
            names = [n for n, v in search_db.items() if v.get()]
            extra_txt = other_db.get().strip()
            if extra_txt:
                names += [x.strip() for x in extra_txt.split(";") if x.strip()]
            return names

        def persist_dbs() -> None:
            if not actions.has_data_root():
                return
            data = actions.load_settings()
            data["databases"] = selected_dbs()
            actions.save_settings(data)

        def save_query() -> bool:
            if not self._need_folder():
                return False
            try:
                par = parse()
            except Exception as exc:
                messagebox.showerror("Search", str(exc))
                return False
            persist_dbs()
            draft = actions.save_search_draft(par, selected_dbs())
            frozen = actions.freeze_search(par, selected_dbs())
            actions.journal("search", "query", True, str(frozen))
            self.log_msg(f"Draft: {draft}")
            self.log_msg(f"Frozen: {frozen}")
            self._refresh_tree()
            self._mark_done(query_btn, "Query saved ✓")
            return True

        btns = ttk.Frame(p)
        btns.pack(anchor="w", pady=8)
        query_btn = ui.button(btns, "Save query (draft + freeze)", save_query, kind="accent")
        query_btn.pack(side="left")
        self._hint(p, "One click writes 01_raw (draft history) and 02_final (frozen query). Order does not matter.")
        self._before_continue["search"] = save_query

    # --- RIS + merge ---
    def _frame_raw(self, p: ttk.Frame) -> None:
        self._hint(
            p,
            "Input: 2 or 3 RIS exports. For each, fill database, date and file together. "
            "Then Merge (combines them, removes duplicates and books).",
        )
        host = ttk.Frame(p)
        host.pack(fill="x", pady=4)
        slots: list[dict] = []

        def add_slot(prefill: dict | None = None) -> None:
            if len(slots) >= 4:
                return
            i = len(slots) + 1
            box = ttk.Frame(host)
            box.pack(fill="x", pady=8)
            box.grid_columnconfigure(1, weight=1)
            ttk.Label(box, text=f"Export {i}", style="Head.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 4))
            ttk.Label(box, text="Database").grid(row=1, column=0, sticky="w")
            raw_db = (prefill or {}).get("database") or ""
            db = tk.StringVar(value=actions.canonical_database(raw_db) or raw_db)
            ttk.Combobox(box, textvariable=db, values=DATABASE_CHOICES, width=22).grid(
                row=1, column=1, sticky="ew", padx=(8, 8)
            )
            ttk.Label(box, text="Date").grid(row=2, column=0, sticky="w", pady=4)
            raw_date = (prefill or {}).get("downloaded_at") or date.today().isoformat()
            date_var = tk.StringVar(value=actions.iso_date(raw_date))
            ttk.Entry(box, textvariable=date_var).grid(row=2, column=1, sticky="ew", padx=(8, 8))
            self._icon_btn(box, "calendar", lambda v=date_var: self._pick_date(v), "Calendar").grid(
                row=2, column=2, sticky="e",
            )
            ttk.Label(box, text="RIS file").grid(row=3, column=0, sticky="w")
            file_var = tk.StringVar(value=(prefill or {}).get("path") or (prefill or {}).get("file") or "")
            ttk.Entry(box, textvariable=file_var).grid(row=3, column=1, sticky="ew", padx=(8, 8))

            def browse(fv=file_var) -> None:
                path = filedialog.askopenfilename(
                    title="RIS file", filetypes=[("RIS", "*.ris"), ("All", "*.*")]
                )
                if path:
                    fv.set(path)

            def remove_slot(b=box) -> None:
                slots[:] = [s for s in slots if s["box"] is not b]
                b.destroy()

            self._icon_btn(box, "delete", remove_slot, "Remove this export").grid(row=0, column=2, sticky="e")
            self._icon_btn(box, "folder", browse, "Choose RIS file").grid(row=3, column=2, sticky="e")
            slots.append({"db": db, "date": date_var, "file": file_var, "box": box})

        def filled() -> list[dict]:
            rows = []
            for s in slots:
                path = s["file"].get().strip()
                db = s["db"].get().strip()
                if not path and not db:
                    continue
                iso = actions.iso_date(s["date"].get())
                s["date"].set(iso)
                rows.append({"database": db, "date": iso, "path": path})
            return rows

        def refresh() -> None:
            recs = actions.ris_exports() if actions.has_data_root() else []
            while slots:
                slot = slots.pop()
                slot["box"].destroy()
            n = max(2, min(4, len(recs) or 2))
            for i in range(n):
                pre = recs[i] if i < len(recs) else None
                if pre:
                    stored = actions.p("10_data_raw", "12_final", pre.get("file") or "")
                    pre = dict(pre)
                    if stored.exists():
                        pre["path"] = str(stored)
                add_slot(pre)

        def save_and_merge() -> None:
            if not self._need_folder():
                return
            rows = filled()
            ready = [r for r in rows if r["path"] and r["database"]]
            if len(ready) < 1:
                messagebox.showinfo("RIS", "Fill database, date and file for at least one export.")
                return
            missing_db = [r for r in rows if r["path"] and not r["database"]]
            if missing_db:
                messagebox.showinfo("RIS", "Each file needs a database name.")
                return
            names = [actions.canonical_database(r["database"]) for r in ready]
            if len(names) != len(set(names)):
                messagebox.showinfo(
                    "RIS",
                    "Two exports use the same database. Keep one file per database.",
                )
                return
            actions.ensure_step_dirs("raw")
            for r in ready:
                src = Path(r["path"])
                if not src.exists():
                    messagebox.showerror("RIS", f"File not found:\n{src}")
                    return
            if not self._guard_script_outputs("raw", replace_merge):
                return
            packed = actions.replace_ris_exports(ready)
            for info in packed["exports"]:
                self.log_msg(f"{info['database']}: {info['n_records']} records  ({info['file']})")
            if packed["removed"]:
                labels = []
                for name in packed["removed"]:
                    stem = Path(name).stem.replace("export_", "").replace("_", " ")
                    labels.append(actions.canonical_database(stem) or name)
                self.log_msg("Left out leftover files: " + ", ".join(labels))
            result = actions.run_script("pipeline/merge_and_classify.py")
            actions.journal("raw", "merge", result["ok"], seconds=result["seconds"])
            self.log_msg(result["log"])
            if not result["ok"]:
                messagebox.showerror("Merge", result["log"][-1500:])
            else:
                self.log_msg("Merged. Continue to Audit for the counts.")
                self._apply_formats(actions.p("20_data_clean"), merge_fmt)
                self._mark_done(merge_btn, "Merged ✓")
            refresh()
            self._refresh_tree()

        self._hint(p, "Working files stay as xlsx for the next step. Tick extra formats if you need copies.")
        merge_fmt = self._format_bar(p, include_ris=False, include_xlsx=False)
        btns = ttk.Frame(p)
        btns.pack(anchor="w", pady=8)
        self._icon_btn(btns, "add", lambda: add_slot(), "Add export").pack(side="left", padx=(0, 6))
        merge_btn = ui.button(btns, "Merge these files", save_and_merge, kind="accent")
        merge_btn.pack(side="left")
        replace_merge = tk.BooleanVar(value=False)
        ttk.Checkbutton(btns, text="Replace existing script files", variable=replace_merge).pack(
            side="left", padx=(12, 0)
        )
        self._ris_slots = slots
        self._refresh_raw = refresh

    def _audit_rows(self, kind: str) -> tuple[list[dict], list[dict]]:
        if kind == "both":
            groups = record_audit.keep_both_groups() if actions.has_data_root() else []
            applied = record_audit.apply_decisions(self._audit_data)
            fwd = set(applied.get("forward") or [])
            rows = []
            for g in groups:
                for m in g["members"]:
                    item = dict(m)
                    item["_group"] = g["key"]
                    item["_kind"] = g.get("kind") or "doi"
                    item["forward"] = int(m["row_ix"]) in fwd
                    rows.append(item)
            return self._with_record_notes(rows, groups)
        if kind in {"doi", "title"}:
            groups = actions.duplicate_groups(kind) if actions.has_data_root() else []
            if kind == "doi" and groups:
                groups = record_audit.sort_doi_groups(groups)
            saved = ((self._audit_data.get("duplicates") or {}).get(kind) or {})
            rows = []
            for g in groups:
                rec = saved.get(g["key"]) or {}
                keep_set = record_audit.keep_set_for_group(g, rec or None)
                for m in g["members"]:
                    item = dict(m)
                    item["_group"] = g["key"]
                    item["forward"] = int(m["row_ix"]) in keep_set
                    rows.append(item)
            return self._with_record_notes(rows, groups)
        if kind == "nodoi":
            rows = record_audit.records_without_doi() if actions.has_data_root() else []
            return self._with_record_notes(rows, [])
        status = "non_article_type" if kind == "book" else "correct_record"
        rows = actions.records_for_status(status) if actions.has_data_root() else []
        return self._with_record_notes(rows, [])

    def _with_record_notes(self, rows: list[dict], groups: list[dict]) -> tuple[list[dict], list[dict]]:
        notes = record_audit.record_note_map(self._audit_data)
        for row in rows:
            try:
                ix = int(row["row_ix"])
            except (TypeError, ValueError, KeyError):
                continue
            row["note"] = notes.get(ix, row.get("note") or "")
        return rows, groups

    def _audit_list_window(self, kind: str) -> None:
        if not self._need_folder():
            return
        self._audit_data = actions.load_record_decisions()
        rows, groups = self._audit_rows(kind)
        if not rows:
            messagebox.showinfo("Audit", "No records in this group.")
            return
        title = dict(AUDIT_TABS).get(kind, kind)
        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg=BG)
        win.geometry("1200x680")
        win.transient(self)
        outer = ttk.Frame(win)
        outer.pack(fill="both", expand=True, padx=12, pady=10)
        ttk.Label(outer, text=title, style="Head.TLabel").pack(anchor="w")
        if kind == "both":
            self._hint(
                outer,
                "These pairs currently keep two copies of the same work. Check each pair, "
                "untick a copy if only one should go forward, then Save to confirm.",
            )
        elif kind == "nodoi":
            self._hint(
                outer,
                "These records were not a Duplicate DOI or Duplicate title match. "
                "Look the DOI up (Crossref) and type it into DO — double-click the cell, or Set DOI. "
                "Export CSV has year, title, authors and T2 for searching; fill DOI and Import DOI CSV. "
                "No DOI is not a reason to drop them. Untick only those you want to hold back. "
                "A note can go on this group or on a row. If you do not decide, they go forward.",
            )
        elif kind == "title":
            self._hint(
                outer,
                "Title and year after DOI. If one copy has no DOI, Assign DOI copies it from the other. "
                "Tick which copies stay. The merge file is not replaced.",
            )
        elif kind == "doi":
            self._hint(
                outer,
                "Same DOI, two (or more) RIS records. Filter by form (journal / conference) "
                "and by whether the copies are identical or differ in title, authors, year or type. "
                "Save writes the counts and which copy was kept into the protocol. "
                "A note can go on this group or on a row. The merge file is not replaced.",
            )
        else:
            self._hint(
                outer,
                "Tick Keep for records that go to screening. Double-click DO or note to edit. "
                "A note can go on this group or on a row. The merge file is not replaced.",
            )
        q = tk.StringVar()
        qrow = ttk.Frame(outer)
        qrow.pack(fill="x", pady=(6, 4))
        ttk.Entry(qrow, textvariable=q).pack(side="left", fill="x", expand=True)
        form_box = None
        match_box = None
        form_by_group: dict[str, str] = {}
        match_by_group: dict[str, str] = {}
        form_keys: list[str] = []
        form_labels: list[str] = []
        match_keys: list[str] = []
        match_labels: list[str] = []
        if kind == "doi" and groups:
            from collections import Counter

            def _filter_combo(filters, by_group, width: int):
                n_cls = Counter(by_group.values())
                keys, labels = [], []
                for key, label in filters:
                    n = len(groups) if key == "all" else int(n_cls.get(key, 0))
                    if key != "all" and n == 0:
                        continue
                    keys.append(key)
                    labels.append(f"{label} ({n})")
                box = ttk.Combobox(qrow, values=labels, state="readonly", width=width)
                box.set(labels[0] if labels else "")
                box.pack(side="left", padx=(8, 0))
                return box, keys, labels

            form_by_group = {g["key"]: record_audit.doi_pair_form(g) for g in groups}
            match_by_group = {g["key"]: record_audit.doi_pair_match(g) for g in groups}
            form_box, form_keys, form_labels = _filter_combo(
                record_audit.DOI_FORM_FILTERS, form_by_group, 34,
            )
            match_box, match_keys, match_labels = _filter_combo(
                record_audit.DOI_MATCH_FILTERS, match_by_group, 42,
            )

            def form_key_of_label(text: str) -> str:
                for k, lab in zip(form_keys, form_labels):
                    if text == lab:
                        return k
                return "all"

            def match_key_of_label(text: str) -> str:
                for k, lab in zip(match_keys, match_labels):
                    if text == lab:
                        return k
                return "all"
        note_fr = ttk.LabelFrame(outer, text="Note for this group")
        note_fr.pack(fill="x", pady=(0, 6))
        group_note = text_widget(note_fr, height=3)
        group_note.pack(fill="x", padx=6, pady=6)
        saved_group_note = ((self._audit_data.get("group_notes") or {}).get(kind) or "")
        if saved_group_note:
            group_note.insert("1.0", saved_group_note)
        cols = record_audit.list_columns(rows)
        cols = list(cols)
        if kind in {"nodoi", "title", "kept"}:
            if "DO" not in cols:
                cols.insert(cols.index("TI") + 1 if "TI" in cols else 0, "DO")
            if "T2" not in cols:
                after = "AU" if "AU" in cols else ("TI" if "TI" in cols else None)
                cols.insert(cols.index(after) + 1 if after else 0, "T2")
        if "note" in cols:
            cols = [c for c in cols if c != "note"]
        if "DO" in cols:
            cols.insert(cols.index("DO") + 1, "note")
        else:
            cols.append("note")
        tree = self._full_record_tree(outer, cols)
        on, off = record_audit.KEEP_ON, record_audit.KEEP_OFF

        def row_values(rec: dict) -> list[str]:
            return [on if rec.get("forward") else off] + [rec.get(c) or "" for c in cols]

        by_iid: dict[str, dict] = {}
        iid_order: list[str] = []
        for rec in rows:
            keep = bool(rec.get("forward"))
            iid = str(int(rec["row_ix"]))
            by_iid[iid] = rec
            iid_order.append(iid)
            tree.insert(
                "", "end", iid=iid,
                values=row_values(rec),
                tags=("on" if keep else "off",),
            )
        self._bind_tree_cell_edit(tree, editable={"DO", "note"}, by_iid=by_iid)

        def apply_doi_filters(_e=None) -> None:
            if kind != "doi":
                return
            want_form = form_key_of_label(form_box.get()) if form_box is not None else "all"
            want_match = match_key_of_label(match_box.get()) if match_box is not None else "all"
            for iid in iid_order:
                rec = by_iid.get(iid) or {}
                gk = rec.get("_group") or ""
                form_ok = want_form == "all" or form_by_group.get(gk, "same_other") == want_form
                match_ok = want_match == "all" or match_by_group.get(gk, "identical") == want_match
                if form_ok and match_ok:
                    tree.reattach(iid, "", "end")
                else:
                    tree.detach(iid)
            if hasattr(tree, "_sort_apply"):
                tree._sort_apply()

        if form_box is not None:
            form_box.bind("<<ComboboxSelected>>", apply_doi_filters)
        if match_box is not None:
            match_box.bind("<<ComboboxSelected>>", apply_doi_filters)

        def toggle(iid: str) -> None:
            vals = list(tree.item(iid, "values"))
            if not vals:
                return
            keep = vals[0] != on
            vals[0] = on if keep else off
            tree.item(iid, values=vals, tags=("on" if keep else "off",))

        def on_click(e) -> None:
            if tree.identify_region(e.x, e.y) != "cell":
                return
            if tree.identify_column(e.x) != "#1":
                return
            iid = tree.identify_row(e.y)
            if iid:
                toggle(iid)

        def on_space(_e=None):
            for iid in tree.selection():
                toggle(iid)
            return "break"

        tree.bind("<Button-1>", on_click)
        tree.bind("<space>", on_space)

        def filter_tree(*_a) -> None:
            needle = q.get().strip().lower()
            if not needle:
                return
            for iid in tree.get_children():
                if needle in " ".join(str(v) for v in tree.item(iid, "values")).lower():
                    tree.see(iid)
                    tree.selection_set(iid)
                    return

        q.trace_add("write", filter_tree)

        def keep_all(value: bool) -> None:
            mark = on if value else off
            tag = "on" if value else "off"
            for iid in tree.get_children():
                vals = list(tree.item(iid, "values"))
                if not vals:
                    continue
                vals[0] = mark
                tree.item(iid, values=vals, tags=(tag,))

        def apply_row_edits(data: dict) -> dict:
            for iid in iid_order:
                rec = by_iid.get(iid) or {}
                title_v = rec.get("TI") or ""
                if tree.exists(iid) and "TI" in cols:
                    title_v = tree.set(iid, "TI") or title_v
                if tree.exists(iid) and "DO" in cols:
                    new = tree.set(iid, "DO") or ""
                    old = rec.get("DO") or ""
                    if record_audit._norm_doi(new) != record_audit._norm_doi(old):
                        data = record_audit.assign_doi(
                            data, int(iid), new, rec.get("_doi_from"),
                        )
                note_v = tree.set(iid, "note") if tree.exists(iid) and "note" in cols else (rec.get("note") or "")
                data = record_audit.set_record_note(data, int(iid), note_v, title_v)
            return record_audit.set_group_note(
                data, kind, group_note.get("1.0", "end").strip(),
            )

        def apply_tree(data: dict) -> dict:
            if kind in {"doi", "title", "both"}:
                for g in groups:
                    keep = []
                    for m in g["members"]:
                        iid = str(int(m["row_ix"]))
                        if tree.exists(iid) and tree.set(iid, "keep") == on:
                            keep.append(int(m["row_ix"]))
                    actions.set_duplicate_choice(
                        data, g, "keep_both" if len(keep) > 1 else "keep_one", keep,
                    )
                return apply_row_edits(data)
            if kind == "book":
                data["include"] = [
                    e for e in data.get("include") or []
                    if str(e.get("status")) != "non_article_type"
                ]
                for iid in iid_order:
                    if tree.exists(iid) and tree.set(iid, "keep") == on:
                        title_v = tree.set(iid, "TI") if "TI" in cols else ""
                        record_audit.set_row_keep(data, int(iid), True, title_v, "non_article_type")
                return apply_row_edits(data)
            status_fallback = "missing_doi" if kind == "nodoi" else "correct_record"
            for iid in iid_order:
                if not tree.exists(iid):
                    continue
                title_v = tree.set(iid, "TI") if "TI" in cols else ""
                status_v = tree.set(iid, "status") if "status" in cols else status_fallback
                if tree.set(iid, "keep") == on:
                    data["exclude"] = [
                        e for e in data.get("exclude") or [] if int(e.get("row_ix")) != int(iid)
                    ]
                else:
                    record_audit.set_row_keep(data, int(iid), False, title_v, status_v)
            return apply_row_edits(data)

        def save() -> None:
            data = actions.load_record_decisions()
            data = apply_tree(data)
            data.setdefault("reviewed", {})
            data["reviewed"][kind] = True
            dest = actions.save_record_decisions(data)
            self._audit_data = data
            applied = record_audit.apply_decisions(data)
            self.log_msg(
                f"Saved audit list ({title}) → {dest.name}  ·  "
                f"{applied.get('n_forward')} go to screening."
            )
            if hasattr(self, "_refresh_clean"):
                self._refresh_clean()
            self._mark_done(save_btn, "Saved ✓")

        def current_doi(iid: str) -> str:
            if "DO" in cols and tree.exists(iid):
                return tree.set(iid, "DO") or ""
            return (by_iid.get(iid) or {}).get("DO") or ""

        def assign_doi_from_pair() -> None:
            targets = list(tree.selection()) or list(tree.get_children())
            n = 0
            for iid in targets:
                if record_audit._norm_doi(current_doi(iid)):
                    continue
                rec = by_iid.get(iid) or {}
                g = next((x for x in groups if x["key"] == rec.get("_group")), None)
                if not g:
                    continue
                found: list[tuple[str, int]] = []
                for m in g["members"]:
                    mid = str(int(m["row_ix"]))
                    doi = current_doi(mid)
                    if record_audit._norm_doi(doi):
                        found.append((doi, int(m["row_ix"])))
                keys = {record_audit._norm_doi(d) for d, _ix in found}
                if len(keys) != 1:
                    continue
                doi, from_ix = found[0]
                if "DO" in cols and tree.exists(iid):
                    tree.set(iid, "DO", doi)
                rec["DO"] = doi
                rec["_doi_from"] = from_ix
                n += 1
            if n == 0:
                messagebox.showinfo(
                    "Assign DOI",
                    "No row could get a DOI. Select a record without DOI in a pair where the other copy has one.",
                )
            else:
                self.log_msg(f"Assigned DOI to {n} record(s) from the title pair. Save to keep it.")

        def selected_iid() -> str | None:
            cur = list(tree.selection())
            if cur:
                return cur[0]
            kids = list(tree.get_children())
            return kids[0] if len(kids) == 1 else None

        def lookup_selected() -> None:
            iid = selected_iid()
            if not iid:
                messagebox.showinfo("Look up DOI", "Select a row first.", parent=win)
                return
            rec = by_iid.get(iid) or {}
            title_v = tree.set(iid, "TI") if "TI" in cols else rec.get("TI") or ""
            year_v = tree.set(iid, "PY") if "PY" in cols else rec.get("PY") or ""
            au_v = tree.set(iid, "AU") if "AU" in cols else rec.get("AU") or ""
            t2_v = tree.set(iid, "T2") if "T2" in cols else rec.get("T2") or ""
            self._open_doi_lookup(title_v, year_v, au_v, t2_v)

        def set_doi_selected() -> None:
            iid = selected_iid()
            if not iid:
                messagebox.showinfo("Set DOI", "Select the row to fill.", parent=win)
                return
            rec = by_iid.get(iid) or {}
            title_v = tree.set(iid, "TI") if "TI" in cols else rec.get("TI") or ""
            year_v = tree.set(iid, "PY") if "PY" in cols else rec.get("PY") or ""
            au_v = tree.set(iid, "AU") if "AU" in cols else rec.get("AU") or ""
            t2_v = tree.set(iid, "T2") if "T2" in cols else rec.get("T2") or ""
            current = current_doi(iid)
            got = self._ask_doi(win, title=title_v, year=year_v, authors=au_v, current=current, t2=t2_v)
            if got is None:
                return
            text = record_audit._norm_doi(got) or got.strip()
            if "DO" in cols and tree.exists(iid):
                tree.set(iid, "DO", text)
            rec["DO"] = text
            self.log_msg("DOI filled in the table. Save to keep it.")

        foot = ttk.Frame(outer)
        foot.pack(fill="x", pady=(8, 0))
        if kind != "both":
            ui.button(foot, "Keep all", lambda: keep_all(True)).pack(side="left", padx=(0, 6))
            ui.button(foot, "Keep none", lambda: keep_all(False)).pack(side="left", padx=(0, 6))
        ui.button(foot, "Copy", lambda: tree.event_generate("<Control-c>")).pack(side="left", padx=(0, 6))
        if kind in {"nodoi", "title", "kept"}:
            ui.button(foot, "Look up DOI", lookup_selected).pack(side="left", padx=(0, 6))
            ui.button(foot, "Set DOI", set_doi_selected).pack(side="left", padx=(0, 6))
            ui.button(
                foot, "Export CSV",
                lambda: self._export_doi_lookup_csv(tree, by_iid, iid_order, win),
            ).pack(side="left", padx=(0, 6))
            ui.button(
                foot, "Import DOI CSV",
                lambda: self._import_doi_lookup_csv(tree, by_iid, win),
            ).pack(side="left", padx=(0, 6))
        if kind == "title":
            ui.button(foot, "Assign DOI", assign_doi_from_pair).pack(side="left", padx=(0, 6))
        save_btn = ui.button(foot, "Save", save, kind="accent")
        save_btn.pack(side="right")
        ui.button(foot, "Close", win.destroy).pack(side="right", padx=(0, 8))
        win.lift()
        win.focus_force()

    # --- audit ---
    def _frame_clean(self, p: ttk.Frame) -> None:
        summary = ttk.Label(p, text="", style="Head.TLabel")
        summary.pack(anchor="w")
        note = ttk.Label(p, text="", style="Muted.TLabel", wraplength=760)
        note.pack(anchor="w", pady=(2, 10))
        cards = ttk.Frame(p)
        cards.pack(fill="x")
        self._audit_tab_btns = {}
        hints = {
            "doi": "Same DOI — open the list and tick which copies stay.",
            "title": "After DOI. Same title and year — tick which copies stay, or Assign DOI when one copy has none.",
            "both": "Pairs that still keep two copies. Open, check, and save before you continue.",
            "book": "Books / e-books. Tick only if one should still go forward.",
            "nodoi": "Export CSV (year, title, authors, T2) to look up DOIs, then Import or Set DOI.",
            "kept": "Result after the groups above. Untick any that should not go to screening.",
        }
        hint_lbls: dict[str, ttk.Label] = {}
        for key, label in AUDIT_TABS:
            if key == "kept":
                rule = ttk.Frame(cards)
                rule.pack(fill="x", pady=(14, 8))
                ttk.Separator(rule, orient="horizontal").pack(side="left", fill="x", expand=True)
                ttk.Label(rule, text="Result", style="Muted.TLabel").pack(side="left", padx=8)
                ttk.Separator(rule, orient="horizontal").pack(side="left", fill="x", expand=True)
            box = ttk.Frame(cards)
            box.pack(fill="x", pady=6)
            btn = ui.button(
                box, label, lambda k=key: self._audit_list_window(k),
                kind="chip", height=32, padx=12,
            )
            btn.pack(side="left")
            self._audit_tab_btns[key] = btn
            hl = ttk.Label(box, text=hints[key], style="Muted.TLabel")
            hl.pack(side="left", padx=10)
            hint_lbls[key] = hl

        def refresh() -> None:
            if not actions.has_data_root():
                summary.configure(text="No merge yet")
                note.configure(text="Merge the RIS files in the previous step.")
                return
            self._audit_data = actions.load_record_decisions()
            dirty = False
            if not self._audit_data.get("original_applied") and record_audit.original_selection_path():
                self._audit_data = record_audit.apply_original_kept(self._audit_data)
                dirty = True
            if self._audit_data.get("original_applied"):
                self._audit_data, n_rel = record_audit.release_nodoi_original_excludes(self._audit_data)
                if n_rel:
                    dirty = True
            if dirty:
                actions.save_record_decisions(self._audit_data)
            info = actions.audit_overview()
            reviewed = self._audit_data.get("reviewed") or {}
            n_doi = info.get("n_doi") or 0
            n_doi_rec = info.get("n_doi_records") or 0
            n_title = info.get("n_title") or 0
            n_title_rec = info.get("n_title_records") or 0
            counts = {
                "doi": f"{n_doi}",
                "title": f"{n_title}",
                "both": f"{info.get('n_keep_both') or 0}",
                "book": f"{info['n_book']}",
                "nodoi": f"{info.get('n_nodoi') or 0}",
                "kept": f"{info.get('n_forward') or info['n_kept']}",
            }
            if int(info.get("n_keep_both") or 0) == 0:
                reviewed["both"] = True
            for key, label in AUDIT_TABS:
                n = counts[key]
                done_k = bool(reviewed.get(key))
                self._audit_tab_btns[key].set_text(
                    f"✓  {label} ({n})" if done_k else f"{label} ({n})"
                )
                self._audit_tab_btns[key].set_kind("done" if done_k else "chip")
            hint_lbls["doi"].configure(
                text=f"{n_doi} unique DOI · {n_doi_rec} records. Same DOI — tick which copies stay."
            )
            hint_lbls["title"].configure(
                text=(
                    f"{n_title} unique titles · {n_title_rec} records after DOI. "
                    "Tick which copies stay, or Assign DOI when one copy has none."
                )
            )
            orig = info.get("n_original") or 0
            summary.configure(text=f"After merge: {info.get('n_master') or 0}")
            bits = [
                "Open a group to see every column. Keep is a checkbox. Save in that window; the merge file stays.",
            ]
            if info.get("original_applied"):
                bits.append(
                    f"Original selection is locked for extra DOI rows ({orig} records with DOI). "
                    "Records without a DOI stay in the complete list that goes to screening."
                )
            if int(info.get("n_keep_both") or 0):
                bits.append("Open Keep both and save that table before continuing.")
            note.configure(text=" ".join(bits))

        def save_audit() -> bool:
            if not self._need_folder():
                return False
            if not self._audit_data:
                self._audit_data = actions.load_record_decisions()
            if not self._audit_data.get("original_applied") and record_audit.original_selection_path():
                self._audit_data = record_audit.apply_original_kept(self._audit_data)
            self._audit_data.setdefault("reviewed", {})
            if record_audit.keep_both_unconfirmed(self._audit_data):
                messagebox.showinfo(
                    "Keep both",
                    "Open Keep both, check those pairs, and save that table before continuing.",
                )
                return False
            dest = actions.save_record_decisions(self._audit_data)
            applied = record_audit.apply_decisions(self._audit_data)
            self.log_msg(
                f"Saved audit → {dest.name}  ·  {applied.get('n_forward')} go to screening."
            )
            self._mark_done(save_btn, "Audit saved ✓")
            refresh()
            return True

        btns = ttk.Frame(p)
        btns.pack(anchor="w", pady=(16, 0))
        save_btn = ui.button(btns, "Save", save_audit, kind="accent")
        save_btn.pack(side="left")
        self._refresh_clean = refresh
        self._before_continue["clean"] = save_audit

    # --- screen ---
    def _frame_screen(self, p: ttk.Frame) -> None:
        cfg = actions.load_screening_config()
        tabs = ttk.Frame(p)
        tabs.pack(fill="x", pady=(0, 8))
        host = ttk.Frame(p)
        host.pack(fill="x")
        panes = {key: ttk.Frame(host) for key, _label in SCREEN_TABS}
        self._screen_panes = panes
        self._screen_tab_btns = {}
        for key, label in SCREEN_TABS:
            btn = ui.button(
                tabs, label, lambda k=key: self._show_screen_tab(k),
                kind="chip", height=32, padx=12,
            )
            btn.pack(side="left", padx=(0, 6), pady=2)
            self._screen_tab_btns[key] = btn

        kw = panes["keywords"]
        self._hint(
            kw,
            "Select a group, then tick its words and set the weight. "
            "A match in title, abstract or keywords adds that weight. Review terms set records aside.",
        )
        thr = ttk.Frame(kw)
        thr.pack(fill="x", pady=(4, 10))
        ttk.Label(thr, text="Include ≥").pack(side="left")
        inc = ttk.Entry(thr, width=5)
        inc.insert(0, str((cfg.get("thresholds") or {}).get("include_min", 6)))
        inc.pack(side="left", padx=(4, 16))
        ttk.Label(thr, text="Maybe ≥").pack(side="left")
        may = ttk.Entry(thr, width=5)
        may.insert(0, str((cfg.get("thresholds") or {}).get("maybe_min", 3)))
        may.pack(side="left", padx=(4, 16))
        ttk.Label(thr, text="Strict ≥").pack(side="left")
        strict_e = ttk.Entry(thr, width=5)
        strict_e.insert(0, str((cfg.get("must_cite_strict") or {}).get("score_min", 7)))
        strict_e.pack(side="left", padx=4)

        body = ttk.Frame(kw)
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body)
        left.pack(side="left", fill="y", padx=(0, 16))
        ttk.Label(left, text="Groups", style="Muted.TLabel").pack(anchor="w")
        lb = tk.Listbox(
            left, height=14, width=38, activestyle="none", exportselection=False,
            bg=CARD, fg=FG, selectbackground=ACCENT, selectforeground=ACCENT_FG,
            relief="flat", highlightthickness=1, highlightbackground=BORDER,
            font=FONT,
        )
        lb.pack(fill="y", expand=True, pady=(4, 0))
        detail = ttk.Frame(body)
        detail.pack(side="left", fill="both", expand=True)

        term_groups: dict[str, dict] = {}
        group_panes: dict[str, ttk.Frame] = {}
        saved_terms = cfg.get("terms") or {}
        saved_w = cfg.get("weights") or {}
        alias = {"uav": "uav_direct", "domain": "agriculture"}
        defaults_w = {"soil_moisture": 2, "uav": 3, "scaling": 2, "domain": 1}

        def add_term_check(key: str, word: str, checked: bool = True) -> None:
            rec = term_groups[key]
            var = tk.BooleanVar(value=checked)
            ttk.Checkbutton(rec["items"], text=word, variable=var).pack(anchor="w", pady=1)
            rec["vars"].append((var, word))

        def list_line(i: int) -> str:
            key, label = TERM_GROUPS[i]
            w = term_groups[key]["weight"].get().strip() or "0"
            return f"{label}   ·  {w}"

        def refresh_list(keep_sel: int | None = None) -> None:
            sel = keep_sel
            if sel is None:
                cur = lb.curselection()
                sel = int(cur[0]) if cur else 0
            lb.delete(0, "end")
            for i, _pair in enumerate(TERM_GROUPS):
                lb.insert("end", list_line(i))
            lb.selection_set(sel)
            lb.activate(sel)
            lb.see(sel)

        for i, (key, label) in enumerate(TERM_GROUPS):
            pane = ttk.Frame(detail)
            group_panes[key] = pane
            head = ttk.Frame(pane)
            head.pack(anchor="w", fill="x")
            ttk.Label(head, text=label, style="Head.TLabel").pack(side="left")
            ttk.Label(head, text="weight", style="Muted.TLabel").pack(side="left", padx=(16, 4))
            w_e = ttk.Entry(head, width=5)
            raw = saved_w.get(key)
            if raw is None:
                raw = saved_w.get(alias.get(key, ""), defaults_w.get(key, 0))
            w_e.insert(0, str(raw if raw is not None else 0))
            w_e.pack(side="left")
            w_e.bind("<KeyRelease>", lambda _e, idx=i: refresh_list(idx))
            items = ttk.Frame(pane)
            items.pack(anchor="w", fill="both", expand=True, pady=(10, 6))
            term_groups[key] = {"items": items, "vars": [], "weight": w_e, "label": label}
            for word in saved_terms.get(key) or []:
                add_term_check(key, word, True)
            add_row = ttk.Frame(pane)
            add_row.pack(anchor="w", fill="x")
            add_row.grid_columnconfigure(0, weight=1)
            add_e = ttk.Entry(add_row)
            add_e.grid(row=0, column=0, sticky="ew")

            def _add(_e=None, k=key, entry=add_e, idx=i) -> None:
                word = entry.get().strip()
                if not word:
                    return
                if word.lower() in {t.lower() for _v, t in term_groups[k]["vars"]}:
                    entry.delete(0, "end")
                    return
                add_term_check(k, word, True)
                entry.delete(0, "end")
                refresh_list(idx)
                self._set_choice(f"Added “{word}”")

            self._icon_btn(add_row, "add", _add, "Add word").grid(row=0, column=1, padx=(8, 0), sticky="e")
            add_e.bind("<Return>", _add)

        def show_group(_e=None) -> None:
            cur = lb.curselection()
            idx = int(cur[0]) if cur else 0
            key = TERM_GROUPS[idx][0]
            for k, pane in group_panes.items():
                pane.pack_forget()
            group_panes[key].pack(fill="both", expand=True, anchor="nw")

        lb.bind("<<ListboxSelect>>", show_group)
        refresh_list(0)
        show_group()

        dl = panes["download"]
        self._hint(
            dl,
            "xlsx for screened_records and review_articles is required (Extraction reads those files) "
            "and cannot be turned off. Tick extra formats only if you need copies. "
            "Empty = skip an optional file. Existing script files are not replaced.",
        )
        saved_fmts = cfg.get("output_formats") or {}
        old_out = cfg.get("outputs") or {}
        fmt_vars: dict[str, dict[str, tk.BooleanVar]] = {}

        def initial_formats(item: dict) -> list[str]:
            key = item["key"]
            if key in saved_fmts:
                got = [str(x).lower() for x in (saved_fmts.get(key) or [])]
            elif key == "summary":
                got = []
                if old_out.get("summary_txt", True):
                    got.append("txt")
                if old_out.get("summary_xlsx"):
                    got.append("xlsx")
                got = got or list(item["default"])
            elif old_out.get(key, bool(item["default"])):
                got = list(item["default"])
            else:
                got = []
            for fmt in item.get("required") or ():
                if fmt not in got:
                    got.append(fmt)
            return got

        for group in SCREEN_OUTPUT_GROUPS:
            ttk.Label(dl, text=group["title"], style="Head.TLabel").pack(anchor="w", pady=(10, 0))
            ttk.Label(dl, text=group["folder"], style="Muted.TLabel").pack(anchor="w")
            box = ttk.Frame(dl)
            box.pack(fill="x", pady=(2, 2))
            for item in group["items"]:
                row = ttk.Frame(box)
                row.pack(fill="x", pady=3)
                ttk.Label(row, text=item["stem"], width=24, anchor="w").pack(side="left")
                chips = ttk.Frame(row)
                chips.pack(side="left")
                picked = {f.lower() for f in initial_formats(item)}
                required = {str(x).lower() for x in (item.get("required") or ())}
                fmt_vars[item["key"]] = {}
                for fmt in item["formats"]:
                    locked = fmt.lower() in required
                    var = tk.BooleanVar(value=True if locked else fmt in picked)
                    fmt_vars[item["key"]][fmt] = var
                    chip = ui.button(
                        chips, fmt.upper(), kind="chip_on" if var.get() else "chip",
                        height=28, padx=10,
                    )

                    def toggle(b=chip, v=var, lock=locked, name=fmt, stem=item["stem"]) -> None:
                        if lock and v.get():
                            self._set_choice(f"{name.upper()} for {stem} is required for Extraction.")
                            return
                        v.set(not v.get())
                        b.set_kind("chip_on" if v.get() else "chip")

                    chip.set_command(toggle)
                    chip.pack(side="left", padx=(0, 6))

        def collect() -> dict:
            data = actions.load_screening_config()
            weights = {}
            for key, rec in term_groups.items():
                try:
                    w = int(float(rec["weight"].get() or 0))
                except ValueError:
                    w = 0
                weights[key] = w
                if key == "uav":
                    weights["uav_direct"] = w
                if key == "domain":
                    weights["agriculture"] = w
            data["weights"] = weights
            data["thresholds"] = {
                "include_min": int(float(inc.get() or 6)),
                "maybe_min": int(float(may.get() or 3)),
            }
            data.setdefault("must_cite_strict", {})["score_min"] = int(float(strict_e.get() or 7))
            terms = data.setdefault("terms", {})
            for key, rec in term_groups.items():
                terms[key] = [word for var, word in rec["vars"] if var.get()]
            formats = {
                key: [fmt for fmt, var in rec.items() if var.get()]
                for key, rec in fmt_vars.items()
            }
            for group in SCREEN_OUTPUT_GROUPS:
                for item in group["items"]:
                    for fmt in item.get("required") or ():
                        bucket = formats.setdefault(item["key"], [])
                        if fmt not in bucket:
                            bucket.append(fmt)
            data["output_formats"] = formats
            data["outputs"] = {
                "screened_xlsx": bool(formats.get("screened_xlsx")),
                "summary_txt": "txt" in formats.get("summary", []),
                "summary_xlsx": "xlsx" in formats.get("summary", []),
                "keyword_txt": bool(formats.get("keyword_txt")),
                "ris_all": bool(formats.get("ris_all")),
                "ris_include": bool(formats.get("ris_include")),
                "ris_core": bool(formats.get("ris_core")),
                "ris_must_cite": bool(formats.get("ris_must_cite")),
                "ris_extended_not_strict": bool(formats.get("ris_extended_not_strict")),
                "vos_pair": bool(formats.get("vos_pair")),
                "reviews_xlsx_ris": bool(formats.get("reviews_xlsx_ris")),
                "reviews_uav_ris": bool(formats.get("reviews_uav_ris")),
                "csv": False,
                "json": False,
            }
            return data

        def save_cfg() -> Path | None:
            if not self._need_folder():
                return None
            path = actions.save_screening_config(collect())
            actions.journal("screen", "save_config", True, str(path))
            self.log_msg(f"Config → {path}")
            return path

        def run_screen() -> None:
            path = save_cfg()
            if not path:
                return
            if not self._guard_script_outputs("screen", replace_screen):
                return
            result = actions.run_script(
                "pipeline/screening_and_deep_classify.py",
                extra_args=["--config", str(path)],
            )
            actions.journal("screen", "run", result["ok"], seconds=result["seconds"])
            self.log_msg(result["log"])
            if not result["ok"]:
                messagebox.showerror("Screening", result["log"][-1500:])
            else:
                self._mark_done(screen_btn, "Screening done ✓")
            self._refresh_tree()

        actions_row = ttk.Frame(p)
        self._screen_actions = actions_row
        ui.button(actions_row, "Save config", save_cfg).pack(side="left", padx=(0, 6))
        screen_btn = ui.button(actions_row, "Run screening", run_screen, kind="accent")
        screen_btn.pack(side="left")
        replace_screen = tk.BooleanVar(value=False)
        ttk.Checkbutton(actions_row, text="Replace existing script files", variable=replace_screen).pack(
            side="left", padx=(12, 6)
        )
        self._manual_check_row(dl, "screen")
        self._before_continue["screen"] = lambda: save_cfg() is not None
        self._show_screen_tab("keywords")

    def _extract_group_tree(self, parent) -> ttk.Treeview:
        wrap = ttk.Frame(parent)
        wrap.pack(fill="x", pady=(6, 0))
        wrap.grid_rowconfigure(0, weight=1)
        wrap.grid_columnconfigure(0, weight=1)
        cols = ("year", "title", "authors", "doi", "decision", "flags")
        tree = ttk.Treeview(wrap, columns=cols, show="headings", selectmode="extended", height=12)
        ybar = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        xbar = ttk.Scrollbar(wrap, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        widths = {
            "year": 55, "title": 420, "authors": 180, "doi": 170,
            "decision": 80, "flags": 90,
        }
        heads = {
            "year": "Year", "title": "Title", "authors": "Authors",
            "doi": "DOI", "decision": "Group", "flags": "Flags",
        }
        for col in cols:
            tree.heading(col, text=heads[col], anchor="w")
            tree.column(col, width=widths[col], minwidth=48, stretch=(col == "title"), anchor="w")
        tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        self._bind_tree_copy(tree)
        return tree

    def _extract_selected_keys(self, kind: str) -> list[str]:
        tree = self._extract_trees.get(kind)
        if tree is None:
            return []
        mapping = self._extract_rowkeys.get(kind) or {}
        return [mapping[iid] for iid in tree.selection() if iid in mapping]

    @staticmethod
    def _extract_dest_options(kind: str) -> list[tuple[str, str]]:
        flag = kind in {"core", "extended", "must_cite"}
        items: list[tuple[str, str]] = []
        if flag:
            items.append(("clear_flag", "Clear flag only (stay in Include)"))
        skip = {kind}
        if kind == "unclassified":
            skip.add("unclassified")
        if kind in {"include", "include_rest", "core", "extended", "must_cite"}:
            skip.add("include")
        for key, label in (
            ("unclassified", "Unclassified (drop from this list)"),
            ("reviews", "Reviews"),
            ("include", "Include"),
            ("maybe", "Maybe"),
            ("exclude", "Exclude"),
        ):
            if key in skip:
                continue
            items.append((key, label))
        if kind in {"include", "include_rest"}:
            items.append(("include", "Include + Core/Extended flag"))
        elif flag:
            items.append(("include", "Include (rest or new flag)"))
        return items

    def _extract_preview_parent(self, kind: str):
        win = self._extract_preview_wins.get(kind)
        try:
            if win is not None and win.winfo_exists():
                return win
        except tk.TclError:
            pass
        return self

    def _extract_row_in_group(self, tree, iid: str) -> bool:
        vals = tree.item(iid, "values")
        if not vals:
            return False
        return str(vals[0]).strip() == record_audit.KEEP_ON

    def _extract_checked_keys(self, kind: str, *, in_group: bool) -> list[str]:
        tree = self._extract_trees.get(kind)
        if tree is None:
            return []
        mapping = self._extract_rowkeys.get(kind) or {}
        checks = self._extract_in_group.setdefault(kind, {})
        keys = []
        for iid in tree.get_children():
            key = mapping.get(iid)
            if not key:
                continue
            marked = self._extract_row_in_group(tree, iid)
            checks[key] = marked
            if marked == in_group:
                keys.append(key)
        return keys

    def _fill_extract_tree(self, kind: str, needle: str = "") -> None:
        tree = self._extract_trees.get(kind)
        if tree is None:
            return
        tree.delete(*tree.get_children())
        mapping: dict[str, str] = {}
        self._extract_rowkeys[kind] = mapping
        checks = self._extract_in_group.setdefault(kind, {})
        cols = self._extract_tree_cols.get(kind) or []
        if not actions.has_data_root():
            return
        rows = actions.extract_rows(kind)
        want = (needle or "").strip().lower()
        on, off = record_audit.KEEP_ON, record_audit.KEEP_OFF
        default_on = kind != "unclassified"
        for i, rec in enumerate(rows):
            key = rec.get("_key") or str(rec.get("row_ix") or i)
            blob = " ".join(str(v or "") for v in rec.values()).lower()
            if want and want not in blob:
                continue
            in_g = checks.get(key, default_on)
            checks[key] = in_g
            iid = str(i)
            mapping[iid] = key
            cells = []
            for col in cols:
                val = rec.get(col)
                if val is True:
                    cells.append("yes")
                elif val is False or val is None:
                    cells.append("")
                else:
                    cells.append(str(val))
            tree.insert(
                "",
                "end",
                iid=iid,
                values=([on if in_g else off] + cells),
                tags=("on" if in_g else "off",),
            )
        if hasattr(tree, "_sort_apply"):
            tree._sort_apply()

    def _extract_apply_preview(self, kind: str, *, confirm: bool = False) -> bool:
        parent = self._extract_preview_parent(kind)
        if not self._need_folder():
            return False
        dest_var = self._extract_move_dest.get(kind)
        if dest_var is None:
            messagebox.showinfo("Extraction", "Pick a destination group.", parent=parent)
            return False
        label = dest_var.get()
        dest = ""
        for key, lab in self._extract_dest_options(kind):
            if lab == label:
                dest = key
                break
        if not dest:
            messagebox.showinfo("Extraction", "Pick a destination group.", parent=parent)
            return False
        unclassified = kind == "unclassified"
        keys = self._extract_checked_keys(kind, in_group=unclassified)
        if not keys:
            keys = self._extract_selected_keys(kind)
        if not keys:
            messagebox.showinfo(
                "Extraction",
                "Tick the records to assign, then Save."
                if unclassified
                else "Untick (☐) or select the rows that do not belong, then Save.",
                parent=parent,
            )
            return False
        core = False
        extended = False
        if dest == "include":
            core_var = self._extract_move_core.get(kind)
            ext_var = self._extract_move_ext.get(kind)
            core = bool(core_var.get()) if core_var is not None else False
            extended = bool(ext_var.get()) if ext_var is not None else False
        title = EXTRACT_GROUP_LABELS.get(kind, kind)
        dest_title = label
        verb = "Assign" if unclassified else "Save"
        if confirm and not messagebox.askyesno(
            "Extraction",
            f"{verb} {len(keys)} record(s) from {title} → {dest_title}?",
            parent=parent,
        ):
            return False
        result = actions.extract_move(
            kind, keys, dest,
            must_cite=extended or core,
            must_cite_strict=core,
        )
        n = int(result.get("n_moved") or 0)
        if n <= 0:
            messagebox.showerror(
                "Extraction",
                "Nothing was saved. The ticked rows could not be matched in the screening table. "
                "Leave this window open and try Save again, or copy the title into Search first.",
                parent=parent,
            )
            return False
        self.log_msg(f"Extraction recode: {kind} → {dest} n={n}")
        checks = self._extract_in_group.get(kind) or {}
        for key in keys:
            checks.pop(key, None)
        self._refresh_extract()
        messagebox.showinfo(
            "Extraction",
            f"Saved {n} record(s): {title} → {dest_title}. Written to the protocol.",
            parent=parent,
        )
        return True

    def _extract_warn_unclassified(self, *, for_continue: bool) -> bool:
        if not actions.has_data_root():
            return True
        info = actions.extract_overview()
        n_unc = int(info.get("n_unclassified") or 0)
        if n_unc <= 0:
            return True
        if for_continue:
            ok = messagebox.askyesno(
                "Unclassified records",
                f"{n_unc} record(s) are still unclassified. Continue anyway?",
            )
            if not ok:
                self._show_extract_tab("groups")
            return ok
        return messagebox.askyesno(
            "Unclassified records",
            f"{n_unc} record(s) are still unclassified and will not go into the templates. Run templates anyway?",
        )

    def _extract_list_window(self, kind: str) -> None:
        self._extract_preview_window(kind)

    def _extract_preview_window(self, kind: str) -> None:
        if not self._need_folder():
            return
        wins = self._extract_preview_wins
        existing = wins.get(kind)
        if existing is not None:
            try:
                if existing.winfo_exists():
                    existing.lift()
                    existing.focus_force()
                    self._fill_extract_tree(kind)
                    return
            except tk.TclError:
                wins.pop(kind, None)
        title = EXTRACT_GROUP_LABELS.get(kind, kind)
        win = tk.Toplevel(self)
        win.title(f"{title} — records")
        win.configure(bg=BG)
        win.geometry("1200x680")
        win.transient(self)
        wins[kind] = win
        outer = ttk.Frame(win)
        outer.pack(fill="both", expand=True, padx=12, pady=10)
        ttk.Label(outer, text=title, style="Head.TLabel").pack(anchor="w")
        hints = {
            "reviews": (
                "Set aside before scoring — not Include / Maybe / Exclude. "
                "Untick a row that is not a review, pick where it belongs, then Move."
            ),
            "include": (
                "Exclusive screening group. Untick rows that do not belong, pick another group, then Move. "
                "To add Core or Extended, choose Include + flag."
            ),
            "include_rest": (
                "Include records that are not must-cite. Untick to move them, or choose Include + flag "
                "to mark Core or Extended."
            ),
            "maybe": (
                "Middle score band — not the same as Exclude. Full template = Include + Maybe; "
                "refined template = Include only. Default PRISMA leaves Maybe out of full-text retrieval. "
                "If you will not get the PDF, move to Exclude. If it should be extracted, move to Include."
            ),
            "exclude": "Exclusive group. Not extracted. Untick a row that should not stay here, pick a group, then Move.",
            "must_cite": (
                "Working total = Core ∪ Extended (HIGH in the template). Untick to drop the flag or move the record."
            ),
            "core": "Flag on Include (direct UAV plus scaling / fusion). Untick, then Clear flag only or Move to another group.",
            "extended": "Flag on Include (wider must-cite). Untick, then Clear flag only or Move to another group.",
            "unclassified": (
                "Holding tank after a record left an automatic group. Tick the rows, pick Reviews / Include / Maybe / Exclude, then Assign."
            ),
        }
        self._hint(outer, hints.get(kind, "Untick records that do not belong, pick a group, then Move."))
        q = tk.StringVar()
        qrow = ttk.Frame(outer)
        qrow.pack(fill="x", pady=(6, 4))
        ttk.Entry(qrow, textvariable=q).pack(side="left", fill="x", expand=True)
        rows = actions.extract_rows(kind) if actions.has_data_root() else []
        cols = record_audit.list_columns(rows)
        front = [
            c for c in (
                "PY", "TI", "AU", "DO", "screening_decision", "relevance_score",
                "must_cite", "must_cite_strict", "is_review",
            ) if c in cols
        ]
        cols = front + [c for c in cols if c not in front]
        if not cols:
            cols = [
                "PY", "TI", "AU", "DO", "screening_decision", "relevance_score",
                "must_cite", "must_cite_strict", "is_review", "AB", "KW",
            ]
        self._extract_tree_cols[kind] = cols
        keep_heading = "Assign" if kind == "unclassified" else "In group"
        tree = self._full_record_tree(
            outer, cols, keep_heading=keep_heading, selectmode="extended",
        )
        self._extract_trees[kind] = tree
        on, off = record_audit.KEEP_ON, record_audit.KEEP_OFF

        def toggle(iid: str) -> None:
            vals = list(tree.item(iid, "values"))
            if not vals:
                return
            keep = vals[0] != on
            vals[0] = on if keep else off
            tree.item(iid, values=vals, tags=("on" if keep else "off",))
            mapping = self._extract_rowkeys.get(kind) or {}
            key = mapping.get(iid)
            if key:
                self._extract_in_group.setdefault(kind, {})[key] = keep

        def on_click(e) -> None:
            if tree.identify_region(e.x, e.y) != "cell":
                return
            if tree.identify_column(e.x) != "#1":
                return
            iid = tree.identify_row(e.y)
            if iid:
                toggle(iid)

        def on_space(_e=None):
            for iid in tree.selection():
                toggle(iid)
            return "break"

        tree.bind("<Button-1>", on_click)
        tree.bind("<space>", on_space)
        self._fill_extract_tree(kind)

        def refill(*_a) -> None:
            self._fill_extract_tree(kind, q.get())

        q.trace_add("write", refill)
        options = self._extract_dest_options(kind)
        labels = [lab for _key, lab in options]
        default = labels[0] if labels else "Unclassified"
        if kind == "unclassified":
            default = next((lab for key, lab in options if key == "include"), default)
        dest = tk.StringVar(value=default)
        self._extract_move_dest[kind] = dest
        core_var = tk.BooleanVar(value=False)
        ext_var = tk.BooleanVar(value=False)
        self._extract_move_core[kind] = core_var
        self._extract_move_ext[kind] = ext_var
        below = ttk.Frame(outer)
        below.pack(fill="x", pady=(8, 0))
        flags_row = ttk.Frame(below)
        ttk.Label(flags_row, text="If Include, also set a flag:").pack(side="left")
        ttk.Checkbutton(flags_row, text="Core", variable=core_var).pack(side="left", padx=(8, 4))
        ttk.Checkbutton(flags_row, text="Extended", variable=ext_var).pack(side="left")
        foot = ttk.Frame(below)
        foot.pack(fill="x")
        ttk.Label(foot, text="Move to" if kind != "unclassified" else "Assign to").pack(side="left")
        ttk.Combobox(
            foot, textvariable=dest, values=labels, state="readonly", width=36,
        ).pack(side="left", padx=8)
        ui.button(
            foot,
            "Save",
            lambda k=kind: self._extract_apply_preview(k),
            kind="accent",
        ).pack(side="left", padx=(0, 8))
        ttk.Label(
            foot,
            text=(
                "Tick rows, pick a group, then Save."
                if kind == "unclassified"
                else "Untick (☐) rows that do not belong, pick where they go, then Save."
            ),
            style="Muted.TLabel",
        ).pack(side="left")

        def dest_is_include() -> bool:
            return dest.get().startswith("Include")

        def sync_flags(*_a) -> None:
            if dest_is_include():
                flags_row.pack(fill="x", pady=(0, 6), before=foot)
            else:
                flags_row.pack_forget()
                core_var.set(False)
                ext_var.set(False)

        dest.trace_add("write", sync_flags)
        if dest_is_include():
            flags_row.pack(fill="x", pady=(0, 6), before=foot)

        def on_close() -> None:
            unclassified = kind == "unclassified"
            dirty = self._extract_checked_keys(kind, in_group=unclassified)
            if dirty:
                go = messagebox.askyesnocancel(
                    "Extraction",
                    f"{len(dirty)} record(s) were changed and not saved. Save now?",
                    parent=win,
                )
                if go is True:
                    if not self._extract_apply_preview(kind):
                        return
                elif go is None:
                    return
            self._extract_trees.pop(kind, None)
            self._extract_rowkeys.pop(kind, None)
            self._extract_tree_cols.pop(kind, None)
            self._extract_in_group.pop(kind, None)
            self._extract_move_dest.pop(kind, None)
            self._extract_move_core.pop(kind, None)
            self._extract_move_ext.pop(kind, None)
            wins.pop(kind, None)
            win.destroy()

        ui.button(foot, "Close", on_close).pack(side="right")
        win.protocol("WM_DELETE_WINDOW", on_close)
        win.lift()
        win.focus_force()

    def _extract_group_row(self, parent, kind: str, title: str, hint: str, *, indent: bool = False) -> ttk.Label:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4, padx=(28, 0) if indent else 0)
        ui.button(
            row, "Open", lambda k=kind: self._extract_preview_window(k), height=32, padx=12,
        ).pack(side="left")
        ttk.Label(row, text=title, style="Head.TLabel").pack(side="left", padx=(10, 8))
        count = ttk.Label(row, text="—", style="Head.TLabel")
        count.pack(side="left")
        ttk.Label(row, text=hint, style="Muted.TLabel").pack(side="left", padx=12)
        self._extract_count_lbls[kind] = count
        return count

    def _frame_extract(self, p: ttk.Frame) -> None:
        summary = ttk.Label(p, text="", style="Head.TLabel")
        summary.pack(anchor="w")
        ov_split = ttk.Label(p, text="", style="Muted.TLabel", wraplength=760)
        ov_split.pack(anchor="w", pady=(2, 0))
        note = ttk.Label(p, text="", style="Muted.TLabel", wraplength=760)
        note.pack(anchor="w", pady=(0, 8))
        self._extract_summary = summary
        self._extract_split = ov_split
        self._extract_note = note

        tabs = ttk.Frame(p)
        tabs.pack(fill="x", pady=(0, 8))
        host = ttk.Frame(p)
        host.pack(fill="x")
        panes: dict[str, ttk.Frame] = {key: ttk.Frame(host) for key, _label in EXTRACT_TABS}
        self._extract_panes = panes
        self._extract_tab_btns = {}
        for key, label in EXTRACT_TABS:
            btn = ui.button(
                tabs, label, lambda k=key: self._show_extract_tab(k),
                kind="chip", height=32, padx=12,
            )
            btn.pack(side="left", padx=(0, 6), pady=2)
            self._extract_tab_btns[key] = btn

        groups = panes["groups"]
        self._hint(
            groups,
            "Four exclusive groups plus Unclassified. Open a list to see every field. "
            "Untick a row that the automatic step got wrong and move it. "
            "Inside Include the sub-rows sum to Include: Must-cite (Core + Extended) + rest.",
        )
        self._extract_count_lbls = {}
        self._extract_group_row(
            groups, "reviews", "Reviews",
            "Set aside before scoring. Outside the screened total. Untick if it is not a review.",
        )

        inc_box = ttk.LabelFrame(groups, text="Include")
        inc_box.pack(fill="x", pady=(10, 6))
        self._extract_include_box = inc_box
        self._extract_group_row(
            inc_box, "include", "All Include",
            "Exclusive group. Open to recode any include record.",
        )
        must_box = ttk.LabelFrame(inc_box, text="Must-cite")
        must_box.pack(fill="x", padx=8, pady=(6, 4))
        self._extract_must_box = must_box
        self._extract_group_row(
            must_box, "must_cite", "All must-cite",
            "Working total = Core ∪ Extended. HIGH in the template; default sought for full text.",
        )
        self._extract_group_row(
            must_box, "core", "└ Core",
            "Direct UAV plus scaling / fusion.",
            indent=True,
        )
        self._extract_group_row(
            must_box, "extended", "└ Extended",
            "Wider must-cite, still HIGH.",
            indent=True,
        )
        self._extract_group_row(
            inc_box, "include_rest", "Rest of Include",
            "Include minus must-cite. In the refined template, not HIGH.",
        )
        must_lbl = ttk.Label(inc_box, text="", style="Muted.TLabel", wraplength=700)
        must_lbl.pack(anchor="w", padx=8, pady=(2, 6))
        self._extract_must_lbl = must_lbl

        self._extract_group_row(
            groups, "maybe", "Maybe",
            "Middle score band — not Exclude.",
        )
        ttk.Label(
            groups,
            text=(
                "Maybe is the score band between Exclude and Include (title–abstract keywords). "
                "It is not the same as Exclude: those records still go into the full extraction sheet "
                "with Include; the refined sheet is Include only. Default PRISMA does not take Maybe "
                "to full text (sought = must-cite). If you will not retrieve the PDF, move the record "
                "to Exclude. If it belongs in the extraction, move it to Include."
            ),
            style="Muted.TLabel",
            wraplength=760,
        ).pack(anchor="w", padx=(0, 8), pady=(0, 6))
        self._extract_group_row(
            groups, "exclude", "Exclude",
            "Exclusive group. Not extracted.",
        )
        self._extract_group_row(
            groups, "unclassified", "Unclassified",
            "Left an automatic group. Tick rows, then assign Reviews / Include / Maybe / Exclude.",
        )

        prisma = panes["prisma"]
        ttk.Label(prisma, text="From the run — already filled", style="Head.TLabel").pack(anchor="w")
        self._hint(
            prisma,
            "These numbers come from merge, audit and screening. You do not type them here. "
            "Registers and other sources are on Setup → Other sources.",
        )
        auto_grid = ttk.Frame(prisma)
        auto_grid.pack(anchor="w", pady=(6, 10), padx=(0, 40))
        self._prisma_auto_vals = {}
        auto_specs = (
            ("wos", "WoS"),
            ("scopus", "Scopus"),
            ("identified", "Identified from databases"),
            ("registers", "Registers (Setup)"),
            ("other", "Websites + organisations + citations (Setup)"),
            ("duplicates", "Duplicate records removed"),
            ("books", "Books / e-books removed"),
            ("missing_doi", "Missing DOI (kept — not a PRISMA remove box)"),
            ("retained", "Retained after audit"),
            ("reviews", "Reviews set aside"),
            ("screened", "Records screened"),
            ("include", "Include"),
            ("maybe", "Maybe"),
            ("exclude", "Exclude"),
            ("not_to_ft", "Not taken to full text (screened − sought)"),
            ("sought_used", "Sought for retrieval (used in the diagram)"),
            ("assessed", "Reports assessed (sought − not retrieved)"),
        )
        for i, (key, label) in enumerate(auto_specs):
            ttk.Label(auto_grid, text=label).grid(row=i, column=0, sticky="w", pady=1, padx=(0, 20))
            val = ttk.Label(auto_grid, text="—", style="Head.TLabel")
            val.grid(row=i, column=1, sticky="w", padx=(0, 20))
            ttk.Label(auto_grid, text="automatic", style="Muted.TLabel").grid(
                row=i, column=2, sticky="w", padx=(8, 16),
            )
            self._prisma_auto_vals[key] = val

        ttk.Label(prisma, text="Type only what the scripts cannot know", style="Head.TLabel").pack(
            anchor="w", pady=(8, 0),
        )
        self._hint(
            prisma,
            "Leave a box blank until you know it. Sought blank uses must-cite. "
            "Not retrieved = 0 if you obtained every PDF. Included studies/reports stay empty until full text. "
            "One exclusion reason per line: Reason, n.",
        )
        sought_hint = ttk.Label(prisma, text="", style="Muted.TLabel", wraplength=760)
        sought_hint.pack(anchor="w", pady=(4, 0))
        self._prisma_sought_hint = sought_hint
        self._entry_field(
            prisma, "prisma_sought", "Sought for retrieval — leave blank to use must-cite",
            "Type a number only if you retrieved extra full texts (more than must-cite).",
        )
        self._entry_field(
            prisma, "prisma_not_retrieved", "Reports not retrieved (n)",
            "PDFs you could not obtain. Keep 0 if you got them all.",
        )
        self._text_field(
            prisma, "prisma_not_retrieved_notes", "Which reports were not retrieved",
            "Titles or cite keys. Needed only when the count above is not 0.",
            height=3,
        )
        self._entry_field(
            prisma, "prisma_included_studies", "Included studies (n)",
            "Unique studies after full text. Empty until you know.",
        )
        self._entry_field(
            prisma, "prisma_included_reports", "Reports of included studies (n)",
            "Bibliographic records of those studies. Empty until you know.",
        )
        self._text_field(
            prisma, "prisma_ft_excluded", "Full-text exclusions",
            "One line per reason: Duplicate report of the same study, 2",
            height=4,
        )
        self._text_field(
            prisma, "prisma_screen_excluded_notes", "Notes only if sought is not must-cite",
            "If extra full texts came from maybe or from include leftover, write that here (e.g. 7 extra from maybe).",
            height=3,
        )

        def save_prisma() -> None:
            if not self._need_folder():
                return
            self._save_settings()
            try:
                result = actions.save_prisma_flow()
            except Exception as exc:
                messagebox.showerror("PRISMA counts", str(exc))
                return
            payload = result["payload"]
            warns = payload.get("warnings") or []
            files = result.get("files") or []
            msg = "Wrote " + ", ".join(files) + " in 60_prisma/."
            if warns:
                msg += "\n\n" + "\n".join(warns)
            self.log_msg(msg)
            actions.journal("extract", "prisma_counts", True, ", ".join(files))
            actions.note_protocol(
                "prisma",
                "Saved PRISMA full-text counts (sought, not retrieved, exclusions, included).",
                records=list(warns),
                files=list(files),
            )
            messagebox.showinfo("PRISMA counts", msg)
            refresh()

        def make_png() -> None:
            if not self._need_folder():
                return
            save_prisma()
            png = actions.render_prisma_png()
            self.log_msg(png.get("log") or "")
            if png.get("ok"):
                self._mark_done(png_btn, "PNG written ✓")
                messagebox.showinfo("PRISMA PNG", "60_prisma/PRISMA_diagram.png")
            else:
                messagebox.showerror("PRISMA PNG", png.get("log") or "Could not write PNG.")

        prisma_row = ttk.Frame(prisma)
        prisma_row.pack(anchor="w", pady=8)
        ui.button(prisma_row, "Save PRISMA counts", save_prisma, kind="accent").pack(side="left")
        png_btn = ui.button(prisma_row, "Make PNG", make_png)
        png_btn.pack(side="left", padx=8)

        tpl = panes["templates"]
        ttk.Label(tpl, text="Excel templates", style="Head.TLabel").pack(anchor="w")
        self._hint(
            tpl,
            "Writes the extraction sheets from the current groups (after recodes). "
            "HIGH in the template = Core ∪ Extended. Tick extra formats for copies.",
        )
        listing = text_widget(tpl, height=8)
        listing.pack(fill="x", pady=(12, 4))
        self._extract_listing = listing
        extract_fmt = self._format_bar(tpl, include_ris=False, include_xlsx=False)

        def run_ex() -> None:
            if not self._need_folder():
                return
            if not self._extract_warn_unclassified(for_continue=False):
                self._show_extract_tab("groups")
                return
            if not self._guard_script_outputs("extract", replace_ex):
                return
            result = actions.run_script("pipeline/extraction_templ.py")
            actions.journal("extract", "run", result["ok"], seconds=result["seconds"])
            self.log_msg(result["log"])
            if result["ok"]:
                self._apply_formats(actions.p("40_extraction"), extract_fmt, recursive=True)
            if not result["ok"]:
                messagebox.showerror("Extraction", result["log"][-1500:])
            else:
                self._mark_done(extract_btn, "Templates written ✓")
            refresh()
            self._refresh_tree()

        extract_row = ttk.Frame(tpl)
        extract_row.pack(anchor="w", pady=6)
        extract_btn = ui.button(extract_row, "Run templates", run_ex, kind="accent")
        extract_btn.pack(side="left")
        replace_ex = tk.BooleanVar(value=False)
        ttk.Checkbutton(extract_row, text="Replace existing script files", variable=replace_ex).pack(
            side="left", padx=(12, 6)
        )
        self._icon_btn(extract_row, "refresh", lambda: self._refresh_extract(), "Refresh").pack(side="left", padx=8)
        self._manual_check_row(tpl, "extract")

        def _show_n(key: str, value) -> None:
            lbl = self._prisma_auto_vals.get(key)
            if lbl is None:
                return
            if value is None or value == "":
                lbl.configure(text="—")
            else:
                lbl.configure(text=str(value))

        def fill_prisma(info: dict) -> None:
            settings = actions.load_settings()
            for key, widget in self.fields.items():
                if not str(key).startswith("prisma_"):
                    continue
                if isinstance(widget, tk.Text):
                    settings[key] = get_text(widget)
                else:
                    settings[key] = widget.get().strip()
            payload = actions.prisma_assemble(settings) or {}
            ident = payload.get("identification") or {}
            scr = payload.get("screening") or {}
            ret = payload.get("retrieval") or {}
            other = (
                (ident.get("website_results") or 0)
                + (ident.get("organisation_results") or 0)
                + (ident.get("citations_results") or 0)
            )
            split = scr.get("split") or {}
            not_to = scr.get("records_excluded")
            split_txt = ""
            if split.get("auto"):
                split_txt = (
                    f"  (exclude {split.get('exclude')}"
                    f" + maybe {split.get('maybe')}"
                    f" + include leftover {split.get('include_not_sought')})"
                )
            _show_n("wos", ident.get("wos"))
            _show_n("scopus", ident.get("scopus"))
            _show_n("identified", ident.get("database_results"))
            _show_n("registers", ident.get("register_results"))
            _show_n("other", other)
            _show_n("duplicates", ident.get("duplicates"))
            _show_n("books", ident.get("excluded_other"))
            _show_n("missing_doi", ident.get("missing_doi_not_removed"))
            _show_n("retained", ident.get("retained"))
            _show_n("reviews", ident.get("reviews_set_aside"))
            _show_n("screened", scr.get("records_screened"))
            _show_n("include", info.get("n_include") or 0)
            _show_n("maybe", info.get("n_maybe") or 0)
            _show_n("exclude", info.get("n_exclude") or 0)
            not_lbl = self._prisma_auto_vals.get("not_to_ft")
            if not_lbl is not None:
                not_lbl.configure(text=f"{not_to if not_to is not None else '—'}{split_txt}")
            src = ret.get("sought_source") or "must_cite"
            sought = ret.get("sought")
            n_must = info.get("n_must_cite") or 0
            _show_n("sought_used", f"{sought}  ({'must-cite' if src != 'typed' else 'you typed'})")
            _show_n("assessed", ret.get("assessed"))
            if self._prisma_sought_hint is not None:
                self._prisma_sought_hint.configure(
                    text=(
                        f"Blank sought uses must-cite {n_must}. "
                        f"Diagram currently uses sought = {sought}."
                    )
                )

        def refresh() -> None:
            listing_w = self._extract_listing
            if listing_w is not None:
                files = []
                for rel in (
                    "40_extraction/41_input",
                    "40_extraction/42_reviews",
                    "40_extraction/42_working",
                    "40_extraction/43_recode",
                ):
                    files.append(rel)
                    rows = actions.list_files(rel)
                    files.extend(f"  {r['name']}  {r['kb']} kB" for r in rows) or ["  —"]
                set_text(listing_w, "\n".join(files))
            if not actions.has_data_root():
                summary.configure(text="No screening yet")
                ov_split.configure(text="Run screening in the previous step.")
                note.configure(text="")
                return
            info = actions.extract_overview()
            if info.get("error") and not info.get("missing_screened"):
                summary.configure(text=info["error"])
                ov_split.configure(text="Groups come from screened_records.xlsx after screening.")
                note.configure(text="")
                fill_prisma(info)
                return
            if info.get("missing_screened"):
                summary.configure(text=info["error"])
                ov_split.configure(
                    text="Reviews can still show; Include / Maybe / Exclude need screened_records.xlsx. "
                    "Run screening again (xlsx stays on)."
                )
            n_sc = info.get("n_screen") or 0
            n_inc = info.get("n_include") or 0
            n_may = info.get("n_maybe") or 0
            n_exc = info.get("n_exclude") or 0
            n_rev = info.get("n_reviews") or 0
            n_must = info.get("n_must_cite") or 0
            n_core = info.get("n_core") or 0
            n_ext = info.get("n_extended") or 0
            n_rest = info.get("n_include_rest") or 0
            n_unc = info.get("n_unclassified") or 0
            n_recode = info.get("n_recode") or 0
            summary.configure(
                text=f"Screened {n_sc}  ·  reviews {n_rev}  ·  unclassified {n_unc}  ·  recodes {n_recode}"
            )
            ov_split.configure(
                text=f"Screened = Include {n_inc} + Maybe {n_may} + Exclude {n_exc}. Reviews are outside this total."
            )
            counts = {
                "reviews": n_rev,
                "include": n_inc,
                "maybe": n_may,
                "exclude": n_exc,
                "must_cite": n_must,
                "core": n_core,
                "extended": n_ext,
                "include_rest": n_rest,
                "unclassified": n_unc,
            }
            for key, n in counts.items():
                lbl = self._extract_count_lbls.get(key)
                if lbl is not None:
                    lbl.configure(text=str(n))
            if self._extract_include_box is not None:
                self._extract_include_box.configure(text=f"Include  ·  {n_inc} records")
            if self._extract_must_box is not None:
                self._extract_must_box.configure(text=f"Must-cite  ·  {n_must} records")
            if self._extract_must_lbl is not None:
                self._extract_must_lbl.configure(
                    text=(
                        f"Include {n_inc} = Must-cite {n_must} + rest {n_rest}. "
                        f"Must-cite {n_must} = Core {n_core} + Extended {n_ext}."
                    )
                )
            note.configure(
                text=(
                    "Open a group to recode. Script Excel is not replaced; "
                    "moves are logged to the protocol with exact DOI/title."
                )
            )
            for kind, tree in list(self._extract_trees.items()):
                try:
                    if tree.winfo_exists():
                        self._fill_extract_tree(kind)
                except tk.TclError:
                    self._extract_trees.pop(kind, None)
            fill_prisma(info)

        def before_extract():
            self._save_settings()
            return self._extract_warn_unclassified(for_continue=True)

        self._before_continue["extract"] = before_extract
        self._refresh_extract = refresh
        self._show_extract_tab("groups")
        refresh()

    # --- help ---
    def _frame_help(self, p: ttk.Frame) -> None:
        names = [s["title"] for s in STEPS]
        choice = tk.StringVar(value=names[0])
        ttk.Combobox(p, textvariable=choice, values=names, state="readonly", width=28).pack(anchor="w")
        box = text_widget(p, height=18)
        box.pack(fill="both", expand=True, pady=8)
        set_text(box, REPRODUCE)

        def show_help(*_a) -> None:
            spec = next(s for s in STEPS if s["title"] == choice.get())
            set_text(
                box,
                f"{spec['headline']}\n\n{spec['what']}\n\nInput: {spec['inputs']}\nOutput: {spec['outputs']}"
                + (f"\nPython: {step_script(spec)}" if step_script(spec) else "")
                + "\n\n"
                + REPRODUCE,
            )

        choice.trace_add("write", show_help)

        def show_step_script() -> None:
            spec = next(s for s in STEPS if s["title"] == choice.get())
            rel = step_script(spec)
            if not rel:
                messagebox.showinfo("Script", "This step has no Python file.")
                return
            self._script_window(rel)

        row = ttk.Frame(p)
        row.pack(anchor="w", pady=(8, 0))
        self._icon_btn(row, "edit", show_step_script, "Python file for this step").pack(side="left")
        ui.button(row, "Python and packages", self._packages_window).pack(side="left", padx=8)

    def _packages_window(self) -> None:
        ok = ensure_env.show_window(self)
        miss = ", ".join(p.name for p in ensure_env.missing()) or "none"
        self.log_msg(
            f"Python {ensure_env.python_line()} — "
            + ("packages ready" if ok else f"still missing: {miss}")
        )


def main() -> None:
    app = RunnerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
