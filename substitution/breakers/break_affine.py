from substitution.breakers.break_caesar import chi_squared, frequency_table
from substitution.cyphers.affine import decrypt as affine_decrypt, valid_keys


def break_affine(ciphertext: str, language: str = "en") -> tuple[tuple[int, int], str]:
    table = frequency_table(language)
    # only 12 * 26 = 312 keys, so just try them all
    a, b = min(valid_keys(), key=lambda k: chi_squared(affine_decrypt(ciphertext, *k), table))
    return (a, b), affine_decrypt(ciphertext, a, b)
