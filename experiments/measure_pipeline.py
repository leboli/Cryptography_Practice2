# Practice 2 D - measurement for the mono / poly decision in attack.py.
# For each text length: 300 random fragments encrypted with a random monoalphabetic
# key, and 300 with a random Vigenere key of each length m. We count how often the
# index of coincidence lands on the wrong side of the threshold, for the midpoint
# (first try) and for the C1 clear-peak threshold (the one attack.py uses).
# Run with: py -m experiments.measure_pipeline
import random

from analysis.keylength import RANDOM_IC, clear_threshold, language_ic
from analysis.measure import index_of_coincidence
from substitution.cyphers.monoalpha import encrypt as mono_encrypt
from substitution.cyphers.vigenere import encrypt as vigenere_encrypt
from experiments.measure_break_caesar import random_fragment
from utils.basics import ALPHABET
from utils.constants import ENGLISH_TEXT, SPANISH_TEXT

LENGTHS = [100, 200, 300]
KEY_LENGTHS = [2, 3, 5]
TRIALS = 300

random.seed(1)


def error_rates(text: str, length: int, threshold: float) -> list[float]:
    # first the monoalphabetic error (read as poly), then one per Vigenere key length (read as mono)
    errors = 0
    for _ in range(TRIALS):
        key = "".join(random.sample(ALPHABET, 26))
        if index_of_coincidence(mono_encrypt(random_fragment(text, length), key)) < threshold:
            errors += 1
    rates = [errors / TRIALS]

    for m in KEY_LENGTHS:
        errors = 0
        for _ in range(TRIALS):
            key = "".join(random.choice(ALPHABET) for _ in range(m))
            if index_of_coincidence(vigenere_encrypt(random_fragment(text, length), key)) >= threshold:
                errors += 1
        rates.append(errors / TRIALS)
    return rates


def print_table(title: str, text: str, threshold: float) -> None:
    print(f"{title}  (threshold {threshold:.4f})")
    print(f"{'len':>4}{'mono':>8}" + "".join(f"{'m=' + str(m):>8}" for m in KEY_LENGTHS))
    for length in LENGTHS:
        print(f"{length:>4}" + "".join(f"{r:>8.1%}" for r in error_rates(text, length, threshold)))
    print()


if __name__ == "__main__":
    for text, language in [(ENGLISH_TEXT, "en"), (SPANISH_TEXT, "es")]:
        midpoint = (RANDOM_IC + language_ic(language)) / 2
        print_table(f"[{language}] error rate, midpoint", text, midpoint)
        print_table(f"[{language}] error rate, clear-peak (used)", text, clear_threshold(language))
