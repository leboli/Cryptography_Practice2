# Practice 2 C2 - measurement for the automatic Vigenere attack (key length not given).
# For each key length m and text length: 100 random fragments encrypted with a
# random key of length m. We count how often attack() gets the whole key back,
# and how often find_key_length alone gets m right.
# Run with: py -m experiments.measure_attack_vigenere
import random

from analysis.keylength import find_key_length
from substitution.cyphers.vigenere import encrypt as vigenere_encrypt
from substitution.breakers.break_vigenere import attack
from experiments.measure_break_caesar import random_fragment
from utils.basics import ALPHABET
from utils.constants import ENGLISH_TEXT, SPANISH_TEXT

KEY_LENGTHS = [3, 5, 7, 9]
LENGTHS = [100, 150, 200, 300, 400]
TRIALS = 100

random.seed(42)


def rates(text: str, length: int, m: int, language: str) -> tuple[float, float]:
    keys_found, lengths_found = 0, 0
    for _ in range(TRIALS):
        key = "".join(random.choice(ALPHABET) for _ in range(m))
        ciphertext = vigenere_encrypt(random_fragment(text, length), key)
        if attack(ciphertext, language)[0] == key:
            keys_found += 1
        if find_key_length(ciphertext, language=language) == m:
            lengths_found += 1
    return keys_found / TRIALS, lengths_found / TRIALS


def print_table(title: str, results: dict) -> None:
    print(title)
    print(f"{'len':>4}" + "".join(f"{'m=' + str(m):>8}" for m in KEY_LENGTHS))
    for length in LENGTHS:
        print(f"{length:>4}" + "".join(f"{results[length, m]:>8.0%}" for m in KEY_LENGTHS))
    print()


if __name__ == "__main__":
    for text, language in [(ENGLISH_TEXT, "en"), (SPANISH_TEXT, "es")]:
        keys, lengths = {}, {}
        for m in KEY_LENGTHS:
            for length in LENGTHS:
                keys[length, m], lengths[length, m] = rates(text, length, m, language)
        print_table(f"[{language}] complete key recovered", keys)
        print_table(f"[{language}] key length correct", lengths)
