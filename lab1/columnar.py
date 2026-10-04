"""Columnar transposition and its double variant.

The text is written into a table row by row and read column by column
in the order given by the keyword.
"""

from typing import List

from helpers.keyword import read_order


def _columns(text: str, width: int) -> List[str]:
    """Table columns: column c holds every width-th symbol starting at c."""
    return ["".join(text[i] for i in range(c, len(text), width)) for c in range(width)]


def encrypt(text: str, keyword: str) -> str:
    order = read_order(keyword)
    columns = _columns(text, len(order))
    return "".join(columns[c] for c in order)


def decrypt(cipher: str, keyword: str) -> str:
    order = read_order(keyword)
    width = len(order)
    full, tail = divmod(len(cipher), width)

    # Column length: the first `tail` columns of the table are one symbol longer
    lengths = [full + (1 if c < tail else 0) for c in range(width)]

    columns = [""] * width
    pos = 0
    for c in order:                       # columns are cut out in reading order
        columns[c] = cipher[pos:pos + lengths[c]]
        pos += lengths[c]

    rows = max(lengths) if lengths else 0
    return "".join(columns[c][r] for r in range(rows)
                   for c in range(width) if r < lengths[c])


def encrypt_double(text: str, keyword1: str, keyword2: str) -> str:
    """Double transposition: encrypt with the first key, then with the second."""
    return encrypt(encrypt(text, keyword1), keyword2)


def decrypt_double(cipher: str, keyword1: str, keyword2: str) -> str:
    return decrypt(decrypt(cipher, keyword2), keyword1)
