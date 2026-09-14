"""ЛР1: демонстрация всех методов на примерах методички."""

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

# Ожидаемые шифротексты из методического пособия
EXPECTED = {
    "Железнодорожная изгородь": "ЭОНОИТБРРАБТКООААОЯААОКЛТРПИ",
    "Столбцовый метод": "ААОООЯКООЭНИББЛРИТАОРТААТПРК",
    "Двойная перестановка": "КИРЯРПЭОАИТОАОТКОЛТОБАОБААНР",
    "Поворачивающаяся решётка": "ШВСОТТГИАЕФДЕРКБ",
    "Шифр Плейфейра (вариант №2)": "PDHIMGRKZP",
    "Шифр Виженера, прямой ключ": "OFBTFCJVMDKC",
    "Шифр Виженера, прогрессивный ключ": "OFBTGDKWOFME",
    "Шифр Виженера, самогенерирующийся ключ": "OFBTVFEGTDNP",
}


def _report(title: str, key: str, plain: str, cipher: str, restored: str) -> None:
    logger.info("--- %s (%s) ---", title, key)
    logger.info("M = %s", group(plain))
    logger.info("C = %s", group(cipher))
    logger.info("D = %s", group(restored))

    marks = ["дешифрование корректно" if restored.startswith(plain)
             else "ОШИБКА ДЕШИФРОВАНИЯ"]
    if title in EXPECTED:
        marks.append("совпадает с методичкой" if cipher == EXPECTED[title]
                     else f"РАСХОЖДЕНИЕ, ожидалось {EXPECTED[title]}")
    logger.info("%s\n", "; ".join(marks))


def _permutations() -> None:
    logger.info("=== Перестановочные методы ===\n")
    plain = normalize(DEMO_TEXT)

    cipher = fence.encrypt(plain, FENCE_KEY)
    _report("Железнодорожная изгородь", f"K = {FENCE_KEY}",
            plain, cipher, fence.decrypt(cipher, FENCE_KEY))

    logger.info("Ключ %s -> %s", COLUMN_KEY, " ".join(map(str, key_numbers(COLUMN_KEY))))
    cipher = columnar.encrypt(plain, COLUMN_KEY)
    _report("Столбцовый метод", f"K = {COLUMN_KEY}",
            plain, cipher, columnar.decrypt(cipher, COLUMN_KEY))

    logger.info("Ключ %s -> %s", COLUMN_KEY2, " ".join(map(str, key_numbers(COLUMN_KEY2))))
    cipher = columnar.encrypt_double(plain, COLUMN_KEY, COLUMN_KEY2)
    _report("Двойная перестановка", f"K1 = {COLUMN_KEY}, K2 = {COLUMN_KEY2}",
            plain, cipher, columnar.decrypt_double(cipher, COLUMN_KEY, COLUMN_KEY2))

    holes, size = grille.parse_key(GRILLE_KEY)
    plain = normalize(DEMO_GRILLE_TEXT)
    cipher = grille.encrypt(plain, holes, size)
    _report("Поворачивающаяся решётка", f"{size}x{size}, отверстия {GRILLE_KEY}",
            plain, cipher, grille.decrypt(cipher, holes, size))


def _substitutions() -> None:
    logger.info("=== Подстановочные методы ===\n")

    plain = normalize(DEMO_TEXT)
    cipher = caesar.encrypt(plain, CAESAR_KEY)
    _report("Шифр Цезаря (вариант №1)", f"k = {CAESAR_KEY}",
            plain, cipher, caesar.decrypt(cipher, CAESAR_KEY))

    plain = normalize(DEMO_VIGENERE_TEXT)
    cipher = caesar.encrypt(plain, 5, mul=3)
    _report("Аффинное преобразование", "k1 = 3, k2 = 5",
            plain, cipher, caesar.decrypt(cipher, 5, mul=3))

    plain = normalize(DEMO_PLAYFAIR_TEXT)
    logger.info("Шифрующая таблица для ключа %s:\n%s",
                PLAYFAIR_KEY, playfair.render(PLAYFAIR_KEY, detect(plain)))
    cipher = playfair.encrypt(plain, PLAYFAIR_KEY)
    _report("Шифр Плейфейра (вариант №2)", f"K = {PLAYFAIR_KEY}",
            plain, cipher, playfair.decrypt(cipher, PLAYFAIR_KEY))

    plain = normalize(DEMO_VIGENERE_TEXT)
    for mode, title in (("direct", "прямой ключ"),
                        ("progressive", "прогрессивный ключ"),
                        ("autokey", "самогенерирующийся ключ")):
        cipher = vigenere.encrypt(plain, VIGENERE_KEY, mode)
        _report(f"Шифр Виженера, {title}", f"K = {VIGENERE_KEY}",
                plain, cipher, vigenere.decrypt(cipher, VIGENERE_KEY, mode))


def run_lab1() -> None:
    logger.info("=== ЛР1: шифрование методами перестановок и подстановок ===\n")
    _permutations()
    _substitutions()
