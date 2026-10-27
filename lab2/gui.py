"""Lab 2 window: RSA key computation, encryption and decryption.

KeyWindow holds what labs 2 and 3 share: the p, q, e fields, the computed keys,
the step-by-step pane and the language switch; lab3/gui.py builds on it.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Tuple

from configs.cfg import RSA_E, RSA_P, RSA_Q
from helpers.numtheory import EuclidStep
from lab2 import rsa
from lab2.runner import euclid_table, exp_table

MONO = ("Menlo", 12)
LANGUAGES = {"en": "English", "ru": "Русский"}

STRINGS: Dict[str, Dict[str, str]] = {
    "en": {
        "app.title": "Lab 2 - RSA cryptosystem",
        "frame.keys": "Keys",
        "frame.explain": "How it works",
        "btn.keys": "Compute keys",
        "label.codec": "Text codec:",
        "label.plain": "Plaintext",
        "label.cipher": "Ciphertext (numbers)",
        "btn.encrypt": "Encrypt →",
        "btn.decrypt": "← Decrypt",
        "btn.clear": "Clear",
        "status.ready": "Set p, q, e and press \"Compute keys\"",
        "status.keys": "Keys are ready: Ko = ({e}, {r}), Kc = ({d}, {r})",
        "status.encrypted": "encrypted: {count} blocks",
        "status.decrypted": "decrypted: {count} blocks",
        "status.error": "Error: {message}",
        "status.number": "{name} must be an integer",
        "explain.keys": "r = p*q = {r}, phi(r) = (p-1)(q-1) = {phi}\n"
                        "Extended Euclid for a = phi(r), b = e:",
        "explain.d": "d = {d}: e*d mod phi(r) = {check}",
    },
    "ru": {
        "app.title": "ЛР2 - криптосистема RSA",
        "frame.keys": "Ключи",
        "frame.explain": "Как это работает",
        "btn.keys": "Вычислить ключи",
        "label.codec": "Кодировка текста:",
        "label.plain": "Открытый текст",
        "label.cipher": "Шифротекст (числа)",
        "btn.encrypt": "Зашифровать →",
        "btn.decrypt": "← Расшифровать",
        "btn.clear": "Очистить",
        "status.ready": "Задайте p, q, e и нажмите «Вычислить ключи»",
        "status.keys": "Ключи готовы: Ko = ({e}, {r}), Kc = ({d}, {r})",
        "status.encrypted": "зашифровано блоков: {count}",
        "status.decrypted": "расшифровано блоков: {count}",
        "status.error": "Ошибка: {message}",
        "status.number": "{name} должно быть целым числом",
        "explain.keys": "r = p*q = {r}, phi(r) = (p-1)(q-1) = {phi}\n"
                        "Расширенный алгоритм Евклида для a = phi(r), b = e:",
        "explain.d": "d = {d}: e*d mod phi(r) = {check}",
    },
}


class KeyWindow(tk.Tk):
    """p, q, e inputs, key computation, explanation pane, language switch."""

    strings = STRINGS
    defaults: Tuple[int, int, int] = (RSA_P, RSA_Q, RSA_E)

    def __init__(self) -> None:
        super().__init__()
        self.language = "en"
        self.minsize(860, 640)
        self.columnconfigure(0, weight=1)
        self.keys: Optional[rsa.Keys] = None
        self.status = tk.StringVar()
        self.labels: List[Tuple[tk.Widget, str]] = []
        self.fields: Dict[str, tk.StringVar] = {}

        self._build_keys()
        self.build_body()
        self._build_explain()
        ttk.Label(self, textvariable=self.status, padding=(10, 0, 10, 8)).grid(
            row=4, column=0, sticky="w")
        self._retranslate()
        self.status.set(self.t("status.ready"))

    # ------------------------------------------------------------------ helpers
    def t(self, key: str, **values: object) -> str:
        return self.strings[self.language][key].format(**values)

    def tr(self, widget: tk.Widget, key: str) -> tk.Widget:
        self.labels.append((widget, key))
        return widget

    def number(self, name: str) -> int:
        try:
            return int(self.fields[name].get().strip())
        except ValueError:
            raise ValueError(self.t("status.number", name=name)) from None

    def set_explain(self, text: str) -> None:
        self.explain.configure(state="normal")
        self.explain.delete("1.0", "end")
        self.explain.insert("1.0", text)
        self.explain.configure(state="disabled")

    def fail(self, error: Exception) -> None:
        self.status.set(self.t("status.error", message=error))

    # ------------------------------------------------------------------ widgets
    def _build_keys(self) -> None:
        frame = self.tr(ttk.LabelFrame(self, padding=10), "frame.keys")
        frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        for column, (name, value) in enumerate(zip("pqe", self.defaults)):
            ttk.Label(frame, text=f"{name} =").grid(row=0, column=2 * column, padx=(0, 4))
            self.fields[name] = tk.StringVar(value=str(value))
            ttk.Entry(frame, width=14, textvariable=self.fields[name], font=MONO).grid(
                row=0, column=2 * column + 1, padx=(0, 14))
        self.add_key_fields(frame, 6)
        self.tr(ttk.Button(frame, command=self.compute_keys), "btn.keys").grid(
            row=0, column=20, padx=(6, 0))

        self.language_box = ttk.Combobox(frame, state="readonly", width=10,
                                         values=list(LANGUAGES.values()))
        self.language_box.current(0)
        self.language_box.grid(row=0, column=22, padx=(24, 0))
        self.language_box.bind("<<ComboboxSelected>>", self._on_language)
        frame.columnconfigure(21, weight=1)

        self.key_info = tk.StringVar()
        ttk.Label(frame, textvariable=self.key_info, font=MONO).grid(
            row=1, column=0, columnspan=23, sticky="w", pady=(8, 0))

    def add_key_fields(self, frame: ttk.Frame, column: int) -> None:
        """Extra parameters next to p, q, e (lab 3 adds H0)."""

    def _build_explain(self) -> None:
        frame = self.tr(ttk.LabelFrame(self, padding=8), "frame.explain")
        frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        self.rowconfigure(3, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        self.explain = tk.Text(frame, height=12, wrap="none", font=MONO, state="disabled")
        self.explain.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.explain.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.explain.configure(yscrollcommand=scroll.set)

    def build_body(self) -> None:
        raise NotImplementedError

    def _on_language(self, _event: object = None) -> None:
        self.language = list(LANGUAGES)[self.language_box.current()]
        self._retranslate()

    def _retranslate(self) -> None:
        self.title(self.t("app.title"))
        for widget, key in self.labels:
            widget.configure(text=self.t(key))

    # ------------------------------------------------------------------ keys
    def compute_keys(self) -> Optional[rsa.Keys]:
        try:
            trace: List[EuclidStep] = []
            self.keys = rsa.make_keys(self.number("p"), self.number("q"), self.number("e"), trace)
        except ValueError as error:
            self.keys = None
            self.key_info.set("")
            self.fail(error)
            return None
        k = self.keys
        self.key_info.set(f"r = {k.r}   phi(r) = {k.phi}   d = {k.d}")
        self.set_explain("\n".join([self.t("explain.keys", r=k.r, phi=k.phi), "",
                                    *euclid_table(trace), "",
                                    self.t("explain.d", d=k.d, check=k.e * k.d % k.phi)]))
        self.status.set(self.t("status.keys", e=k.e, d=k.d, r=k.r))
        return k


class App(KeyWindow):
    """Lab 2: encryption and decryption with the computed keys."""

    def build_body(self) -> None:
        frame = ttk.Frame(self, padding=(10, 0))
        frame.grid(row=2, column=0, sticky="nsew")
        self.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(1, weight=1)

        self.tr(ttk.Label(frame), "label.plain").grid(row=0, column=0, sticky="w")
        self.tr(ttk.Label(frame), "label.cipher").grid(row=0, column=2, sticky="w")
        self.plain = tk.Text(frame, height=8, wrap="word", font=MONO)
        self.plain.grid(row=1, column=0, sticky="nsew")
        self.plain.insert("1.0", "CAT")
        self.cipher = tk.Text(frame, height=8, wrap="word", font=MONO)
        self.cipher.grid(row=1, column=2, sticky="nsew")

        buttons = ttk.Frame(frame, padding=8)
        buttons.grid(row=1, column=1)
        self.tr(ttk.Label(buttons), "label.codec").pack()
        self.codec = ttk.Combobox(buttons, state="readonly", width=10, values=rsa.CODECS)
        self.codec.current(0)
        self.codec.pack(pady=(0, 10))
        for key, command in (("btn.encrypt", self._encrypt), ("btn.decrypt", self._decrypt),
                             ("btn.clear", self._clear)):
            self.tr(ttk.Button(buttons, width=16, command=command), key).pack(pady=3)

    def _encrypt(self) -> None:
        keys = self.compute_keys()
        if keys is None:
            return
        try:
            blocks = rsa.encode(self.plain.get("1.0", "end").rstrip("\n"), self.codec.get())
            cipher = rsa.encrypt(blocks, keys.e, keys.r)
        except ValueError as error:
            self.fail(error)
            return
        self._show(self.cipher, " ".join(map(str, cipher)))
        self._explain_blocks(("m", blocks), ("c", cipher), keys.e, keys.r)
        self.status.set(self.t("status.encrypted", count=len(cipher)))

    def _decrypt(self) -> None:
        keys = self.compute_keys()
        if keys is None:
            return
        try:
            cipher = rsa.parse_blocks(self.cipher.get("1.0", "end"))
            blocks = rsa.decrypt(cipher, keys.d, keys.r)
            text = rsa.decode(blocks, self.codec.get())
        except ValueError as error:
            self.fail(error)
            return
        self._show(self.plain, text)
        self._explain_blocks(("c", cipher), ("m", blocks), keys.d, keys.r)
        self.status.set(self.t("status.decrypted", count=len(blocks)))

    def _explain_blocks(self, source: Tuple[str, List[int]], target: Tuple[str, List[int]],
                        z: int, r: int) -> None:
        """Append the blocks and the fast_exp trace of the first block to the key explanation."""
        current = self.explain.get("1.0", "end").rstrip("\n")
        lines = [current, ""] + [f"{name} = {' '.join(map(str, blocks[:30]))}"
                                 for name, blocks in (source, target)]
        source = source[1]
        if source:
            lines += ["", *exp_table(source[0], z, r)]
        self.set_explain("\n".join(lines))

    @staticmethod
    def _show(widget: tk.Text, text: str) -> None:
        widget.delete("1.0", "end")
        widget.insert("1.0", text)

    def _clear(self) -> None:
        self.plain.delete("1.0", "end")
        self.cipher.delete("1.0", "end")
        self.set_explain("")


def run() -> None:
    App().mainloop()


if __name__ == "__main__":
    run()
