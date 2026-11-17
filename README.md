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

## Lab 2: RSA cryptosystem (variant 1)

Key pair from given p, q, e via the extended Euclidean algorithm, encryption and
decryption via fast modular exponentiation. The manual's example (p = 3, q = 11, e = 7:
d = 3, CAT -> 16 29 21) is reproduced exactly.
Report: [PDF](report_lab2/main.pdf), [source](report_lab2/main.tex).

## Lab 3: RSA digital signature (variant 1)

Signing and verification with the manual's quadratic hash H_i = (H_{i-1} + m_i)^2 mod n.
The manual's example (h(БГУИР) = 93, d = 67, S = 206, forged БРУИР -> 123) is
reproduced exactly; the demo also finds a hash collision that forges a signature.
Report: [PDF](report_lab3/main.pdf), [source](report_lab3/main.tex).

## Lab 4: steganography

Text methods (spaces of different length, invisible characters, letter case, synonyms
with a mixed-radix code, CFG mimicry), LSB and BPCS for colour PNG/BMP images, CPT and
the distance-matrix modification of CPT for binary images. All numeric examples of
chapter 7 are reproduced exactly (кОмПьютер, the CPT sets S1..S7 and the flipped bit
(2,4), the mimicry sentence for 1010, alpha and beta of the reference blocks). PNG and
BMP are read and written with the standard library only.
Variant: the full name hidden in a text file by spaces in base 3 (a digit d is d + 1
spaces, 1-3 spaces per gap); any base 2..6 via `text -b`.
Report: [PDF](report_lab4/main.pdf), [source](report_lab4/main.tex).

## Quick start

Python 3.9+, standard library only.

```bash
python3 main.py gui     # window: pick a cipher, set parameters, see how it works
python3 main.py demo    # run all manual examples with verification (demo 1|2|3|4 for one lab)
python3 main.py gui 2   # lab 2 window (gui 3, gui 4 for labs 3 and 4)
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

```bash
python3 main.py rsa keys -p 3 -q 11 -e 7                 # r, phi(r), Euclid trace, d
python3 main.py rsa enc -t CAT                           # 16 29 21
python3 main.py rsa dec -d 3 -r 33 -t "16 29 21"         # CAT
python3 main.py sign -t БГУИР -v                         # h(M) = 93, S = 206
python3 main.py verify -e 43 -r 323 -s 206 -t БРУИР      # INVALID: 123 != 93
```

```bash
python3 main.py sample photo -o photo.png                # test container
python3 main.py lsb embed -i photo.png -k secret -t "Hidden"   # -> photo_stego.png
python3 main.py lsb extract -i photo_stego.png -k secret
python3 main.py bpcs embed -i photo.png -a 0.3 --planes 4 -t "BPCS"
python3 main.py cpt embed -i stamp.png -k ITMCP --modified -t "БГУИР"
python3 main.py text embed -s mixed -c container.txt -t Hi > stego.txt
python3 main.py text extract -s mixed -c stego.txt
```

`dec` reverses the transform with the same key, `--raw` turns off 5-symbol grouping,
and text can be piped through stdin.

## Layout

```
main.py       CLI for all labs
configs/      default keys and settings (overridable via environment variables)
helpers/      text normalization, keyword to numeric key, alphabet detection,
              number theory (fast_exp, extended Euclid, Miller-Rabin)
lab1/         the ciphers and the demo runner
lab2/         RSA: keys, encryption, demo runner, window
lab3/         quadratic hash, RSA signature, demo runner, window
lab4/         steganography: text methods, LSB, BPCS, CPT, PNG/BMP I/O, window
gui/          Lab 1 tkinter window (methods.py: cipher registry, i18n.py: translations)
report/       Lab 1 report (LaTeX + PDF)
report_lab2/  Lab 2 report
report_lab3/  Lab 3 report
report_lab4/  Lab 4 report
referat/      essay (LaTeX + PDF)
```

## Building the PDFs

```bash
cd report && tectonic main.tex    # or: latexmk -pdf main.tex
```
