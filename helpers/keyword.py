"""Numeric permutation key derived from a keyword."""

from typing import List

from helpers.text import normalize


def read_order(keyword: str) -> List[int]:
    """Column reading order: column indexes sorted by their number.

    Key letters are numbered alphabetically; equal letters are numbered
    left to right (the secondary sort key `i` takes care of that).
    """
    letters = normalize(keyword)
    if not letters:
        raise ValueError("The keyword contains no letters")
    return sorted(range(len(letters)), key=lambda i: (letters[i], i))


def key_numbers(keyword: str) -> List[int]:
    """Column numbers 1..d in the order of the key letters (for display)."""
    order = read_order(keyword)
    numbers = [0] * len(order)
    for rank, column in enumerate(order, start=1):
        numbers[column] = rank
    return numbers
