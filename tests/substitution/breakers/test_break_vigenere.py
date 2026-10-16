import random

import pytest

from substitution.cyphers.vigenere import encrypt
from substitution.breakers.break_vigenere import break_vigenere
from utils.basics import ALPHABET, normalise
from utils.constants import ENGLISH_TEXT, SPANISH_TEXT
from tests.helpers import random_fragments

# From the C3 measurement: reliable once every coset has about 40 letters,
# so the total length needed is about 40 * m.
RELIABLE_LENGTHS = {3: 120, 5: 200, 7: 300}


class TestBreakVigenere:
    @pytest.mark.parametrize("m", [3, 5, 7])
    @pytest.mark.parametrize("text, language", [(ENGLISH_TEXT, "en"), (SPANISH_TEXT, "es")])
    def test_20_generated_ciphertexts_at_reliable_length(self, text, language, m):
        rng = random.Random(m)
        for fragment in random_fragments(text, RELIABLE_LENGTHS[m], count=20, seed=m):
            key = "".join(rng.choice(ALPHABET) for _ in range(m))
            found_key, found_plaintext = break_vigenere(encrypt(fragment, key), m, language)
            assert found_key == key
            assert found_plaintext == fragment

    def test_long_text_with_punctuation(self):
        plaintext = ("Every single journey begins with just a simple step, no matter how "
                     "long or difficult the path may be. Cryptography is the only branch "
                     "of computing designed against an intelligent adaptive opponent!")
        found_key, found_plaintext = break_vigenere(encrypt(plaintext, "LEMON"), 5)
        assert found_key == "LEMON"
        assert found_plaintext == normalise(plaintext)

    def test_m_equal_to_one_is_caesar(self):
        found_key, _ = break_vigenere(encrypt(ENGLISH_TEXT[:300], "H"), 1)
        assert found_key == "H"

    def test_invalid_m_rejected(self):
        with pytest.raises(ValueError):
            break_vigenere("LXFOPVEFRNHR", 0)

    def test_unknown_language_rejected(self):
        with pytest.raises(ValueError):
            break_vigenere("LXFOPVEFRNHR", 5, "fr")

    def test_ciphertext_shorter_than_key_does_not_crash(self):
        found_key, found_plaintext = break_vigenere("AB", 4)
        assert len(found_key) == 4
        assert len(found_plaintext) == 2
