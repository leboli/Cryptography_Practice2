from collections import Counter

from substitution.cyphers.caesar import decrypt as caesar_decrypt
from utils.basics import normalise
from utils.constants import ENGLISH_FREQUENCY_TABLE, SPANISH_FREQUENCY_TABLE


def frequency_table(language: str) -> dict[str, float]:
    if language == "en":
        return ENGLISH_FREQUENCY_TABLE
    if language == "es":
        return SPANISH_FREQUENCY_TABLE
    raise ValueError(f"Unknown language '{language}' (use 'en' or 'es')")


def chi_squared(text: str, table: dict[str, float]) -> float:
    counts = Counter(normalise(text))
    total = sum(counts.values())
    if total == 0:
        return float("inf")

    chi = 0.0
    for letter, freq in table.items():
        expected = freq * total
        chi += (counts[letter] - expected) ** 2 / expected
    # divide by the length so scores of different texts can be compared
    return chi / total


def break_caesar(ciphertext: str, language: str = "en") -> tuple[int, str]:
    table = frequency_table(language)
    # try all 26 shifts and keep the one that looks most like the language
    key = min(range(26), key=lambda k: chi_squared(caesar_decrypt(ciphertext, k), table))
    return key, caesar_decrypt(ciphertext, key)
