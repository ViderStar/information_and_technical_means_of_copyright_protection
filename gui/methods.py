"""Описание шифров для GUI: параметры, вызовы и разбор «как это работает».

Чтобы добавить в приложение новый шифр, достаточно дописать одну запись в METHODS:
виджеты параметров строятся по описанию автоматически.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Sequence

from helpers.alphabet import detect
from helpers.keyword import key_numbers, read_order
from helpers.text import group
from lab1 import caesar, columnar, fence, grille, playfair, vigenere

Values = Dict[str, Any]


@dataclass
class Param:
    """Один настраиваемый параметр шифра."""

    key: str
    label: str
    kind: str                      # int | text | choice | grille
    default: Any = ""
    choices: Sequence[Any] = ()
    limits: tuple = (0, 99)
    hint: str = ""


@dataclass
class Method:
    """Шифр: параметры, прямое и обратное преобразование, разбор."""

    title: str
    params: List[Param]
    encrypt: Callable[[str, Values], str]
    decrypt: Callable[[str, Values], str]
    explain: Callable[[str, Values], str] = field(default=lambda text, values: "")


# --------------------------------------------------------------------------
# Разбор: показывает промежуточное представление, а не только результат
# --------------------------------------------------------------------------

def _explain_fence(text: str, values: Values) -> str:
    key = values["key"]
    rows = fence.row_pattern(len(text), key)
    lines = ["Зигзаг по %d строкам (шифротекст читается построчно):" % key, ""]
    for row in range(key):
        lines.append("".join(ch if r == row else "·" for ch, r in zip(text, rows)))
    return "\n".join(lines)


def _table_rows(text: str, width: int) -> List[str]:
    return [text[i:i + width] for i in range(0, len(text), width)]


def _explain_column(text: str, values: Values) -> str:
    keyword = values["keyword"]
    numbers = key_numbers(keyword)
    lines = ["Ключ %s -> номера столбцов %s" % (keyword, " ".join(map(str, numbers))),
             "", "Таблица (текст записан построчно, читается по столбцам):", "",
             " ".join(f"{n:>2}" for n in numbers)]
    lines += [" ".join(f"{ch:>2}" for ch in row) for row in _table_rows(text, len(numbers))]

    order = read_order(keyword)
    columns = ["".join(text[i] for i in range(c, len(text), len(numbers))) for c in range(len(numbers))]
    lines += ["", "Порядок чтения: " + " | ".join(columns[c] for c in order)]

    if values.get("keyword2"):
        first = columnar.encrypt(text, keyword)
        lines += ["", "Второй проход, ключ %s -> %s" % (
            values["keyword2"], " ".join(map(str, key_numbers(values["keyword2"])))),
            "Вход второго прохода: " + group(first)]
    return "\n".join(lines)


def _explain_grille(text: str, values: Values) -> str:
    holes, size = grille.parse_key(values["holes"])
    orbits = grille.orbit_map(size)
    lines = ["Разметка орбит поворота (одинаковые номера — одна орбита):", ""]
    for row in range(size):
        lines.append(" ".join(str(orbits[(row, col)] + 1) for col in range(size)))

    order = grille.fill_order(holes, size)
    lines += ["", "Порядок заполнения по четырём поворотам:"]
    for step in range(4):
        cells = order[step * len(holes):(step + 1) * len(holes)]
        lines.append("  %3d°: %s" % (step * 90,
                                     " ".join(f"({i // size},{i % size})" for i in cells)))

    cipher = grille.encrypt(text, holes, size)
    lines += ["", "Заполненная матрица (читается построчно):", ""]
    for start in range(0, len(cipher), size * size):
        block = cipher[start:start + size * size]
        lines += [" ".join(block[r * size:(r + 1) * size]) for r in range(size)] + [""]
    return "\n".join(lines)


def _explain_caesar(text: str, values: Values) -> str:
    alphabet = detect(text)
    n, k1, k2 = len(alphabet), values["mul"], values["key"]
    shifted = "".join(alphabet[(i * k1 + k2) % n] for i in range(n))
    return "\n".join([
        f"Алфавит из {n} букв, E(i) = (i * {k1} + {k2}) mod {n}",
        "", "исходный:  " + " ".join(alphabet), "заменяется:" + " " + " ".join(shifted),
    ])


def _explain_playfair(text: str, values: Values) -> str:
    keyword = values["keyword"]
    alphabet = detect(text, keyword)
    pairs = playfair.digraphs(text.replace("J", "I"), alphabet)
    cipher = playfair.encrypt(text, keyword)
    return "\n".join([
        f"Шифрующая таблица для ключа {keyword}:", "",
        playfair.render(keyword, alphabet), "",
        "Биграммы: " + " ".join(pairs),
        "Результат: " + " ".join(cipher[i:i + 2] for i in range(0, len(cipher), 2)),
    ])


def _explain_vigenere(text: str, values: Values) -> str:
    stream = vigenere.keystream(text, values["keyword"], values["scheme"])
    return "\n".join([
        f"Схема ключа: {values['scheme']}", "",
        "текст: " + " ".join(text),
        "ключ:  " + " ".join(stream),
        "шифр:  " + " ".join(vigenere.encrypt(text, values["keyword"], values["scheme"])),
    ])


# --------------------------------------------------------------------------
# Реестр шифров
# --------------------------------------------------------------------------

METHODS: Dict[str, Method] = {
    "Железнодорожная изгородь": Method(
        title="Перестановка: текст пишется зигзагом по K строкам",
        params=[Param("key", "Высота изгороди K", "int", 4, limits=(2, 40))],
        encrypt=lambda text, v: fence.encrypt(text, v["key"]),
        decrypt=lambda text, v: fence.decrypt(text, v["key"]),
        explain=_explain_fence,
    ),
    "Столбцовый метод": Method(
        title="Перестановка: чтение по столбцам в порядке, заданном ключевым словом",
        params=[
            Param("keyword", "Ключевое слово", "text", "КРИПТОГРАФИЯ"),
            Param("keyword2", "Второй ключ (двойная перестановка)", "text", "",
                  hint="пусто — одинарная перестановка"),
        ],
        encrypt=lambda text, v: (columnar.encrypt_double(text, v["keyword"], v["keyword2"])
                                 if v["keyword2"] else columnar.encrypt(text, v["keyword"])),
        decrypt=lambda text, v: (columnar.decrypt_double(text, v["keyword"], v["keyword2"])
                                 if v["keyword2"] else columnar.decrypt(text, v["keyword"])),
        explain=_explain_column,
    ),
    "Поворачивающаяся решётка": Method(
        title="Перестановка: запись через отверстия решётки с поворотом на 90°",
        params=[
            Param("size", "Размер решётки", "choice", 4, choices=(4, 6, 8)),
            Param("holes", "Отверстия (по одному на орбиту)", "grille", "0,7,10,13"),
        ],
        encrypt=lambda text, v: grille.encrypt(text, *grille.parse_key(v["holes"])),
        decrypt=lambda text, v: grille.decrypt(text, *grille.parse_key(v["holes"])),
        explain=_explain_grille,
    ),
    "Шифр Цезаря / аффинный": Method(
        title="Подстановка: E(i) = (i · k1 + k2) mod n, при k1 = 1 — шифр Цезаря",
        params=[
            Param("key", "Сдвиг k2", "int", 3, limits=(0, 40)),
            Param("mul", "Множитель k1", "int", 1, limits=(1, 40),
                  hint="должен быть взаимно прост с мощностью алфавита"),
        ],
        encrypt=lambda text, v: caesar.encrypt(text, v["key"], v["mul"]),
        decrypt=lambda text, v: caesar.decrypt(text, v["key"], v["mul"]),
        explain=_explain_caesar,
    ),
    "Шифр Плейфейра": Method(
        title="Подстановка: биграммы заменяются по шифрующей таблице",
        params=[Param("keyword", "Ключевое слово таблицы", "text", "CRYPTOGRAPHY",
                      hint="ключ и текст — в одном алфавите")],
        encrypt=lambda text, v: playfair.encrypt(text, v["keyword"]),
        decrypt=lambda text, v: playfair.decrypt(text, v["keyword"]),
        explain=_explain_playfair,
    ),
    "Шифр Виженера": Method(
        title="Подстановка: каждая позиция шифруется своим сдвигом из ключа",
        params=[
            Param("keyword", "Ключевое слово", "text", "MODE",
                  hint="ключ и текст — в одном алфавите"),
            Param("scheme", "Схема ключа", "choice", "direct", choices=vigenere.MODES),
        ],
        encrypt=lambda text, v: vigenere.encrypt(text, v["keyword"], v["scheme"]),
        decrypt=lambda text, v: vigenere.decrypt(text, v["keyword"], v["scheme"]),
        explain=_explain_vigenere,
    ),
}
