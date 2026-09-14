"""Рабочий алфавит: русский (32 буквы, Ё отождествлена с Е) или английский."""

RUSSIAN = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
ENGLISH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def detect(*texts: str) -> str:
    """Алфавит определяется по первой букве текста или ключа."""
    for text in texts:
        for symbol in text:
            if symbol in RUSSIAN:
                return RUSSIAN
            if symbol in ENGLISH:
                return ENGLISH
    return RUSSIAN


def check(text: str, alphabet: str) -> None:
    unknown = sorted(set(text) - set(alphabet))
    if unknown:
        raise ValueError(f"символы вне алфавита: {' '.join(unknown)} "
                         "(текст и ключ должны быть в одном алфавите)")
