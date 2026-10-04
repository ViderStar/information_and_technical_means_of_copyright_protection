"""Application window: cipher choice, parameter setup and step-by-step view."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Tuple

from configs.cfg import GROUP_SIZE
from gui.i18n import DEFAULT_LANGUAGE, LANGUAGES, set_language, t
from gui.methods import METHODS, Param
from helpers.text import group, normalize
from lab1 import grille

MONO = ("Menlo", 12)
CELL_ON = ("#2d6cdf", "white")
CELL_OFF = ("#f2f2f2", "#888888")


class GrilleSelector(ttk.Frame):
    """Grille with clickable holes: one hole per rotation orbit."""

    def __init__(self, master: tk.Misc, key: str):
        super().__init__(master)
        self.cells: Dict[Tuple[int, int], tk.Label] = {}
        self.chosen: Dict[int, Tuple[int, int]] = {}
        self.set_key(key)

    def set_key(self, key: str) -> None:
        holes, size = grille.parse_key(key)
        self._build(size)
        for cell in holes:
            self.chosen[self.orbits[cell]] = cell
        self._repaint()

    def set_size(self, size: int) -> None:
        """On resize the first cell of every orbit is picked by default."""
        self._build(size)
        for cell, orbit in sorted(self.orbits.items()):
            self.chosen.setdefault(orbit, cell)
        self._repaint()

    def get(self) -> str:
        cells = sorted(self.chosen.values())
        return ",".join(str(row * self.size + col) for row, col in cells)

    def _build(self, size: int) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self.size, self.chosen = size, {}
        self.orbits = grille.orbit_map(size)
        self.cells = {}
        for (row, col), orbit in self.orbits.items():
            label = tk.Label(self, text=str(orbit + 1), width=3, height=1,
                             relief="solid", borderwidth=1, font=MONO)
            label.grid(row=row, column=col, padx=1, pady=1)
            label.bind("<Button-1>", lambda _e, c=(row, col): self._pick(c))
            self.cells[(row, col)] = label

    def _pick(self, cell: Tuple[int, int]) -> None:
        self.chosen[self.orbits[cell]] = cell          # one orbit, one hole
        self._repaint()
        self.event_generate("<<GrilleChanged>>")

    def _repaint(self) -> None:
        picked = set(self.chosen.values())
        for cell, label in self.cells.items():
            background, foreground = CELL_ON if cell in picked else CELL_OFF
            label.configure(background=background, foreground=foreground)


class App(tk.Tk):
    """Main window."""

    def __init__(self) -> None:
        super().__init__()
        set_language(DEFAULT_LANGUAGE)
        self.minsize(900, 700)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.method_id = next(iter(METHODS))
        self.group_size = tk.IntVar(value=GROUP_SIZE)
        self.show_explain = tk.BooleanVar(value=True)
        self.status = tk.StringVar()
        self.controls: Dict[str, object] = {}
        # (widget, i18n key) pairs whose "text" is re-translated on language change
        self.labels: List[Tuple[ttk.Widget, str]] = []
        # last successful run, kept so the explanation can be re-rendered
        self.last_run: Optional[Tuple[str, str, Dict[str, object]]] = None

        self._build_top()
        self._build_params_frame()
        self._build_texts()
        self._build_explain()
        self._build_status()
        self._reload_params()
        self._retranslate()

    # ---------------------------------------------------------------- widgets
    def _tr(self, widget: ttk.Widget, key: str) -> ttk.Widget:
        """Register a widget whose text follows the interface language."""
        self.labels.append((widget, key))
        return widget

    def _build_top(self) -> None:
        bar = ttk.Frame(self, padding=(10, 10, 10, 0))
        bar.grid(row=0, column=0, sticky="ew")

        self._tr(ttk.Label(bar), "top.cipher").pack(side="left")
        self.chooser = ttk.Combobox(bar, state="readonly", width=28)
        self.chooser.pack(side="left", padx=(6, 18))
        self.chooser.bind("<<ComboboxSelected>>", self._on_method)

        self._tr(ttk.Label(bar), "top.group_by").pack(side="left")
        ttk.Spinbox(bar, from_=0, to=10, width=4, textvariable=self.group_size).pack(side="left", padx=6)
        self._tr(ttk.Label(bar), "top.group_unit").pack(side="left", padx=(0, 18))
        self._tr(ttk.Checkbutton(bar, variable=self.show_explain, command=self._toggle_explain),
                 "top.show_explain").pack(side="left")

        # language switcher: packed right-to-left, so the combobox goes first
        self.language_box = ttk.Combobox(bar, state="readonly", width=10,
                                         values=list(LANGUAGES.values()))
        self.language_box.current(list(LANGUAGES).index(DEFAULT_LANGUAGE))
        self.language_box.pack(side="right")
        self.language_box.bind("<<ComboboxSelected>>", self._on_language)
        ttk.Label(bar, text="Language / Язык:").pack(side="right", padx=6)

    def _build_params_frame(self) -> None:
        self.params_frame = self._tr(ttk.LabelFrame(self, padding=10), "frame.params")
        self.params_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

    def _build_texts(self) -> None:
        frame = ttk.Frame(self, padding=(10, 0))
        frame.grid(row=2, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(1, weight=1)

        self._tr(ttk.Label(frame), "label.plain").grid(row=0, column=0, sticky="w")
        self._tr(ttk.Label(frame), "label.cipher").grid(row=0, column=2, sticky="w")

        self.plain = tk.Text(frame, height=7, wrap="word", font=MONO)
        self.plain.grid(row=1, column=0, sticky="nsew")
        self.plain.insert("1.0", "Это лабораторная работа по КиОКИ")

        buttons = ttk.Frame(frame, padding=8)
        buttons.grid(row=1, column=1)
        for key, command in (("btn.encrypt", lambda: self._run("enc")),
                             ("btn.decrypt", lambda: self._run("dec")),
                             ("btn.swap", self._swap),
                             ("btn.clear", self._clear)):
            self._tr(ttk.Button(buttons, width=16, command=command), key).pack(pady=3)

        self.cipher = tk.Text(frame, height=7, wrap="word", font=MONO)
        self.cipher.grid(row=1, column=2, sticky="nsew")

    def _build_explain(self) -> None:
        self.explain_frame = self._tr(ttk.LabelFrame(self, padding=8), "frame.explain")
        self.explain_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        self.explain_frame.columnconfigure(0, weight=1)
        self.explain_frame.rowconfigure(0, weight=1)

        self.explain = tk.Text(self.explain_frame, height=12, wrap="none", font=MONO)
        self.explain.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(self.explain_frame, orient="vertical", command=self.explain.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.explain.configure(yscrollcommand=scroll.set, state="disabled")

    def _build_status(self) -> None:
        self.status_label = ttk.Label(self, textvariable=self.status, padding=(10, 0, 10, 8))
        self.status_label.grid(row=4, column=0, sticky="w")

    # --------------------------------------------------------------- language
    def _on_language(self, _event: object = None) -> None:
        code = list(LANGUAGES)[self.language_box.current()]
        saved = self._saved_params()
        set_language(code)
        self._retranslate()
        self._reload_params(saved)
        self.status_label.configure(foreground="")
        self.status.set(t("status.ready"))

    def _retranslate(self) -> None:
        self.title(t("app.title"))
        for widget, key in self.labels:
            widget.configure(text=t(key))

        names = [t(f"method.{method_id}.name") for method_id in METHODS]
        self.chooser.configure(values=names)
        self.chooser.current(list(METHODS).index(self.method_id))

        if self.last_run:                      # re-render the explanation in the new language
            method_id, text, values = self.last_run
            self._set_explain(METHODS[method_id].explain(text, values))
        self.status.set(t("status.ready"))

    def _on_method(self, _event: object = None) -> None:
        self.method_id = list(METHODS)[self.chooser.current()]
        self.last_run = None
        self._reload_params()

    # ------------------------------------------------------------- parameters
    def _saved_params(self) -> Dict[str, str]:
        """Current parameter values, kept across a rebuild of the parameter panel."""
        return {key: control.get() for key, control in self.controls.items()}

    def _reload_params(self, saved: Optional[Dict[str, str]] = None) -> None:
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        self.controls = {}
        saved = saved or {}

        method_id = self.method_id
        method = METHODS[method_id]
        ttk.Label(self.params_frame, text=t(f"method.{method_id}.title"),
                  foreground="#555555").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        row = 1
        for param in method.params:
            ttk.Label(self.params_frame, text=t(f"param.{method_id}.{param.key}") + ":").grid(
                row=row, column=0, sticky="w", pady=3)
            self._build_control(param, row, saved.get(param.key, param.default))
            if param.hint:
                ttk.Label(self.params_frame, text=t(f"param.{method_id}.{param.key}.hint"),
                          foreground="#888888").grid(row=row, column=2, sticky="w", padx=8)
            row += 1
        if not saved:
            self._clear_explain()

    def _build_control(self, param: Param, row: int, initial: object) -> None:
        if param.kind == "grille":
            selector = GrilleSelector(self.params_frame, str(initial))
            selector.grid(row=row, column=1, sticky="w", padx=8, pady=3)
            selector.bind("<<GrilleChanged>>", lambda _e: self.status.set(
                t("status.holes", holes=selector.get())))
            self.controls[param.key] = selector
            return

        variable = tk.StringVar(value=str(initial))
        if param.kind == "int":
            widget = ttk.Spinbox(self.params_frame, from_=param.limits[0], to=param.limits[1],
                                 textvariable=variable, width=6)
        elif param.kind == "choice":
            widget = ttk.Combobox(self.params_frame, textvariable=variable, state="readonly",
                                  values=[str(choice) for choice in param.choices], width=16)
            if param.key == "size":
                widget.bind("<<ComboboxSelected>>", lambda _e: self._resize_grille(variable))
        else:
            widget = ttk.Entry(self.params_frame, textvariable=variable, width=26, font=MONO)
        widget.grid(row=row, column=1, sticky="w", padx=8, pady=3)
        self.controls[param.key] = variable

    def _resize_grille(self, size_variable: tk.StringVar) -> None:
        selector = self.controls.get("holes")
        if isinstance(selector, GrilleSelector):
            selector.set_size(int(size_variable.get()))

    def _values(self) -> Dict[str, object]:
        method = METHODS[self.method_id]
        values: Dict[str, object] = {}
        for param in method.params:
            control = self.controls[param.key]
            if isinstance(control, GrilleSelector):
                values[param.key] = control.get()
            elif param.kind == "int":
                values[param.key] = int(control.get())
            elif param.kind == "text":
                values[param.key] = normalize(control.get())
            else:
                values[param.key] = control.get()
        return values

    # ---------------------------------------------------------------- actions
    def _run(self, direction: str) -> None:
        method = METHODS[self.method_id]
        source, target = ((self.plain, self.cipher) if direction == "enc"
                          else (self.cipher, self.plain))
        text = normalize(source.get("1.0", "end"))
        if not text:
            self._fail(t("status.error", message=t("status.empty")))
            return

        try:
            values = self._values()
            result = (method.encrypt if direction == "enc" else method.decrypt)(text, values)
            explain_input = text if direction == "enc" else result
            explanation = method.explain(explain_input, values)
        except ValueError as error:
            self._fail(t("status.error", message=error))
            return

        size = max(0, self.group_size.get())
        target.delete("1.0", "end")
        target.insert("1.0", group(result, size) if size else result)
        self.last_run = (self.method_id, explain_input, values)
        self._set_explain(explanation)
        self.status_label.configure(foreground="")
        self.status.set(t("status.encrypted" if direction == "enc" else "status.decrypted",
                          src=len(text), dst=len(result)))

    def _swap(self) -> None:
        plain, cipher = self.plain.get("1.0", "end").strip(), self.cipher.get("1.0", "end").strip()
        self.plain.delete("1.0", "end"), self.plain.insert("1.0", cipher)
        self.cipher.delete("1.0", "end"), self.cipher.insert("1.0", plain)

    def _clear(self) -> None:
        self.plain.delete("1.0", "end")
        self.cipher.delete("1.0", "end")
        self.last_run = None
        self._clear_explain()
        self.status.set(t("status.cleared"))

    def _fail(self, message: str) -> None:
        self.status_label.configure(foreground="#c0392b")
        self.status.set(message)

    def _toggle_explain(self) -> None:
        if self.show_explain.get():
            self.explain_frame.grid()
        else:
            self.explain_frame.grid_remove()

    def _set_explain(self, text: str) -> None:
        self.explain.configure(state="normal")
        self.explain.delete("1.0", "end")
        self.explain.insert("1.0", text)
        self.explain.configure(state="disabled")

    def _clear_explain(self) -> None:
        self._set_explain("")


def run() -> None:
    App().mainloop()
