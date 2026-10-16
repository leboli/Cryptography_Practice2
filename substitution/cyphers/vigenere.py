from utils.basics import ALPHABET, normalise, to_numbers, to_letters


def check_key(key: str) -> list[int]:
    if len(key) == 0 or any(c not in ALPHABET for c in key.upper()):
        raise ValueError("Key must be a non-empty string of letters A-Z")
    return to_numbers(key)


def shift(text: str, key: str, direction: int) -> str:
    # direction = 1 to encrypt, -1 to decrypt
    shifts = check_key(key)
    nums = to_numbers(text)
    return to_letters([(x + direction * shifts[i % len(shifts)]) % 26 for i, x in enumerate(nums)])


def encrypt(plaintext: str, key: str) -> str:
    return shift(plaintext, key, 1)


def decrypt(ciphertext: str, key: str) -> str:
    return shift(ciphertext, key, -1)


def cosets(ciphertext: str, m: int) -> list[str]:
    if m < 1:
        raise ValueError(f"Key length m must be at least 1, got {m}")
    letters = normalise(ciphertext)
    return [letters[i::m] for i in range(m)]
