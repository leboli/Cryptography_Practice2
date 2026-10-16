import pytest

from substitution.cyphers.affine import encrypt, valid_keys
from substitution.breakers.break_affine import break_affine
from utils.basics import normalise
from utils.constants import ENGLISH_TEXT, SPANISH_TEXT
from tests.helpers import random_fragments

RELIABLE_LENGTH = 60  # from the C2 measurement


class TestBreakAffine:
    @pytest.mark.parametrize("text, language", [(ENGLISH_TEXT, "en"), (SPANISH_TEXT, "es")])
    def test_20_generated_ciphertexts_at_reliable_length(self, text, language):
        fragments = random_fragments(text, RELIABLE_LENGTH, count=20, seed=2)
        keys = valid_keys()
        for i, fragment in enumerate(fragments):
            a, b = keys[(i * 37) % len(keys)]  # spread over the whole key space
            found_key, found_plaintext = break_affine(encrypt(fragment, a, b), language)
            assert found_key == (a, b)
            assert found_plaintext == fragment

    def test_long_text_with_punctuation(self):
        plaintext = "Cryptography is the only branch of computing designed against an intelligent, adaptive opponent."
        found_key, found_plaintext = break_affine(encrypt(plaintext, 5, 8))
        assert found_key == (5, 8)
        assert found_plaintext == normalise(plaintext)

    def test_unknown_language_rejected(self):
        with pytest.raises(ValueError):
            break_affine("IZZISG", "fr")

    def test_no_letters_does_not_crash(self):
        found_key, found_plaintext = break_affine("123 !?")
        assert found_key in valid_keys()
        assert found_plaintext == ""
