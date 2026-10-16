from utils.basics import to_numbers, to_letters


def encrypt(plaintext: str, k: int) -> str:
    return to_letters([(x + k) % 26 for x in to_numbers(plaintext)])


def decrypt(ciphertext: str, k: int) -> str:
    return encrypt(ciphertext, -k)
