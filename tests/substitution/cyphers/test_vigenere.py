import pytest

from substitution.cyphers.vigenere import encrypt, decrypt, cosets
from utils.basics import normalise

TEXT = "Cryptography is the only branch of computing designed against an intelligent opponent!"


class TestCheckValues:
    def test_encrypt_values(self):
        assert encrypt("MYSECRETMESSAGE", "KEY") == "WCQOGPOXKOWQKKC"
        assert encrypt("attackatdawn", "LEMON") == "LXFOPVEFRNHR"

    def test_decrypt_values(self):
        assert decrypt("WCQOGPOXKOWQKKC", "KEY") == "MYSECRETMESSAGE"
        assert decrypt("LXFOPVEFRNHR", "LEMON") == "ATTACKATDAWN"

    def test_cosets_value(self):
        assert cosets("ABCDEF", 3) == ["AD", "BE", "CF"]


class TestRoundTrip:
    @pytest.mark.parametrize("key", ["A", "KEY", "LEMON", "lemon", "NETWORK", "ZZZZZZZZZZZZ"])
    def test_round_trip(self, key):
        assert decrypt(encrypt(TEXT, key), key) == normalise(TEXT)

    def test_key_a_is_identity(self):
        assert encrypt("hello", "A") == "HELLO"

    def test_key_does_not_advance_on_punctuation(self):
        assert encrypt("attack at dawn!", "LEMON") == "LXFOPVEFRNHR"


class TestCosets:
    def test_each_coset_was_shifted_by_one_key_letter(self):
        ciphertext = encrypt(TEXT, "KEY")
        plain_cosets = cosets(normalise(TEXT), 3)
        for coset, plain, key_letter in zip(cosets(ciphertext, 3), plain_cosets, "KEY"):
            assert decrypt(coset, key_letter) == plain

    def test_joining_cosets_back_gives_all_letters(self):
        parts = cosets("LXFOPVEFRNHR", 5)
        assert sorted("".join(parts)) == sorted("LXFOPVEFRNHR")

    def test_ignores_non_letters(self):
        assert cosets("AB CD, EF", 3) == ["AD", "BE", "CF"]

    def test_m_equal_to_one(self):
        assert cosets("ABCDEF", 1) == ["ABCDEF"]

    def test_text_shorter_than_m(self):
        assert cosets("AB", 4) == ["A", "B", "", ""]

    @pytest.mark.parametrize("m", [0, -1])
    def test_rejects_invalid_m(self, m):
        with pytest.raises(ValueError):
            cosets("ABCDEF", m)


class TestInvalidKeys:
    @pytest.mark.parametrize("key", ["", "123", "K3Y", "KEY WORD", "KEY!", "CLÉ"])
    def test_rejects_bad_key(self, key):
        with pytest.raises(ValueError):
            encrypt("hello", key)
        with pytest.raises(ValueError):
            decrypt("HELLO", key)


class TestEdgeCases:
    def test_empty_input(self):
        assert encrypt("", "KEY") == ""
        assert decrypt("", "KEY") == ""

    def test_single_character(self):
        assert encrypt("a", "KEY") == "K"
        assert decrypt("K", "KEY") == "A"

    def test_no_letters(self):
        assert encrypt("123 !?", "KEY") == ""
        assert decrypt("123 !?", "KEY") == ""

    def test_input_shorter_than_key(self):
        assert encrypt("hi", "LEMON") == "SM"
        assert decrypt("SM", "LEMON") == "HI"
