import unicodedata

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def normalise(text: str) -> str:
    # uppercase, accents folded (É -> E, Ñ -> N), everything outside A-Z removed
    text = unicodedata.normalize("NFD", text.upper())
    return "".join(c for c in text if c in ALPHABET)


def to_numbers(text: str) -> list[int]: # normalised text -> 0..25
    return [ALPHABET.index(c) for c in normalise(text)]


def to_letters(nums: list[int]) -> str: # 0..25 -> text
    for n in nums:
        if not 0 <= n <= 25:
            raise ValueError(f"{n} is not a letter number (must be 0..25)")
    return "".join(ALPHABET[n] for n in nums)


def egcd(a: int, b: int) -> tuple[int, int, int]:
    """
    Euclidian algorithm. Returns (gcd, x, y) such that gcd = ax + by.
    """
    if b == 0:
        gcd, x, y = a, 1, 0
    else:
        gcd, x1, y1 = egcd(b, a % b)
        x, y = y1, x1 - (a // b) * y1
    if gcd < 0:
        gcd, x, y = -gcd, -x, -y
    return gcd, x, y


def modinv(a: int, m: int) -> int:
    gcd, x, _ = egcd(a, m)
    if gcd != 1:
        raise ValueError(f"No modular inverse for {a} mod {m} (gcd is {gcd})")
    return x % m


def xor_bytes(data: bytes, key: bytes) -> bytes: # key repeats cyclically
    if len(key) == 0:
        raise ValueError("XOR key must not be empty")
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
