"""Minimal PNG and BMP reader/writer on the standard library (zlib + struct).

Supported: PNG 8 bit per channel, gray / gray+alpha / RGB / RGBA / palette,
non-interlaced; BMP 24 and 32 bit uncompressed. Images are kept as a flat
bytearray of samples, row by row, `channels` samples per pixel. Steganography
needs lossless storage, so there is no JPEG: its compression destroys the LSBs.
"""

import struct
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
COLOR_TYPES = {1: 0, 2: 4, 3: 2, 4: 6}


@dataclass
class Image:
    width: int
    height: int
    channels: int                     # 1 gray, 2 gray+alpha, 3 RGB, 4 RGBA
    data: bytearray = field(repr=False)

    def __post_init__(self) -> None:
        if len(self.data) != self.width * self.height * self.channels:
            raise ValueError("The pixel data does not match the image size")

    @property
    def color_channels(self) -> int:
        """Channels that carry colour; alpha is never modified."""
        return 3 if self.channels >= 3 else 1

    def copy(self) -> "Image":
        return Image(self.width, self.height, self.channels, bytearray(self.data))

    def sample_indices(self) -> List[int]:
        """Indices of colour samples in data, in pixel order, alpha skipped."""
        step, colors = self.channels, self.color_channels
        return [i + c for i in range(0, len(self.data), step) for c in range(colors)]

    def to_rgb(self) -> bytes:
        """Packed RGB for display and the PPM preview."""
        out = bytearray()
        step = self.channels
        for i in range(0, len(self.data), step):
            if self.channels >= 3:
                out += self.data[i:i + 3]
            else:
                out += bytes((self.data[i],)) * 3
        return bytes(out)


# ---------------------------------------------------------------------- PNG
def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def _unfilter(raw: bytes, width: int, height: int, bpp: int) -> bytearray:
    stride = width * bpp
    out = bytearray(stride * height)
    previous = bytearray(stride)
    pos = 0
    for y in range(height):
        kind = raw[pos]
        line = bytearray(raw[pos + 1:pos + 1 + stride])
        pos += 1 + stride
        if kind == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 0xFF
        elif kind == 2:
            for x in range(stride):
                line[x] = (line[x] + previous[x]) & 0xFF
        elif kind == 3:
            for x in range(stride):
                left = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + ((left + previous[x]) >> 1)) & 0xFF
        elif kind == 4:
            for x in range(stride):
                left = line[x - bpp] if x >= bpp else 0
                up_left = previous[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + _paeth(left, previous[x], up_left)) & 0xFF
        elif kind != 0:
            raise ValueError(f"Unknown PNG filter type {kind}")
        out[y * stride:(y + 1) * stride] = line
        previous = line
    return out


def read_png(blob: bytes) -> Image:
    if not blob.startswith(PNG_SIGNATURE):
        raise ValueError("Not a PNG file")
    pos, idat, palette, header = 8, bytearray(), b"", None
    while pos < len(blob):
        length, kind = struct.unpack(">I4s", blob[pos:pos + 8])
        chunk = blob[pos + 8:pos + 8 + length]
        pos += 12 + length
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", chunk)
        elif kind == b"PLTE":
            palette = chunk
        elif kind == b"IDAT":
            idat += chunk
        elif kind == b"IEND":
            break
    if header is None:
        raise ValueError("PNG without IHDR")
    width, height, depth, color_type, _, _, interlace = header
    if depth != 8 or color_type not in PNG_CHANNELS:
        raise ValueError(f"Only 8-bit PNG is supported (got depth {depth}, "
                         f"colour type {color_type})")
    if interlace:
        raise ValueError("Interlaced PNG is not supported")
    channels = PNG_CHANNELS[color_type]
    data = _unfilter(zlib.decompress(bytes(idat)), width, height, channels)
    if color_type == 3:                             # palette -> RGB
        rgb = bytearray()
        for index in data:
            rgb += palette[3 * index:3 * index + 3]
        return Image(width, height, 3, rgb)
    return Image(width, height, channels, data)


def _chunk(kind: bytes, body: bytes) -> bytes:
    return (struct.pack(">I", len(body)) + kind + body
            + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF))


def write_png(image: Image) -> bytes:
    stride = image.width * image.channels
    raw = b"".join(b"\x00" + bytes(image.data[y * stride:(y + 1) * stride])
                   for y in range(image.height))
    header = struct.pack(">IIBBBBB", image.width, image.height, 8,
                         COLOR_TYPES[image.channels], 0, 0, 0)
    return (PNG_SIGNATURE + _chunk(b"IHDR", header)
            + _chunk(b"IDAT", zlib.compress(raw, 9)) + _chunk(b"IEND", b""))


# ---------------------------------------------------------------------- BMP
def read_bmp(blob: bytes) -> Image:
    if blob[:2] != b"BM":
        raise ValueError("Not a BMP file")
    offset = struct.unpack("<I", blob[10:14])[0]
    width, height, _, bpp, compression = struct.unpack("<iiHHI", blob[18:34])
    if bpp not in (24, 32) or compression not in (0, 3):
        raise ValueError(f"Only uncompressed 24/32-bit BMP is supported (got {bpp} bit)")
    step = bpp // 8
    stride = (width * step + 3) & ~3
    rows = range(abs(height) - 1, -1, -1) if height > 0 else range(abs(height))
    data = bytearray()
    for y in rows:
        line = blob[offset + y * stride:offset + y * stride + width * step]
        for x in range(0, width * step, step):
            data += bytes((line[x + 2], line[x + 1], line[x]))   # BGR -> RGB
    return Image(width, abs(height), 3, data)


def write_bmp(image: Image) -> bytes:
    rgb = image.to_rgb()
    stride = (image.width * 3 + 3) & ~3
    pixels = bytearray()
    for y in range(image.height - 1, -1, -1):
        line = rgb[y * image.width * 3:(y + 1) * image.width * 3]
        for x in range(0, len(line), 3):
            pixels += bytes((line[x + 2], line[x + 1], line[x]))
        pixels += b"\x00" * (stride - image.width * 3)
    header = struct.pack("<2sIHHI", b"BM", 54 + len(pixels), 0, 0, 54)
    info = struct.pack("<IiiHHIIiiII", 40, image.width, image.height, 1, 24, 0,
                       len(pixels), 2835, 2835, 0, 0)
    return header + info + bytes(pixels)


# ---------------------------------------------------------------------- files
def load(path: Union[str, Path]) -> Image:
    blob = Path(path).read_bytes()
    if blob.startswith(PNG_SIGNATURE):
        return read_png(blob)
    if blob[:2] == b"BM":
        return read_bmp(blob)
    raise ValueError(f"{path}: only PNG and BMP are supported (lossless formats)")


def save(image: Image, path: Union[str, Path]) -> None:
    path = Path(path)
    if path.suffix.lower() == ".bmp":
        if image.channels not in (1, 3):
            raise ValueError("BMP output keeps only RGB: save as PNG to keep alpha")
        path.write_bytes(write_bmp(image))
    else:
        path.write_bytes(write_png(image))


def to_ppm(image: Image) -> bytes:
    """PPM for tkinter.PhotoImage, which reads it on any Tk version."""
    return b"P6 %d %d 255\n" % (image.width, image.height) + image.to_rgb()
