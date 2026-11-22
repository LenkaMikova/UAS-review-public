"""Rounded controls in the style of the dark dashboard (rounded squares, navy chrome)."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

BG = "#0c1422"
PANEL = "#121a2b"
CARD = "#161e30"
FG = "#e7edf6"
MUTED = "#8b97ad"
ACCENT = "#00a0aa"
ACCENT_FG = "#f4fbfd"
BRAND = "#3d8ef0"
BTN = "#1a2436"
BTN_HOVER = "#243044"
BORDER = "#2a3650"
DANGER = "#e07070"
DONE = "#007a82"
UI = "Calibri"
FONT = (UI, 12)
FONT_SMALL = (UI, 11)
FONT_BTN = (UI, 12)
FONT_HEAD = (UI, 14, "bold")
FONT_TITLE = (UI, 22, "bold")
FONT_ICON = ("Segoe UI Emoji", 15)
FONT_ICON_SYM = ("Segoe UI Symbol", 15)
FONT_MDL = ("Segoe MDL2 Assets", 12)
ICON_SIZE = 28

ICONS = {
    "preview": ("\uE890", FONT_MDL, "Preview"),
    "compare": ("\uE8F1", FONT_MDL, "Compare"),
    "delete": ("\uE74D", FONT_MDL, "Delete"),
    "edit": ("\uE70F", FONT_MDL, "Edit"),
    "settings": ("\uE713", FONT_MDL, "Settings"),
    "help": ("\uE897", FONT_MDL, "Help"),
    "add": ("\uE710", FONT_MDL, "Add"),
    "refresh": ("\uE72C", FONT_MDL, "Refresh"),
    "packages": ("\uE896", FONT_MDL, "Python and packages"),
    "folder": ("\uE8B7", FONT_MDL, "Choose folder"),
    "folder_open": ("\uED25", FONT_MDL, "Open folder"),
    "calendar": ("\uE787", FONT_MDL, "Calendar"),
}

KIND_FILL = {
    "default": BTN,
    "accent": ACCENT,
    "done": DONE,
    "danger": BTN,
    "icon": BTN,
    "nav": PANEL,
    "nav_on": ACCENT,
    "nav_done": PANEL,
    "nav_locked": BG,
    "ghost": CARD,
    "chip": BTN,
    "chip_on": ACCENT,
}
KIND_FG = {
    "default": FG,
    "accent": ACCENT_FG,
    "done": FG,
    "danger": DANGER,
    "icon": FG,
    "nav": FG,
    "nav_on": ACCENT_FG,
    "nav_done": ACCENT,
    "nav_locked": MUTED,
    "ghost": FG,
    "chip": FG,
    "chip_on": ACCENT_FG,
}
STYLE_KIND = {
    "TButton": "default",
    "Accent.TButton": "accent",
    "Done.TButton": "done",
    "Nav.TButton": "nav",
    "NavOn.TButton": "nav_on",
    "NavDone.TButton": "nav_done",
    "NavLocked.TButton": "nav_locked",
}


def _is_mdl(text: str) -> bool:
    return bool(text) and "\uE000" <= text[0] <= "\uF8FF"


def brand_icon_image(size: int = 32) -> tk.PhotoImage:
    img = tk.PhotoImage(width=size, height=size)
    img.put(BRAND, to=(0, 0, size, size))
    return img


def _round_rect(canvas: tk.Canvas, x1, y1, x2, y2, r, **kw):
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    return canvas.create_polygon(
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        smooth=True, **kw,
    )


class Tip:
    def __init__(self, root: tk.Misc):
        self.root = root
        self.win: tk.Toplevel | None = None

    def hide(self, _e=None) -> None:
        if self.win is not None:
            try:
                self.win.destroy()
            except tk.TclError:
                pass
            self.win = None

    def show(self, widget: tk.Widget, text: str) -> None:
        self.hide()
        if not text:
            return
        tip = tk.Toplevel(self.root)
        tip.wm_overrideredirect(True)
        tip.configure(bg=BORDER)
        tk.Label(tip, text=text, bg=BTN, fg=FG, font=FONT_SMALL, padx=8, pady=4).pack()
        tip.update_idletasks()
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height() + 6
        tip.wm_geometry(f"+{x}+{y}")
        self.win = tip


class RoundButton(tk.Canvas):
    """Rounded rectangle button (pill or square icon), dashboard style."""

    def __init__(
        self,
        parent,
        text: str = "",
        command=None,
        kind: str = "default",
        tip: str = "",
        width: int | None = None,
        height: int = 36,
        radius: int | None = None,
        padx: int = 14,
        align: str | None = None,
        **_kw,
    ):
        super().__init__(parent, highlightthickness=0, bd=0, cursor="hand2")
        self._text = text
        self._command = command
        self._kind = kind
        self._tip = tip
        self._state = "normal"
        self._hover = False
        self._height = height
        self._padx = padx
        self._align = align or ("left" if kind.startswith("nav") else "center")
        self._fixed_width = width
        self._radius = radius if radius is not None else (10 if kind != "icon" else 10)
        self._shape = None
        self._label = None
        self.configure(height=height, bg=BG)
        self._draw()
        self.bind("<Button-1>", self._click)
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)

    def _fill(self) -> str:
        if self._hover and self._state == "normal" and self._kind not in {"accent", "chip_on", "nav_on"}:
            return BTN_HOVER
        return KIND_FILL.get(self._kind, BTN)

    def _fg(self) -> str:
        if self._state == "disabled":
            return MUTED
        return KIND_FG.get(self._kind, FG)

    def _draw(self) -> None:
        self.delete("all")
        text = self._text
        font = FONT_BTN
        if _is_mdl(text):
            font = FONT_MDL
        elif self._kind == "icon":
            font = FONT_ICON_SYM
        elif self._kind in {"icon", "danger"} and len(text) <= 2:
            font = FONT_BTN
        self._measure(font)
        w = self._fixed_width or max(ICON_SIZE if self._kind == "icon" else 36, self._text_w + self._padx * 2)
        h = self._height
        self.configure(width=w, height=h, bg=BG)
        r = self._radius
        outline = DANGER if self._kind == "danger" else BORDER
        self._shape = _round_rect(self, 1, 1, w - 1, h - 1, r, fill=self._fill(), outline=outline)
        if self._align == "left":
            self._label = self.create_text(
                self._padx, h / 2, text=text, fill=self._fg(), font=font, anchor="w",
            )
        else:
            self._label = self.create_text(
                w / 2, h / 2, text=text, fill=self._fg(), font=font, anchor="center",
            )

    def _measure(self, font) -> None:
        try:
            self._text_w = tkfont.Font(self, font=font).measure(self._text or " ")
        except tk.TclError:
            self._text_w = max(12, 8 * len(self._text or " "))

    def _click(self, _e) -> None:
        if self._state == "disabled":
            return
        if callable(self._command):
            self._command()

    def _enter(self, _e) -> None:
        if self._state == "disabled":
            return
        self._hover = True
        self._draw()
        app = self.winfo_toplevel()
        tip = getattr(app, "_ui_tip", None)
        if tip and self._tip:
            tip.show(self, self._tip)

    def _leave(self, _e) -> None:
        self._hover = False
        self._draw()
        app = self.winfo_toplevel()
        tip = getattr(app, "_ui_tip", None)
        if tip:
            tip.hide()

    def set_text(self, text: str) -> None:
        self._text = text
        self._draw()

    def set_kind(self, kind: str) -> None:
        self._kind = kind
        self._draw()

    def set_state(self, state: str) -> None:
        self._state = state
        self.configure(cursor="" if state == "disabled" else "hand2")
        self._draw()

    def set_command(self, command) -> None:
        self._command = command

    def configure(self, cnf=None, **kw):  # type: ignore[override]
        kw = dict(cnf or {}, **kw)
        if "text" in kw:
            self.set_text(kw.pop("text"))
        if "state" in kw:
            self.set_state(kw.pop("state"))
        if "style" in kw:
            self.set_kind(STYLE_KIND.get(kw.pop("style"), "default"))
        if "command" in kw:
            self.set_command(kw.pop("command"))
        if kw:
            return super().configure(**kw)
        return None

    def cget(self, key: str):
        if key == "text":
            return self._text
        return super().cget(key)


def button(parent, text: str, command=None, kind: str = "default", tip: str = "", **kw) -> RoundButton:
    return RoundButton(parent, text=text, command=command, kind=kind, tip=tip, **kw)


def icon_button(parent, kind: str, command, tip: str | None = None, danger: bool = False) -> RoundButton:
    glyph, _font, default_tip = ICONS[kind]
    style = "danger" if danger or kind == "delete" else "icon"
    return RoundButton(
        parent,
        text=glyph,
        command=command,
        kind=style,
        tip=tip or default_tip,
        width=ICON_SIZE,
        height=ICON_SIZE,
        radius=8,
        padx=0,
    )


def apply_theme(root: tk.Tk) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    root.configure(bg=BG)
    root.option_add("*Font", FONT)
    style.configure(".", background=BG, foreground=FG, fieldbackground=CARD, font=FONT)
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=FG, font=FONT)
    style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=FONT_SMALL)
    style.configure("Head.TLabel", background=BG, foreground=ACCENT, font=FONT_HEAD)
    style.configure("AppTitle.TLabel", background=BG, foreground=BRAND, font=FONT_TITLE)
    style.configure("Choice.TLabel", background=BG, foreground=ACCENT, font=(UI, 12, "italic"))
    style.configure("TCheckbutton", background=BG, foreground=FG, font=FONT)
    style.configure("TRadiobutton", background=BG, foreground=FG, font=FONT)
    style.configure("TEntry", fieldbackground=CARD, foreground=FG, font=FONT, borderwidth=0)
    style.configure("TSpinbox", fieldbackground=CARD, foreground=FG, background=CARD, arrowcolor=FG, font=FONT)
    style.configure(
        "TCombobox",
        fieldbackground=CARD,
        background=CARD,
        foreground=FG,
        arrowcolor=FG,
        insertcolor=FG,
        font=FONT,
        padding=6,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", CARD), ("!readonly", CARD)],
        foreground=[("readonly", FG), ("!readonly", FG)],
        background=[("readonly", CARD)],
        selectbackground=[("readonly", CARD)],
        selectforeground=[("readonly", FG)],
        arrowcolor=[("readonly", FG)],
    )
    root.option_add("*TCombobox*Listbox.background", CARD)
    root.option_add("*TCombobox*Listbox.foreground", FG)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", ACCENT_FG)
    style.configure(
        "Treeview",
        background=CARD,
        foreground=FG,
        fieldbackground=CARD,
        font=FONT,
        rowheight=32,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=PANEL,
        foreground=MUTED,
        font=(UI, 11),
        relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", "#1e3a5f")],
        foreground=[("selected", FG)],
    )
    style.map("Treeview.Heading", background=[("active", BTN)])
    style.configure("TScrollbar", background=PANEL, troughcolor=BG, borderwidth=0, arrowcolor=FG)


class Scrollable(ttk.Frame):
    """Viewport with a vertical bar only when the inner content is taller."""

    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0, bd=0)
        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self._set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner.bind("<Configure>", self._inner_cfg)
        self.canvas.bind("<Configure>", self._canvas_cfg)
        self.bind("<Map>", lambda _e: self._bind_wheel())
        self.bind("<Unmap>", lambda _e: self._unbind_wheel())
        self._wheel_bound = False

    def _set(self, first, last) -> None:
        self.vbar.set(first, last)
        overflow = float(first) > 0.001 or float(last) < 0.999
        mapped = bool(self.vbar.winfo_ismapped())
        if overflow and not mapped:
            self.vbar.pack(side="right", fill="y")
        elif not overflow and mapped:
            self.vbar.pack_forget()
            self.canvas.yview_moveto(0)

    def _inner_cfg(self, _e=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all") or (0, 0, 0, 0))

    def _canvas_cfg(self, event) -> None:
        self.canvas.itemconfigure(self._win, width=max(1, event.width))

    def reset(self) -> None:
        self.canvas.yview_moveto(0)

    def _bind_wheel(self) -> None:
        if self._wheel_bound:
            return
        self.bind_all("<MouseWheel>", self._wheel)
        self._wheel_bound = True

    def _unbind_wheel(self) -> None:
        if not self._wheel_bound:
            return
        self.unbind_all("<MouseWheel>")
        self._wheel_bound = False

    def _wheel(self, event) -> str | None:
        try:
            x, y = event.x_root, event.y_root
            x0, y0 = self.winfo_rootx(), self.winfo_rooty()
            if not (x0 <= x < x0 + self.winfo_width() and y0 <= y < y0 + self.winfo_height()):
                return None
        except tk.TclError:
            return None
        target = self.winfo_containing(x, y)
        klass = target.winfo_class() if target else ""
        if klass in {"Text", "Listbox", "Treeview"}:
            return None
        steps = int(-event.delta / 120) if event.delta else 0
        if steps:
            self.canvas.yview_scroll(steps, "units")
        return "break"


def text_widget(parent, height=6, font=None, **kw) -> tk.Text:
    return tk.Text(
        parent, height=height, wrap="word", bg=CARD, fg=FG,
        insertbackground=FG, relief="flat", padx=10, pady=8,
        highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT,
        font=font or FONT, **kw,
    )
