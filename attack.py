import argparse
import sys

from analysis.keylength import RANDOM_IC, clear_threshold, coset_ic, find_key_length, language_ic
from analysis.measure import CHI_THRESHOLD, classify, index_of_coincidence
from substitution.breakers.assist import report
from substitution.breakers.break_caesar import chi_squared, frequency_table
from substitution.breakers.break_vigenere import break_vigenere
from transposition.breakers.break_columnar import attack as columnar_attack, bigram_score
from utils.basics import normalise

MAX_M = 16


def attack_substitution(ciphertext: str, ic: float, language: str) -> list[str]:
    # a monoalphabetic cipher keeps the language index, a polyalphabetic one flattens it.
    # Same cut as C1: monoalphabetic means m = 1 already stands clearly above random.
    threshold = clear_threshold(language)
    lines = [f"IC threshold:      {threshold:.4f}  (random {RANDOM_IC:.4f}, "
             f"language {language_ic(language):.4f})"]

    if ic >= threshold:
        lines.append(f"IC {ic:.4f} >= {threshold:.4f} -> monoalphabetic")
        lines.append("")
        lines.append(report(ciphertext, language))
        return lines

    lines.append(f"IC {ic:.4f} < {threshold:.4f} -> polyalphabetic (Vigenere)")
    lines.append("")
    lines.append("Average coset IC for each key length m:")
    for m in range(1, MAX_M + 1):
        lines.append(f"  m={m:<3}{coset_ic(ciphertext, m):.4f}")

    m = find_key_length(ciphertext, MAX_M, language)
    lines.append(f"Key length: {m}  (smallest m above {threshold:.4f}, "
                 "or the highest average if none is)")
    key, plaintext = break_vigenere(ciphertext, m, language)
    lines += ["", f"key: {key}", plaintext]
    return lines


def attack_transposition(ciphertext: str, cols: int | None, language: str) -> list[str]:
    if cols is not None:
        if cols < 2 or len(ciphertext) % cols != 0:
            raise ValueError(f"--cols {cols} does not divide the ciphertext length {len(ciphertext)}")
        candidates = [cols]
    else:
        candidates = [n for n in range(2, 9) if len(ciphertext) % n == 0]
        if not candidates:
            raise ValueError(f"no column count from 2 to 8 divides the ciphertext length "
                             f"{len(ciphertext)}, use --cols")

    lines = [f"Column counts tried: {candidates}", "Bigram log-probability of the best order for each:"]
    best = None
    for n in candidates:
        order, plaintext = columnar_attack(ciphertext, n, language)
        score = bigram_score(plaintext, language)
        lines.append(f"  n={n:<3}score={score:10.1f}  order={order}")
        if best is None or score > best[0]:
            best = (score, n, order, plaintext)

    _, n, order, plaintext = best
    lines += ["", f"columns: {n}", f"order: {order}", plaintext]
    return lines


def run(ciphertext: str, language: str = "en", cols: int | None = None) -> str:
    ciphertext = normalise(ciphertext)
    if len(ciphertext) < 2:
        raise ValueError("the ciphertext needs at least two letters")

    ic = index_of_coincidence(ciphertext)
    chi = chi_squared(ciphertext, frequency_table(language))
    family = classify(ciphertext, language)

    lines = ["Measurements",
             f"Length:            {len(ciphertext)}",
             f"Language:          {language}",
             f"Index of coinc.:   {ic:.4f}",
             f"Chi-squared / n:   {chi:.4f}  (threshold {CHI_THRESHOLD})",
             f"Family:            {family}"]

    if family == "transposition":
        lines += attack_transposition(ciphertext, cols, language)
    else:
        lines += attack_substitution(ciphertext, ic, language)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(prog="attack.py", description="Identify and break a ciphertext")
    parser.add_argument("--in", dest="infile", help="ciphertext file (default: stdin)")
    parser.add_argument("--lang", choices=["en", "es"], default="en")
    parser.add_argument("--cols", type=int, help="number of columns, if it is a transposition")
    args = parser.parse_args()

    try:
        if args.infile:
            with open(args.infile, encoding="utf-8") as f:
                text = f.read()
        else:
            text = sys.stdin.read()
        print(run(text, args.lang, args.cols))
    except (ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
