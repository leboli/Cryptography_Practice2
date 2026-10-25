from analysis.measure import index_of_coincidence
from substitution.breakers.break_caesar import frequency_table
from substitution.cyphers.vigenere import cosets
from utils.basics import ALPHABET

RANDOM_IC = 1 / len(ALPHABET)

# How far from random text towards the language a coset average must get
# to count as "clearly above the baseline" (3/4 of the way).
CLEAR_FRACTION = 0.75


def coset_ic(ciphertext: str, m: int) -> float:
    parts = cosets(ciphertext, m)
    return sum(index_of_coincidence(part) for part in parts) / m


def language_ic(language: str) -> float:
    # expected index of a plain text: sum of p^2 over the letters
    return sum(p * p for p in frequency_table(language).values())


def clear_threshold(language: str) -> float:
    return RANDOM_IC + CLEAR_FRACTION * (language_ic(language) - RANDOM_IC)


def find_key_length(ciphertext: str, max_m: int = 16, language: str = "en") -> int:
    threshold = clear_threshold(language)
    averages = {m: coset_ic(ciphertext, m) for m in range(1, max_m + 1)}

    # multiples of the key length are just as high, so take the first one that passes
    for m, average in averages.items():
        if average >= threshold:
            return m
    # nothing passed (usually a very short text): best guess is the highest average
    return max(averages, key=averages.get)
