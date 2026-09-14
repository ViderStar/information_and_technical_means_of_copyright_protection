"""Настройки лабораторных работ (переопределяются переменными окружения)."""

import os

# ЛР1: ключи по умолчанию из примеров методички
FENCE_KEY = int(os.getenv("FENCE_KEY", "4"))
COLUMN_KEY = os.getenv("COLUMN_KEY", "КРИПТОГРАФИЯ")
COLUMN_KEY2 = os.getenv("COLUMN_KEY2", "ШИФРОВАНИЕ")
GRILLE_KEY = os.getenv("GRILLE_KEY", "0,7,10,13")

# Символы-заполнители для пустых клеток решётки
FILLERS = os.getenv("FILLERS", "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ")

# Размер группы при выводе шифротекста (ЭОНОИ ТБРРА ...)
GROUP_SIZE = int(os.getenv("GROUP_SIZE", "5"))

# ЛР1, подстановочные шифры (варианты №1-3)
CAESAR_KEY = int(os.getenv("CAESAR_KEY", "3"))
CAESAR_MUL = int(os.getenv("CAESAR_MUL", "1"))       # 1 — Цезарь, иначе аффинный шифр
PLAYFAIR_KEY = os.getenv("PLAYFAIR_KEY", "CRYPTOGRAPHY")
VIGENERE_KEY = os.getenv("VIGENERE_KEY", "MODE")
VIGENERE_MODE = os.getenv("VIGENERE_MODE", "direct")
