"""Message <-> bit sequence conversions shared by all lab 4 methods.

A payload is the message in UTF-8 preceded by its length, so the receiver knows
where the hidden data ends:  [length: LENGTH_BITS bits][UTF-8 bytes].
"""

from typing import Iterable, List

LENGTH_BITS = 32


def int_to_bits(value: int, width: int) -> List[int]:
    if not 0 <= value < 1 << width:
        raise ValueError(f"{value} does not fit into {width} bits")
    return [(value >> (width - 1 - i)) & 1 for i in range(width)]


def bits_to_int(bits: Iterable[int]) -> int:
    value = 0
    for bit in bits:
        value = value << 1 | bit
    return value


def bytes_to_bits(data: bytes) -> List[int]:
    return [(byte >> (7 - i)) & 1 for byte in data for i in range(8)]


def bits_to_bytes(bits: List[int]) -> bytes:
    if len(bits) % 8:
        raise ValueError("The bit count is not a multiple of 8")
    return bytes(bits_to_int(bits[i:i + 8]) for i in range(0, len(bits), 8))


def parse_bits(text: str) -> List[int]:
    """'0100 0001' -> [0, 1, 0, 0, 0, 0, 0, 1]."""
    bits = [int(ch) for ch in text if ch in "01"]
    if any(ch not in "01 \t\n_," for ch in text):
        raise ValueError("A bit string may contain only 0 and 1")
    return bits


def format_bits(bits: Iterable[int]) -> str:
    return "".join(map(str, bits))


def payload(message: str, length_bits: int = LENGTH_BITS) -> List[int]:
    data = message.encode("utf-8")
    return int_to_bits(len(data), length_bits) + bytes_to_bits(data)


def read_payload(bits: Iterable[int], length_bits: int = LENGTH_BITS) -> str:
    """Decode a payload from a bit stream; extra trailing bits are ignored."""
    stream = iter(bits)
    head = [next(stream, None) for _ in range(length_bits)]
    if None in head:
        raise ValueError("The container is too small to hold even the length field")
    size = bits_to_int(head)
    body = []
    for _ in range(size * 8):
        bit = next(stream, None)
        if bit is None:
            raise ValueError(f"Length field = {size} bytes, more than the container holds: "
                             "wrong key or no hidden message")
        body.append(bit)
    try:
        return bits_to_bytes(body).decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("The extracted bytes are not UTF-8 text: wrong key or "
                         "no hidden message") from None
