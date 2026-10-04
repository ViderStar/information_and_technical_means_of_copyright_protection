"""Turning grille cipher (Cardano grille).

An n x n grille with n*n/4 holes: the text is written through the holes,
then the grille is turned by 90 degrees, four times in total.
The ciphertext is read from the resulting matrix row by row.
"""

from typing import Dict, List, Tuple

from configs.cfg import FILLERS
from helpers.alphabet import ENGLISH, RUSSIAN, detect

Cell = Tuple[int, int]


def rotate(cell: Cell, n: int) -> Cell:
    """Rotate a cell by 90 degrees clockwise."""
    row, col = cell
    return col, n - 1 - row


def orbit_map(n: int) -> Dict[Cell, int]:
    """Matrix layout: cells that coincide under rotation share one number."""
    orbits: Dict[Cell, int] = {}
    for row in range(n):
        for col in range(n):
            if (row, col) in orbits:
                continue
            cell, number = (row, col), len(set(orbits.values()))
            for _ in range(4):
                orbits[cell] = number
                cell = rotate(cell, n)
    return orbits


def parse_key(spec: str) -> Tuple[List[Cell], int]:
    """Key '0,7,10,13' -> holes [(0,0),(1,3),(2,2),(3,1)] and size n."""
    indexes = [int(part) for part in spec.replace(";", ",").split(",") if part.strip()]
    n = int(round((4 * len(indexes)) ** 0.5))
    if n % 2 or n * n != 4 * len(indexes):
        raise ValueError("The number of holes must equal n*n/4 for an even n")

    holes = [(i // n, i % n) for i in indexes]
    if any(not 0 <= i < n * n for i in indexes):
        raise ValueError("A hole lies outside the grille")

    orbits = orbit_map(n)
    if len({orbits[cell] for cell in holes}) != len(holes):
        raise ValueError("Holes overlap when the grille is turned")
    return holes, n


def fill_order(holes: List[Cell], n: int) -> List[int]:
    """Matrix positions in filling order: 4 turns, row by row within each."""
    order: List[int] = []
    current = list(holes)
    for _ in range(4):
        order.extend(row * n + col for row, col in sorted(current))
        current = [rotate(cell, n) for cell in current]
    return order


def encrypt(text: str, holes: List[Cell], n: int) -> str:
    order = fill_order(holes, n)
    block = n * n
    # fillers come from the same alphabet as the text
    fillers = FILLERS if detect(text) is RUSSIAN else ENGLISH
    cipher = []
    for start in range(0, len(text), block):
        chunk = text[start:start + block]
        chunk += "".join(fillers[i % len(fillers)] for i in range(block - len(chunk)))
        grid = [""] * block
        for position, symbol in zip(order, chunk):
            grid[position] = symbol
        cipher.append("".join(grid))
    return "".join(cipher)


def decrypt(cipher: str, holes: List[Cell], n: int) -> str:
    order = fill_order(holes, n)
    block = n * n
    if len(cipher) % block:
        raise ValueError(f"Ciphertext length must be a multiple of {block}")
    return "".join(cipher[start + position]
                   for start in range(0, len(cipher), block)
                   for position in order)
