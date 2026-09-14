"""CLI лабораторных работ по ИТСЗАП."""

from __future__ import annotations

import argparse
import logging
import sys

from configs.cfg import (CAESAR_KEY, CAESAR_MUL, COLUMN_KEY, COLUMN_KEY2,
                         FENCE_KEY, GRILLE_KEY, GROUP_SIZE, PLAYFAIR_KEY,
                         VIGENERE_KEY, VIGENERE_MODE)
from helpers.text import group, normalize
from lab1 import caesar, columnar, fence, grille, playfair, vigenere
from lab1.runner import run_lab1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="ЛР1: шифрование методами перестановок и подстановок.")
    methods = parser.add_subparsers(dest="method", required=True)

    fence_cmd = methods.add_parser("fence", help="железнодорожная изгородь")
    fence_cmd.add_argument("mode", choices=("enc", "dec"))
    fence_cmd.add_argument("-k", "--key", type=int, default=FENCE_KEY,
                           help="высота изгороди (по умолчанию %(default)s)")

    column_cmd = methods.add_parser("column", help="столбцовый метод")
    column_cmd.add_argument("mode", choices=("enc", "dec"))
    column_cmd.add_argument("-k", "--key", default=COLUMN_KEY,
                            help="ключевое слово (по умолчанию %(default)s)")
    column_cmd.add_argument("-d", "--key2", nargs="?", const=COLUMN_KEY2,
                            help="второй ключ — двойная перестановка")

    grille_cmd = methods.add_parser("grille", help="поворачивающаяся решётка")
    grille_cmd.add_argument("mode", choices=("enc", "dec"))
    grille_cmd.add_argument("-k", "--key", default=GRILLE_KEY,
                            help="номера отверстий через запятую "
                                 "(по умолчанию %(default)s)")

    caesar_cmd = methods.add_parser("caesar", help="шифр Цезаря (вариант №1)")
    caesar_cmd.add_argument("mode", choices=("enc", "dec"))
    caesar_cmd.add_argument("-k", "--key", type=int, default=CAESAR_KEY,
                            help="сдвиг k2 (по умолчанию %(default)s)")
    caesar_cmd.add_argument("-m", "--mul", type=int, default=CAESAR_MUL,
                            help="множитель k1 — аффинное преобразование "
                                 "(по умолчанию %(default)s)")

    playfair_cmd = methods.add_parser("playfair", help="шифр Плейфейра (вариант №2)")
    playfair_cmd.add_argument("mode", choices=("enc", "dec"))
    playfair_cmd.add_argument("-k", "--key", default=PLAYFAIR_KEY,
                              help="ключевое слово таблицы (по умолчанию %(default)s)")

    vigenere_cmd = methods.add_parser("vigenere", help="шифр Виженера (вариант №3)")
    vigenere_cmd.add_argument("mode", choices=("enc", "dec"))
    vigenere_cmd.add_argument("-k", "--key", default=VIGENERE_KEY,
                              help="ключевое слово (по умолчанию %(default)s)")
    vigenere_cmd.add_argument("-s", "--scheme", choices=vigenere.MODES,
                              default=VIGENERE_MODE,
                              help="схема применения ключа (по умолчанию %(default)s)")

    methods.add_parser("demo", help="прогон примеров из методички")
    methods.add_parser("gui", help="графический интерфейс (tkinter)")

    for command in (fence_cmd, column_cmd, grille_cmd,
                    caesar_cmd, playfair_cmd, vigenere_cmd):
        command.add_argument("-t", "--text", help="текст (иначе читается stdin)")
        command.add_argument("--raw", action="store_true",
                             help=f"не разбивать вывод на группы по {GROUP_SIZE} символов")

    return parser


def read_text(args: argparse.Namespace) -> str:
    text = args.text if args.text is not None else sys.stdin.read()
    result = normalize(text)
    if not result:
        raise SystemExit("Пустой текст: нечего шифровать")
    return result


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = build_parser().parse_args()

    if args.method == "demo":
        run_lab1()
        return

    if args.method == "gui":
        from gui import run          # tkinter импортируется только при запуске окна
        run()
        return

    text = read_text(args)

    try:
        result = encipher(args, text)
    except ValueError as error:      # некорректный ключ — сообщение без трассировки
        raise SystemExit(f"Ошибка: {error}")

    print(result if args.raw else group(result))


def encipher(args: argparse.Namespace, text: str) -> str:
    if args.method == "fence":
        handler = fence.encrypt if args.mode == "enc" else fence.decrypt
        result = handler(text, args.key)
    elif args.method == "column":
        if args.key2:
            handler = (columnar.encrypt_double if args.mode == "enc"
                       else columnar.decrypt_double)
            result = handler(text, args.key, args.key2)
        else:
            handler = columnar.encrypt if args.mode == "enc" else columnar.decrypt
            result = handler(text, args.key)
    elif args.method == "grille":
        holes, size = grille.parse_key(args.key)
        handler = grille.encrypt if args.mode == "enc" else grille.decrypt
        result = handler(text, holes, size)
    elif args.method == "caesar":
        handler = caesar.encrypt if args.mode == "enc" else caesar.decrypt
        result = handler(text, args.key, args.mul)
    elif args.method == "playfair":
        handler = playfair.encrypt if args.mode == "enc" else playfair.decrypt
        result = handler(text, normalize(args.key))
    else:
        handler = vigenere.encrypt if args.mode == "enc" else vigenere.decrypt
        result = handler(text, normalize(args.key), args.scheme)
    return result


if __name__ == "__main__":
    main()
