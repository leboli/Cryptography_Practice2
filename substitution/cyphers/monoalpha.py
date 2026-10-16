from utils.basics import ALPHABET, normalise, to_numbers, to_letters


def check_key(key: str) -> list[int]:
    # the key must be the 26 letters A-Z, each exactly once (any case)
    if sorted(key.upper()) != list(ALPHABET):
        raise ValueError("Key must be a permutation of the alphabet (26 unique letters A-Z)")
    return to_numbers(key)


def encrypt(plaintext: str, key: str) -> str:
    key_nums = check_key(key)
    return to_letters([key_nums[x] for x in to_numbers(plaintext)])


def decrypt(ciphertext: str, key: str) -> str:
    key_nums = check_key(key)
    inverse = [key_nums.index(i) for i in range(26)]
    return to_letters([inverse[y] for y in to_numbers(ciphertext)])


def key_from_keyword(keyword: str) -> str:
    # keyword letters first (no repeats), then the rest of the alphabet
    letters = normalise(keyword)
    if not letters:
        raise ValueError("Keyword must contain at least one letter")

    key = ""
    for c in letters + ALPHABET:
        if c not in key:
            key += c
    return key
