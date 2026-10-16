import pytest

from substitution.cyphers.affine import encrypt, decrypt, valid_keys
from utils.basics import normalise

TEXT = "Cryptography is the only branch of computing designed against an intelligent opponent!"


class TestCheckValues:
    def test_handout_value(self):
        assert encrypt("attack", 5, 8) == "IZZISG"
        assert decrypt("IZZISG", 5, 8) == "ATTACK"


class TestValidKeys:
    def test_size_is_12_times_26(self):
        assert len(valid_keys()) == 312

    def test_keys_are_unique_and_in_range(self):
        keys = valid_keys()
        assert len(set(keys)) == len(keys)
        assert all(0 <= b < 26 for _, b in keys)

    def test_valid_a_values(self):
        assert sorted({a for a, _ in valid_keys()}) == [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]


class TestRoundTrip:
    def test_every_valid_key(self):
        for a, b in valid_keys():
            assert decrypt(encrypt(TEXT, a, b), a, b) == normalise(TEXT)

    def test_b_outside_range(self):
        assert encrypt("attack", 5, 8 + 26) == "IZZISG"
        assert decrypt(encrypt(TEXT, 5, -3), 5, -3) == normalise(TEXT)

    def test_every_valid_key_is_a_permutation(self):
        # a real key must never send two letters to the same letter
        for a, b in valid_keys():
            assert len(set(encrypt("ABCDEFGHIJKLMNOPQRSTUVWXYZ", a, b))) == 26


class TestInvalidKeys:
    @pytest.mark.parametrize("a", [0, 2, 4, 13, 26, 52])
    def test_encrypt_rejects_a_not_coprime_with_26(self, a):
        with pytest.raises(ValueError, match=str(a)):
            encrypt("hello", a, 5)

    @pytest.mark.parametrize("a", [0, 2, 4, 13, 26, 52])
    def test_decrypt_rejects_a_not_coprime_with_26(self, a):
        with pytest.raises(ValueError, match=str(a)):
            decrypt("HELLO", a, 5)


class TestEdgeCases:
    def test_empty_input(self):
        assert encrypt("", 5, 8) == ""
        assert decrypt("", 5, 8) == ""

    def test_single_character(self):
        assert encrypt("a", 5, 8) == "I"
        assert decrypt("I", 5, 8) == "A"

    def test_no_letters(self):
        assert encrypt("123 !?", 5, 8) == ""
        assert decrypt("123 !?", 5, 8) == ""
