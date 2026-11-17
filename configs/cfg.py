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

# Lab 2, RSA cryptosystem: keys from the "CAT" example in the lab manual
RSA_P = int(os.getenv("RSA_P", "3"))
RSA_Q = int(os.getenv("RSA_Q", "11"))
RSA_E = int(os.getenv("RSA_E", "7"))

# Lab 3, RSA digital signature: keys and hash parameters from the "БГУИР" example
SIGN_P = int(os.getenv("SIGN_P", "17"))
SIGN_Q = int(os.getenv("SIGN_Q", "19"))
SIGN_E = int(os.getenv("SIGN_E", "43"))
HASH_H0 = int(os.getenv("HASH_H0", "100"))

# Lab 4, steganography: method parameters from chapter 7
LSB_DEPTH = int(os.getenv("LSB_DEPTH", "1"))            # LSBs per colour sample
BPCS_ALPHA = float(os.getenv("BPCS_ALPHA", "0.3"))      # complexity threshold alpha0
BPCS_PLANES = int(os.getenv("BPCS_PLANES", "4"))        # lowest bit planes used
CPT_BLOCK = os.getenv("CPT_BLOCK", "4x4")               # block m x n
CPT_R = int(os.getenv("CPT_R", "4"))                    # bits per block, r <= log2(mn + 1)

# Lab 4 variant: the full name is hidden in a text file by the spaces method in base
# SPACES_BASE (digit d = d + 1 spaces). Binary and base 4 are taken in the group,
# base 3 (1-3 spaces) was free.
SPACES_BASE = int(os.getenv("SPACES_BASE", "3"))
STEGO_NAME = os.getenv("STEGO_NAME", "Лебедевич Артем Владимирович")
