"""RSA digital signature (variant 1 of lab 3).

Signing:       m = h(M),   S = m^d mod r        with the secret key  Kc = (d, r)
Verification:  m = S^e mod r,   m' = h(M'),   the signature is valid if m = m'

The hash is computed modulo r, the RSA modulus, so every hash value is a valid
RSA block (in the manual's example the two moduli coincide: n = r = 323).
"""

from typing import List, NamedTuple, Optional

from helpers.numtheory import fast_exp
from lab3.hashing import HashStep, quad_hash


class Verdict(NamedTuple):
    computed: int         # m' = h(M') from the received message
    recovered: int        # m = S^e mod r from the signature
    valid: bool


def sign(text: str, d: int, r: int, h0: int,
         trace: Optional[List[HashStep]] = None) -> int:
    return fast_exp(quad_hash(text, r, h0, trace), d, r)


def verify(text: str, signature: int, e: int, r: int, h0: int,
           trace: Optional[List[HashStep]] = None) -> Verdict:
    if not 0 <= signature < r:
        raise ValueError(f"The signature must be in 0..r-1 = 0..{r - 1}")
    computed = quad_hash(text, r, h0, trace)
    recovered = fast_exp(signature, e, r)
    return Verdict(computed, recovered, computed == recovered)
