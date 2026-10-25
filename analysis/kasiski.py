from utils.basics import normalise


def repeats(ciphertext: str, min_len: int = 3) -> dict[str, list[int]]:
    text = normalise(ciphertext)
    found = {}
    for length in range(min_len, len(text)):
        positions = {}
        for i in range(len(text) - length + 1):
            positions.setdefault(text[i:i + length], []).append(i)

        repeated = {seq: pos for seq, pos in positions.items() if len(pos) > 1}
        if not repeated:
            break
        found.update(repeated)
    return found


def distances(ciphertext: str, min_len: int = 3) -> list[int]:
    gaps = set()
    for positions in repeats(ciphertext, min_len).values():
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                gaps.add(positions[j] - positions[i])
    return sorted(gaps)


def factor_tally(ciphertext: str, max_factor: int = 20) -> dict[int, int]:
    gaps = distances(ciphertext)
    return {f: sum(1 for d in gaps if d % f == 0) for f in range(2, max_factor + 1)}
