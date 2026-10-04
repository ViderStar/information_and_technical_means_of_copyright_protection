"""Interface translations: English (default) and Russian.

Every user-visible string of the window lives here. To add a language, add
its code to LANGUAGES and a matching dictionary to STRINGS.
"""

from typing import Dict

LANGUAGES: Dict[str, str] = {"en": "English", "ru": "Русский"}
DEFAULT_LANGUAGE = "en"

STRINGS: Dict[str, Dict[str, str]] = {
    "en": {
        "app.title": "Lab 1 - transposition and substitution ciphers",
        "top.cipher": "Cipher:",
        "top.group_by": "Group by",
        "top.group_unit": "symbols (0 = no groups)",
        "top.show_explain": "Show explanation",
        "frame.params": "Parameters",
        "frame.explain": "How it works",
        "label.plain": "Plaintext",
        "label.cipher": "Ciphertext",
        "btn.encrypt": "Encrypt →",
        "btn.decrypt": "← Decrypt",
        "btn.swap": "⇄ Swap",
        "btn.clear": "Clear",
        "status.ready": "Pick a cipher, set the parameters and press \"Encrypt\"",
        "status.holes": "Holes: {holes}",
        "status.empty": "Empty text: nothing to process",
        "status.error": "Error: {message}",
        "status.encrypted": "encrypted: {src} symbols -> {dst} symbols",
        "status.decrypted": "decrypted: {src} symbols -> {dst} symbols",
        "status.cleared": "Cleared",

        "method.fence.name": "Rail fence",
        "method.fence.title": "Transposition: the text is written in a zigzag over K rows",
        "param.fence.key": "Fence height K",

        "method.column.name": "Columnar transposition",
        "method.column.title": "Transposition: columns are read in the order set by the keyword",
        "param.column.keyword": "Keyword",
        "param.column.keyword2": "Second key (double transposition)",
        "param.column.keyword2.hint": "empty = single transposition",

        "method.grille.name": "Turning grille",
        "method.grille.title": "Transposition: writing through grille holes, turned by 90°",
        "param.grille.size": "Grille size",
        "param.grille.holes": "Holes (one per orbit)",

        "method.caesar.name": "Caesar / affine cipher",
        "method.caesar.title": "Substitution: E(i) = (i · k1 + k2) mod n, Caesar when k1 = 1",
        "param.caesar.key": "Shift k2",
        "param.caesar.mul": "Multiplier k1",
        "param.caesar.mul.hint": "must be coprime with the alphabet size",

        "method.playfair.name": "Playfair cipher",
        "method.playfair.title": "Substitution: digraphs are replaced using a cipher table",
        "param.playfair.keyword": "Table keyword",
        "param.playfair.keyword.hint": "key and text must use the same alphabet",

        "method.vigenere.name": "Vigenere cipher",
        "method.vigenere.title": "Substitution: every position is shifted by its own key symbol",
        "param.vigenere.keyword": "Keyword",
        "param.vigenere.keyword.hint": "key and text must use the same alphabet",
        "param.vigenere.scheme": "Key scheme",

        "explain.fence.header": "Zigzag over {rows} rows (the ciphertext is read row by row):",
        "explain.column.key": "Key {keyword} -> column numbers {numbers}",
        "explain.column.table": "Table (text written row by row, read by columns):",
        "explain.column.order": "Reading order: ",
        "explain.column.second": "Second pass, key {keyword} -> {numbers}",
        "explain.column.second_input": "Second pass input: ",
        "explain.grille.orbits": "Rotation orbit layout (equal numbers belong to one orbit):",
        "explain.grille.order": "Filling order over four turns:",
        "explain.grille.matrix": "Filled matrix (read row by row):",
        "explain.caesar.header": "Alphabet of {n} letters, E(i) = (i * {k1} + {k2}) mod {n}",
        "explain.caesar.source": "plain:  ",
        "explain.caesar.mapped": "cipher: ",
        "explain.playfair.table": "Cipher table for key {keyword}:",
        "explain.playfair.digraphs": "Digraphs: ",
        "explain.playfair.result": "Result:   ",
        "explain.vigenere.scheme": "Key scheme: {scheme}",
        "explain.vigenere.text": "text:   ",
        "explain.vigenere.key": "key:    ",
        "explain.vigenere.cipher": "cipher: ",
    },
    "ru": {
        "app.title": "ЛР1 — шифры перестановок и подстановок",
        "top.cipher": "Шифр:",
        "top.group_by": "Группировать по",
        "top.group_unit": "символов (0 — без групп)",
        "top.show_explain": "Показывать разбор",
        "frame.params": "Параметры",
        "frame.explain": "Как это работает",
        "label.plain": "Открытый текст",
        "label.cipher": "Шифротекст",
        "btn.encrypt": "Зашифровать →",
        "btn.decrypt": "← Расшифровать",
        "btn.swap": "⇄ Поменять",
        "btn.clear": "Очистить",
        "status.ready": "Выберите шифр, задайте параметры и нажмите «Зашифровать»",
        "status.holes": "Отверстия: {holes}",
        "status.empty": "Пустой текст: нечего обрабатывать",
        "status.error": "Ошибка: {message}",
        "status.encrypted": "зашифровано: {src} символов -> {dst} символов",
        "status.decrypted": "расшифровано: {src} символов -> {dst} символов",
        "status.cleared": "Очищено",

        "method.fence.name": "Железнодорожная изгородь",
        "method.fence.title": "Перестановка: текст пишется зигзагом по K строкам",
        "param.fence.key": "Высота изгороди K",

        "method.column.name": "Столбцовый метод",
        "method.column.title": "Перестановка: чтение по столбцам в порядке, заданном ключевым словом",
        "param.column.keyword": "Ключевое слово",
        "param.column.keyword2": "Второй ключ (двойная перестановка)",
        "param.column.keyword2.hint": "пусто — одинарная перестановка",

        "method.grille.name": "Поворачивающаяся решётка",
        "method.grille.title": "Перестановка: запись через отверстия решётки с поворотом на 90°",
        "param.grille.size": "Размер решётки",
        "param.grille.holes": "Отверстия (по одному на орбиту)",

        "method.caesar.name": "Шифр Цезаря / аффинный",
        "method.caesar.title": "Подстановка: E(i) = (i · k1 + k2) mod n, при k1 = 1 — шифр Цезаря",
        "param.caesar.key": "Сдвиг k2",
        "param.caesar.mul": "Множитель k1",
        "param.caesar.mul.hint": "должен быть взаимно прост с мощностью алфавита",

        "method.playfair.name": "Шифр Плейфейра",
        "method.playfair.title": "Подстановка: биграммы заменяются по шифрующей таблице",
        "param.playfair.keyword": "Ключевое слово таблицы",
        "param.playfair.keyword.hint": "ключ и текст — в одном алфавите",

        "method.vigenere.name": "Шифр Виженера",
        "method.vigenere.title": "Подстановка: каждая позиция шифруется своим сдвигом из ключа",
        "param.vigenere.keyword": "Ключевое слово",
        "param.vigenere.keyword.hint": "ключ и текст — в одном алфавите",
        "param.vigenere.scheme": "Схема ключа",

        "explain.fence.header": "Зигзаг по {rows} строкам (шифротекст читается построчно):",
        "explain.column.key": "Ключ {keyword} -> номера столбцов {numbers}",
        "explain.column.table": "Таблица (текст записан построчно, читается по столбцам):",
        "explain.column.order": "Порядок чтения: ",
        "explain.column.second": "Второй проход, ключ {keyword} -> {numbers}",
        "explain.column.second_input": "Вход второго прохода: ",
        "explain.grille.orbits": "Разметка орбит поворота (одинаковые номера — одна орбита):",
        "explain.grille.order": "Порядок заполнения по четырём поворотам:",
        "explain.grille.matrix": "Заполненная матрица (читается построчно):",
        "explain.caesar.header": "Алфавит из {n} букв, E(i) = (i * {k1} + {k2}) mod {n}",
        "explain.caesar.source": "исходный:   ",
        "explain.caesar.mapped": "заменяется: ",
        "explain.playfair.table": "Шифрующая таблица для ключа {keyword}:",
        "explain.playfair.digraphs": "Биграммы:  ",
        "explain.playfair.result": "Результат: ",
        "explain.vigenere.scheme": "Схема ключа: {scheme}",
        "explain.vigenere.text": "текст: ",
        "explain.vigenere.key": "ключ:  ",
        "explain.vigenere.cipher": "шифр:  ",
    },
}

_current = DEFAULT_LANGUAGE


def set_language(code: str) -> None:
    global _current
    if code not in STRINGS:
        raise ValueError(f"Unknown language: {code}")
    _current = code


def get_language() -> str:
    return _current


def t(key: str, **values: object) -> str:
    """Translate `key` into the current language, filling `{placeholders}`."""
    text = STRINGS[_current][key]
    return text.format(**values) if values else text
