"""Cipher descriptions for the GUI: parameters, calls and the "how it works" view.

To add a cipher to the application, add one entry to METHODS and its strings to
gui/i18n.py: the parameter widgets are built from the description automatically.
Names, titles, labels and hints are looked up in i18n by key:
method.<id>.name, method.<id>.title, param.<id>.<key>[.hint].
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Sequence

from helpers.alphabet import detect
from helpers.keyword import key_numbers, read_order
from gui.i18n import t
from helpers.text import group
from lab1 import caesar, columnar, fence, grille, playfair, vigenere

Values = Dict[str, Any]


@dataclass
class Param:
    """One configurable cipher parameter."""

    key: str
    kind: str                      # int | text | choice | grille
    default: Any = ""
    choices: Sequence[Any] = ()
    limits: tuple = (0, 99)
    hint: bool = False             # whether i18n has a param.<id>.<key>.hint string


@dataclass
class Method:
    """A cipher: parameters, forward and inverse transforms, explanation."""

    params: List[Param]
    encrypt: Callable[[str, Values], str]
    decrypt: Callable[[str, Values], str]
    explain: Callable[[str, Values], str] = field(default=lambda text, values: "")


# --------------------------------------------------------------------------
# Explanations: show the intermediate representation, not just the result
# --------------------------------------------------------------------------

def _explain_fence(text: str, values: Values) -> str:
    key = values["key"]
    rows = fence.row_pattern(len(text), key)
    lines = [t("explain.fence.header", rows=key), ""]
    for row in range(key):
        lines.append("".join(ch if r == row else "·" for ch, r in zip(text, rows)))
    return "\n".join(lines)


def _table_rows(text: str, width: int) -> List[str]:
    return [text[i:i + width] for i in range(0, len(text), width)]


def _explain_column(text: str, values: Values) -> str:
    keyword = values["keyword"]
    numbers = key_numbers(keyword)
    lines = [t("explain.column.key", keyword=keyword, numbers=" ".join(map(str, numbers))),
             "", t("explain.column.table"), "",
             " ".join(f"{n:>2}" for n in numbers)]
    lines += [" ".join(f"{ch:>2}" for ch in row) for row in _table_rows(text, len(numbers))]

    order = read_order(keyword)
    columns = ["".join(text[i] for i in range(c, len(text), len(numbers))) for c in range(len(numbers))]
    lines += ["", t("explain.column.order") + " | ".join(columns[c] for c in order)]

    if values.get("keyword2"):
        first = columnar.encrypt(text, keyword)
        lines += ["", t("explain.column.second", keyword=values["keyword2"],
                        numbers=" ".join(map(str, key_numbers(values["keyword2"])))),
                  t("explain.column.second_input") + group(first)]
    return "\n".join(lines)


def _explain_grille(text: str, values: Values) -> str:
    holes, size = grille.parse_key(values["holes"])
    orbits = grille.orbit_map(size)
    lines = [t("explain.grille.orbits"), ""]
    for row in range(size):
        lines.append(" ".join(str(orbits[(row, col)] + 1) for col in range(size)))

    order = grille.fill_order(holes, size)
    lines += ["", t("explain.grille.order")]
    for step in range(4):
        cells = order[step * len(holes):(step + 1) * len(holes)]
        lines.append("  %3d°: %s" % (step * 90,
                                     " ".join(f"({i // size},{i % size})" for i in cells)))

    cipher = grille.encrypt(text, holes, size)
    lines += ["", t("explain.grille.matrix"), ""]
    for start in range(0, len(cipher), size * size):
        block = cipher[start:start + size * size]
        lines += [" ".join(block[r * size:(r + 1) * size]) for r in range(size)] + [""]
    return "\n".join(lines)


def _explain_caesar(text: str, values: Values) -> str:
    alphabet = detect(text)
    n, k1, k2 = len(alphabet), values["mul"], values["key"]
    shifted = "".join(alphabet[(i * k1 + k2) % n] for i in range(n))
    return "\n".join([
        t("explain.caesar.header", n=n, k1=k1, k2=k2),
        "", t("explain.caesar.source") + " ".join(alphabet),
        t("explain.caesar.mapped") + " ".join(shifted),
    ])


def _explain_playfair(text: str, values: Values) -> str:
    keyword = values["keyword"]
    alphabet = detect(text, keyword)
    pairs = playfair.digraphs(text.replace("J", "I"), alphabet)
    cipher = playfair.encrypt(text, keyword)
    return "\n".join([
        t("explain.playfair.table", keyword=keyword), "",
        playfair.render(keyword, alphabet), "",
        t("explain.playfair.digraphs") + " ".join(pairs),
        t("explain.playfair.result") + " ".join(cipher[i:i + 2] for i in range(0, len(cipher), 2)),
    ])


def _explain_vigenere(text: str, values: Values) -> str:
    stream = vigenere.keystream(text, values["keyword"], values["scheme"])
    return "\n".join([
        t("explain.vigenere.scheme", scheme=values["scheme"]), "",
        t("explain.vigenere.text") + " ".join(text),
        t("explain.vigenere.key") + " ".join(stream),
        t("explain.vigenere.cipher") + " ".join(vigenere.encrypt(text, values["keyword"], values["scheme"])),
    ])


# --------------------------------------------------------------------------
# Cipher registry
# --------------------------------------------------------------------------

METHODS: Dict[str, Method] = {
    "fence": Method(
        params=[Param("key", "int", 4, limits=(2, 40))],
        encrypt=lambda text, v: fence.encrypt(text, v["key"]),
        decrypt=lambda text, v: fence.decrypt(text, v["key"]),
        explain=_explain_fence,
    ),
    "column": Method(
        params=[
            Param("keyword", "text", "КРИПТОГРАФИЯ"),
            Param("keyword2", "text", "", hint=True),
        ],
        encrypt=lambda text, v: (columnar.encrypt_double(text, v["keyword"], v["keyword2"])
                                 if v["keyword2"] else columnar.encrypt(text, v["keyword"])),
        decrypt=lambda text, v: (columnar.decrypt_double(text, v["keyword"], v["keyword2"])
                                 if v["keyword2"] else columnar.decrypt(text, v["keyword"])),
        explain=_explain_column,
    ),
    "grille": Method(
        params=[
            Param("size", "choice", 4, choices=(4, 6, 8)),
            Param("holes", "grille", "0,7,10,13"),
        ],
        encrypt=lambda text, v: grille.encrypt(text, *grille.parse_key(v["holes"])),
        decrypt=lambda text, v: grille.decrypt(text, *grille.parse_key(v["holes"])),
        explain=_explain_grille,
    ),
    "caesar": Method(
        params=[
            Param("key", "int", 3, limits=(0, 40)),
            Param("mul", "int", 1, limits=(1, 40), hint=True),
        ],
        encrypt=lambda text, v: caesar.encrypt(text, v["key"], v["mul"]),
        decrypt=lambda text, v: caesar.decrypt(text, v["key"], v["mul"]),
        explain=_explain_caesar,
    ),
    "playfair": Method(
        params=[Param("keyword", "text", "CRYPTOGRAPHY", hint=True)],
        encrypt=lambda text, v: playfair.encrypt(text, v["keyword"]),
        decrypt=lambda text, v: playfair.decrypt(text, v["keyword"]),
        explain=_explain_playfair,
    ),
    "vigenere": Method(
        params=[
            Param("keyword", "text", "MODE", hint=True),
            Param("scheme", "choice", "direct", choices=vigenere.MODES),
        ],
        encrypt=lambda text, v: vigenere.encrypt(text, v["keyword"], v["scheme"]),
        decrypt=lambda text, v: vigenere.decrypt(text, v["keyword"], v["scheme"]),
        explain=_explain_vigenere,
    ),
}
