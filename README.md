# Information and Technical Means of Copyright Protection

**English** · [Русский](README.ru.md)

Lab works for the BSUIR course on information security and copyright protection, from
classical ciphers to public-key cryptography, digital signatures, steganography and
physical unclonable functions.

**Course author:** Prof. Vyacheslav N. Yarmolik, Dr. Sc. (Eng.) —
[BSUIR personal page](https://www.bsuir.by/ru/kaf-poit/yarmolik-v-n)

## Lab 1: transposition and substitution ciphers

- **Transposition:** rail fence, columnar (single and double), turning grille.
- **Substitution:** Caesar and affine, Playfair, Vigenere (direct, progressive, autokey).

All eight reference examples from the lab manual are reproduced symbol by symbol.
The report ([PDF](report/main.pdf), [source](report/main.tex)), the essay on zero-knowledge
proofs ([PDF](referat/main.pdf)) and the [theory notes](labs_info/lab1_theory.md) are in Russian.

## Quick start

Python 3.9+, standard library only.

```bash
python3 main.py gui     # window: pick a cipher, set parameters, see how it works
python3 main.py demo    # run all manual examples with verification
```

The window opens in English; the language selector in the top bar switches to Russian.

```bash
python3 main.py fence    enc -k 4 -t "Это лабораторная работа по КиОКИ"
python3 main.py column   enc -k КРИПТОГРАФИЯ -d ШИФРОВАНИЕ -t "Это лабораторная работа по КиОКИ"
python3 main.py grille   enc -k 0,7,10,13 -t "ШИФРОТЕКСТ"
python3 main.py caesar   enc -k 5 -m 3 -t "Cryptography"
python3 main.py playfair enc -k CRYPTOGRAPHY -t "ciphertext"
python3 main.py vigenere enc -k MODE -s progressive -t "Cryptography"
```

`dec` reverses the transform with the same key, `--raw` turns off 5-symbol grouping,
and text can be piped through stdin.

## Layout

```
main.py       CLI for all labs
configs/      default keys and settings (overridable via environment variables)
helpers/      text normalization, keyword to numeric key, alphabet detection
lab1/         the ciphers and the demo runner
gui/          tkinter window (methods.py: cipher registry, i18n.py: translations)
report/       Lab 1 report (LaTeX + PDF)
referat/      essay (LaTeX + PDF)
```

## Building the PDFs

```bash
cd report && tectonic main.tex    # or: latexmk -pdf main.tex
```
