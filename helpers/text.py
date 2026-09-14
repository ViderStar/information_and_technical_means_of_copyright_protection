"""Подготовка текста: нормализация и группировка."""

from configs.cfg import GROUP_SIZE


def normalize(text: str) -> str:
    """Оставить только буквы, привести к верхнему регистру, Ё -> Е."""
    return "".join(ch for ch in text.upper().replace("Ё", "Е") if ch.isalpha())


def group(text: str, size: int = GROUP_SIZE) -> str:
    """Разбить строку на группы по `size` символов: ЭОНОИ ТБРРА ..."""
    if size <= 0:
        return text
    return " ".join(text[i:i + size] for i in range(0, len(text), size))
