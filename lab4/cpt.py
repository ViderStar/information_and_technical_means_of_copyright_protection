"""CPT method (Chen, Pan, Tseng; section 7.4.4) for binary images and its
modification with the distance matrix (section 7.4.5).

A binary image is split into m x n blocks F; every block hides r <= log2(mn + 1)
bits b1..br and changes at most two of its bits. The secret key is a random
binary matrix K and a weight matrix W with values 1..2^r - 1, each of them used
at least once. Extraction:  b1..br = SUM((F xor K) * W) mod 2^r.

Matrices are lists of rows of ints; indices in traces are 1-based as in the manual.
"""

import math
import random
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

from lab4.bits import bits_to_int, format_bits, int_to_bits
from lab4.imageio import Image

Matrix = List[List[int]]
Cell = Tuple[int, int]


class Key(NamedTuple):
    k: Matrix
    w: Matrix
    r: int


class BlockTrace(NamedTuple):
    bits: List[int]
    xor: Matrix                     # F xor K
    total: int                      # SUM((F xor K) * W) before mod
    sets: Dict[int, List[Cell]]     # S_w, w = 1..2^r - 1
    d: int
    h: Optional[int]                # chosen h (None when d = 0)
    flipped: List[Cell]             # changed cells (1-based)
    result: Matrix                  # F'


def parse_matrix(text: str) -> Matrix:
    """'1100/0100/1110/0010' or '1 2 3 4; 5 6 7 1' -> matrix."""
    rows = [row.replace(",", " ").strip()
            for row in text.replace(";", "/").replace("\n", "/").split("/")]
    try:
        matrix = [[int(x) for x in (row.split() if " " in row else row)]
                  for row in rows if row]
    except ValueError:
        raise ValueError(f"Not a matrix of integers: {text!r}") from None
    if not matrix or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("Matrix rows must have equal length")
    return matrix


def format_matrix(matrix: Matrix) -> str:
    return "/".join("".join(map(str, row)) if max(map(max, matrix)) < 10
                    else " ".join(map(str, row)) for row in matrix)


def max_r(m: int, n: int) -> int:
    """r <= floor(log2(mn + 1))."""
    return int(math.log2(m * n + 1))


def check_key(key: Key) -> None:
    m, n = len(key.k), len(key.k[0])
    if (len(key.w), len(key.w[0])) != (m, n):
        raise ValueError("K and W must have the same size")
    if not 1 <= key.r <= max_r(m, n):
        raise ValueError(f"r must be 1..{max_r(m, n)} for a {m}x{n} block")
    if any(v not in (0, 1) for row in key.k for v in row):
        raise ValueError("K must be a binary matrix")
    if {v for row in key.w for v in row} != set(range(1, 1 << key.r)):
        raise ValueError(f"W must contain every value 1..{(1 << key.r) - 1} and nothing else")


def generate_key(m: int, n: int, r: int, seed: str) -> Key:
    """Random K and W from a stego key string (both parties derive the same)."""
    if not 1 <= r <= max_r(m, n):
        raise ValueError(f"r must be 1..{max_r(m, n)} for a {m}x{n} block")
    rng = random.Random(seed)
    k = [[rng.randrange(2) for _ in range(n)] for _ in range(m)]
    values = list(range(1, 1 << r))
    values += [rng.choice(values) for _ in range(m * n - len(values))]
    rng.shuffle(values)
    w = [values[i * n:(i + 1) * n] for i in range(m)]
    return Key(k, w, r)


def weight_matrix_count(m: int, n: int, r: int) -> int:
    """Number of m x n matrices over {1..2^r-1} that contain every value
    (surjections, by inclusion-exclusion)."""
    q = (1 << r) - 1
    return sum((-1) ** j * math.comb(q, j) * (q - j) ** (m * n) for j in range(q + 1))


def _xor(f: Matrix, k: Matrix) -> Matrix:
    return [[a ^ b for a, b in zip(fr, kr)] for fr, kr in zip(f, k)]


def weighted_sum(f: Matrix, key: Key) -> int:
    return sum(x * w for xr, wr in zip(_xor(f, key.k), key.w) for x, w in zip(xr, wr))


def change_sets(xor: Matrix, key: Key) -> Dict[int, List[Cell]]:
    """S_w: cells whose flip changes the sum by +w (mod 2^r).
    A cell with [F xor K] = 0 adds W, a cell with 1 subtracts W = adds 2^r - W."""
    size = 1 << key.r
    sets: Dict[int, List[Cell]] = {w: [] for w in range(1, size)}
    for j, (xr, wr) in enumerate(zip(xor, key.w)):
        for k, (x, w) in enumerate(zip(xr, wr)):
            delta = w if x == 0 else (size - w) % size
            if delta:
                sets[delta].append((j, k))
    return sets


DIST_CAP = 8      # farther than this from a colour border: all equally bad


def distance(image: Matrix, y: int, x: int, cap: int = DIST_CAP) -> float:
    """Euclidean distance from (y, x) to the nearest bit of the other colour,
    searched ring by ring; inf when there is none within cap."""
    h, w, colour = len(image), len(image[0]), image[y][x]
    best = math.inf
    for rho in range(1, cap + 1):
        for dy in range(-rho, rho + 1):
            row = y + dy
            if not 0 <= row < h:
                continue
            step = 1 if abs(dy) == rho else 2 * rho
            for dx in range(-rho, rho + 1, step):
                col = x + dx
                if 0 <= col < w and image[row][col] != colour:
                    best = min(best, math.hypot(dy, dx))
        if best <= rho + 1:          # every unchecked cell is at least rho + 1 away
            break
    return best


def distance_matrix(image: Matrix, cap: int = DIST_CAP) -> List[List[float]]:
    """dist(F) of section 7.4.5 for the whole image."""
    return [[distance(image, y, x, cap) for x in range(len(image[0]))]
            for y in range(len(image))]


def embed_block(block: Matrix, bits: Sequence[int], key: Key,
                rng: Optional[random.Random] = None,
                dist: Optional[List[List[float]]] = None) -> BlockTrace:
    """Steps 1-4 of the manual. Among the admissible h the variants with the
    fewest changed bits are kept (one flip when d itself is in a non-empty S_d,
    as in the manual's example), the rest is a random choice. With dist (the
    modified method) the cells nearest to a colour border are preferred, so the
    change lands on an edge where it is least visible."""
    rng = rng or random.Random()
    size = 1 << key.r
    xor = _xor(block, key.k)
    total = sum(x * w for xr, wr in zip(xor, key.w) for x, w in zip(xr, wr))
    sets = change_sets(xor, key)
    d = (bits_to_int(bits) - total) % size
    result = [row[:] for row in block]
    if d == 0:
        return BlockTrace(list(bits), xor, total, sets, d, None, [], result)

    def members(value: int) -> List[Cell]:
        value %= size
        return [] if value == 0 else sets[value]

    def cost(cells: Tuple[Cell, ...]) -> float:
        return sum(dist[j][k] for j, k in cells) if dist else 0.0

    # h with S_hd and S_-(h-1)d non-empty; S_0 counts as non-empty (no change)
    plans: List[Tuple[int, Tuple[Cell, ...]]] = []
    for h in range(size):
        first, second = (h * d) % size, (-(h - 1) * d) % size
        a_cells = members(first) if first else [None]
        b_cells = members(second) if second else [None]
        for a in a_cells:
            for b in b_cells:
                if a is not None and a == b:
                    continue
                plans.append((h, tuple(c for c in (a, b) if c is not None)))
    if not plans:                          # impossible when W holds every 1..2^r-1
        raise ValueError("No h found: W does not contain every value 1..2^r-1")
    fewest = min(len(cells) for _, cells in plans)
    plans = [p for p in plans if len(p[1]) == fewest]
    if dist:
        best = min(cost(cells) for _, cells in plans)
        plans = [p for p in plans if cost(p[1]) == best]
    h, flipped = rng.choice(plans)
    for j, k in flipped:
        result[j][k] ^= 1
    return BlockTrace(list(bits), xor, total, sets, d, h,
                      [(j + 1, k + 1) for j, k in flipped], result)


def extract_block(block: Matrix, key: Key) -> List[int]:
    return int_to_bits(weighted_sum(block, key) % (1 << key.r), key.r)


# ---------------------------------------------------------------------- images
def split(image: Matrix, m: int, n: int) -> List[Tuple[int, int]]:
    """Top-left corners of the whole m x n blocks, row by row."""
    return [(y, x) for y in range(0, len(image) - m + 1, m)
            for x in range(0, len(image[0]) - n + 1, n)]


def _cut(image: Matrix, y: int, x: int, m: int, n: int) -> Matrix:
    return [row[x:x + n] for row in image[y:y + m]]


def embed_bits(image: Matrix, bits: Sequence[int], key: Key, seed: str = "",
               modified: bool = False) -> Tuple[Matrix, List[BlockTrace]]:
    m, n = len(key.k), len(key.k[0])
    corners = split(image, m, n)
    chunks = [list(bits[i:i + key.r]) for i in range(0, len(bits), key.r)]
    if len(chunks) > len(corners):
        raise ValueError(f"{len(bits)} bits need {len(chunks)} blocks of {m}x{n}, "
                         f"the image has {len(corners)}")
    out = [row[:] for row in image]
    rng = random.Random(seed)
    traces = []
    for (y, x), chunk in zip(corners, chunks):
        chunk += [0] * (key.r - len(chunk))
        local = ([[distance(out, y + j, x + k) for k in range(n)] for j in range(m)]
                 if modified else None)
        trace = embed_block(_cut(out, y, x, m, n), chunk, key, rng, local)
        for j in range(m):
            out[y + j][x:x + n] = trace.result[j]
        traces.append(trace)
    return out, traces


def extract_bits(image: Matrix, key: Key, count: Optional[int] = None) -> List[int]:
    m, n = len(key.k), len(key.k[0])
    bits: List[int] = []
    for y, x in split(image, m, n):
        bits += extract_block(_cut(image, y, x, m, n), key)
        if count is not None and len(bits) >= count:
            return bits[:count]
    return bits


LENGTH_BITS_CPT = 16          # binary images are small: 16-bit byte count


def capacity(image: Matrix, key: Key) -> int:
    blocks = len(split(image, len(key.k), len(key.k[0])))
    return max(0, (blocks * key.r - LENGTH_BITS_CPT) // 8)


def embed(image: Matrix, message: str, key: Key, seed: str = "",
          modified: bool = False) -> Tuple[Matrix, List[BlockTrace]]:
    check_key(key)
    data = message.encode("utf-8")
    if len(data) >= 1 << LENGTH_BITS_CPT:
        raise ValueError("The message is too long")
    bits = int_to_bits(len(data), LENGTH_BITS_CPT) + [
        (byte >> (7 - i)) & 1 for byte in data for i in range(8)]
    if len(bits) > len(split(image, len(key.k), len(key.k[0]))) * key.r:
        raise ValueError(f"The message does not fit: at most {capacity(image, key)} bytes")
    return embed_bits(image, bits, key, seed, modified)


def extract(image: Matrix, key: Key) -> str:
    check_key(key)
    head = extract_bits(image, key, LENGTH_BITS_CPT)
    size = bits_to_int(head)
    bits = extract_bits(image, key, LENGTH_BITS_CPT + 8 * size)
    if len(bits) < LENGTH_BITS_CPT + 8 * size:
        raise ValueError("The length field points past the image: wrong key "
                         "or no hidden message")
    body = bits[LENGTH_BITS_CPT:]
    try:
        return bytes(bits_to_int(body[i:i + 8]) for i in range(0, len(body), 8)).decode()
    except UnicodeDecodeError:
        raise ValueError("The extracted bytes are not UTF-8 text: wrong key "
                         "or no hidden message") from None


def from_image(image: Image, threshold: int = 128) -> Matrix:
    """Binary matrix, 1 = black (dark pixel), as in the manual."""
    step = image.channels
    values = [image.data[i] if image.channels < 3 else
              (image.data[i] * 299 + image.data[i + 1] * 587 + image.data[i + 2] * 114) // 1000
              for i in range(0, len(image.data), step)]
    return [[1 if values[y * image.width + x] < threshold else 0
             for x in range(image.width)] for y in range(image.height)]


def to_image(matrix: Matrix) -> Image:
    data = bytearray(0 if v else 255 for row in matrix for v in row)
    return Image(len(matrix[0]), len(matrix), 1, data)


def bit_changes(a: Matrix, b: Matrix) -> int:
    return sum(x != y for ra, rb in zip(a, b) for x, y in zip(ra, rb))


__all__ = ["Key", "BlockTrace", "parse_matrix", "format_matrix", "format_bits",
           "generate_key", "embed_block", "extract_block", "embed", "extract",
           "distance", "distance_matrix", "from_image", "to_image", "capacity", "max_r"]
