"""Lab 3: RSA digital signature demo on the example from the lab manual and on larger keys."""

import itertools
import logging
import random
from typing import List, Optional

from configs.cfg import HASH_H0, SIGN_E, SIGN_P, SIGN_Q
from lab2 import rsa
from lab2.runner import euclid_table
from helpers.numtheory import EuclidStep
from lab3 import signature
from lab3.hashing import RUSSIAN, HashStep, quad_hash

logger = logging.getLogger(__name__)

DEMO_TEXT = "БГУИР"
DEMO_FORGED = "БРУИР"
DEMO_LONG = "Лебедевич Артем Владимирович, лабораторная работа 3, 2026"

# Expected values from the lab manual (sections 3.1 and 3.2.2)
EXPECTED = {"hash": 93, "d": 67, "signature": 206, "forged hash": 123}
MANUAL_PARAMS = (17, 19, 43, 100)


def hash_table(steps: List[HashStep], h0: int, n: int) -> List[str]:
    lines = [f"H0 = {h0}"]
    previous = h0
    for i, step in enumerate(steps, start=1):
        lines.append(f"H{i} = (H{i - 1} + m{i})^2 mod n = ({previous} + {step.m})^2 mod {n}"
                     f" = {step.h}    [{step.symbol}]")
        previous = step.h
    return lines


def _expect(name: str, value: int) -> str:
    if (SIGN_P, SIGN_Q, SIGN_E, HASH_H0) != MANUAL_PARAMS:
        return ""
    return ("; matches the lab manual" if value == EXPECTED[name]
            else f"; MISMATCH, expected {EXPECTED[name]}")


def _verify(title: str, text: str, s: int, keys: rsa.Keys, h0: int,
            expected: Optional[str] = None) -> signature.Verdict:
    steps: List[HashStep] = []
    verdict = signature.verify(text, s, keys.e, keys.r, h0, steps)
    logger.info("--- %s ---", title)
    logger.info("M' = %s\nS = %d", text, s)
    if len(steps) <= 8:
        logger.info("%s", "\n".join(hash_table(steps, h0, keys.r)))
    logger.info("m' = h(M') = %d\nm = S^e mod r = %d\nsignature is %s%s\n",
                verdict.computed, verdict.recovered,
                "VALID" if verdict.valid else "INVALID",
                _expect("forged hash", verdict.computed) if expected else "")
    return verdict


def _manual_example() -> rsa.Keys:
    logger.info("=== Example from the lab manual ===\n")
    trace: List[EuclidStep] = []
    keys = rsa.make_keys(SIGN_P, SIGN_Q, SIGN_E, trace)
    logger.info("p = %d, q = %d, r = %d, phi(r) = %d, e = %d",
                keys.p, keys.q, keys.r, keys.phi, keys.e)
    logger.info("Extended Euclid:\n%s", "\n".join(euclid_table(trace)))
    logger.info("d = %d%s", keys.d, _expect("d", keys.d))
    logger.info("Ko = (%d, %d), Kc = (%d, %d)\n", keys.e, keys.r, keys.d, keys.r)

    steps: List[HashStep] = []
    m = quad_hash(DEMO_TEXT, keys.r, HASH_H0, steps)
    logger.info("--- Hash of %s (n = r = %d) ---", DEMO_TEXT, keys.r)
    logger.info("%s", "\n".join(hash_table(steps, HASH_H0, keys.r)))
    logger.info("h(M) = %d%s\n", m, _expect("hash", m))

    s = signature.sign(DEMO_TEXT, keys.d, keys.r, HASH_H0)
    logger.info("S = m^d mod r = %d^%d mod %d = %d%s", m, keys.d, keys.r, s,
                _expect("signature", s))
    logger.info("Signed message: {%s, %d}\n", DEMO_TEXT, s)

    _verify("Genuine message", DEMO_TEXT, s, keys, HASH_H0)
    _verify("Message changed in transit", DEMO_FORGED, s, keys, HASH_H0, expected="forged hash")
    _verify("Signature changed in transit", DEMO_TEXT, (s + 1) % keys.r, keys, HASH_H0)
    return keys


def _collision(keys: rsa.Keys) -> None:
    """With a 323-value hash a forger only needs a message with the same hash."""
    logger.info("=== Weakness of a small modulus: hash collision ===\n")
    target = quad_hash(DEMO_TEXT, keys.r, HASH_H0)
    s = signature.sign(DEMO_TEXT, keys.d, keys.r, HASH_H0)
    tried = 0
    for letters in itertools.product(RUSSIAN, repeat=3):
        tried += 1
        word = "".join(letters)
        if quad_hash(word, keys.r, HASH_H0) == target:
            logger.info("h(%s) = h(%s) = %d, found after %d tries", word, DEMO_TEXT, target, tried)
            _verify("Forged message with the stolen signature", word, s, keys, HASH_H0)
            return
    logger.info("No three-letter collision found\n")


def _larger_keys() -> None:
    logger.info("=== 256-bit modulus, e = 65537 ===\n")
    keys = rsa.generate(128, rng=random.Random(2026))     # fixed seed: reproducible report
    logger.info("r = %d\nd = %d\n", keys.r, keys.d)
    s = signature.sign(DEMO_LONG, keys.d, keys.r, HASH_H0)
    _verify("Genuine message", DEMO_LONG, s, keys, HASH_H0)
    _verify("One digit changed", DEMO_LONG.replace("3", "4"), s, keys, HASH_H0)


def _self_check() -> None:
    rng = random.Random(3)
    alphabet = RUSSIAN + "ABCXYZ0123456789"
    detected = 0
    for _ in range(200):
        keys = rsa.generate(rng.randrange(16, 80), rng=rng)
        text = "".join(rng.choice(alphabet) for _ in range(rng.randrange(1, 40)))
        s = signature.sign(text, keys.d, keys.r, HASH_H0)
        assert signature.verify(text, s, keys.e, keys.r, HASH_H0).valid
        i = rng.randrange(len(text))
        changed = text[:i] + rng.choice(alphabet.replace(text[i], "")) + text[i + 1:]
        detected += not signature.verify(changed, s, keys.e, keys.r, HASH_H0).valid
    logger.info("Self-check: 200 random messages and keys, every signature verified;\n"
                "a one-symbol change detected in %d of 200 cases\n", detected)


def run_lab3() -> None:
    logger.info("=== Lab 3: RSA digital signature ===\n")
    keys = _manual_example()
    _collision(keys)
    _larger_keys()
    _self_check()
