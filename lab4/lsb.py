"""LSB method (section 7.4.1): message bits replace the least significant bits
of the colour samples (R, G, B or gray), `depth` lowest bits per sample.

Without a key the samples are used in order. With a stego key the order is a
key-driven pseudo-random permutation, so the hidden bits are scattered over the
whole image and cannot be read without the key.
"""

import math
import random
from typing import Iterator, List, Optional, Sequence

from lab4.bits import LENGTH_BITS, payload, read_payload
from lab4.imageio import Image


def embed_bits(samples: Sequence[int], bits: Sequence[int], depth: int = 1) -> List[int]:
    """Low-level step from the manual: write bits into the LSBs of a byte sequence."""
    out = list(samples)
    mask = (1 << depth) - 1
    for i in range(0, len(bits), depth):
        chunk = list(bits[i:i + depth]) + [0] * (depth - len(bits[i:i + depth]))
        value = 0
        for bit in chunk:
            value = value << 1 | bit
        j = i // depth
        if j >= len(out):
            raise ValueError("Not enough bytes for the message")
        out[j] = out[j] & ~mask | value
    return out


def extract_bits(samples: Sequence[int], count: int, depth: int = 1) -> List[int]:
    bits: List[int] = []
    for value in samples:
        for shift in range(depth - 1, -1, -1):
            if len(bits) == count:
                return bits
            bits.append(value >> shift & 1)
    return bits


def _order(n: int, key: Optional[str]) -> Iterator[int]:
    """0..n-1 in order, or a key-driven permutation built lazily (Fisher-Yates
    with a sparse swap table): the first k positions do not depend on how many
    are requested, so embedding and extraction agree."""
    if not key:
        yield from range(n)
        return
    rng = random.Random(key)
    swapped = {}
    for i in range(n):
        j = rng.randrange(i, n)
        yield swapped.get(j, j)
        swapped[j] = swapped.get(i, i)


def _check_depth(depth: int) -> None:
    if not 1 <= depth <= 8:
        raise ValueError("The number of LSBs must be 1..8")


def capacity(image: Image, depth: int = 1) -> int:
    """Message bytes that fit after the 32-bit length field."""
    return max(0, (image.width * image.height * image.color_channels * depth
                   - LENGTH_BITS) // 8)


def embed(image: Image, message: str, depth: int = 1, key: Optional[str] = None) -> Image:
    _check_depth(depth)
    bits = payload(message)
    slots = image.width * image.height * image.color_channels
    need = math.ceil(len(bits) / depth)
    if need > slots:
        raise ValueError(f"The message needs {need} samples, the image has {slots}: "
                         f"at most {capacity(image, depth)} bytes fit with {depth} LSB")
    stego = image.copy()
    samples = image.sample_indices() if image.channels in (2, 4) else None
    mask = (1 << depth) - 1
    order = _order(slots, key)
    for i in range(need):
        chunk = bits[i * depth:(i + 1) * depth]
        value = 0
        for bit in chunk + [0] * (depth - len(chunk)):
            value = value << 1 | bit
        slot = next(order)
        index = samples[slot] if samples else slot
        stego.data[index] = stego.data[index] & ~mask | value
    return stego


def extract(image: Image, depth: int = 1, key: Optional[str] = None) -> str:
    _check_depth(depth)
    slots = image.width * image.height * image.color_channels
    samples = image.sample_indices() if image.channels in (2, 4) else None

    def stream() -> Iterator[int]:
        for slot in _order(slots, key):
            value = image.data[samples[slot] if samples else slot]
            for shift in range(depth - 1, -1, -1):
                yield value >> shift & 1

    return read_payload(stream())


def psnr(original: Image, changed: Image) -> float:
    """Peak signal-to-noise ratio over colour samples, dB (inf for equal images)."""
    if (original.width, original.height, original.channels) != \
            (changed.width, changed.height, changed.channels):
        raise ValueError("The images differ in size")
    indices = original.sample_indices()
    error = sum((original.data[i] - changed.data[i]) ** 2 for i in indices)
    if error == 0:
        return math.inf
    return 10 * math.log10(255 ** 2 * len(indices) / error)


def changed_samples(original: Image, changed: Image) -> int:
    return sum(a != b for a, b in zip(original.data, changed.data))


def bit_plane(image: Image, bit: int = 0, channel: int = 0) -> Image:
    """Black-and-white picture of one bit plane: what the LSB 'looks like'."""
    step = image.channels
    data = bytearray(255 if image.data[i + channel] >> bit & 1 else 0
                     for i in range(0, len(image.data), step))
    return Image(image.width, image.height, 1, data)


def difference(original: Image, changed: Image) -> Image:
    """White where any colour sample of the pixel changed."""
    step = original.channels
    data = bytearray(255 if original.data[i:i + step] != changed.data[i:i + step] else 0
                     for i in range(0, len(original.data), step))
    return Image(original.width, original.height, 1, data)
