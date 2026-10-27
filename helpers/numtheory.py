"""Number theory for the public-key labs: fast exponentiation, extended Euclid, primes.

The functions follow the pseudocode of the lab manual and can return a trace of
their steps, so the GUI, the demo and the report show the same intermediate values.
"""

import random
from typing import List, NamedTuple, Optional, Tuple

# Small primes: trial division before Miller-Rabin and fixed witnesses
_SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)


class EuclidStep(NamedTuple):
    """One iteration of EUCLIDEX: quotient and the new (d, x, y) triple."""

    q: int
    d: int
    x: int
    y: int


class ExpStep(NamedTuple):
    """One multiplication of fast_exp: the exponent left, current base and result."""

    z: int
    a: int
    x: int


def euclid_ex(a: int, b: int, trace: Optional[List[EuclidStep]] = None) -> Tuple[int, int, int]:
    """Extended Euclid from the manual: returns (x, y, g) with x*a + y*b = g = gcd(a, b).

    The loop stops at d1 = 1 (or 0), so for coprime a and b the last row already
    holds the inverse: y*b mod a = 1.
    """
    d0, d1 = a, b
    x0, x1 = 1, 0
    y0, y1 = 0, 1
    if trace is not None:
        trace += [EuclidStep(0, d0, x0, y0), EuclidStep(0, d1, x1, y1)]
    while d1 > 1:
        q, d2 = divmod(d0, d1)
        x2, y2 = x0 - q * x1, y0 - q * y1
        d0, d1, x0, x1, y0, y1 = d1, d2, x1, x2, y1, y2
        if trace is not None:
            trace.append(EuclidStep(q, d1, x1, y1))
    if d1 == 0:                      # b divides a: gcd is the previous remainder
        return x0, y0, d0
    return x1, y1, d1


def inverse(value: int, modulus: int, trace: Optional[List[EuclidStep]] = None) -> int:
    """Multiplicative inverse of value modulo modulus via euclid_ex."""
    _, y, g = euclid_ex(modulus, value % modulus, trace)
    if g != 1:
        raise ValueError(f"{value} is not invertible modulo {modulus}: gcd = {g}")
    return y % modulus               # a negative y1 is corrected by adding the modulus


def fast_exp(a: int, z: int, n: int, trace: Optional[List[ExpStep]] = None) -> int:
    """a^z mod n by repeated squaring, exactly as fast_exp in the manual."""
    if z < 0:
        raise ValueError("The exponent must be non-negative")
    a1, z1, x = a % n, z, 1 % n
    while z1 != 0:
        while z1 % 2 == 0:
            z1 //= 2
            a1 = a1 * a1 % n
        z1 -= 1
        x = x * a1 % n
        if trace is not None:
            trace.append(ExpStep(z1, a1, x))
    return x


def is_prime(n: int, rounds: int = 32) -> bool:
    """Miller-Rabin; deterministic below 3.3e24 thanks to the fixed witnesses."""
    if n < 2:
        return False
    for p in _SMALL_PRIMES:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1

    witnesses = list(_SMALL_PRIMES)
    if n.bit_length() > 81:
        witnesses += [random.randrange(2, n - 1) for _ in range(rounds)]
    for a in witnesses:
        x = fast_exp(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def random_prime(bits: int, rng: random.Random) -> int:
    """Random prime of exactly `bits` bits (the two top bits are set, so p*q has 2*bits)."""
    if bits < 3:
        raise ValueError("A prime needs at least 3 bits")
    while True:
        candidate = rng.getrandbits(bits) | (0b11 << (bits - 2)) | 1
        if is_prime(candidate):
            return candidate
