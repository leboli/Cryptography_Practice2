import pytest

from substitution.cyphers.caesar import encrypt, decrypt
from utils.basics import normalise

TEXT = "Cryptography is the only branch of computing designed against an intelligent opponent!"


class TestCheckValues:
    def test_handout_value(self):
        assert encrypt("MYSECRETMESSAGE", 3) == "PBVHFUHWPHVVDJH"

    def test_wraparound(self):
        assert encrypt("xyz", 3) == "ABC"
        assert decrypt("ABC", 3) == "XYZ"


class TestRoundTrip:
    @pytest.mark.parametrize("k", range(26))
    def test_every_key(self, k):
        assert decrypt(encrypt(TEXT, k), k) == normalise(TEXT)

    def test_accents_and_punctuation(self):
        text = "¡Mañana viajaré con mi familia!"
        assert decrypt(encrypt(text, 7), 7) == "MANANAVIAJARECONMIFAMILIA"


class TestKeysOutsideRange:
    @pytest.mark.parametrize("k", [29, 55, -23, -49])
    def test_reduced_mod_26(self, k):
        # all of these are 3 mod 26
        assert encrypt("MYSECRETMESSAGE", k) == "PBVHFUHWPHVVDJH"
        assert decrypt("PBVHFUHWPHVVDJH", k) == "MYSECRETMESSAGE"

    def test_key_26_is_identity(self):
        assert encrypt("HELLO", 26) == "HELLO"


class TestEdgeCases:
    def test_empty_input(self):
        assert encrypt("", 5) == ""
        assert decrypt("", 5) == ""

    def test_single_character(self):
        assert encrypt("a", 1) == "B"
        assert decrypt("B", 1) == "A"

    def test_no_letters(self):
        assert encrypt("123 !?", 5) == ""
        assert decrypt("123 !?", 5) == ""
