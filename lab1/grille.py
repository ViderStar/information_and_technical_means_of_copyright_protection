"""Метод поворачивающейся решётки (решётка Кардано).

Решётка n x n с n*n/4 отверстиями: текст пишется в отверстия, после
заполнения решётка поворачивается на 90 градусов, и так четыре раза.
Шифротекст читается из полученной матрицы построчно.
"""

from typing import Dict, List, Tuple

from configs.cfg import FILLERS
from helpers.alphabet import ENGLISH, RUSSIAN, detect

Cell = Tuple[int, int]


def rotate(cell: Cell, n: int) -> Cell:
    """Поворот клетки на 90 градусов по часовой стрелке."""
    row, col = cell
    return col, n - 1 - row


def orbit_map(n: int) -> Dict[Cell, int]:
    """Разметка матрицы: клетки, совпадающие при поворотах, — один номер."""
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
    """Ключ '0,7,10,13' -> отверстия [(0,0),(1,3),(2,2),(3,1)] и размер n."""
    indexes = [int(part) for part in spec.replace(";", ",").split(",") if part.strip()]
    n = int(round((4 * len(indexes)) ** 0.5))
    if n % 2 or n * n != 4 * len(indexes):
        raise ValueError("Число отверстий должно равняться n*n/4 при чётном n")

    holes = [(i // n, i % n) for i in indexes]
    if any(not 0 <= i < n * n for i in indexes):
        raise ValueError("Отверстие выходит за пределы решётки")

    orbits = orbit_map(n)
    if len({orbits[cell] for cell in holes}) != len(holes):
        raise ValueError("Отверстия перекрываются при поворотах решётки")
    return holes, n


def fill_order(holes: List[Cell], n: int) -> List[int]:
    """Позиции матрицы в порядке заполнения: 4 поворота, внутри — построчно."""
    order: List[int] = []
    current = list(holes)
    for _ in range(4):
        order.extend(row * n + col for row, col in sorted(current))
        current = [rotate(cell, n) for cell in current]
    return order


def encrypt(text: str, holes: List[Cell], n: int) -> str:
    order = fill_order(holes, n)
    block = n * n
    # заполнители берутся из того же алфавита, что и текст
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
        raise ValueError(f"Длина шифротекста должна быть кратна {block}")
    return "".join(cipher[start + position]
                   for start in range(0, len(cipher), block)
                   for position in order)
