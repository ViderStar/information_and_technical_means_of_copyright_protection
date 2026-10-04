"""CLI for the ITMCP lab works."""

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
        description="Lab 1: transposition and substitution ciphers.")
    methods = parser.add_subparsers(dest="method", required=True)

    fence_cmd = methods.add_parser("fence", help="rail fence")
    fence_cmd.add_argument("mode", choices=("enc", "dec"))
    fence_cmd.add_argument("-k", "--key", type=int, default=FENCE_KEY,
                           help="fence height (default: %(default)s)")

    column_cmd = methods.add_parser("column", help="columnar transposition")
    column_cmd.add_argument("mode", choices=("enc", "dec"))
    column_cmd.add_argument("-k", "--key", default=COLUMN_KEY,
                            help="keyword (default: %(default)s)")
    column_cmd.add_argument("-d", "--key2", nargs="?", const=COLUMN_KEY2,
                            help="second key: double transposition")

    grille_cmd = methods.add_parser("grille", help="turning grille")
    grille_cmd.add_argument("mode", choices=("enc", "dec"))
    grille_cmd.add_argument("-k", "--key", default=GRILLE_KEY,
                            help="comma-separated hole numbers "
                                 "(default: %(default)s)")

    caesar_cmd = methods.add_parser("caesar", help="Caesar cipher (variant 1)")
    caesar_cmd.add_argument("mode", choices=("enc", "dec"))
    caesar_cmd.add_argument("-k", "--key", type=int, default=CAESAR_KEY,
                            help="shift k2 (default: %(default)s)")
    caesar_cmd.add_argument("-m", "--mul", type=int, default=CAESAR_MUL,
                            help="multiplier k1: affine transformation "
                                 "(default: %(default)s)")

    playfair_cmd = methods.add_parser("playfair", help="Playfair cipher (variant 2)")
    playfair_cmd.add_argument("mode", choices=("enc", "dec"))
    playfair_cmd.add_argument("-k", "--key", default=PLAYFAIR_KEY,
                              help="table keyword (default: %(default)s)")

    vigenere_cmd = methods.add_parser("vigenere", help="Vigenere cipher (variant 3)")
    vigenere_cmd.add_argument("mode", choices=("enc", "dec"))
    vigenere_cmd.add_argument("-k", "--key", default=VIGENERE_KEY,
                              help="keyword (default: %(default)s)")
    vigenere_cmd.add_argument("-s", "--scheme", choices=vigenere.MODES,
                              default=VIGENERE_MODE,
                              help="key scheme (default: %(default)s)")

    methods.add_parser("demo", help="run the examples from the lab manual")
    methods.add_parser("gui", help="graphical interface (tkinter)")

    for command in (fence_cmd, column_cmd, grille_cmd,
                    caesar_cmd, playfair_cmd, vigenere_cmd):
        command.add_argument("-t", "--text", help="text (read from stdin if omitted)")
        command.add_argument("--raw", action="store_true",
                             help=f"do not split the output into groups of {GROUP_SIZE} symbols")

    return parser


def read_text(args: argparse.Namespace) -> str:
    text = args.text if args.text is not None else sys.stdin.read()
    result = normalize(text)
    if not result:
        raise SystemExit("Empty text: nothing to process")
    return result


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = build_parser().parse_args()

    if args.method == "demo":
        run_lab1()
        return

    if args.method == "gui":
        from gui import run          # tkinter is imported only when the window starts
        run()
        return

    text = read_text(args)

    try:
        result = encipher(args, text)
    except ValueError as error:      # invalid key: print the message without a traceback
        raise SystemExit(f"Error: {error}")

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
