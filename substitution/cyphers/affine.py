from utils.basics import egcd, modinv, to_numbers, to_letters


def check_key(a: int):
    if egcd(a, 26)[0] != 1:
        raise ValueError(f"Invalid key: a={a} is not coprime with 26")


def encrypt(plaintext: str, a: int, b: int) -> str:
    check_key(a)
    return to_letters([(a * x + b) % 26 for x in to_numbers(plaintext)])


def decrypt(ciphertext: str, a: int, b: int) -> str:
    check_key(a)
    a_inv = modinv(a, 26)
    return to_letters([a_inv * (y - b) % 26 for y in to_numbers(ciphertext)])


def valid_keys() -> list[tuple[int, int]]:
    return [(a, b) for a in range(1, 26) if egcd(a, 26)[0] == 1 for b in range(26)]
