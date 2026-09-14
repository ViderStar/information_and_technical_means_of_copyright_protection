"""Числовой ключ перестановки из ключевого слова."""

from typing import List

from helpers.text import normalize


def read_order(keyword: str) -> List[int]:
    """Порядок чтения столбцов: индексы столбцов в порядке возрастания номера.

    Буквам ключа назначаются номера по алфавиту; одинаковые буквы нумеруются
    слева направо (за это отвечает вторичный ключ сортировки `i`).
    """
    letters = normalize(keyword)
    if not letters:
        raise ValueError("Ключевое слово не содержит букв")
    return sorted(range(len(letters)), key=lambda i: (letters[i], i))


def key_numbers(keyword: str) -> List[int]:
    """Номера столбцов 1..d в порядке следования букв ключа (для наглядности)."""
    order = read_order(keyword)
    numbers = [0] * len(order)
    for rank, column in enumerate(order, start=1):
        numbers[column] = rank
    return numbers
