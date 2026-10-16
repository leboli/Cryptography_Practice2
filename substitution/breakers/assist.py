from collections import Counter

from substitution.breakers.break_caesar import frequency_table
from utils.basics import normalise
from utils.constants import (
    ENGLISH_BIGRAM_FREQUENCY_TABLE,
    ENGLISH_TRIGRAM_FREQUENCY_TABLE,
    SPANISH_BIGRAM_FREQUENCY_TABLE,
    SPANISH_TRIGRAM_FREQUENCY_TABLE,
)


def by_count(items):
    # sort (key, count) pairs by count descending, ties alphabetically
    return sorted(items, key=lambda kv: (-kv[1], kv[0]))


def ngrams(letters: str, n: int) -> list[str]:
    return [letters[i:i + n] for i in range(len(letters) - n + 1)]


def letter_frequencies(letters: str) -> list[tuple[str, int, float]]:
    return [(l, c, c / len(letters) * 100) for l, c in by_count(Counter(letters).items())]


def repeated_ngrams(letters: str, n: int) -> dict[str, list[int]]:
    # positions are 1-indexed
    positions = {}
    for i, gram in enumerate(ngrams(letters, n)):
        positions.setdefault(gram, []).append(i + 1)
    return {gram: pos for gram, pos in positions.items() if len(pos) > 1}


def top_bigrams(letters: str, n: int = 10) -> list[tuple[str, int, float]]:
    bigrams = ngrams(letters, 2)
    top = by_count(Counter(bigrams).items())[:n]
    return [(bg, c, c / len(bigrams) * 100) for bg, c in top]


def doubled_letters(letters: str) -> dict[str, list[int]]:
    positions = {}
    for i in range(len(letters) - 1):
        if letters[i] == letters[i + 1]:
            positions.setdefault(letters[i], []).append(i + 1)
    return positions


def suggested_mapping(letters: str, freq_table: dict[str, float]) -> dict[str, str]:
    # first guess: i-th most common cipher letter -> i-th most common language letter
    cipher_ranked = [l for l, _, _ in letter_frequencies(letters)]
    plain_ranked = [l for l, _ in by_count(freq_table.items())]
    return dict(zip(cipher_ranked, plain_ranked))


def report(ciphertext: str, language: str = "en") -> str:
    freq_table = frequency_table(language)
    if language == "es":
        name, bigram_table, trigram_table = (
            "Spanish", SPANISH_BIGRAM_FREQUENCY_TABLE, SPANISH_TRIGRAM_FREQUENCY_TABLE)
    else:
        name, bigram_table, trigram_table = (
            "English", ENGLISH_BIGRAM_FREQUENCY_TABLE, ENGLISH_TRIGRAM_FREQUENCY_TABLE)

    letters = normalise(ciphertext)
    lines = []

    def section(title):
        lines.extend(["-" * 70, title, "-" * 70])

    lines += ["=" * 70, "FREQUENCY ASSISTANT REPORT", "=" * 70]
    lines.append(f"Language: {name}")
    lines.append(f"Total letters analyzed: {len(letters)}")
    lines.append(f"Distinct ciphertext letters: {len(set(letters))}")
    lines.append("")

    section(f"LETTER FREQUENCIES  (ciphertext, ranked)   vs   expected {name}")
    lines.append(f"{'Rank':<5}{'Ltr':<5}{'Count':<7}{'%':<8}   {'Expect ltr':<12}{'Expect %':<8}")
    cipher_freqs = letter_frequencies(letters)
    plain_freqs = by_count(freq_table.items())
    for i in range(max(len(cipher_freqs), len(plain_freqs))):
        cipher_part = " " * 20
        if i < len(cipher_freqs):
            l, c, pct = cipher_freqs[i]
            cipher_part = f"{l:<5}{c:<7}{pct:<8.2f}"
        plain_part = ""
        if i < len(plain_freqs):
            l, freq = plain_freqs[i]
            plain_part = f"{l:<12}{freq * 100:<8.2f}"
        lines.append(f"{i + 1:<5}{cipher_part}   {plain_part}")
    lines.append("")

    section("REPEATED TRIGRAMS  (ciphertext trigrams that occur more than once)")
    repeated = repeated_ngrams(letters, 3)
    for tg, pos in sorted(repeated.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        lines.append(f"{tg}: count={len(pos)}, positions={pos}")
    if not repeated:
        lines.append("(none)")
    lines.append("")
    top = by_count(trigram_table.items())[:10]
    lines.append(f"For reference, top {name} trigrams: "
                 + ", ".join(f"{tg} ({f * 100:.2f}%)" for tg, f in top))
    lines.append("")

    section("TOP 10 MOST FREQUENT BIGRAMS  (ciphertext)")
    for bg, c, pct in top_bigrams(letters, 10):
        lines.append(f"{bg}: count={c}, {pct:.2f}%")
    lines.append("")
    top = by_count(bigram_table.items())[:10]
    lines.append(f"For reference, top {name} bigrams: "
                 + ", ".join(f"{bg} ({f * 100:.2f}%)" for bg, f in top))
    lines.append("")

    section("DOUBLED LETTERS  (ciphertext)")
    doubles = doubled_letters(letters)
    for l, pos in sorted(doubles.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        lines.append(f"{l}{l}: count={len(pos)}, positions={pos}")
    if not doubles:
        lines.append("(none)")
    lines.append("")

    section("SUGGESTED INITIAL MAPPING  (rank alignment: cipher letter -> plaintext guess)")
    for c, p in sorted(suggested_mapping(letters, freq_table).items()):
        lines.append(f"{c} -> {p}")
    lines.append("")
    lines.append("This is only a starting point based on frequency rank. Check it against")
    lines.append("the bigrams, trigrams, doubled letters and common short words above.")

    return "\n".join(lines)
