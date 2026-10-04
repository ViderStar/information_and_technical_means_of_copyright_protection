"""Playfair digraph cipher (variant 2).

The key is a cipher table: the keyword followed by the remaining alphabet letters.
English uses a 5x5 table (J is merged with I), Russian a 4x8 table (32 letters).
"""

from typing import Dict, List, Tuple

from helpers.alphabet import ENGLISH, RUSSIAN, detect

# Separator letters for repeated letters and odd-length padding
PADDING = {ENGLISH: "XQ", RUSSIAN: "ЪЫ"}


def _shape(size: int) -> Tuple[int, int]:
    """The table closest to a square: 25 -> 5x5, 32 -> 4x8."""
    for rows in range(int(size ** 0.5), 0, -1):
        if size % rows == 0:
            return rows, size // rows
    raise ValueError("Could not build the table")


def build_table(keyword: str, alphabet: str) -> Tuple[List[str], int, int]:
    """The table as a flat list of letters plus its dimensions."""
    if alphabet is ENGLISH:
        alphabet = alphabet.replace("J", "")       # I/J share one cell
        keyword = keyword.replace("J", "I")

    letters: List[str] = []
    for symbol in keyword + alphabet:
        if symbol in alphabet and symbol not in letters:
            letters.append(symbol)

    rows, columns = _shape(len(letters))
    return letters, rows, columns


def digraphs(text: str, alphabet: str) -> List[str]:
    """Split into digraphs: repeats are separated, odd length is padded."""
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
    """step = +1 encrypts, -1 decrypts."""
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
        if r1 == r2:                                   # same row: shift sideways
            c1, c2 = (c1 + step) % columns, (c2 + step) % columns
        elif c1 == c2:                                 # same column: shift down
            r1, r2 = (r1 + step) % rows, (r2 + step) % rows
        else:                                          # rectangle: swap the columns
            c1, c2 = c2, c1
        result.append(letters[r1 * columns + c1] + letters[r2 * columns + c2])
    return "".join(result)


def encrypt(text: str, keyword: str) -> str:
    return _swap(text, keyword, step=1)


def decrypt(cipher: str, keyword: str) -> str:
    return _swap(cipher, keyword, step=-1)


def render(keyword: str, alphabet: str) -> str:
    """The table as text rows, for the report and the demo."""
    letters, _, columns = build_table(keyword, alphabet)
    cells = ["I/J" if letter == "I" and alphabet is ENGLISH else letter
             for letter in letters]
    return "\n".join(" ".join(f"{c:<3}" for c in cells[i:i + columns])
                     for i in range(0, len(cells), columns))
