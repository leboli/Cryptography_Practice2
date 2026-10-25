import random

from analysis.measure import CHI_THRESHOLD, classify
from substitution.breakers.break_caesar import chi_squared
from substitution.cyphers.monoalpha import encrypt as mono_encrypt
from transposition.cyphers.columnar import encrypt as columnar_encrypt
from utils.basics import ALPHABET, normalise
from utils.constants import ENGLISH_FREQUENCY_TABLE, ENGLISH_TEXT

LENGTHS = [60, 120, 250, 400]
SAMPLES = 150              
KEY_LENGTHS = range(4, 11)  # columnar keywords of 4..10 letters
CALIBRATION_SEED = 1
TEST_SEED = 42

LETTERS = normalise(ENGLISH_TEXT)


def random_fragment(length: int) -> str:
    start = random.randrange(len(LETTERS) - length + 1)
    return LETTERS[start:start + length]


def random_pad() -> str:
    # one letter, drawn with the English letter frequencies
    letters = list(ENGLISH_FREQUENCY_TABLE)
    weights = list(ENGLISH_FREQUENCY_TABLE.values())
    return random.choices(letters, weights)[0]


def columnar_sample(length: int, pad: str | None) -> str:
    # pad=None means "draw a random pad letter for this message"
    keyword = "".join(random.sample(ALPHABET, random.choice(KEY_LENGTHS)))
    return columnar_encrypt(random_fragment(length), keyword, pad or random_pad())


def mono_sample(length: int) -> str:
    key = "".join(random.sample(ALPHABET, 26))
    return mono_encrypt(random_fragment(length), key)


def make_samples(length: int, pad: str | None) -> tuple[list[str], list[str]]:
    transpositions = [columnar_sample(length, pad) for _ in range(SAMPLES)]
    substitutions = [mono_sample(length) for _ in range(SAMPLES)]
    return transpositions, substitutions


def calibrate() -> float:
    # every cut point between two scores is a candidate; keep the one with fewest errors
    random.seed(CALIBRATION_SEED)
    trans_scores, subs_scores = [], []
    for length in LENGTHS:
        transpositions, substitutions = make_samples(length, "X")
        trans_scores += [chi_squared(c, ENGLISH_FREQUENCY_TABLE) for c in transpositions]
        subs_scores += [chi_squared(c, ENGLISH_FREQUENCY_TABLE) for c in substitutions]

    scores = sorted(trans_scores + subs_scores)
    best_threshold, best_errors = None, None
    for low, high in zip(scores, scores[1:]):
        threshold = (low + high) / 2
        errors = (sum(s > threshold for s in trans_scores)
                  + sum(s <= threshold for s in subs_scores))
        if best_errors is None or errors < best_errors:
            best_threshold, best_errors = threshold, errors

    print(f"Calibration (seed {CALIBRATION_SEED}, X pad): best threshold = {best_threshold:.4f}, "
          f"{best_errors} errors out of {len(scores)}")
    print(f"  transposition scores: min {min(trans_scores):.3f}, max {max(trans_scores):.3f}")
    print(f"  substitution scores:  min {min(subs_scores):.3f}, max {max(subs_scores):.3f}")
    return best_threshold


def error_rates(length: int, pad: str | None) -> tuple[float, float, float]:
    transpositions, substitutions = make_samples(length, pad)
    trans_wrong = sum(classify(c) != "transposition" for c in transpositions)
    subs_wrong = sum(classify(c) != "substitution" for c in substitutions)
    total = 2 * SAMPLES
    return trans_wrong / SAMPLES, subs_wrong / SAMPLES, (trans_wrong + subs_wrong) / total


def pad_contribution(length: int, pads: int, pad_letter: str = "X") -> float:
    # chi-squared term of the pad letter alone, if all its occurrences are pad
    expected = ENGLISH_FREQUENCY_TABLE[pad_letter] * length
    return (pads - expected) ** 2 / expected / length


if __name__ == "__main__":
    calibrate()
    print(f"Threshold used by classify (CHI_THRESHOLD) = {CHI_THRESHOLD}\n")

    random.seed(TEST_SEED)
    print(f"Test (seed {TEST_SEED}), {SAMPLES} columnar + {SAMPLES} mono samples per length")
    print(f"{'':>4} {'----- pad = X -----':^26} {'--- pad = random ---':^26}")
    print(f"{'len':>4} {'trans':>8} {'subs':>8} {'total':>8} {'trans':>8} {'subs':>8} {'total':>8}")
    for length in LENGTHS:
        x_rates = error_rates(length, "X")
        r_rates = error_rates(length, None)
        print(f"{length:>4} " + " ".join(f"{r:>8.1%}" for r in x_rates + r_rates))

    contribution = pad_contribution(66, 6)
    print(f"\n66 letters with 6 X pads: pad term = {contribution:.3f} "
          f"(threshold {CHI_THRESHOLD}, ratio {contribution / CHI_THRESHOLD:.1f}x)")
