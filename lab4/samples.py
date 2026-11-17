"""Reproducible test containers: a photo-like colour image and a binary stamp.

The colour image imitates a scanned photograph: smooth shapes plus Gaussian
sensor noise, so its low bit planes are noise-like, as the manual recommends
for containers. Fixed seeds make the report figures reproducible.
"""

import math
import random

from lab4.imageio import Image


def photo(width: int = 256, height: int = 256, noise: float = 3.0, seed: int = 2026) -> Image:
    rng = random.Random(seed)
    data = bytearray()
    for y in range(height):
        for x in range(width):
            u, v = x / width, y / height
            sky = v < 0.55 + 0.08 * math.sin(6 * u)
            if sky:                                         # sky with a sun
                sun = math.exp(-((u - 0.72) ** 2 + (v - 0.22) ** 2) / 0.006)
                base = (90 + 120 * v + 140 * sun, 140 + 90 * v + 100 * sun, 230 - 40 * v)
            else:                                           # hills with stripes
                shade = 0.6 + 0.4 * math.sin(14 * u + 9 * v) * math.cos(5 * v)
                base = (60 + 70 * shade, 110 + 90 * shade, 40 + 30 * shade)
            for channel in base:
                value = channel + rng.gauss(0, noise)
                data.append(max(0, min(255, int(round(value)))))
    return Image(width, height, 3, data)


def stamp(width: int = 128, height: int = 96) -> Image:
    """Binary picture (black on white): a ring, a filled square, stripes, a cross."""
    data = bytearray()
    for y in range(height):
        for x in range(width):
            r = math.hypot(x - 32, y - 40)
            black = (18 <= r <= 26
                     or (70 <= x <= 100 and 15 <= y <= 45)
                     or (y >= 62 and (x + y) % 12 < 4 and x < 118)
                     or (abs(x - 32) <= 2 and 30 <= y <= 50)
                     or (abs(y - 40) <= 2 and 22 <= x <= 42))
            data.append(0 if black else 255)
    return Image(width, height, 1, data)
