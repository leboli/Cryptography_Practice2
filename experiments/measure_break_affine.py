# C2 - measurement for the Affine breaker.
# Same idea as the Caesar one: 200 random fragments per length, random (a, b)
# key, and we count how often break_affine gets the key back.
# Run with: py -m experiments.measure_break_affine
import random

from substitution.cyphers.affine import encrypt as affine_encrypt, valid_keys
from substitution.breakers.break_affine import break_affine
from experiments.measure_break_caesar import random_fragment
from utils.constants import ENGLISH_TEXT, SPANISH_TEXT

LENGTHS = [20, 30, 40, 60, 100]
TRIALS = 200

random.seed(42)


def recovery_rate(text: str, length: int, language: str) -> float:
    correct = 0
    for _ in range(TRIALS):
        fragment = random_fragment(text, length)
        a, b = random.choice(valid_keys())
        found_key, _ = break_affine(affine_encrypt(fragment, a, b), language)
        if found_key == (a, b):
            correct += 1
    return correct / TRIALS


if __name__ == "__main__":
    print(f"{'len':>4} {'EN/EN':>8} {'EN/ES':>8} {'ES/ES':>8} {'ES/EN':>8}")
    for length in LENGTHS:
        row = [recovery_rate(ENGLISH_TEXT, length, "en"),
               recovery_rate(ENGLISH_TEXT, length, "es"),
               recovery_rate(SPANISH_TEXT, length, "es"),
               recovery_rate(SPANISH_TEXT, length, "en")]
        print(f"{length:>4} " + " ".join(f"{r:>8.1%}" for r in row))
