"""Working alphabet: Russian (32 letters, Ё merged with Е) or English."""

RUSSIAN = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
ENGLISH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def detect(*texts: str) -> str:
    """The alphabet is chosen by the first letter of the text or key."""
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
        raise ValueError(f"symbols outside the alphabet: {' '.join(unknown)} "
                         "(text and key must use the same alphabet)")
