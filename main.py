"""CLI for the ITMCP lab works."""

from __future__ import annotations

import argparse
import logging
import sys

from typing import Optional, Tuple

from pathlib import Path

from configs.cfg import (BPCS_ALPHA, BPCS_PLANES, CAESAR_KEY, CAESAR_MUL, COLUMN_KEY,
                         COLUMN_KEY2, CPT_BLOCK, CPT_R, FENCE_KEY, GRILLE_KEY, GROUP_SIZE,
                         HASH_H0, LSB_DEPTH, PLAYFAIR_KEY, RSA_E, RSA_P, RSA_Q, SIGN_E,
                         SIGN_P, SIGN_Q, VIGENERE_KEY, VIGENERE_MODE)
from helpers.text import group, normalize
from lab1 import caesar, columnar, fence, grille, playfair, vigenere
from lab1.runner import run_lab1
from lab2 import rsa
from lab2.runner import euclid_table, run_lab2
from lab3 import signature
from lab3.runner import hash_table, run_lab3
from lab4 import bpcs, cpt, imageio, lsb, samples, textsteg
from lab4.runner import run_lab4

LAB_COMMANDS = ("rsa", "sign", "verify")
STEGO_COMMANDS = ("lsb", "bpcs", "cpt", "text", "sample")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Lab 1: transposition and substitution ciphers; "
                    "lab 2: RSA cryptosystem; lab 3: RSA digital signature; "
                    "lab 4: steganography.")
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

    lsb_cmd = methods.add_parser("lsb", help="lab 4: LSB method for PNG/BMP images")
    lsb_cmd.add_argument("-b", "--bits", type=int, default=LSB_DEPTH,
                         help="LSBs per colour sample, 1..8 (default: %(default)s)")
    lsb_cmd.add_argument("-k", "--key", help="stego key: scatter the bits pseudo-randomly")

    bpcs_cmd = methods.add_parser("bpcs", help="lab 4: BPCS steganography for PNG/BMP")
    bpcs_cmd.add_argument("-a", "--alpha", type=float, default=BPCS_ALPHA,
                          help="complexity threshold alpha0 (default: %(default)s)")
    bpcs_cmd.add_argument("--planes", type=int, default=BPCS_PLANES,
                          help="lowest bit planes used (default: %(default)s)")

    cpt_cmd = methods.add_parser("cpt", help="lab 4: CPT method for binary images")
    cpt_cmd.add_argument("-k", "--key", required=True,
                         help="stego key: K and W are derived from it")
    cpt_cmd.add_argument("--block", default=CPT_BLOCK,
                         help="block size m x n (default: %(default)s)")
    cpt_cmd.add_argument("-r", type=int, default=CPT_R,
                         help="bits per block, r <= log2(mn+1) (default: %(default)s)")
    cpt_cmd.add_argument("--modified", action="store_true",
                         help="modified CPT: change bits next to a colour border")

    for command in (lsb_cmd, bpcs_cmd, cpt_cmd):
        command.add_argument("mode", choices=("embed", "extract", "capacity"))
        command.add_argument("-i", "--input", required=True, help="container image (PNG/BMP)")
        command.add_argument("-o", "--output",
                             help="stego image (default: <input>_stego.png)")
        command.add_argument("-t", "--text", help="message (read from stdin if omitted)")

    text_cmd = methods.add_parser("text", help="lab 4: text steganography")
    text_cmd.add_argument("mode", choices=("embed", "extract", "capacity"))
    text_cmd.add_argument("-s", "--scheme", choices=textsteg.METHODS, default="spaces",
                          help="method; mixed = synonyms with the mixed radix "
                               "(default: %(default)s)")
    text_cmd.add_argument("-c", "--container",
                          help="container text file (embed, capacity); "
                               "the stego text file for extract")
    text_cmd.add_argument("-t", "--text", help="message (read from stdin if omitted)")

    sample_cmd = methods.add_parser("sample", help="lab 4: write a test container image")
    sample_cmd.add_argument("kind", choices=("photo", "stamp"))
    sample_cmd.add_argument("-o", "--output", required=True, help="PNG or BMP file")

    demo_cmd = methods.add_parser("demo", help="run the examples from the lab manual")
    demo_cmd.add_argument("lab", nargs="?", type=int, choices=(1, 2, 3, 4),
                          help="lab number (default: all labs)")
    demo_cmd.add_argument("--figures", type=Path,
                          help="lab 4: also save the report figures to this folder")
    gui_cmd = methods.add_parser("gui", help="graphical interface (tkinter)")
    gui_cmd.add_argument("lab", nargs="?", type=int, choices=(1, 2, 3, 4), default=1,
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
        if args.lab in (None, 4):
            run_lab4(args.figures)
        return

    if args.method == "gui":
        # tkinter is imported only when the window starts
        if args.lab == 2:
            from lab2.gui import run
        elif args.lab == 3:
            from lab3.gui import run
        elif args.lab == 4:
            from lab4.gui import run
        else:
            from gui import run
        run()
        return

    if args.method in LAB_COMMANDS + STEGO_COMMANDS:
        try:
            (run_public_key if args.method in LAB_COMMANDS else run_stego)(args)
        except (ValueError, OSError) as error:
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


def message(args: argparse.Namespace) -> str:
    text = args.text if args.text is not None else sys.stdin.read().rstrip("\n")
    if not text:
        raise SystemExit("Empty message: nothing to hide")
    return text


def run_stego(args: argparse.Namespace) -> None:
    """Lab 4: hide a message in an image or a text, or extract it."""
    if args.method == "sample":
        imageio.save(samples.photo() if args.kind == "photo" else samples.stamp(), args.output)
        print(f"saved {args.output}")
        return

    if args.method == "text":
        if args.container is None and args.scheme != "mimicry":
            raise ValueError("-c is required: the container (or stego) text file")
        container = Path(args.container).read_text(encoding="utf-8") if args.container else ""
        if args.mode == "capacity":
            bits = textsteg.capacity(args.scheme, container)
            print(f"{bits} bits = {bits // 8} bytes (Windows-1251 symbols)")
        elif args.mode == "embed":
            sys.stdout.write(textsteg.embed(args.scheme, container, message(args)))
            if args.scheme == "mimicry":
                sys.stdout.write("\n")
        else:
            print(textsteg.extract(args.scheme, container))
        return

    image = imageio.load(args.input)
    output = args.output or str(Path(args.input).with_name(Path(args.input).stem + "_stego.png"))
    if args.method == "cpt":
        try:
            m, n = (int(v) for v in args.block.lower().split("x"))
        except ValueError:
            raise ValueError("--block must look like 4x4") from None
        key = cpt.generate_key(m, n, args.r, args.key)
        matrix = cpt.from_image(image)
        if args.mode == "capacity":
            print(f"{cpt.capacity(matrix, key)} bytes in {len(cpt.split(matrix, m, n))} "
                  f"blocks of {m}x{n}, r = {args.r}")
        elif args.mode == "embed":
            out, traces = cpt.embed(matrix, message(args), key, args.key, args.modified)
            imageio.save(cpt.to_image(out), output)
            print(f"saved {output}: {len(traces)} blocks, "
                  f"{cpt.bit_changes(matrix, out)} bits changed")
        else:
            print(cpt.extract(matrix, key))
        return

    if args.method == "lsb":
        if args.mode == "capacity":
            print(f"{lsb.capacity(image, args.bits)} bytes with {args.bits} LSB")
        elif args.mode == "embed":
            stego = lsb.embed(image, message(args), args.bits, args.key)
            imageio.save(stego, output)
            print(f"saved {output}: PSNR {lsb.psnr(image, stego):.1f} dB")
        else:
            print(lsb.extract(image, args.bits, args.key))
        return

    if args.mode == "capacity":
        noisy, room = bpcs.capacity(image, args.alpha, args.planes)
        print(f"{room} bytes in {noisy} noise-like blocks (alpha0 = {args.alpha}, "
              f"{args.planes} planes)")
    elif args.mode == "embed":
        stego, stats = bpcs.embed(image, message(args), args.alpha, args.planes)
        imageio.save(stego, output)
        print(f"saved {output}: {stats.used} blocks, {stats.conjugated} conjugated, "
              f"PSNR {lsb.psnr(image, stego):.1f} dB")
    else:
        print(bpcs.extract(image, args.alpha, args.planes))


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
