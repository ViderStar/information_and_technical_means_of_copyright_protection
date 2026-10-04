"""Text preparation: normalization and grouping."""

from configs.cfg import GROUP_SIZE


def normalize(text: str) -> str:
    """Keep letters only, upper-case them, Ё -> Е."""
    return "".join(ch for ch in text.upper().replace("Ё", "Е") if ch.isalpha())


def group(text: str, size: int = GROUP_SIZE) -> str:
    """Split a string into groups of `size` symbols: ЭОНОИ ТБРРА ..."""
    if size <= 0:
        return text
    return " ".join(text[i:i + size] for i in range(0, len(text), size))
