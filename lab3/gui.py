"""Lab 3 window: RSA digital signature, signing and verification."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List

from configs.cfg import HASH_H0, SIGN_E, SIGN_P, SIGN_Q
from lab2.gui import MONO, STRINGS as KEY_STRINGS, KeyWindow
from lab3 import signature
from lab3.hashing import HashStep
from lab3.runner import hash_table

VALID_COLOR, INVALID_COLOR = "#1a7f37", "#cf222e"

STRINGS: Dict[str, Dict[str, str]] = {
    "en": {
        **KEY_STRINGS["en"],
        "app.title": "Lab 3 - RSA digital signature",
        "label.message": "Message M",
        "label.signature": "Signature S:",
        "btn.sign": "Sign",
        "btn.verify": "Verify",
        "status.signed": "signed: h(M) = {m}, S = {s}",
        "verdict.valid": "Signature is VALID: h(M') = S^e mod r = {m}",
        "verdict.invalid": "Signature is INVALID: h(M') = {computed}, S^e mod r = {recovered}",
        "explain.sign": "S = h(M)^d mod r = {m}^{d} mod {r} = {s}",
        "explain.verify": "m' = h(M') = {computed}\nm = S^e mod r = {s}^{e} mod {r} = {recovered}",
        "explain.hash": "Hash (formula 3.2, n = r = {r}):",
    },
    "ru": {
        **KEY_STRINGS["ru"],
        "app.title": "ЛР3 - электронная цифровая подпись RSA",
        "label.message": "Сообщение M",
        "label.signature": "Подпись S:",
        "btn.sign": "Подписать",
        "btn.verify": "Проверить",
        "status.signed": "подписано: h(M) = {m}, S = {s}",
        "verdict.valid": "Подпись ПОДЛИННАЯ: h(M') = S^e mod r = {m}",
        "verdict.invalid": "Подпись НЕДЕЙСТВИТЕЛЬНА: h(M') = {computed}, S^e mod r = {recovered}",
        "explain.sign": "S = h(M)^d mod r = {m}^{d} mod {r} = {s}",
        "explain.verify": "m' = h(M') = {computed}\nm = S^e mod r = {s}^{e} mod {r} = {recovered}",
        "explain.hash": "Хеш-образ (формула 3.2, n = r = {r}):",
    },
}


class App(KeyWindow):
    """Lab 3: the signer computes S, the receiver checks {M', S}."""

    strings = STRINGS
    defaults = (SIGN_P, SIGN_Q, SIGN_E)

    def add_key_fields(self, frame: ttk.Frame, column: int) -> None:
        ttk.Label(frame, text="H0 =").grid(row=0, column=column, padx=(0, 4))
        self.fields["H0"] = tk.StringVar(value=str(HASH_H0))
        ttk.Entry(frame, width=8, textvariable=self.fields["H0"], font=MONO).grid(
            row=0, column=column + 1, padx=(0, 14))

    def build_body(self) -> None:
        frame = ttk.Frame(self, padding=(10, 0))
        frame.grid(row=2, column=0, sticky="nsew")
        self.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        self.tr(ttk.Label(frame), "label.message").grid(row=0, column=0, sticky="w")
        self.message = tk.Text(frame, height=6, wrap="word", font=MONO)
        self.message.grid(row=1, column=0, columnspan=6, sticky="nsew")
        self.message.insert("1.0", "БГУИР")

        self.tr(ttk.Label(frame), "label.signature").grid(row=2, column=0, sticky="w", pady=8)
        self.signature = tk.StringVar()
        ttk.Entry(frame, textvariable=self.signature, font=MONO, width=60).grid(
            row=2, column=1, sticky="ew", padx=6)
        frame.columnconfigure(1, weight=1)
        self.tr(ttk.Button(frame, width=14, command=self._sign), "btn.sign").grid(row=2, column=2)
        self.tr(ttk.Button(frame, width=14, command=self._verify), "btn.verify").grid(
            row=2, column=3, padx=6)

        self.verdict = tk.Label(frame, font=MONO + ("bold",), anchor="w")
        self.verdict.grid(row=3, column=0, columnspan=6, sticky="ew")

    def _text(self) -> str:
        return self.message.get("1.0", "end").rstrip("\n")

    def _hash_lines(self, steps: List[HashStep], h0: int, r: int) -> List[str]:
        return ["", self.t("explain.hash", r=r), *hash_table(steps, h0, r)]

    def _sign(self) -> None:
        keys = self.compute_keys()
        if keys is None:
            return
        try:
            h0 = self.number("H0")
            steps: List[HashStep] = []
            s = signature.sign(self._text(), keys.d, keys.r, h0, steps)
        except ValueError as error:
            self.fail(error)
            return
        m = steps[-1].h if steps else h0 % keys.r
        self.signature.set(str(s))
        self.verdict.configure(text="")
        current = self.explain.get("1.0", "end").rstrip("\n")
        self.set_explain("\n".join([current, *self._hash_lines(steps, h0, keys.r), "",
                                    self.t("explain.sign", m=m, d=keys.d, r=keys.r, s=s)]))
        self.status.set(self.t("status.signed", m=m, s=s))

    def _verify(self) -> None:
        keys = self.compute_keys()
        if keys is None:
            return
        try:
            h0 = self.number("H0")
            try:
                s = int(self.signature.get().strip())
            except ValueError:
                raise ValueError(self.t("status.number", name="S")) from None
            steps: List[HashStep] = []
            verdict = signature.verify(self._text(), s, keys.e, keys.r, h0, steps)
        except ValueError as error:
            self.fail(error)
            return
        if verdict.valid:
            text, color = self.t("verdict.valid", m=verdict.computed), VALID_COLOR
        else:
            text = self.t("verdict.invalid", computed=verdict.computed,
                          recovered=verdict.recovered)
            color = INVALID_COLOR
        self.verdict.configure(text=text, foreground=color)
        current = self.explain.get("1.0", "end").rstrip("\n")
        self.set_explain("\n".join([current, *self._hash_lines(steps, h0, keys.r), "",
                                    self.t("explain.verify", computed=verdict.computed, s=s,
                                           e=keys.e, r=keys.r, recovered=verdict.recovered)]))
        self.status.set(text)


def run() -> None:
    App().mainloop()


if __name__ == "__main__":
    run()
