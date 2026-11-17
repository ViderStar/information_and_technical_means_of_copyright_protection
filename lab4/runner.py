"""Lab 4: steganography demo on the examples from chapter 7 and on test images."""

import logging
import textwrap
import random
from pathlib import Path
from typing import List, Optional

from lab4 import bpcs, cpt, imageio, lsb, samples
from lab4 import textsteg as ts
from lab4.bits import format_bits, parse_bits
from lab4.imageio import Image

logger = logging.getLogger(__name__)

DEMO_MESSAGE = "Лебедевич Артем, лабораторная работа 4: стеганография, 2026"
CONTAINER = ("Хороший программист быстро находит ошибку в большом проекте. Он внимательно "
             "читает код и сразу видит проблему. Такая работа требует опыта и терпения.")

# Manual examples (chapter 7)
LSB_BYTES = ["00100111", "11101001", "11001000", "00100111", "11001000", "11101001",
             "11001000", "01000111", "11101001"]
LSB_EXPECTED = ["00100110", "11101001", "11001000", "00100110", "11001000", "11101000",
                "11001000", "01000111", "11101001"]
CPT_IMAGE = ["01011000", "10001010", "10000111", "00000111"]
CPT_K = "1100/0100/1110/0010"
CPT_W = "1 2 3 4/5 6 7 1/2 3 4 5/6 7 1 2"
CPT_SETS = {1: [(2, 4)], 2: [(1, 2), (2, 2), (3, 1), (4, 4)], 3: [(1, 3), (2, 1)],
            4: [(1, 4), (3, 3)], 5: [(3, 2), (3, 4)], 6: [(4, 1)],
            7: [(1, 1), (2, 3), (4, 2), (4, 3)]}
MIMICRY_EXPECTED = "Иван поехал домой, чтобы забрать одежду."


def _wrap(text: str, indent: str = "  ") -> str:
    """Long texts wrapped to fit the report listing."""
    return textwrap.fill(text, 96, initial_indent=indent, subsequent_indent=indent)


def _mark(ok: bool) -> str:
    return "matches the manual" if ok else "MISMATCH with the manual"


def _matrix_lines(matrix: List[List[int]], indent: str = "  ") -> List[str]:
    return [indent + " ".join(map(str, row)) for row in matrix]


# ---------------------------------------------------------------------- text
def _text_methods() -> None:
    logger.info("=== Text steganography (sections 7.2-7.3) ===\n")
    bits = ts.message_bits("Hi")
    logger.info("Container (%d words):\n%s", len(CONTAINER.split()), _wrap(CONTAINER))
    logger.info("Message 'Hi' in Windows-1251: %s\n", format_bits(bits))

    for method, title in (("spaces", "Spaces of different length (1 = two spaces)"),
                          ("invisible", "Invisible characters (0 = no-break space)"),
                          ("case", "Letter case (1 = upper case)")):
        stego = ts.embed(method, CONTAINER, "Hi")
        shown = stego.replace(ts.NBSP, "~") if method == "invisible" else stego
        logger.info("--- %s ---", title)
        logger.info("capacity %d bits, stego text%s:\n%s",
                    ts.capacity(method, CONTAINER),
                    " (~ marks a no-break space)" if method == "invisible" else "", _wrap(shown))
        logger.info("extracted: %r\n", ts.extract(method, stego))

    example = ts.case_embed("компьютер", parse_bits("01010"))
    logger.info("Manual example: 'компьютер' + 01010 -> '%s'; %s\n", example,
                _mark(example == "кОмПьютер"))

    logger.info("--- Synonyms ---")
    group = [["propensity", "predilection", "penchant", "proximity"]]
    replaced = ts.synonyms_embed("penchant", parse_bits("01"), groups=group)
    logger.info("Manual example: S0 = {propensity, predilection, penchant, proximity},\n"
                "'penchant' + 01 -> '%s'; %s", replaced, _mark(replaced == "predilection"))
    groups = [["AAA", "BBB", "CCC"], ["MMM", "NNN", "OOO", "PPP", "QQQ"], ["WWW", "XXX", "YYY"]]
    plain = ts.synonyms_capacity("AAA MMM WWW", False, groups)
    mixed = ts.synonyms_capacity("AAA MMM WWW", True, groups)
    logger.info("Sets of 3, 5, 3 words: separate coding %d bits, mixed radix "
                "floor(log2 45) = %d bits;\n%s", plain, mixed, _mark((plain, mixed) == (4, 5)))
    code = parse_bits("10110")
    text = ts.synonyms_embed("AAA MMM WWW", code, True, groups)
    logger.info("Mixed radix: 10110 = 22 = 1 + 3*(2 + 5*1) -> '%s' -> %s",
                text, format_bits(ts.synonyms_extract(text, True, groups)))
    for mode in ("synonyms", "mixed"):
        stego = ts.embed(mode, CONTAINER, "Hi")
        logger.info("%s: capacity %d bits, stego text:\n%s\nextracted: %r",
                    "Separate sets" if mode == "synonyms" else "Mixed radix",
                    ts.capacity(mode, CONTAINER), _wrap(stego), ts.extract(mode, stego))
    logger.info("")

    logger.info("--- Mimicry (context-free grammar, figure 7.3) ---")
    trace: List[ts.Step] = []
    sentence = ts.mimicry_sentence(parse_bits("1010") + [1], trace)
    for step in trace:
        logger.info("  %-40s bit %d: %s -> %s", step.sentence, step.bit, step.rule, step.choice)
    logger.info("Code 1010 (+ filler bit 1 for the fifth node): %s\n%s", sentence,
                _mark(sentence == MIMICRY_EXPECTED))
    stego = ts.embed("mimicry", "", "Hi", seed="lab4")
    logger.info("'Hi' (%d bits + zero byte, %d sentences of %d bits):\n%s\nextracted: %r\n",
                len(bits), stego.count("."), ts.mimicry_depth(), _wrap(stego),
                ts.extract("mimicry", stego))


# ---------------------------------------------------------------------- LSB
def _lsb(photo: Image, flat: Image, figures: Optional[Path]) -> None:
    logger.info("=== LSB method (section 7.4.1) ===\n")
    source = [int(b, 2) for b in LSB_BYTES]
    result = [format(v, "08b") for v in lsb.embed_bits(source, parse_bits("01000001"))]
    logger.info("Symbol A = 01000001 in three RGB pixels:")
    for i in range(0, 9, 3):
        logger.info("  (%s) -> (%s)", ", ".join(LSB_BYTES[i:i + 3]), ", ".join(result[i:i + 3]))
    logger.info("%s; changed bytes: %d of 9\n", _mark(result == LSB_EXPECTED),
                sum(a != b for a, b in zip(LSB_BYTES, result)))
    raw = 1024 * 768 * 3 // 8
    logger.info("Capacity of a 1024x768 RGB image with 1 LSB: 1024*768*3/8 = %d bytes; %s\n",
                raw, _mark(raw == 294912))

    logger.info("Container: %dx%d RGB test photo, capacity %d bytes with 1 LSB",
                photo.width, photo.height, lsb.capacity(photo, 1))
    stego = lsb.embed(photo, DEMO_MESSAGE, key="ITMCP")
    logger.info("Message: %s (%d bytes)", DEMO_MESSAGE, len(DEMO_MESSAGE.encode()))
    logger.info("Embedded with key 'ITMCP': changed samples %d, PSNR %.1f dB",
                lsb.changed_samples(photo, stego), lsb.psnr(photo, stego))
    logger.info("Extracted with the key: %s", lsb.extract(stego, key="ITMCP"))
    try:
        wrong = lsb.extract(stego, key="ITMCQ")
        logger.info("Extracted with a wrong key: %r", wrong[:30])
    except ValueError as error:
        logger.info("Extracted with a wrong key:\n  %s", error)
    try:
        lsb.extract(stego)
    except ValueError as error:
        logger.info("Extracted without the key:\n  %s\n", error)

    logger.info("%-10s %12s %10s %10s", "LSBs", "capacity, B", "share", "PSNR, dB")
    rng = random.Random(4)
    full = {}
    for depth in (1, 2, 3, 4):
        room = lsb.capacity(photo, depth)
        message = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz ") for _ in range(room))
        stego_full = lsb.embed(photo, message, depth)
        assert lsb.extract(stego_full, depth) == message
        full[depth] = stego_full
        logger.info("%-10d %12d %9.1f%% %10.1f", depth, room,
                    100 * room / len(photo.data), lsb.psnr(photo, stego_full))
    logger.info("(container filled completely, every extraction verified)\n")

    half = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz ") for _ in range(lsb.capacity(flat) // 2))
    flat_stego = lsb.embed(flat, half)
    logger.info("Visual attack: half of the LSBs filled sequentially (upper half of the picture);\n"
                "share of equal horizontal neighbours in the red LSB plane, upper half:")
    for name, cover in (("noise-free picture", flat), ("photo with sensor noise", photo)):
        stego_half = flat_stego if cover is flat else lsb.embed(photo, half)
        logger.info("  %-24s cover %.3f -> stego %.3f", name,
                    _smoothness(lsb.bit_plane(cover, 0)), _smoothness(lsb.bit_plane(stego_half, 0)))
    logger.info("(0.5 means random bits)\n")

    if figures:
        imageio.save(photo, figures / "photo.png")
        imageio.save(full[1], figures / "lsb_full1.png")
        imageio.save(full[4], figures / "lsb_full4.png")
        imageio.save(lsb.bit_plane(photo, 0), figures / "lsb_plane_photo.png")
        imageio.save(lsb.bit_plane(flat, 0), figures / "lsb_plane_flat.png")
        imageio.save(lsb.bit_plane(flat_stego, 0), figures / "lsb_plane_flat_stego.png")


def _smoothness(plane: Image) -> float:
    """Share of equal horizontal neighbours in the upper half of a bit plane."""
    w, rows = plane.width, plane.height // 2
    same = sum(plane.data[y * w + x] == plane.data[y * w + x + 1]
               for y in range(rows) for x in range(w - 1))
    return same / (rows * (w - 1))


# ---------------------------------------------------------------------- BPCS
P_EXAMPLE = ["00000000", "00000000", "00111100", "00111100",
             "00111100", "00111100", "00000000", "00000000"]


def _bpcs(photo: Image, figures: Optional[Path]) -> None:
    logger.info("=== BPCS steganography (section 7.4.2) ===\n")
    rows = [("W (white)", 0), ("B (black)", (1 << 64) - 1), ("WC", bpcs.WC), ("BC", bpcs.BC)]
    for name, block in rows:
        logger.info("%-10s alpha = %d/112 = %.3f, beta = %d/64 = %.6f", name,
                    bpcs.border(block), bpcs.alpha(block), bpcs.regions(block), bpcs.beta(block))
    ok = (bpcs.alpha(0), bpcs.beta(0), bpcs.alpha(bpcs.WC), bpcs.beta(bpcs.WC)) == (0, 0.015625, 1, 1)
    logger.info("%s (figure 7.4)\n", _mark(ok))

    p = bpcs.from_rows(P_EXAMPLE)
    star = bpcs.conjugate(p)
    logger.info("Conjugation P* = P xor BC:")
    for left, right in zip(bpcs.to_rows(p), bpcs.to_rows(star)):
        logger.info("  %s    %s", left, right)
    logger.info("alpha(P) = %d/112 = %.2f, alpha(P*) = %d/112 = %.2f = 1 - alpha(P); "
                "(P*)* = P: %s\n", bpcs.border(p), bpcs.alpha(p), bpcs.border(star),
                bpcs.alpha(star), bpcs.conjugate(star) == p)

    logger.info("Capacity of the %dx%d test photo, 4 lowest bit planes of R, G, B "
                "(%d blocks 8x8):", photo.width, photo.height,
                3 * 4 * (photo.width // 8) * (photo.height // 8))
    logger.info("%-8s %14s %12s %8s", "alpha0", "noisy blocks", "bytes", "share")
    for alpha0 in (0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5):
        noisy, room = bpcs.capacity(photo, alpha0)
        logger.info("%-8.2f %14d %12d %7.1f%%", alpha0, noisy, room, 100 * room / len(photo.data))

    stego, stats = bpcs.embed(photo, DEMO_MESSAGE)
    logger.info("\nalpha0 = 0.3: message of %d bytes -> %d blocks, %d of them conjugated",
                len(DEMO_MESSAGE.encode()), stats.used, stats.conjugated)
    logger.info("Extracted: %s", bpcs.extract(stego))
    _, room = bpcs.capacity(photo)
    rng = random.Random(5)
    message = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz ") for _ in range(room))
    full, stats = bpcs.embed(photo, message)
    assert bpcs.extract(full) == message
    logger.info("Container filled completely: %d bytes (%.1f%% of the image),\n%d of %d blocks "
                "conjugated, PSNR %.1f dB, extraction verified\n", room,
                100 * room / len(photo.data), stats.conjugated, stats.used, lsb.psnr(photo, full))
    if figures:
        imageio.save(full, figures / "bpcs_full.png")


# ---------------------------------------------------------------------- CPT
def _scale(image: Image, factor: int) -> Image:
    data = bytearray()
    step = image.channels
    for y in range(image.height * factor):
        for x in range(image.width * factor):
            i = ((y // factor) * image.width + x // factor) * step
            data += image.data[i:i + step]
    return Image(image.width * factor, image.height * factor, image.channels, data)


def _highlight(before: cpt.Matrix, after: cpt.Matrix) -> Image:
    """Changed pixels in red over the binary picture."""
    data = bytearray()
    for row_a, row_b in zip(before, after):
        for a, b in zip(row_a, row_b):
            data += bytes((220, 30, 30)) if a != b else bytes((0, 0, 0) if b else (255, 255, 255))
    return Image(len(before[0]), len(before), 3, data)


def _cpt(figures: Optional[Path]) -> None:
    logger.info("=== CPT method (section 7.4.4) ===\n")
    image = [[int(ch) for ch in row] for row in CPT_IMAGE]
    key = cpt.Key(cpt.parse_matrix(CPT_K), cpt.parse_matrix(CPT_W), 3)
    cpt.check_key(key)
    logger.info("P = F1 | F2 (4x8), m = n = 4, r = 3 <= floor(log2 17) = %d, b = 001001",
                cpt.max_r(4, 4))
    out, traces = cpt.embed_bits(image, parse_bits("001001"), key, seed="lab4")
    for number, trace in enumerate(traces, start=1):
        logger.info("--- Block F%d, b = %s ---", number, format_bits(trace.bits))
        logger.info("F xor K:\n%s", "\n".join(_matrix_lines(trace.xor)))
        logger.info("SUM((F xor K) * W) = %d, mod 8 = %d", trace.total, trace.total % 8)
        for w, cells in trace.sets.items():
            logger.info("  S%d = {%s}", w, ", ".join(f"({j + 1},{k + 1})" for j, k in cells))
        logger.info("d = %s - %s mod 8 = %d", format_bits(trace.bits),
                    format(trace.total % 8, "03b"), trace.d)
        if trace.flipped:
            logger.info("h = %d, changed bits: %s", trace.h,
                        ", ".join(f"({j},{k})" for j, k in trace.flipped))
        logger.info("F':\n%s", "\n".join(_matrix_lines(trace.result)))
        if number == 1:
            sets = {w: [(j + 1, k + 1) for j, k in cells] for w, cells in trace.sets.items()}
            ok = (trace.total % 8 == 0 and sets == {w: sorted(c) for w, c in CPT_SETS.items()}
                  and trace.d == 1 and trace.flipped == [(2, 4)])
            logger.info("SUM = 0, sets S1..S7, d = 1, changed bit (2,4): %s", _mark(ok))
        logger.info("")
    logger.info("Extraction: SUM((F' xor K) * W) mod 8 per block -> %s\n",
                format_bits(cpt.extract_bits(out, key)))
    logger.info("Weight matrices for m = n = 6, r = 4 (every value 1..15 present): %.3e\n",
                cpt.weight_matrix_count(6, 6, 4))

    logger.info("--- Modified CPT: distance matrix (section 7.4.5) ---")
    dist = cpt.distance_matrix(image)
    for row in dist:
        logger.info("  %s", " ".join(f"{v:4.2f}" for v in row))

    stamp = cpt.from_image(samples.stamp())
    key = cpt.generate_key(4, 4, 4, "ITMCP")
    logger.info("\nBinary %dx%d picture, blocks 4x4, r = 4, key K, W from the stego key "
                "'ITMCP'; capacity %d bytes", len(stamp[0]), len(stamp), cpt.capacity(stamp, key))
    results = {}
    for modified in (False, True):
        out, traces = cpt.embed(stamp, DEMO_MESSAGE, key, seed="lab4", modified=modified)
        assert cpt.extract(out, key) == DEMO_MESSAGE
        cells = [(y, x) for y, row in enumerate(stamp) for x, v in enumerate(row)
                 if out[y][x] != v]
        edge = [(y, x) for y, x in cells if _mixed_block(stamp, y, x)]
        border = sum(cpt.distance(stamp, y, x) == 1 for y, x in edge)
        isolated = sum(_isolated(out, y, x) for y, x in cells)
        results[modified] = out
        logger.info("%-9s changed bits %d (%.2f per block), isolated dots %d;\n"
                    "          in blocks with an edge %d, of them on the border %d (%.0f%%)",
                    "modified" if modified else "basic", len(cells), len(cells) / len(traces),
                    isolated, len(edge), border, 100 * border / max(1, len(edge)))
    logger.info("Extraction (both): %s", cpt.extract(results[True], key))
    wrong = cpt.generate_key(4, 4, 4, "ITMCQ")
    try:
        logger.info("Wrong key: %r\n", cpt.extract(results[True], wrong)[:30])
    except ValueError as error:
        logger.info("Wrong key: %s\n", error)
    if figures:
        imageio.save(_scale(_highlight(stamp, results[False]), 4), figures / "cpt_basic.png")
        imageio.save(_scale(_highlight(stamp, results[True]), 4), figures / "cpt_modified.png")


def _mixed_block(image: cpt.Matrix, y: int, x: int, side: int = 4) -> bool:
    """The 4x4 block holding (y, x) has both colours: there is an edge to hide in."""
    y0, x0 = y - y % side, x - x % side
    values = {v for row in image[y0:y0 + side] for v in row[x0:x0 + side]}
    return len(values) == 2


def _isolated(image: cpt.Matrix, y: int, x: int) -> bool:
    """A pixel whose four neighbours all have the other colour: a visible dot."""
    h, w = len(image), len(image[0])
    neighbours = [image[y + dy][x + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))
                  if 0 <= y + dy < h and 0 <= x + dx < w]
    return all(v != image[y][x] for v in neighbours)


# ---------------------------------------------------------------------- self-check
def _self_check() -> None:
    rng = random.Random(7)
    alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюяABCXYZ0123456789 .,!"
    photo = samples.photo(64, 64, seed=11)
    stamp = cpt.from_image(samples.stamp())
    count = 0
    for _ in range(40):
        message = "".join(rng.choice(alphabet) for _ in range(rng.randrange(1, 30)))
        depth = rng.randrange(1, 4)
        key = rng.choice([None, str(rng.random())])
        assert lsb.extract(lsb.embed(photo, message, depth, key), depth, key) == message
        alpha0 = rng.choice([0.25, 0.3, 0.4, 0.5])
        assert bpcs.extract(bpcs.embed(photo, message, alpha0, 4)[0], alpha0, 4) == message
        m, n = rng.choice([(4, 4), (3, 4), (6, 6), (8, 8)])
        ckey = cpt.generate_key(m, n, rng.randrange(1, cpt.max_r(m, n) + 1), str(rng.random()))
        if len(message.encode()) <= cpt.capacity(stamp, ckey):
            out, traces = cpt.embed(stamp, message, ckey, str(rng.random()), rng.random() < 0.5)
            assert cpt.extract(out, ckey) == message
            assert all(len(t.flipped) <= 2 for t in traces)
        container = CONTAINER * 30
        for method in ts.METHODS:
            short = message[:2] if method in ("synonyms", "mixed") else message
            if method in ("synonyms", "mixed"):
                short = "".join(ch for ch in short if ch.isascii()) or "A"
                text = CONTAINER
            else:
                text = container
            assert ts.extract(method, ts.embed(method, text, short, "s")) == short
        count += 1
    logger.info("Self-check: %d random messages through LSB (random depth and key),\n"
                "BPCS (random alpha0), CPT (random block size, r, key; at most 2 changed bits\n"
                "per block) and all 6 text methods: every message recovered\n", count)


def run_lab4(figures: Optional[Path] = None) -> None:
    logger.info("=== Lab 4: steganography ===\n")
    if figures:
        figures.mkdir(parents=True, exist_ok=True)
    _text_methods()
    photo = samples.photo()
    flat = samples.photo(noise=0)
    _lsb(photo, flat, figures)
    _bpcs(photo, figures)
    _cpt(figures)
    _self_check()
