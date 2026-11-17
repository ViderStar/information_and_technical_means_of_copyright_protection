"""Lab 4 window: text steganography, LSB and BPCS for colour images, CPT for
binary images. Every tab shows the container before and after embedding and
explains the computation on the panel below."""

import base64
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Dict, List, Optional, Tuple

from configs.cfg import (BPCS_ALPHA, BPCS_PLANES, CPT_BLOCK, CPT_R, LSB_DEPTH, SPACES_BASE,
                         STEGO_NAME)
from lab2.gui import LANGUAGES, MONO
from lab4 import bpcs, cpt, imageio, lsb, samples
from lab4 import textsteg as ts
from lab4.bits import format_bits, payload
from lab4.imageio import Image
from lab4.runner import CPT_IMAGE, CPT_K, CPT_W, DEMO_MESSAGE, VARIANT_CONTAINER, digit_table

PREVIEW = 300                      # longest side of an image preview, pixels
CHANGED = (220, 30, 30)

STRINGS: Dict[str, Dict[str, str]] = {
    "en": {
        "app.title": "Lab 4 - Steganography",
        "tab.text": "Text",
        "tab.image": "Colour image: LSB, BPCS",
        "tab.cpt": "Binary image: CPT",
        "frame.explain": "How it works",
        "label.method": "Method:",
        "label.container": "Container text",
        "label.stego": "Stego text (· marks a space)",
        "label.base": "Base (spaces):",
        "label.message": "Message:",
        "label.key": "Stego key:",
        "label.bits": "LSBs:",
        "label.alpha": "alpha0:",
        "label.planes": "planes:",
        "label.block": "Block m x n:",
        "label.cover": "Container",
        "label.result": "Stego image",
        "label.view": "Show:",
        "check.modified": "modified CPT (distance matrix)",
        "view.image": "image",
        "view.plane": "red LSB plane",
        "view.diff": "changed pixels",
        "btn.embed": "Embed →",
        "btn.extract": "← Extract",
        "btn.open": "Open...",
        "btn.sample": "Test image",
        "btn.save": "Save stego...",
        "btn.example": "Manual example",
        "status.ready": "Choose a tab: text, colour image or binary image",
        "status.embedded": "embedded {bits} bits; {extra}",
        "status.digits": "embedded {count} base-{base} digits into {count} gaps",
        "status.extracted": "extracted: {message}",
        "status.loaded": "{name}: {w}x{h}, capacity {room} bytes",
        "status.saved": "saved {name}",
        "status.noimage": "Open a container image or take the test image first",
        "status.nostego": "Embed a message first",
        "status.error": "Error: {message}",
        "status.number": "{name} must be a number",
        "explain.spaces": "Spaces, base {base}: digit d = d + 1 spaces, {width} digits per "
                          "Windows-1251 byte;\ncapacity {room} bytes, used {count} gaps "
                          "(with the zero byte), added {added} spaces",
        "explain.text": "Method: {method}, capacity {room} bits\n"
                        "Message in Windows-1251 + zero byte ({count} bits):\n{bits}",
        "explain.lsb": "LSB: {depth} lowest bit(s) of every R, G, B sample, key: {skey}\n"
                       "Payload = 32-bit length + UTF-8 ({count} bits): {bits}...\n"
                       "Samples changed: {changed}, PSNR = {psnr:.1f} dB, capacity {room} bytes",
        "explain.bpcs": "BPCS: 8x8 blocks of the {planes} lowest bit planes of R, G, B\n"
                        "Noise-like blocks (alpha >= {alpha}): {noisy} of {total}, "
                        "capacity {room} bytes\nMessage blocks: {used} (63 bits + flag), "
                        "conjugated S* = S xor BC: {conj}\nPSNR = {psnr:.1f} dB",
        "explain.cpt": "CPT: blocks {m}x{n}, r = {r} bits per block, {blocks} blocks used, "
                       "{changed} bits changed\nK = {k}\nW = {w}\n",
        "explain.block": "Block {i}: b = {b}, SUM = {total}, SUM mod 2^r = {mod}, d = {d}, "
                         "changed: {cells}",
    },
    "ru": {
        "app.title": "ЛР4 - стеганография",
        "tab.text": "Текст",
        "tab.image": "Цветное изображение: LSB, BPCS",
        "tab.cpt": "Бинарное изображение: CPT",
        "frame.explain": "Как это работает",
        "label.method": "Метод:",
        "label.container": "Текст-контейнер",
        "label.stego": "Стеготекст (· - пробел)",
        "label.base": "Основание (пробелы):",
        "label.message": "Сообщение:",
        "label.key": "Стегоключ:",
        "label.bits": "Младших бит:",
        "label.alpha": "alpha0:",
        "label.planes": "плоскостей:",
        "label.block": "Блок m x n:",
        "label.cover": "Контейнер",
        "label.result": "Стегоизображение",
        "label.view": "Показать:",
        "check.modified": "модифицированный CPT (матрица расстояний)",
        "view.image": "изображение",
        "view.plane": "плоскость LSB (R)",
        "view.diff": "изменённые пиксели",
        "btn.embed": "Встроить →",
        "btn.extract": "← Извлечь",
        "btn.open": "Открыть...",
        "btn.sample": "Тестовое",
        "btn.save": "Сохранить...",
        "btn.example": "Пример пособия",
        "status.ready": "Выберите вкладку: текст, цветное или бинарное изображение",
        "status.embedded": "встроено бит: {bits}; {extra}",
        "status.digits": "встроено {count} цифр {base}-ичной системы в {count} промежутков",
        "status.extracted": "извлечено: {message}",
        "status.loaded": "{name}: {w}x{h}, ёмкость {room} байт",
        "status.saved": "сохранено: {name}",
        "status.noimage": "Сначала откройте изображение-контейнер или возьмите тестовое",
        "status.nostego": "Сначала встройте сообщение",
        "status.error": "Ошибка: {message}",
        "status.number": "{name} должно быть числом",
        "explain.spaces": "Пробелы, основание {base}: цифра d = d + 1 пробелов, {width} цифр "
                          "на байт Windows-1251;\nёмкость {room} байт, занято промежутков "
                          "{count} (с нулевым байтом), добавлено пробелов {added}",
        "explain.text": "Метод: {method}, ёмкость {room} бит\n"
                        "Сообщение в Windows-1251 + нулевой байт ({count} бит):\n{bits}",
        "explain.lsb": "LSB: {depth} младш. бит каждой составляющей R, G, B, ключ: {skey}\n"
                       "Полезная нагрузка = длина 32 бита + UTF-8 ({count} бит): {bits}...\n"
                       "Изменено составляющих: {changed}, PSNR = {psnr:.1f} дБ, "
                       "ёмкость {room} байт",
        "explain.bpcs": "BPCS: блоки 8x8 в {planes} младших битовых плоскостях R, G, B\n"
                        "Шумоподобных блоков (alpha >= {alpha}): {noisy} из {total}, "
                        "ёмкость {room} байт\nБлоков сообщения: {used} (63 бита + флаг), "
                        "конъюнкций S* = S xor BC: {conj}\nPSNR = {psnr:.1f} дБ",
        "explain.cpt": "CPT: блоки {m}x{n}, r = {r} бит на блок, использовано блоков {blocks}, "
                       "изменено бит {changed}\nK = {k}\nW = {w}\n",
        "explain.block": "Блок {i}: b = {b}, SUM = {total}, SUM mod 2^r = {mod}, d = {d}, "
                         "изменены: {cells}",
    },
}

TEXT_METHODS = {"spaces": ("spaces", "пробелы"), "invisible": ("invisible", "невидимые символы"),
                "case": ("case", "регистр букв"), "synonyms": ("synonyms", "синонимы"),
                "mixed": ("synonyms, mixed radix", "синонимы, смешанное основание"),
                "mimicry": ("mimicry", "мимикрия")}


def photo_image(image: Image, limit: int = PREVIEW) -> tk.PhotoImage:
    """PhotoImage scaled to fit `limit` (zoom for small pictures, subsample for big)."""
    picture = tk.PhotoImage(data=base64.b64encode(imageio.write_png(image)), format="png")
    side = max(image.width, image.height)
    if side * 2 <= limit:
        return picture.zoom(max(1, limit // side))
    if side > limit:
        return picture.subsample(-(-side // limit))
    return picture


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.language = "en"
        self.minsize(980, 760)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.labels: List[Tuple[tk.Widget, str]] = []
        self.status = tk.StringVar()
        self.pictures: Dict[str, tk.PhotoImage] = {}       # keep references for Tk
        self.cover: Optional[Image] = None
        self.stego: Optional[Image] = None
        self.binary: Optional[cpt.Matrix] = None
        self.binary_stego: Optional[cpt.Matrix] = None
        self.example_key: Optional[cpt.Key] = None       # K, W of the manual's example

        top = ttk.Frame(self, padding=(10, 8, 10, 0))
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)
        self.language_box = ttk.Combobox(top, state="readonly", width=10,
                                         values=list(LANGUAGES.values()))
        self.language_box.current(0)
        self.language_box.grid(row=0, column=1)
        self.language_box.bind("<<ComboboxSelected>>", self._on_language)

        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=10, pady=6)
        self.tab_frames = [self._build_text(), self._build_image(), self._build_cpt()]
        for frame in self.tab_frames:
            self.tabs.add(frame)

        explain = self.tr(ttk.LabelFrame(self, padding=8), "frame.explain")
        explain.grid(row=2, column=0, sticky="nsew", padx=10)
        explain.columnconfigure(0, weight=1)
        self.explain = tk.Text(explain, height=11, wrap="none", font=MONO, state="disabled")
        self.explain.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(explain, orient="vertical", command=self.explain.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.explain.configure(yscrollcommand=scroll.set)
        ttk.Label(self, textvariable=self.status, padding=(10, 4, 10, 8)).grid(
            row=3, column=0, sticky="w")

        self._retranslate()
        self.status.set(self.t("status.ready"))

    # ------------------------------------------------------------------ helpers
    def t(self, key: str, **values: object) -> str:
        return STRINGS[self.language][key].format(**values)

    def tr(self, widget: tk.Widget, key: str) -> tk.Widget:
        self.labels.append((widget, key))
        return widget

    def set_explain(self, text: str) -> None:
        self.explain.configure(state="normal")
        self.explain.delete("1.0", "end")
        self.explain.insert("1.0", text)
        self.explain.configure(state="disabled")

    def fail(self, error: Exception) -> None:
        self.status.set(self.t("status.error", message=error))

    def number(self, variable: tk.StringVar, name: str, kind: type = int) -> float:
        try:
            return kind(variable.get().strip().replace(",", "."))
        except ValueError:
            raise ValueError(self.t("status.number", name=name)) from None

    def _on_language(self, _event: object = None) -> None:
        self.language = list(LANGUAGES)[self.language_box.current()]
        self._retranslate()

    def _retranslate(self) -> None:
        self.title(self.t("app.title"))
        for widget, key in self.labels:
            widget.configure(text=self.t(key))
        for index, key in enumerate(("tab.text", "tab.image", "tab.cpt")):
            self.tabs.tab(index, text=self.t(key))
        names = [pair[self.language == "ru"] for pair in TEXT_METHODS.values()]
        current = self.text_method.current()
        self.text_method.configure(values=names)
        self.text_method.current(max(current, 0))
        views = [self.t(k) for k in ("view.image", "view.plane", "view.diff")]
        current = self.view_box.current()
        self.view_box.configure(values=views)
        self.view_box.current(max(current, 0))

    def _message_row(self, frame: ttk.Frame, row: int, value: str) -> tk.StringVar:
        self.tr(ttk.Label(frame), "label.message").grid(row=row, column=0, sticky="w")
        variable = tk.StringVar(value=value)
        ttk.Entry(frame, textvariable=variable, font=MONO).grid(
            row=row, column=1, columnspan=8, sticky="ew", pady=4)
        return variable

    # ------------------------------------------------------------------ text tab
    def _build_text(self) -> ttk.Frame:
        frame = ttk.Frame(self.tabs, padding=8)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)
        frame.rowconfigure(3, weight=1)
        self.tr(ttk.Label(frame), "label.method").grid(row=0, column=0, sticky="w")
        self.text_method = ttk.Combobox(frame, state="readonly", width=32)
        self.text_method.grid(row=0, column=1, sticky="w", pady=4)
        self.text_method.bind("<<ComboboxSelected>>", lambda _e: self.stego_text.delete("1.0", "end"))
        self.tr(ttk.Label(frame), "label.base").grid(row=0, column=3, sticky="e")
        self.base = tk.StringVar(value=str(SPACES_BASE))
        ttk.Spinbox(frame, from_=2, to=6, width=4, textvariable=self.base, font=MONO,
                    state="readonly").grid(row=0, column=4, sticky="w", padx=4)
        self.text_message = self._message_row(frame, 1, STEGO_NAME)

        self.tr(ttk.Label(frame), "label.container").grid(row=2, column=0, sticky="w")
        self.tr(ttk.Label(frame), "label.stego").grid(row=2, column=3, sticky="w")
        self.container = tk.Text(frame, height=9, wrap="word", font=MONO, width=40)
        self.container.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.container.insert("1.0", VARIANT_CONTAINER)
        self.stego_text = tk.Text(frame, height=9, wrap="word", font=MONO, width=40)
        self.stego_text.grid(row=3, column=3, columnspan=6, sticky="nsew")
        buttons = ttk.Frame(frame, padding=8)
        buttons.grid(row=3, column=2)
        self.tr(ttk.Button(buttons, width=14, command=self._text_embed), "btn.embed").pack(pady=3)
        self.tr(ttk.Button(buttons, width=14, command=self._text_extract), "btn.extract").pack(pady=3)
        self.tr(ttk.Button(buttons, width=14, command=self._text_save), "btn.save").pack(pady=3)
        return frame

    def _shown(self, text: str) -> str:
        """Spaces (or no-break spaces) as dots, so the hidden digits are visible."""
        return text.replace(" " if self._method() == "spaces" else ts.NBSP, "·")

    def _real(self, text: str) -> str:
        return text.replace("·", " " if self._method() == "spaces" else ts.NBSP)

    def _text_save(self) -> None:
        text = self._real(self.stego_text.get("1.0", "end").rstrip("\n"))
        if not text:
            self.status.set(self.t("status.nostego"))
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as out:
                out.write(text)
            self.status.set(self.t("status.saved", name=path))

    def _method(self) -> str:
        return list(TEXT_METHODS)[self.text_method.current()]

    def _text_embed(self) -> None:
        method = self._method()
        container = self.container.get("1.0", "end").rstrip("\n")
        base = int(self.base.get())
        try:
            stego = ts.embed(method, container, self.text_message.get(), seed="gui", base=base)
        except ValueError as error:
            self.fail(error)
            return
        self.stego_text.delete("1.0", "end")
        self.stego_text.insert("1.0", self._shown(stego))
        if method == "spaces":
            digits = ts.spaces_extract(stego, base)
            used = len(ts.message_digits(self.text_message.get(), base))
            used = min(len(digits), used + ts.digit_width(base))
            self.set_explain("\n".join([
                self.t("explain.spaces", base=base, width=ts.digit_width(base),
                       room=ts.capacity_bytes(method, container, base), count=used,
                       added=len(stego) - len(container)), "",
                *digit_table(self.text_message.get(), base)]))
            self.status.set(self.t("status.digits", count=used, base=base))
            return
        bits = ts.message_bits(self.text_message.get())
        room = ts.capacity(method, container)
        if len(bits) + 8 <= room:
            bits += [0] * 8
        self.set_explain(self.t("explain.text", method=self.text_method.get(), room=room,
                                count=len(bits), bits=format_bits(bits)))
        self.status.set(self.t("status.embedded", bits=len(bits),
                               extra=f"{room} bits max" if room != float("inf") else ""))

    def _text_extract(self) -> None:
        text = self._real(self.stego_text.get("1.0", "end").rstrip("\n"))
        base = int(self.base.get())
        try:
            bits = ts.extract_bits(self._method(), text, base)
            message = (ts.message_from_digits(bits, base) if self._method() == "spaces"
                       else ts.message_from_bits(bits))
        except ValueError as error:
            self.fail(error)
            return
        self.text_message.set(message)
        self.set_explain(f"{format_bits(bits)}\n-> {message}")
        self.status.set(self.t("status.extracted", message=message))

    # ------------------------------------------------------------------ image tab
    def _build_image(self) -> ttk.Frame:
        frame = ttk.Frame(self.tabs, padding=8)
        params = ttk.Frame(frame)
        params.grid(row=0, column=0, columnspan=9, sticky="ew")
        self.image_method = tk.StringVar(value="lsb")
        ttk.Radiobutton(params, text="LSB", value="lsb", variable=self.image_method,
                        command=self._show_capacity).pack(side="left")
        ttk.Radiobutton(params, text="BPCS", value="bpcs", variable=self.image_method,
                        command=self._show_capacity).pack(side="left", padx=(6, 14))
        self.image_fields: Dict[str, tk.StringVar] = {}
        for key, name, value, width in (("label.bits", "bits", LSB_DEPTH, 3),
                                        ("label.key", "key", "", 10),
                                        ("label.alpha", "alpha", BPCS_ALPHA, 5),
                                        ("label.planes", "planes", BPCS_PLANES, 3)):
            self.tr(ttk.Label(params), key).pack(side="left", padx=(8, 2))
            self.image_fields[name] = tk.StringVar(value=str(value))
            ttk.Entry(params, width=width, textvariable=self.image_fields[name],
                      font=MONO).pack(side="left")
        for key, command in (("btn.open", self._open_image), ("btn.sample", self._sample_image),
                             ("btn.save", self._save_image)):
            self.tr(ttk.Button(params, command=command), key).pack(side="left", padx=(8, 0))

        frame.columnconfigure(1, weight=1)
        self.image_message = self._message_row(frame, 1, DEMO_MESSAGE)
        actions = ttk.Frame(frame)
        actions.grid(row=2, column=0, columnspan=9, sticky="w")
        self.tr(ttk.Button(actions, command=self._image_embed), "btn.embed").pack(side="left")
        self.tr(ttk.Button(actions, command=self._image_extract), "btn.extract").pack(
            side="left", padx=6)
        self.tr(ttk.Label(actions), "label.view").pack(side="left", padx=(20, 4))
        self.view_box = ttk.Combobox(actions, state="readonly", width=22)
        self.view_box.pack(side="left")
        self.view_box.bind("<<ComboboxSelected>>", lambda _e: self._show_images())

        self.cover_view, self.stego_view = self._image_pair(frame, 3)
        return frame

    def _image_pair(self, frame: ttk.Frame, row: int) -> Tuple[ttk.Label, ttk.Label]:
        views = []
        for column, key in ((0, "label.cover"), (4, "label.result")):
            box = self.tr(ttk.LabelFrame(frame, padding=4), key)
            box.grid(row=row, column=column, columnspan=4, sticky="nw", padx=(0, 10), pady=6)
            label = ttk.Label(box)
            label.pack()
            views.append(label)
        return views[0], views[1]

    def _set_cover(self, image: Image, name: str) -> None:
        self.cover, self.stego = image, None
        self._show_images()
        self._show_capacity(name)

    def _open_image(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("PNG / BMP", "*.png *.bmp")])
        if not path:
            return
        try:
            self._set_cover(imageio.load(path), path.rsplit("/", 1)[-1])
        except (ValueError, OSError) as error:
            self.fail(error)

    def _sample_image(self) -> None:
        self._set_cover(samples.photo(), "photo.png")

    def _save_image(self) -> None:
        if self.stego is None:
            self.status.set(self.t("status.nostego"))
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG", "*.png"), ("BMP", "*.bmp")])
        if path:
            try:
                imageio.save(self.stego, path)
                self.status.set(self.t("status.saved", name=path))
            except (ValueError, OSError) as error:
                self.fail(error)

    def _params(self) -> Tuple[int, Optional[str], float, int]:
        f = self.image_fields
        return (int(self.number(f["bits"], "LSB")), f["key"].get().strip() or None,
                float(self.number(f["alpha"], "alpha0", float)),
                int(self.number(f["planes"], "planes")))

    def _show_capacity(self, name: str = "") -> None:
        if self.cover is None:
            return
        try:
            depth, _, alpha0, planes = self._params()
            room = (lsb.capacity(self.cover, depth) if self.image_method.get() == "lsb"
                    else bpcs.capacity(self.cover, alpha0, planes)[1])
        except ValueError as error:
            self.fail(error)
            return
        self.status.set(self.t("status.loaded", name=name or "image", w=self.cover.width,
                               h=self.cover.height, room=room))

    def _view(self, image: Image, reference: Optional[Image]) -> Image:
        mode = self.view_box.current()
        if mode == 1:
            return lsb.bit_plane(image, 0)
        if mode == 2 and reference is not None:
            return lsb.difference(reference, image)
        return image

    def _show_images(self) -> None:
        for slot, label, image in (("cover", self.cover_view, self.cover),
                                   ("stego", self.stego_view, self.stego)):
            if image is None:
                label.configure(image="")
                continue
            reference = self.cover if slot == "stego" else image
            self.pictures[slot] = photo_image(self._view(image, reference))
            label.configure(image=self.pictures[slot])

    def _image_embed(self) -> None:
        if self.cover is None:
            self.status.set(self.t("status.noimage"))
            return
        message = self.image_message.get()
        try:
            depth, key, alpha0, planes = self._params()
            if self.image_method.get() == "lsb":
                self.stego = lsb.embed(self.cover, message, depth, key)
                bits = payload(message)
                text = self.t("explain.lsb", depth=depth, skey=key or "-", count=len(bits),
                              bits=format_bits(bits[:64]),
                              changed=lsb.changed_samples(self.cover, self.stego),
                              psnr=lsb.psnr(self.cover, self.stego),
                              room=lsb.capacity(self.cover, depth))
            else:
                self.stego, stats = bpcs.embed(self.cover, message, alpha0, planes)
                bits = payload(message)
                text = self.t("explain.bpcs", planes=planes, alpha=alpha0, noisy=stats.noisy,
                              total=stats.blocks, room=bpcs.capacity(self.cover, alpha0, planes)[1],
                              used=stats.used, conj=stats.conjugated,
                              psnr=lsb.psnr(self.cover, self.stego))
        except ValueError as error:
            self.fail(error)
            return
        self._show_images()
        self.set_explain(text)
        self.status.set(self.t("status.embedded", bits=len(bits), extra=self.image_method.get().upper()))

    def _image_extract(self) -> None:
        image = self.stego or self.cover
        if image is None:
            self.status.set(self.t("status.noimage"))
            return
        try:
            depth, key, alpha0, planes = self._params()
            message = (lsb.extract(image, depth, key) if self.image_method.get() == "lsb"
                       else bpcs.extract(image, alpha0, planes))
        except ValueError as error:
            self.fail(error)
            return
        self.image_message.set(message)
        self.status.set(self.t("status.extracted", message=message))

    # ------------------------------------------------------------------ CPT tab
    def _build_cpt(self) -> ttk.Frame:
        frame = ttk.Frame(self.tabs, padding=8)
        params = ttk.Frame(frame)
        params.grid(row=0, column=0, columnspan=9, sticky="ew")
        self.cpt_fields: Dict[str, tk.StringVar] = {}
        for key, name, value, width in (("label.block", "block", CPT_BLOCK, 6),
                                        (None, "r", CPT_R, 3), ("label.key", "key", "ITMCP", 10)):
            label = ttk.Label(params, text="r:")
            if key:
                self.tr(label, key)
            label.pack(side="left", padx=(8, 2))
            self.cpt_fields[name] = tk.StringVar(value=str(value))
            ttk.Entry(params, width=width, textvariable=self.cpt_fields[name],
                      font=MONO).pack(side="left")
        self.modified = tk.BooleanVar(value=False)
        self.tr(ttk.Checkbutton(params, variable=self.modified), "check.modified").pack(
            side="left", padx=10)
        for key, command in (("btn.open", self._open_binary), ("btn.sample", self._sample_binary),
                             ("btn.example", self._cpt_example)):
            self.tr(ttk.Button(params, command=command), key).pack(side="left", padx=(6, 0))

        frame.columnconfigure(1, weight=1)
        self.cpt_message = self._message_row(frame, 1, "БГУИР 2026")
        actions = ttk.Frame(frame)
        actions.grid(row=2, column=0, columnspan=9, sticky="w")
        self.tr(ttk.Button(actions, command=self._cpt_embed), "btn.embed").pack(side="left")
        self.tr(ttk.Button(actions, command=self._cpt_extract), "btn.extract").pack(
            side="left", padx=6)
        self.binary_view, self.binary_stego_view = self._image_pair(frame, 3)
        return frame

    def _cpt_key(self) -> cpt.Key:
        try:
            m, n = (int(v) for v in self.cpt_fields["block"].get().lower().split("x"))
        except ValueError:
            raise ValueError(self.t("status.number", name="m x n")) from None
        return cpt.generate_key(m, n, int(self.number(self.cpt_fields["r"], "r")),
                                self.cpt_fields["key"].get())

    def _set_binary(self, matrix: cpt.Matrix, name: str) -> None:
        self.binary, self.binary_stego, self.example_key = matrix, None, None
        self._show_binary()
        try:
            room = cpt.capacity(matrix, self._cpt_key())
        except ValueError as error:
            self.fail(error)
            return
        self.status.set(self.t("status.loaded", name=name, w=len(matrix[0]), h=len(matrix),
                               room=room))

    def _open_binary(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("PNG / BMP", "*.png *.bmp")])
        if path:
            try:
                self._set_binary(cpt.from_image(imageio.load(path)), path.rsplit("/", 1)[-1])
            except (ValueError, OSError) as error:
                self.fail(error)

    def _sample_binary(self) -> None:
        self._set_binary(cpt.from_image(samples.stamp()), "stamp.png")

    def _show_binary(self) -> None:
        for slot, label, matrix in (("bin", self.binary_view, self.binary),
                                    ("bin_stego", self.binary_stego_view, self.binary_stego)):
            if matrix is None:
                label.configure(image="")
                continue
            data = bytearray()
            for y, row in enumerate(matrix):
                for x, value in enumerate(row):
                    changed = slot == "bin_stego" and self.binary[y][x] != value
                    data += bytes(CHANGED if changed else ((0, 0, 0) if value else (255, 255, 255)))
            self.pictures[slot] = photo_image(Image(len(matrix[0]), len(matrix), 3, data), 360)
            label.configure(image=self.pictures[slot])

    def _cpt_example(self) -> None:
        """The manual's 4x8 picture, K, W, r = 3, b = 001001."""
        self.cpt_fields["block"].set("4x4")
        self.cpt_fields["r"].set("3")
        self.binary = [[int(ch) for ch in row] for row in CPT_IMAGE]
        key = self.example_key = cpt.Key(cpt.parse_matrix(CPT_K), cpt.parse_matrix(CPT_W), 3)
        out, traces = cpt.embed_bits(self.binary, [0, 0, 1, 0, 0, 1], key, "gui")
        self.binary_stego = out
        self._show_binary()
        self._explain_cpt(key, traces, out)
        self.status.set(self.t("status.embedded", bits=6, extra="b = 001001"))

    def _explain_cpt(self, key: cpt.Key, traces: List[cpt.BlockTrace], out: cpt.Matrix) -> None:
        m, n = len(key.k), len(key.k[0])
        lines = [self.t("explain.cpt", m=m, n=n, r=key.r, blocks=len(traces),
                        changed=cpt.bit_changes(self.binary, out),
                        k=cpt.format_matrix(key.k), w=cpt.format_matrix(key.w))]
        for i, trace in enumerate(traces[:12], start=1):
            cells = ", ".join(f"({j},{k})" for j, k in trace.flipped) or "-"
            lines.append(self.t("explain.block", i=i, b=format_bits(trace.bits),
                                total=trace.total, mod=trace.total % (1 << key.r),
                                d=trace.d, cells=cells))
            if i == 1:
                lines += [f"  S{w} = {{{', '.join(f'({j + 1},{k + 1})' for j, k in c)}}}"
                          for w, c in trace.sets.items()]
        self.set_explain("\n".join(lines))

    def _cpt_embed(self) -> None:
        if self.binary is None:
            self.status.set(self.t("status.noimage"))
            return
        if self.example_key is not None:              # leave the manual's example
            self._sample_binary()
        try:
            key = self._cpt_key()
            out, traces = cpt.embed(self.binary, self.cpt_message.get(), key,
                                    self.cpt_fields["key"].get(), self.modified.get())
        except ValueError as error:
            self.fail(error)
            return
        self.binary_stego = out
        self._show_binary()
        self._explain_cpt(key, traces, out)
        self.status.set(self.t("status.embedded", bits=len(traces) * key.r,
                               extra=f"{cpt.bit_changes(self.binary, out)} bits changed"))

    def _cpt_extract(self) -> None:
        matrix = self.binary_stego or self.binary
        if matrix is None:
            self.status.set(self.t("status.noimage"))
            return
        try:
            if self.example_key is not None:          # raw bits, no length field
                message = format_bits(cpt.extract_bits(matrix, self.example_key))
            else:
                message = cpt.extract(matrix, self._cpt_key())
        except ValueError as error:
            self.fail(error)
            return
        self.cpt_message.set(message)
        self.status.set(self.t("status.extracted", message=message))


def run() -> None:
    App().mainloop()


if __name__ == "__main__":
    run()
