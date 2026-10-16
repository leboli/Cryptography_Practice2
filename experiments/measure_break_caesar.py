# C1 - measurement for the Caesar breaker.
# For each length: 200 random fragments of a reference text, encrypted with a
# random key, and we count how often break_caesar gets the key back.
# Run with: py -m experiments.measure_break_caesar
import random

from substitution.cyphers.caesar import encrypt as caesar_encrypt
from substitution.breakers.break_caesar import break_caesar
from utils.basics import normalise
from utils.constants import ENGLISH_TEXT, SPANISH_TEXT

LENGTHS = [20, 30, 40, 60, 100]
TRIALS = 200

random.seed(42)


def random_fragment(text: str, length: int) -> str:
    # random piece of the (normalised) text with exactly `length` letters
    letters = normalise(text)
    start = random.randrange(len(letters) - length + 1)
    return letters[start:start + length]


def recovery_rate(text: str, length: int, language: str) -> float:
    correct = 0
    for _ in range(TRIALS):
        fragment = random_fragment(text, length)
        key = random.randrange(26)
        found_key, _ = break_caesar(caesar_encrypt(fragment, key), language)
        if found_key == key:
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

# Answers
#
# 1) At which length does the breaker become reliable?
#    From 20 letters it's already above 90% with the right table, and by
#    30 letters it's basically always right (100% in my runs). Below that
#    there just isn't enough text for chi-squared to tell the real key
#    apart from the other 25 shifts.

# 2) How much does the wrong language table cost you?
#    It depends on which table is wrong. Using the English table on
#    Spanish text starts off costly for short texts (~35 points worse at
#    20 letters) but that gap almost disappears by 100 letters, so more
#    ciphertext fixes it. Using the Spanish table on English text is
#    worse and doesn't get better with length - it stays wrong a lot of
#    the time even at 100 letters. The Spanish table's letter shape
#    (extra letter, higher A/E weight) just doesn't match English well,
#    so guessing the wrong table isn't equally bad in both directions.
