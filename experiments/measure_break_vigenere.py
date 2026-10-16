# C3 - measurement for the Vigenere breaker.
# For each key length m and text length: 100 random fragments encrypted with a
# random key of length m, and we count how often break_vigenere gets it back.
# Run with: py -m experiments.measure_break_vigenere
import random

from substitution.cyphers.vigenere import encrypt as vigenere_encrypt
from substitution.breakers.break_vigenere import break_vigenere
from experiments.measure_break_caesar import random_fragment
from utils.basics import ALPHABET
from utils.constants import ENGLISH_TEXT, SPANISH_TEXT

KEY_LENGTHS = [3, 5, 7]
LENGTHS = [60, 120, 200, 300]
TRIALS = 100

random.seed(42)


def recovery_rate(text: str, length: int, m: int, language: str) -> float:
    correct = 0
    for _ in range(TRIALS):
        fragment = random_fragment(text, length)
        key = "".join(random.choice(ALPHABET) for _ in range(m))
        found_key, _ = break_vigenere(vigenere_encrypt(fragment, key), m, language)
        if found_key == key:
            correct += 1
    return correct / TRIALS


if __name__ == "__main__":
    for m in KEY_LENGTHS:
        print(f"key length m = {m}")
        print(f"{'len':>4} {'EN':>8} {'ES':>8} {'~coset len':>11}")
        for length in LENGTHS:
            en = recovery_rate(ENGLISH_TEXT, length, m, "en")
            es = recovery_rate(SPANISH_TEXT, length, m, "es")
            print(f"{length:>4} {en:>8.1%} {es:>8.1%} {length / m:>11.1f}")
        print()
