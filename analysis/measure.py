from substitution.breakers.break_caesar import chi_squared, frequency_table
from utils.basics import normalise

# Chosen from data, not guessed: experiments/measure_classify.py tries every cut point
# on a calibration set (seed 1, X padding) and keeps the one with the fewest errors.
CHI_THRESHOLD = 2.214


def index_of_coincidence(text: str) -> float:
    text = normalise(text)
    if len(text) < 2:
        return 0.0

    unique_letters = set(text)

    index_of_coincidence = 0.0
    for letter in unique_letters:
        index_of_coincidence += text.count(letter) * (text.count(letter) - 1)
    return index_of_coincidence / (len(text) * (len(text) - 1))


def classify(ciphertext: str, language: str = "en") -> str:
    """Return "transposition" or "substitution"."""
    # a transposition keeps the letter counts of the language, so its distance is small
    score = chi_squared(ciphertext, frequency_table(language))
    if score <= CHI_THRESHOLD:
        return "transposition"
    return "substitution"
