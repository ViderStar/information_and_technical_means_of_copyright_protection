"""CLI for the ITMCP lab works."""

from __future__ import annotations

import argparse
import logging
import sys

from typing import Optional, Tuple

from configs.cfg import (CAESAR_KEY, CAESAR_MUL, COLUMN_KEY, COLUMN_KEY2,
                         FENCE_KEY, GRILLE_KEY, GROUP_SIZE, HASH_H0, PLAYFAIR_KEY,
                         RSA_E, RSA_P, RSA_Q, SIGN_E, SIGN_P, SIGN_Q,
                         VIGENERE_KEY, VIGENERE_MODE)
from helpers.text import group, normalize
from lab1 import caesar, columnar, fence, grille, playfair, vigenere
from lab1.runner import run_lab1
from lab2 import rsa
from lab2.runner import euclid_table, run_lab2
from lab3 import signature
from lab3.runner import hash_table, run_lab3

LAB_COMMANDS = ("rsa", "sign", "verify")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Lab 1: transposition and substitution ciphers; "
                    "lab 2: RSA cryptosystem; lab 3: RSA digital signature.")
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

    rsa_cmd = methods.add_parser(
        "rsa", help="lab 2: RSA keys, encryption and decryption",
        description="Keys come from p, q, e (d is computed by the extended Euclid) "
                    "or are given directly: -e/-d with -r.")
    rsa_cmd.add_argument("mode", choices=("keys", "enc", "dec"))
    rsa_cmd.add_argument("--codec", choices=rsa.CODECS, default="letters",
                         help="letters: A=2..Z=27, А=28..Я=60 as in the manual; "
                              "unicode: code points, any symbols (default: %(default)s)")
    rsa_cmd.set_defaults(key_defaults=(RSA_P, RSA_Q, RSA_E))

    sign_cmd = methods.add_parser("sign", help="lab 3: sign a message (RSA)")
    sign_cmd.set_defaults(key_defaults=(SIGN_P, SIGN_Q, SIGN_E))

    verify_cmd = methods.add_parser("verify", help="lab 3: verify a signature (RSA)")
    verify_cmd.add_argument("-s", "--signature", type=int, required=True,
                            help="signature S")
    verify_cmd.set_defaults(key_defaults=(SIGN_P, SIGN_Q, SIGN_E))

    for command in (rsa_cmd, sign_cmd, verify_cmd):
        command.add_argument("-p", type=int, help="prime p")
        command.add_argument("-q", type=int, help="prime q")
        command.add_argument("-e", type=int, help="public exponent e")
        command.add_argument("-d", type=int, help="secret exponent d (with -r)")
        command.add_argument("-r", type=int, help="modulus r = p*q (with -e or -d)")
        command.add_argument("-t", "--text", help="text (read from stdin if omitted)")
    for command in (sign_cmd, verify_cmd):
        command.add_argument("--h0", type=int, default=HASH_H0,
                             help="initial hash value H0 (default: %(default)s)")
        command.add_argument("-v", "--verbose", action="store_true",
                             help="print the hash computation step by step")

    demo_cmd = methods.add_parser("demo", help="run the examples from the lab manual")
    demo_cmd.add_argument("lab", nargs="?", type=int, choices=(1, 2, 3),
                          help="lab number (default: all labs)")
    gui_cmd = methods.add_parser("gui", help="graphical interface (tkinter)")
    gui_cmd.add_argument("lab", nargs="?", type=int, choices=(1, 2, 3), default=1,
                         help="lab number (default: %(default)s)")

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
        for lab, runner in ((1, run_lab1), (2, run_lab2), (3, run_lab3)):
            if args.lab in (None, lab):
                runner()
        return

    if args.method == "gui":
        # tkinter is imported only when the window starts
        if args.lab == 2:
            from lab2.gui import run
        elif args.lab == 3:
            from lab3.gui import run
        else:
            from gui import run
        run()
        return

    if args.method in LAB_COMMANDS:
        try:
            run_public_key(args)
        except ValueError as error:
            raise SystemExit(f"Error: {error}")
        return

    text = read_text(args)

    try:
        result = encipher(args, text)
    except ValueError as error:      # invalid key: print the message without a traceback
        raise SystemExit(f"Error: {error}")

    print(result if args.raw else group(result))


def resolve_keys(args: argparse.Namespace,
                 trace: Optional[list] = None) -> Tuple[Optional[int], Optional[int], int]:
    """(e, d, r) from -p/-q/-e, or from -r with -e and/or -d given directly."""
    if args.r is not None:
        if args.p is not None or args.q is not None:
            raise ValueError("give either -p and -q, or -r")
        return args.e, args.d, args.r
    default_p, default_q, default_e = args.key_defaults
    keys = rsa.make_keys(default_p if args.p is None else args.p,
                         default_q if args.q is None else args.q,
                         default_e if args.e is None else args.e, trace)
    if args.d is not None and args.d != keys.d:
        raise ValueError(f"-d {args.d} does not match p, q, e: d = {keys.d}")
    return keys.e, keys.d, keys.r


def require(value: Optional[int], name: str) -> int:
    if value is None:
        raise ValueError(f"-{name} is required together with -r")
    return value


def run_public_key(args: argparse.Namespace) -> None:
    """Labs 2 and 3: RSA keys, encryption and signatures."""
    if args.method == "rsa" and args.mode == "keys":
        if args.r is not None:
            raise ValueError("keys are computed from p, q and e: drop -r")
        trace: list = []
        e, d, r = resolve_keys(args, trace)
        print(f"r = p*q = {r}")
        print(f"Extended Euclid for a = phi(r) = {trace[0].d}, b = e = {e}:")
        print("\n".join(euclid_table(trace)))
        print(f"d = {d}\nKo = (e, r) = ({e}, {r})\nKc = (d, r) = ({d}, {r})")
        return

    e, d, r = resolve_keys(args)
    text = args.text if args.text is not None else sys.stdin.read().strip()
    if not text:
        raise SystemExit("Empty text: nothing to process")

    if args.method == "rsa":
        if args.mode == "enc":
            print(rsa.encrypt_text(text, require(e, "e"), r, args.codec))
        else:
            print(rsa.decrypt_text(text, require(d, "d"), r, args.codec))
        return

    steps: list = []
    if args.method == "sign":
        s = signature.sign(text, require(d, "d"), r, args.h0, steps)
        if args.verbose:
            print("\n".join(hash_table(steps, args.h0, r)))
        print(f"h(M) = {steps[-1].h if steps else args.h0 % r}\nS = {s}")
        return

    verdict = signature.verify(text, args.signature, require(e, "e"), r, args.h0, steps)
    if args.verbose:
        print("\n".join(hash_table(steps, args.h0, r)))
    print(f"m' = h(M') = {verdict.computed}\nm = S^e mod r = {verdict.recovered}")
    print("signature is VALID" if verdict.valid else "signature is INVALID")
    if not verdict.valid:
        raise SystemExit(1)


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
