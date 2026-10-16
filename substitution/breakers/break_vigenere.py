from substitution.cyphers.vigenere import cosets, decrypt as vigenere_decrypt
from substitution.breakers.break_caesar import break_caesar
from utils.basics import to_letters


def break_vigenere(ciphertext: str, m: int, language: str = "en") -> tuple[str, str]:
    # m is the key length. Each coset is just a Caesar cipher, so break them one by one.
    shifts = [break_caesar(coset, language)[0] for coset in cosets(ciphertext, m)]
    key = to_letters(shifts)
    return key, vigenere_decrypt(ciphertext, key)
