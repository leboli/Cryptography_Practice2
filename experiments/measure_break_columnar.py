# Practice 2 C3 - measurement for the columnar transposition breaker (column count given).
# For each number of columns and text length: 100 random fragments encrypted with a
# random keyword (X padding), and we count how often attack() gives back the
# padded plaintext exactly. The last part times the search for growing n.
# Run with: py -m experiments.measure_break_columnar
import random
import time

from transposition.cyphers.columnar import encrypt as columnar_encrypt
from transposition.breakers.break_columnar import attack
from experiments.measure_break_caesar import random_fragment
from utils.basics import ALPHABET
from utils.constants import ENGLISH_TEXT, SPANISH_TEXT

COLUMNS = [4, 5, 6, 7]
LENGTHS = [60, 120, 200]
TRIALS = 100

random.seed(42)


def padded(plaintext: str, n_cols: int, pad: str = "X") -> str:
    rows = -(-len(plaintext) // n_cols)
    return plaintext.ljust(rows * n_cols, pad)


def recovery_rate(text: str, length: int, n_cols: int, language: str) -> float:
    correct = 0
    for _ in range(TRIALS):
        fragment = random_fragment(text, length)
        keyword = "".join(random.sample(ALPHABET, n_cols))
        _, found = attack(columnar_encrypt(fragment, keyword), n_cols, language)
        if found == padded(fragment, n_cols):
            correct += 1
    return correct / TRIALS


def time_search(n_cols: int, length: int = 200) -> float:
    keyword = ALPHABET[:n_cols]
    ciphertext = columnar_encrypt(random_fragment(ENGLISH_TEXT, length), keyword)
    start = time.perf_counter()
    attack(ciphertext, n_cols)
    return time.perf_counter() - start


if __name__ == "__main__":
    for text, language in [(ENGLISH_TEXT, "en"), (SPANISH_TEXT, "es")]:
        print(f"[{language}] plaintext recovered exactly")
        print(f"{'len':>4}" + "".join(f"{'n=' + str(n):>8}" for n in COLUMNS))
        for length in LENGTHS:
            rates = [recovery_rate(text, length, n, language) for n in COLUMNS]
            print(f"{length:>4}" + "".join(f"{rate:>8.0%}" for rate in rates))
        print()

    print("time for one attack on 200 letters")
    for n in range(4, 10):
        print(f"n={n}: {time_search(n):.2f}s")
