import pytest

from transposition.cyphers.railfence import encrypt, decrypt
from utils.basics import normalise

TEXT = "Cryptography is the only branch of computing designed against an intelligent opponent!"


class TestCheckValues:
    @pytest.mark.parametrize("rails, ciphertext", [
        (2, "MSCEMSAEYERTESG"),
        (3, "MCMAYERTESGSESE"),
        (4, "MEAYRTSGSCMSEEE"),
    ])
    def test_handout_values(self, rails, ciphertext):
        assert encrypt("MYSECRETMESSAGE", rails) == ciphertext
        assert decrypt(ciphertext, rails) == "MYSECRETMESSAGE"

    def test_zigzag_by_hand(self):
        # A . . . E . . . I .
        # . B . D . F . H . J
        # . . C . . . G . . .
        assert encrypt("ABCDEFGHIJ", 3) == "AEIBDFHJCG"
        assert decrypt("AEIBDFHJCG", 3) == "ABCDEFGHIJ"


class TestRoundTrip:
    @pytest.mark.parametrize("rails", range(1, 21))
    def test_every_rail_count(self, rails):
        # the handout asks for the normalised plaintext back, not the raw input
        assert decrypt(encrypt(TEXT, rails), rails) == normalise(TEXT)

    @pytest.mark.parametrize("length", range(0, 30))
    @pytest.mark.parametrize("rails", [2, 3, 5, 7])
    def test_every_length(self, length, rails):
        # the last zigzag is cut at every possible point
        plaintext = normalise(TEXT)[:length]
        assert decrypt(encrypt(plaintext, rails), rails) == plaintext

    @pytest.mark.parametrize("rails", range(1, 10))
    def test_only_reorders_letters(self, rails):
        plaintext = normalise(TEXT)
        assert sorted(encrypt(plaintext, rails)) == sorted(plaintext)


class TestRails:
    def test_one_rail_is_identity(self):
        assert encrypt("MYSECRETMESSAGE", 1) == "MYSECRETMESSAGE"
        assert decrypt("MYSECRETMESSAGE", 1) == "MYSECRETMESSAGE"

    @pytest.mark.parametrize("rails", [15, 16, 100])
    def test_rails_at_least_length_is_identity(self, rails):
        assert encrypt("MYSECRETMESSAGE", rails) == "MYSECRETMESSAGE"
        assert decrypt("MYSECRETMESSAGE", rails) == "MYSECRETMESSAGE"

    @pytest.mark.parametrize("rails", [0, -1, -5])
    def test_invalid_rails(self, rails):
        with pytest.raises(ValueError):
            encrypt("MYSECRETMESSAGE", rails)
        with pytest.raises(ValueError):
            decrypt("MYSECRETMESSAGE", rails)

    @pytest.mark.parametrize("rails", [0, -1])
    def test_invalid_rails_on_empty_input(self, rails):
        # an invalid key is invalid whatever the text is
        with pytest.raises(ValueError):
            encrypt("", rails)
        with pytest.raises(ValueError):
            decrypt("", rails)


class TestEdgeCases:
    def test_empty_input(self):
        assert encrypt("", 5) == ""
        assert decrypt("", 5) == ""

    def test_single_character(self):
        assert encrypt("a", 1) == "A"
        assert decrypt("A", 1) == "A"
        assert encrypt("a", 3) == "A"
        assert decrypt("A", 3) == "A"

    def test_no_letters(self):
        assert encrypt("123 !?", 3) == ""

    def test_input_is_normalised(self):
        assert encrypt("my secret, message!", 3) == "MCMAYERTESGSESE"
