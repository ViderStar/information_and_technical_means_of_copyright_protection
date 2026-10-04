"""Lab 1: demo of all methods on the examples from the lab manual."""

import logging

from configs.cfg import (CAESAR_KEY, COLUMN_KEY, COLUMN_KEY2, FENCE_KEY,
                         GRILLE_KEY, PLAYFAIR_KEY, VIGENERE_KEY)
from helpers.alphabet import detect
from helpers.keyword import key_numbers
from helpers.text import group, normalize
from lab1 import caesar, columnar, fence, grille, playfair, vigenere

logger = logging.getLogger(__name__)

DEMO_TEXT = "Это лабораторная работа по КиОКИ"
DEMO_GRILLE_TEXT = "ШИФРОТЕКСТ"
DEMO_PLAYFAIR_TEXT = "CIPHERTEXT"
DEMO_VIGENERE_TEXT = "Cryptography"

# Expected ciphertexts from the lab manual
EXPECTED = {
    "Rail fence": "ЭОНОИТБРРАБТКООААОЯААОКЛТРПИ",
    "Columnar transposition": "ААОООЯКООЭНИББЛРИТАОРТААТПРК",
    "Double transposition": "КИРЯРПЭОАИТОАОТКОЛТОБАОБААНР",
    "Turning grille": "ШВСОТТГИАЕФДЕРКБ",
    "Playfair cipher (variant 2)": "PDHIMGRKZP",
    "Vigenere cipher, direct key": "OFBTFCJVMDKC",
    "Vigenere cipher, progressive key": "OFBTGDKWOFME",
    "Vigenere cipher, autokey": "OFBTVFEGTDNP",
}


def _report(title: str, key: str, plain: str, cipher: str, restored: str) -> None:
    logger.info("--- %s (%s) ---", title, key)
    logger.info("M = %s", group(plain))
    logger.info("C = %s", group(cipher))
    logger.info("D = %s", group(restored))

    marks = ["decryption is correct" if restored.startswith(plain)
             else "DECRYPTION ERROR"]
    if title in EXPECTED:
        marks.append("matches the lab manual" if cipher == EXPECTED[title]
                     else f"MISMATCH, expected {EXPECTED[title]}")
    logger.info("%s\n", "; ".join(marks))


def _permutations() -> None:
    logger.info("=== Transposition methods ===\n")
    plain = normalize(DEMO_TEXT)

    cipher = fence.encrypt(plain, FENCE_KEY)
    _report("Rail fence", f"K = {FENCE_KEY}",
            plain, cipher, fence.decrypt(cipher, FENCE_KEY))

    logger.info("Key %s -> %s", COLUMN_KEY, " ".join(map(str, key_numbers(COLUMN_KEY))))
    cipher = columnar.encrypt(plain, COLUMN_KEY)
    _report("Columnar transposition", f"K = {COLUMN_KEY}",
            plain, cipher, columnar.decrypt(cipher, COLUMN_KEY))

    logger.info("Key %s -> %s", COLUMN_KEY2, " ".join(map(str, key_numbers(COLUMN_KEY2))))
    cipher = columnar.encrypt_double(plain, COLUMN_KEY, COLUMN_KEY2)
    _report("Double transposition", f"K1 = {COLUMN_KEY}, K2 = {COLUMN_KEY2}",
            plain, cipher, columnar.decrypt_double(cipher, COLUMN_KEY, COLUMN_KEY2))

    holes, size = grille.parse_key(GRILLE_KEY)
    plain = normalize(DEMO_GRILLE_TEXT)
    cipher = grille.encrypt(plain, holes, size)
    _report("Turning grille", f"{size}x{size}, holes {GRILLE_KEY}",
            plain, cipher, grille.decrypt(cipher, holes, size))


def _substitutions() -> None:
    logger.info("=== Substitution methods ===\n")

    plain = normalize(DEMO_TEXT)
    cipher = caesar.encrypt(plain, CAESAR_KEY)
    _report("Caesar cipher (variant 1)", f"k = {CAESAR_KEY}",
            plain, cipher, caesar.decrypt(cipher, CAESAR_KEY))

    plain = normalize(DEMO_VIGENERE_TEXT)
    cipher = caesar.encrypt(plain, 5, mul=3)
    _report("Affine transformation", "k1 = 3, k2 = 5",
            plain, cipher, caesar.decrypt(cipher, 5, mul=3))

    plain = normalize(DEMO_PLAYFAIR_TEXT)
    logger.info("Cipher table for key %s:\n%s",
                PLAYFAIR_KEY, playfair.render(PLAYFAIR_KEY, detect(plain)))
    cipher = playfair.encrypt(plain, PLAYFAIR_KEY)
    _report("Playfair cipher (variant 2)", f"K = {PLAYFAIR_KEY}",
            plain, cipher, playfair.decrypt(cipher, PLAYFAIR_KEY))

    plain = normalize(DEMO_VIGENERE_TEXT)
    for mode, title in (("direct", "direct key"),
                        ("progressive", "progressive key"),
                        ("autokey", "autokey")):
        cipher = vigenere.encrypt(plain, VIGENERE_KEY, mode)
        _report(f"Vigenere cipher, {title}", f"K = {VIGENERE_KEY}",
                plain, cipher, vigenere.decrypt(cipher, VIGENERE_KEY, mode))


def run_lab1() -> None:
    logger.info("=== Lab 1: transposition and substitution ciphers ===\n")
    _permutations()
    _substitutions()
