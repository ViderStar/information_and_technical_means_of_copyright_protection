"""BPCS steganography (section 7.4.2): Bit-Plane Complexity Segmentation.

Every colour channel is split into bit planes, every plane into 8x8 blocks.
A block is noise-like when its border complexity alpha >= alpha0; such blocks
are replaced by 8x8 blocks of the message. A message block that is too simple
(alpha < alpha0) is conjugated with a checkerboard: alpha(S*) = 1 - alpha(S).

Conjugation map. The manual stores the map as the last message block, but that
block can itself be simple and need conjugation. Here the map is distributed:
bit (0, 0) of every embedded block is its conjugation flag, the other 63 bits
carry the message. The checkerboard BC (black, i.e. 1, at the top-left corner)
flips bit (0, 0), so the flag of a conjugated block is 1 and of a plain one 0.

Blocks are 64-bit integers, bit 63 = (0, 0), row-major; alpha is computed with
two XOR-shifts and a popcount.
"""

from typing import Iterator, List, NamedTuple, Tuple

from lab4.bits import LENGTH_BITS, bits_to_int, int_to_bits, payload, read_payload
from lab4.imageio import Image

SIDE = 8
SIZE = SIDE * SIDE
MAX_BORDER = 2 * SIDE * (SIDE - 1)          # 112: max black-white border of 8x8
DATA_BITS = SIZE - 1                        # 63 message bits per block + 1 flag
FLAG = 1 << (SIZE - 1)                      # bit (0, 0)

_ROW_MASK = sum(0x7F << (SIDE * r) for r in range(SIDE))   # pairs (x, x+1) in a row
_COL_MASK = (1 << (SIDE * (SIDE - 1))) - 1                 # pairs (y, y+1)
BC = sum(1 << (SIZE - 1 - (r * SIDE + c))
         for r in range(SIDE) for c in range(SIDE) if (r + c) % 2 == 0)
WC = BC ^ ((1 << SIZE) - 1)


def popcount(x: int) -> int:
    return bin(x).count("1")


def border(block: int) -> int:
    """k: number of black-white transitions between horizontal and vertical neighbours."""
    return popcount((block ^ (block >> 1)) & _ROW_MASK) + popcount((block ^ (block >> SIDE)) & _COL_MASK)


def alpha(block: int) -> float:
    """Border complexity alpha = k / max(B-W) = k / (2 * 2^n * (2^n - 1))."""
    return border(block) / MAX_BORDER


def regions(block: int) -> int:
    """m: number of 4-connected one-colour regions."""
    cells = [block >> (SIZE - 1 - i) & 1 for i in range(SIZE)]
    seen = [False] * SIZE
    count = 0
    for start in range(SIZE):
        if seen[start]:
            continue
        count += 1
        stack = [start]
        seen[start] = True
        while stack:
            i = stack.pop()
            r, c = divmod(i, SIDE)
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                j = nr * SIDE + nc
                if 0 <= nr < SIDE and 0 <= nc < SIDE and not seen[j] and cells[j] == cells[i]:
                    seen[j] = True
                    stack.append(j)
    return count


def beta(block: int) -> float:
    """Region complexity beta = m / (2^n * 2^n)."""
    return regions(block) / SIZE


def conjugate(block: int) -> int:
    """P* = P xor BC; (P*)* = P and alpha(P*) = 1 - alpha(P)."""
    return block ^ BC


def from_rows(rows: List[str]) -> int:
    """['01010101', ...] (8 rows of 8 bits, 1 = black) -> block."""
    return bits_to_int(int(ch) for row in rows for ch in row)


def to_rows(block: int) -> List[str]:
    return ["".join(str(b) for b in int_to_bits(block, SIZE)[r * SIDE:(r + 1) * SIDE])
            for r in range(SIDE)]


# ---------------------------------------------------------------------- image
class Place(NamedTuple):
    plane: int
    channel: int
    y: int          # top-left pixel of the block
    x: int


def _places(image: Image, planes: int) -> Iterator[Place]:
    """Block order: lowest plane first, then channel, then rows of blocks."""
    for plane in range(planes):
        for channel in range(image.color_channels):
            for y in range(0, image.height - SIDE + 1, SIDE):
                for x in range(0, image.width - SIDE + 1, SIDE):
                    yield Place(plane, channel, y, x)


def read_block(image: Image, place: Place) -> int:
    block, step, width = 0, image.channels, image.width
    for r in range(SIDE):
        base = ((place.y + r) * width + place.x) * step + place.channel
        for c in range(SIDE):
            block = block << 1 | (image.data[base + c * step] >> place.plane & 1)
    return block


def write_block(image: Image, place: Place, block: int) -> None:
    step, width, bit = image.channels, image.width, 1 << place.plane
    for r in range(SIDE):
        base = ((place.y + r) * width + place.x) * step + place.channel
        for c in range(SIDE):
            i = base + c * step
            if block >> (SIZE - 1 - (r * SIDE + c)) & 1:
                image.data[i] |= bit
            else:
                image.data[i] &= ~bit & 0xFF


def _check(alpha0: float, planes: int) -> None:
    if not 0 < alpha0 <= 0.5:
        raise ValueError("alpha0 must be in (0, 0.5]: otherwise a conjugated block "
                         "can still be simple")
    if not 1 <= planes <= 8:
        raise ValueError("The number of bit planes must be 1..8")


def noisy_places(image: Image, alpha0: float, planes: int) -> Iterator[Place]:
    threshold = alpha0 * MAX_BORDER
    for place in _places(image, planes):
        if border(read_block(image, place)) >= threshold:
            yield place


class Stats(NamedTuple):
    blocks: int             # all 8x8 blocks in the used planes
    noisy: int              # blocks with alpha >= alpha0
    used: int               # blocks replaced by the message
    conjugated: int         # message blocks stored as S*


def capacity(image: Image, alpha0: float = 0.3, planes: int = 4) -> Tuple[int, int]:
    """(noise-like blocks, message bytes that fit after the length field)."""
    _check(alpha0, planes)
    noisy = sum(1 for _ in noisy_places(image, alpha0, planes))
    return noisy, max(0, (noisy * DATA_BITS - LENGTH_BITS) // 8)


def message_blocks(message: str, alpha0: float) -> List[Tuple[int, bool]]:
    """Message -> 8x8 blocks with the flag bit, conjugated when simple."""
    bits = payload(message)
    blocks = []
    for i in range(0, len(bits), DATA_BITS):
        chunk = bits[i:i + DATA_BITS]
        block = bits_to_int(chunk + [0] * (DATA_BITS - len(chunk)))      # flag = 0
        if alpha(block) < alpha0:
            blocks.append((conjugate(block), True))
        else:
            blocks.append((block, False))
    return blocks


def embed(image: Image, message: str, alpha0: float = 0.3,
          planes: int = 4) -> Tuple[Image, Stats]:
    _check(alpha0, planes)
    blocks = message_blocks(message, alpha0)
    stego = image.copy()
    places = noisy_places(image, alpha0, planes)
    for used, (block, _) in enumerate(blocks):
        place = next(places, None)
        if place is None:
            noisy, room = capacity(image, alpha0, planes)
            raise ValueError(f"The message needs {len(blocks)} noise-like blocks, the image "
                             f"has {noisy}: at most {room} bytes fit")
        write_block(stego, place, block)
    total = image.color_channels * planes * (image.height // SIDE) * (image.width // SIDE)
    noisy = sum(1 for _ in noisy_places(image, alpha0, planes))
    return stego, Stats(total, noisy, len(blocks), sum(c for _, c in blocks))


def extract(image: Image, alpha0: float = 0.3, planes: int = 4) -> str:
    _check(alpha0, planes)

    def stream() -> Iterator[int]:
        for place in noisy_places(image, alpha0, planes):
            block = read_block(image, place)
            if block & FLAG:
                block = conjugate(block)
            yield from int_to_bits(block & (FLAG - 1), DATA_BITS)

    return read_payload(stream())
