"""Rail fence cipher.

The text is written in a zigzag over K rows; the ciphertext is read row by row.
"""

from typing import List


def row_pattern(length: int, key: int) -> List[int]:
    """Row number for each text position: 0,1,..,K-1,K-2,..,1,0,1,..."""
    if key < 2:
        return [0] * length
    period = 2 * key - 2
    return [p if p < key else period - p for p in (i % period for i in range(length))]


def encrypt(text: str, key: int) -> str:
    rows = row_pattern(len(text), key)
    return "".join(ch for row in range(key)
                   for ch, r in zip(text, rows) if r == row)


def decrypt(cipher: str, key: int) -> str:
    rows = row_pattern(len(cipher), key)
    out = [""] * len(cipher)
    symbols = iter(cipher)
    for row in range(key):
        for i, r in enumerate(rows):
            if r == row:
                out[i] = next(symbols)
    return "".join(out)
