"""Окно приложения: выбор шифра, настройка параметров и разбор работы."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Tuple

from configs.cfg import GROUP_SIZE
from gui.methods import METHODS, Param
from helpers.text import group, normalize
from lab1 import grille

MONO = ("Menlo", 12)
CELL_ON = ("#2d6cdf", "white")
CELL_OFF = ("#f2f2f2", "#888888")


class GrilleSelector(ttk.Frame):
    """Решётка с кликабельными отверстиями: по одному на орбиту поворота."""

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
        """Смена размера: по умолчанию выбирается первая клетка каждой орбиты."""
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
        self.chosen[self.orbits[cell]] = cell          # одна орбита — одно отверстие
        self._repaint()
        self.event_generate("<<GrilleChanged>>")

    def _repaint(self) -> None:
        picked = set(self.chosen.values())
        for cell, label in self.cells.items():
            background, foreground = CELL_ON if cell in picked else CELL_OFF
            label.configure(background=background, foreground=foreground)


class App(tk.Tk):
    """Главное окно."""

    def __init__(self) -> None:
        super().__init__()
        self.title("ЛР1 — шифры перестановок и подстановок")
        self.minsize(900, 700)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.method_name = tk.StringVar(value=next(iter(METHODS)))
        self.group_size = tk.IntVar(value=GROUP_SIZE)
        self.show_explain = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Выберите шифр, задайте параметры и нажмите «Зашифровать»")
        self.controls: Dict[str, object] = {}

        self._build_top()
        self._build_params_frame()
        self._build_texts()
        self._build_explain()
        self._build_status()
        self._reload_params()

    # ---------------------------------------------------------------- виджеты
    def _build_top(self) -> None:
        bar = ttk.Frame(self, padding=(10, 10, 10, 0))
        bar.grid(row=0, column=0, sticky="ew")

        ttk.Label(bar, text="Шифр:").pack(side="left")
        chooser = ttk.Combobox(bar, textvariable=self.method_name, state="readonly",
                               values=list(METHODS), width=28)
        chooser.pack(side="left", padx=(6, 18))
        chooser.bind("<<ComboboxSelected>>", lambda _e: self._reload_params())

        ttk.Label(bar, text="Группировать по").pack(side="left")
        ttk.Spinbox(bar, from_=0, to=10, width=4, textvariable=self.group_size).pack(side="left", padx=6)
        ttk.Label(bar, text="символов (0 — без групп)").pack(side="left", padx=(0, 18))
        ttk.Checkbutton(bar, text="Показывать разбор", variable=self.show_explain,
                        command=self._toggle_explain).pack(side="left")

    def _build_params_frame(self) -> None:
        self.params_frame = ttk.LabelFrame(self, text="Параметры", padding=10)
        self.params_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

    def _build_texts(self) -> None:
        frame = ttk.Frame(self, padding=(10, 0))
        frame.grid(row=2, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(1, weight=1)

        ttk.Label(frame, text="Открытый текст").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="Шифротекст").grid(row=0, column=2, sticky="w")

        self.plain = tk.Text(frame, height=7, wrap="word", font=MONO)
        self.plain.grid(row=1, column=0, sticky="nsew")
        self.plain.insert("1.0", "Это лабораторная работа по КиОКИ")

        buttons = ttk.Frame(frame, padding=8)
        buttons.grid(row=1, column=1)
        ttk.Button(buttons, text="Зашифровать →", width=16,
                   command=lambda: self._run("enc")).pack(pady=3)
        ttk.Button(buttons, text="← Расшифровать", width=16,
                   command=lambda: self._run("dec")).pack(pady=3)
        ttk.Button(buttons, text="⇄ Поменять", width=16,
                   command=self._swap).pack(pady=3)
        ttk.Button(buttons, text="Очистить", width=16,
                   command=self._clear).pack(pady=3)

        self.cipher = tk.Text(frame, height=7, wrap="word", font=MONO)
        self.cipher.grid(row=1, column=2, sticky="nsew")

    def _build_explain(self) -> None:
        self.explain_frame = ttk.LabelFrame(self, text="Как это работает", padding=8)
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

    # -------------------------------------------------------------- параметры
    def _reload_params(self) -> None:
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        self.controls = {}

        method = METHODS[self.method_name.get()]
        ttk.Label(self.params_frame, text=method.title,
                  foreground="#555555").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        row = 1
        for param in method.params:
            ttk.Label(self.params_frame, text=param.label + ":").grid(
                row=row, column=0, sticky="w", pady=3)
            self._build_control(param, row)
            if param.hint:
                ttk.Label(self.params_frame, text=param.hint, foreground="#888888").grid(
                    row=row, column=2, sticky="w", padx=8)
            row += 1
        self._clear_explain()

    def _build_control(self, param: Param, row: int) -> None:
        if param.kind == "grille":
            selector = GrilleSelector(self.params_frame, str(param.default))
            selector.grid(row=row, column=1, sticky="w", padx=8, pady=3)
            selector.bind("<<GrilleChanged>>", lambda _e: self.status.set(
                "Отверстия: " + selector.get()))
            self.controls[param.key] = selector
            return

        variable = tk.StringVar(value=str(param.default))
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
        method = METHODS[self.method_name.get()]
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

    # -------------------------------------------------------------- действия
    def _run(self, direction: str) -> None:
        method = METHODS[self.method_name.get()]
        source, target = ((self.plain, self.cipher) if direction == "enc"
                          else (self.cipher, self.plain))
        text = normalize(source.get("1.0", "end"))
        if not text:
            self._fail("Пустой текст: нечего обрабатывать")
            return

        try:
            values = self._values()
            result = (method.encrypt if direction == "enc" else method.decrypt)(text, values)
            explanation = method.explain(text if direction == "enc" else result, values)
        except ValueError as error:
            self._fail(str(error))
            return

        size = max(0, self.group_size.get())
        target.delete("1.0", "end")
        target.insert("1.0", group(result, size) if size else result)
        self._set_explain(explanation)
        self.status_label.configure(foreground="")
        self.status.set("%s: %d символов -> %d символов" % (
            "зашифровано" if direction == "enc" else "расшифровано", len(text), len(result)))

    def _swap(self) -> None:
        plain, cipher = self.plain.get("1.0", "end").strip(), self.cipher.get("1.0", "end").strip()
        self.plain.delete("1.0", "end"), self.plain.insert("1.0", cipher)
        self.cipher.delete("1.0", "end"), self.cipher.insert("1.0", plain)

    def _clear(self) -> None:
        self.plain.delete("1.0", "end")
        self.cipher.delete("1.0", "end")
        self._clear_explain()
        self.status.set("Очищено")

    def _fail(self, message: str) -> None:
        self.status_label.configure(foreground="#c0392b")
        self.status.set("Ошибка: " + message)

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
