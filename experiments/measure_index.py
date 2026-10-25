import random

from analysis.measure import index_of_coincidence
from utils.basics import ALPHABET, normalise
from utils.constants import ENGLISH_FREQUENCY_TABLE, ENGLISH_TEXT

LENGTHS = [13, 20, 30, 40, 50, 60, 80, 100, 150, 200]
TRIALS = 1000
TRUST = 0.95

IC_ENGLISH = sum(p * p for p in ENGLISH_FREQUENCY_TABLE.values())  # ~0.066
IC_RANDOM = 1 / 26                                                 # ~0.0385
THRESHOLD = (IC_ENGLISH + IC_RANDOM) / 2

random.seed(42)


def random_fragment(text: str, length: int) -> str:
    # random piece of the (normalised) text with exactly `length` letters
    letters = normalise(text)
    start = random.randrange(len(letters) - length + 1)
    return letters[start:start + length]


def random_letters(length: int) -> str:
    return "".join(random.choice(ALPHABET) for _ in range(length))


def mean_std(values: list[float]) -> tuple[float, float]:
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return mean, var ** 0.5


if __name__ == "__main__":
    print(f"IC English (table) = {IC_ENGLISH:.4f}, IC random = {IC_RANDOM:.4f}, "
          f"threshold = {THRESHOLD:.4f}")
    print(f"IC of CRYPTANALYSIS = {index_of_coincidence('CRYPTANALYSIS'):.4f}\n")
    print(f"{'len':>4} {'EN mean':>8} {'EN std':>7} {'RND mean':>9} {'RND std':>8} "
          f"{'EN ok':>7} {'RND ok':>7}")
    for length in LENGTHS:
        en = [index_of_coincidence(random_fragment(ENGLISH_TEXT, length)) for _ in range(TRIALS)]
        rnd = [index_of_coincidence(random_letters(length)) for _ in range(TRIALS)]
        en_mean, en_std = mean_std(en)
        rnd_mean, rnd_std = mean_std(rnd)
        en_ok = sum(ic > THRESHOLD for ic in en) / TRIALS
        rnd_ok = sum(ic <= THRESHOLD for ic in rnd) / TRIALS
        mark = "  <- trusted" if min(en_ok, rnd_ok) >= TRUST else ""
        print(f"{length:>4} {en_mean:>8.4f} {en_std:>7.4f} {rnd_mean:>9.4f} {rnd_std:>8.4f} "
              f"{en_ok:>7.1%} {rnd_ok:>7.1%}{mark}")
