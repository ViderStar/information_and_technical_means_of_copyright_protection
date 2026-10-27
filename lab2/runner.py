"""Lab 2: RSA demo on the example from the lab manual and on larger keys."""

import logging
import random
from typing import List

from configs.cfg import RSA_E, RSA_P, RSA_Q
from helpers.numtheory import EuclidStep, ExpStep, fast_exp
from lab2 import rsa

logger = logging.getLogger(__name__)

DEMO_TEXT = "CAT"
DEMO_RUSSIAN = "Защита авторских прав"
DEMO_UNICODE = "Это лабораторная работа по КиОКИ, 2026!"

# Expected values from the lab manual (section 2.1)
EXPECTED_D = 3
EXPECTED_CIPHER = [16, 29, 21]


def euclid_table(steps: List[EuclidStep]) -> List[str]:
    """Rows of the EUCLIDEX trace: the two initial rows, then one row per iteration."""
    lines = [f"{'step':>4} {'q':>6} {'d':>8} {'x':>8} {'y':>8}"]
    for i, step in enumerate(steps):
        q = "" if i < 2 else str(step.q)
        lines.append(f"{i:>4} {q:>6} {step.d:>8} {step.x:>8} {step.y:>8}")
    return lines


def exp_table(a: int, z: int, n: int) -> List[str]:
    steps: List[ExpStep] = []
    fast_exp(a, z, n, steps)
    lines = [f"fast_exp({a}, {z}, {n}):", f"{'z1':>6} {'a1':>8} {'x':>8}"]
    lines += [f"{s.z:>6} {s.a:>8} {s.x:>8}" for s in steps]
    return lines


def short(blocks: List[int], limit: int = 90) -> str:
    """Space-separated blocks; long lists of big numbers keep only the first and last."""
    text = " ".join(map(str, blocks))
    if len(text) <= limit:
        return text
    return (f"{len(blocks)} blocks\n  first: {blocks[0]}\n"
            f"  last:  {blocks[-1]}")


def _keys(p: int, q: int, e: int) -> rsa.Keys:
    trace: List[EuclidStep] = []
    keys = rsa.make_keys(p, q, e, trace)
    logger.info("p = %d, q = %d, r = p*q = %d, phi(r) = %d, e = %d",
                p, q, keys.r, keys.phi, e)
    logger.info("Extended Euclid for a = phi(r) = %d, b = e = %d:\n%s",
                keys.phi, e, "\n".join(euclid_table(trace)))
    logger.info("d = %d (check: e*d mod phi(r) = %d)", keys.d, e * keys.d % keys.phi)
    logger.info("Ko = (%d, %d), Kc = (%d, %d)\n", e, keys.r, keys.d, keys.r)
    return keys


def _round_trip(title: str, text: str, keys: rsa.Keys, codec: str) -> List[int]:
    blocks = rsa.encode(text, codec)
    cipher = rsa.encrypt(blocks, keys.e, keys.r)
    plain = rsa.decrypt(cipher, keys.d, keys.r)
    restored = rsa.decode(plain, codec)
    logger.info("--- %s (codec %s) ---", title, codec)
    logger.info("M = %s", text)
    logger.info("m = %s", short(blocks))
    logger.info("c = %s", short(cipher))
    logger.info("D = %s", restored)
    expected = rsa.decode(blocks, codec)
    logger.info("%s\n", "decryption is correct" if restored == expected
                else "DECRYPTION ERROR")
    return cipher


def _manual_example() -> None:
    logger.info("=== Example from the lab manual ===\n")
    keys = _keys(RSA_P, RSA_Q, RSA_E)
    if (RSA_P, RSA_Q, RSA_E) == (3, 11, 7):
        logger.info("d %s\n", "matches the lab manual" if keys.d == EXPECTED_D
                    else f"MISMATCH, expected {EXPECTED_D}")

    cipher = _round_trip("Encryption of CAT", DEMO_TEXT, keys, "letters")
    if (RSA_P, RSA_Q, RSA_E) == (3, 11, 7):
        logger.info("Ciphertext %s\n", "matches the lab manual" if cipher == EXPECTED_CIPHER
                    else f"MISMATCH, expected {EXPECTED_CIPHER}")
    logger.info("%s\n", "\n".join(exp_table(4, keys.e, keys.r)))


def _larger_keys() -> None:
    logger.info("=== Russian text: the modulus must exceed every letter code ===\n")
    keys = _keys(61, 53, 17)
    _round_trip("Russian letters", DEMO_RUSSIAN, keys, "letters")

    logger.info("=== Any symbols: 128-bit p and q, e = 65537 ===\n")
    keys = rsa.generate(128, rng=random.Random(2026))     # fixed seed: reproducible report
    logger.info("p = %d\nq = %d\nr = %d\nd = %d\n", keys.p, keys.q, keys.r, keys.d)
    _round_trip("Unicode text", DEMO_UNICODE, keys, "unicode")


def _errors() -> None:
    logger.info("=== Invalid parameters are rejected ===\n")
    for p, q, e in ((3, 11, 5), (4, 11, 7), (3, 11, 25)):
        try:
            rsa.make_keys(p, q, e)
        except ValueError as error:
            logger.info("p = %d, q = %d, e = %d: %s", p, q, e, error)
    try:
        rsa.encrypt_text("ЯБЛОКО", 7, 33)
    except ValueError as error:
        logger.info("Text ЯБЛОКО with r = 33:\n  %s\n", error)


def _self_check() -> None:
    rng = random.Random(1)
    for _ in range(2000):
        a, z, n = rng.randrange(10 ** 30), rng.randrange(10 ** 6), rng.randrange(2, 10 ** 30)
        assert fast_exp(a, z, n) == pow(a, z, n)
    for _ in range(50):
        keys = rsa.generate(rng.randrange(10, 96), rng=rng)
        blocks = [rng.randrange(keys.r) for _ in range(20)]
        assert rsa.decrypt(rsa.encrypt(blocks, keys.e, keys.r), keys.d, keys.r) == blocks
    logger.info("Self-check: fast_exp equals pow() on 2000 random triples;\n"
                "50 random key pairs decrypt 20 random blocks each: OK\n")


def run_lab2() -> None:
    logger.info("=== Lab 2: RSA cryptosystem ===\n")
    _manual_example()
    _larger_keys()
    _errors()
    _self_check()
