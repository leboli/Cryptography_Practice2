import math
from functools import cache
from itertools import permutations
from pathlib import Path

from transposition.cyphers.columnar import decrypt as columnar_decrypt
from utils.basics import ALPHABET, normalise

# Bigram tables are built from books that are not used anywhere else:
# The Adventures of Sherlock Holmes (Doyle) and Marianela (Perez Galdos), Project Gutenberg.
DATA = Path(__file__).resolve().parents[2] / "data"
CORPORA = {"en": "english_corpus.txt", "es": "spanish_corpus.txt"}


@cache
def bigram_log_table(language: str) -> dict[str, float]:
    if language not in CORPORA:
        raise ValueError(f"Unknown language '{language}' (use 'en' or 'es')")
    letters = normalise((DATA / CORPORA[language]).read_text(encoding="utf-8"))

    counts = {}
    for a, b in zip(letters, letters[1:]):
        counts[a + b] = counts.get(a + b, 0) + 1
    total = len(letters) - 1
    # a pair never seen in the corpus gets half a count, so the log is never log(0)
    return {a + b: math.log(counts.get(a + b, 0.5) / total) for a in ALPHABET for b in ALPHABET}


def bigram_score(text: str, language: str = "en") -> float:
    table = bigram_log_table(language)
    return sum(table[a + b] for a, b in zip(text, text[1:]))


def order_to_keyword(order: tuple[int, ...]) -> str:
    # (2, 1, 3) -> "BAC", whose key_order is [2, 1, 3]
    return "".join(ALPHABET[rank - 1] for rank in order)


def attack(ciphertext: str, n_cols: int, language: str = "en") -> tuple[tuple[int, ...], str]:
    """Returns (column order, plaintext) for a known number of columns."""
    ciphertext = normalise(ciphertext)
    best_order, best_plaintext, best_score = None, None, -math.inf

    # try all n! orders and keep the one whose plaintext looks most like the language
    for order in permutations(range(1, n_cols + 1)):
        plaintext = columnar_decrypt(ciphertext, order_to_keyword(order))
        score = bigram_score(plaintext, language)
        if score > best_score:
            best_order, best_plaintext, best_score = order, plaintext, score
    return best_order, best_plaintext
