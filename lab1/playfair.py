"""Биграммный шифр Плейфейра (вариант №2).

Ключ — шифрующая таблица: ключевое слово, затем оставшиеся буквы алфавита.
Для английского алфавита таблица 5x5 (J отождествляется с I),
для русского — 4x8 (32 буквы).
"""

from typing import Dict, List, Tuple

from helpers.alphabet import ENGLISH, RUSSIAN, detect

# Буквы-разделители для повторов и дополнения нечётного текста
PADDING = {ENGLISH: "XQ", RUSSIAN: "ЪЫ"}


def _shape(size: int) -> Tuple[int, int]:
    """Наиболее близкая к квадрату таблица: 25 -> 5x5, 32 -> 4x8."""
    for rows in range(int(size ** 0.5), 0, -1):
        if size % rows == 0:
            return rows, size // rows
    raise ValueError("Не удалось построить таблицу")


def build_table(keyword: str, alphabet: str) -> Tuple[List[str], int, int]:
    """Таблица как плоский список букв + размеры."""
    if alphabet is ENGLISH:
        alphabet = alphabet.replace("J", "")       # I/J занимают одну клетку
        keyword = keyword.replace("J", "I")

    letters: List[str] = []
    for symbol in keyword + alphabet:
        if symbol in alphabet and symbol not in letters:
            letters.append(symbol)

    rows, columns = _shape(len(letters))
    return letters, rows, columns


def digraphs(text: str, alphabet: str) -> List[str]:
    """Разбиение на биграммы: повторы разводятся, нечётная длина дополняется."""
    fillers = PADDING[alphabet]
    pairs, i = [], 0
    while i < len(text):
        first = text[i]
        second = text[i + 1] if i + 1 < len(text) else ""
        if not second or first == second:
            second = next(f for f in fillers if f != first)
            i += 1
        else:
            i += 2
        pairs.append(first + second)
    return pairs


def _swap(text: str, keyword: str, step: int) -> str:
    """step = +1 — шифрование, -1 — дешифрование."""
    alphabet = detect(text, keyword)
    letters, rows, columns = build_table(keyword, alphabet)

    if alphabet is ENGLISH:
        text = text.replace("J", "I")
    position: Dict[str, Tuple[int, int]] = {
        letter: divmod(i, columns) for i, letter in enumerate(letters)
    }

    result = []
    for pair in digraphs(text, alphabet):
        (r1, c1), (r2, c2) = position[pair[0]], position[pair[1]]
        if r1 == r2:                                   # одна строка — сдвиг вбок
            c1, c2 = (c1 + step) % columns, (c2 + step) % columns
        elif c1 == c2:                                 # один столбец — сдвиг вниз
            r1, r2 = (r1 + step) % rows, (r2 + step) % rows
        else:                                          # прямоугольник — обмен столбцами
            c1, c2 = c2, c1
        result.append(letters[r1 * columns + c1] + letters[r2 * columns + c2])
    return "".join(result)


def encrypt(text: str, keyword: str) -> str:
    return _swap(text, keyword, step=1)


def decrypt(cipher: str, keyword: str) -> str:
    return _swap(cipher, keyword, step=-1)


def render(keyword: str, alphabet: str) -> str:
    """Таблица в виде строк — для отчёта и demo."""
    letters, _, columns = build_table(keyword, alphabet)
    cells = ["I/J" if letter == "I" and alphabet is ENGLISH else letter
             for letter in letters]
    return "\n".join(" ".join(f"{c:<3}" for c in cells[i:i + columns])
                     for i in range(0, len(cells), columns))
