import pytest

from substitution.cyphers.monoalpha import encrypt, decrypt, key_from_keyword
from utils.basics import normalise

KEY = "MNBVCXZASDFGHJKLPOIUYTREWQ"
TEXT = "Cryptography is the only branch of computing designed against an intelligent opponent!"


class TestCheckValues:
    def test_key_from_keyword(self):
        assert key_from_keyword("CRYPTO") == "CRYPTOABDEFGHIJKLMNQSUVWXZ"

    def test_encrypt_values(self):
        assert encrypt("HELLO", KEY) == "ACGGK"
        assert encrypt("BOB", KEY) == "NKN"

    def test_decrypt_values(self):
        assert decrypt("ACGGK", KEY) == "HELLO"
        assert decrypt("NKN", KEY) == "BOB"


class TestKeyFromKeyword:
    def test_repeated_letters_used_once(self):
        assert key_from_keyword("BALLOON") == "BALONCDEFGHIJKMPQRSTUVWXYZ"

    def test_lowercase_and_spaces(self):
        assert key_from_keyword("crypto 2026") == key_from_keyword("CRYPTO")

    def test_result_is_always_a_permutation(self):
        for keyword in ["A", "ZEBRA", "KEYWORD", "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"]:
            assert sorted(key_from_keyword(keyword)) == list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    @pytest.mark.parametrize("keyword", ["", "123", "!!!"])
    def test_rejects_keyword_without_letters(self, keyword):
        with pytest.raises(ValueError):
            key_from_keyword(keyword)


class TestRoundTrip:
    @pytest.mark.parametrize("key", [
        KEY,
        KEY.lower(),
        key_from_keyword("CRYPTO"),
        key_from_keyword("KEYWORD"),
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    ])
    def test_round_trip(self, key):
        assert decrypt(encrypt(TEXT, key), key) == normalise(TEXT)


class TestInvalidKeys:
    @pytest.mark.parametrize("key", [
        "",                                     # empty
        "SHORTKEY",                             # too short
        "ABCDEFGHIJKLMNOPQRSTUVWXYZA",          # too long
        "AABBCCDDEEFFGGHHIIJJKKLLMM",           # duplicates
        "ABCDEFGHIJKLMNOPQRSTUVWXY1",           # digit
        "ABCDEFGHIJKLMNOPQRSTUVWXY ",           # space
        "ÑBCDEFGHIJKLMNOPQRSTUVWXYZ",           # letter outside A-Z
    ])
    def test_rejects_non_permutation(self, key):
        with pytest.raises(ValueError):
            encrypt("hello", key)
        with pytest.raises(ValueError):
            decrypt("HELLO", key)


class TestEdgeCases:
    def test_empty_input(self):
        assert encrypt("", KEY) == ""
        assert decrypt("", KEY) == ""

    def test_single_character(self):
        assert encrypt("a", KEY) == "M"
        assert decrypt("M", KEY) == "A"

    def test_no_letters(self):
        assert encrypt("123 !?", KEY) == ""
        assert decrypt("123 !?", KEY) == ""
