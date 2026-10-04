"""Lab settings (can be overridden through environment variables)."""

import os

# Lab 1: default keys taken from the examples in the lab manual
FENCE_KEY = int(os.getenv("FENCE_KEY", "4"))
COLUMN_KEY = os.getenv("COLUMN_KEY", "КРИПТОГРАФИЯ")
COLUMN_KEY2 = os.getenv("COLUMN_KEY2", "ШИФРОВАНИЕ")
GRILLE_KEY = os.getenv("GRILLE_KEY", "0,7,10,13")

# Filler letters for the empty cells of the grille
FILLERS = os.getenv("FILLERS", "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ")

# Group size when printing ciphertext (ЭОНОИ ТБРРА ...)
GROUP_SIZE = int(os.getenv("GROUP_SIZE", "5"))

# Lab 1, substitution ciphers (variants 1-3)
CAESAR_KEY = int(os.getenv("CAESAR_KEY", "3"))
CAESAR_MUL = int(os.getenv("CAESAR_MUL", "1"))       # 1 = Caesar, otherwise affine cipher
PLAYFAIR_KEY = os.getenv("PLAYFAIR_KEY", "CRYPTOGRAPHY")
VIGENERE_KEY = os.getenv("VIGENERE_KEY", "MODE")
VIGENERE_MODE = os.getenv("VIGENERE_MODE", "direct")
