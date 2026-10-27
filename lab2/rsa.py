"""RSA cryptosystem (variant 1 of lab 2).

Keys:        r = p*q,  phi(r) = (p-1)(q-1),  e*d mod phi(r) = 1
Encryption:  c_i = m_i^e mod r      with the public key  Ko = (e, r)
Decryption:  m_i = c_i^d mod r      with the secret key  Kc = (d, r)
"""

import random
from dataclasses import dataclass
from math import gcd
from typing import List, Optional

from helpers.numtheory import EuclidStep, fast_exp, inverse, is_prime, random_prime

# Letter codes from the manual: A = 2, B = 3, ..., Z = 27 (0 and 1 are skipped
# because 0^e = 0 and 1^e = 1 would leave those letters unencrypted).
# Russian letters (33, with Ё) continue the table: А = 28, ..., Я = 60.
ENGLISH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
RUSSIAN = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
LETTERS = ENGLISH + RUSSIAN
LETTER_OFFSET = 2

CODECS = ("letters", "unicode")


@dataclass(frozen=True)
class Keys:
    """RSA key pair together with the values it was computed from."""

    p: int
    q: int
    e: int
    d: int

    @property
    def r(self) -> int:
        return self.p * self.q

    @property
    def phi(self) -> int:
        return (self.p - 1) * (self.q - 1)


def make_keys(p: int, q: int, e: int, trace: Optional[List[EuclidStep]] = None) -> Keys:
    """Compute the key pair for given p, q and e; d comes from the extended Euclid."""
    for name, value in (("p", p), ("q", q)):
        if not is_prime(value):
            raise ValueError(f"{name} = {value} is not prime")
    if p == q:
        raise ValueError("p and q must be different: with p = q, phi(r) is not (p-1)(q-1)")
    phi = (p - 1) * (q - 1)
    if not 1 < e < phi:
        raise ValueError(f"e must satisfy 1 < e < phi(r) = {phi}")
    if gcd(e, phi) != 1:
        raise ValueError(f"e = {e} and phi(r) = {phi} are not coprime: gcd = {gcd(e, phi)}")
    return Keys(p, q, e, inverse(e, phi, trace))


def generate(bits: int, e: int = 65537, rng: Optional[random.Random] = None) -> Keys:
    """Random key pair with a modulus of 2*bits bits (p and q of `bits` bits each)."""
    # p, q >= 3 * 2^(bits-2), so phi(r) > 2^(2*bits-1) and e < phi(r) is guaranteed
    if e.bit_length() >= 2 * bits - 1:
        raise ValueError(f"{bits}-bit primes are too small for e = {e}")
    rng = rng or random.SystemRandom()
    while True:
        p, q = random_prime(bits, rng), random_prime(bits, rng)
        if p != q and gcd(e, (p - 1) * (q - 1)) == 1:
            return make_keys(p, q, e)


def _check_blocks(blocks: List[int], r: int) -> None:
    for block in blocks:
        if not 0 <= block < r:
            raise ValueError(f"block {block} is outside 0..r-1 = 0..{r - 1}: "
                             "choose larger p and q")


def encrypt(blocks: List[int], e: int, r: int) -> List[int]:
    _check_blocks(blocks, r)
    return [fast_exp(m, e, r) for m in blocks]


def decrypt(blocks: List[int], d: int, r: int) -> List[int]:
    _check_blocks(blocks, r)
    return [fast_exp(c, d, r) for c in blocks]


def encode(text: str, codec: str = "letters") -> List[int]:
    """Text -> numbers: one block per symbol."""
    if codec == "unicode":
        return [ord(symbol) for symbol in text]
    letters = [ch for ch in text.upper() if ch.isalpha()]
    unknown = sorted(set(letters) - set(LETTERS))
    if unknown:
        raise ValueError(f"letters outside the code table: {' '.join(unknown)} "
                         "(use the unicode codec)")
    return [LETTERS.index(ch) + LETTER_OFFSET for ch in letters]


def decode(blocks: List[int], codec: str = "letters") -> str:
    if codec == "unicode":
        return "".join(chr(block) for block in blocks)
    top = len(LETTERS) + LETTER_OFFSET
    bad = [block for block in blocks if not LETTER_OFFSET <= block < top]
    if bad:
        raise ValueError(f"numbers outside the letter codes {LETTER_OFFSET}..{top - 1}: "
                         f"{' '.join(map(str, bad[:5]))} (wrong key or codec?)")
    return "".join(LETTERS[block - LETTER_OFFSET] for block in blocks)


def parse_blocks(text: str) -> List[int]:
    """'16 29, 21' -> [16, 29, 21]."""
    try:
        return [int(token) for token in text.replace(",", " ").split()]
    except ValueError:
        raise ValueError("The ciphertext must be a list of integers") from None


def encrypt_text(text: str, e: int, r: int, codec: str = "letters") -> str:
    return " ".join(map(str, encrypt(encode(text, codec), e, r)))


def decrypt_text(cipher: str, d: int, r: int, codec: str = "letters") -> str:
    return decode(decrypt(parse_blocks(cipher), d, r), codec)
