import pytest

from analysis.keylength import RANDOM_IC, coset_ic, find_key_length, language_ic
from analysis.measure import index_of_coincidence
from substitution.cyphers.vigenere import encrypt
from utils.constants import ENGLISH_TEXT, SPANISH_TEXT


class TestCosetIc:
    def test_m_one_is_plain_index(self):
        text = encrypt(ENGLISH_TEXT, "LEMON")
        assert coset_ic(text, 1) == pytest.approx(index_of_coincidence(text))

    def test_average_of_cosets(self):
        # cosets of ABAB with m = 2 are AA and BB, both with index 1
        assert coset_ic("ABAB", 2) == pytest.approx(1.0)
        # cosets of ABCABC with m = 3 are AA, BB, CC
        assert coset_ic("ABCABC", 3) == pytest.approx(1.0)
        # with m = 1 it is the whole text: 3 pairs out of 15
        assert coset_ic("ABCABC", 1) == pytest.approx(6 / 30)

    def test_spaces_and_case_ignored(self):
        assert coset_ic("ab ab", 2) == coset_ic("ABAB", 2)

    def test_m_must_be_positive(self):
        with pytest.raises(ValueError):
            coset_ic("ABAB", 0)

    def test_true_length_and_multiples_stand_out(self):
        text = encrypt(ENGLISH_TEXT, "LEMON")
        for m in (5, 10, 15):
            assert coset_ic(text, m) > 0.06
        for m in (1, 2, 3, 4, 6, 7):
            assert coset_ic(text, m) < 0.05


class TestLanguageIc:
    def test_values(self):
        assert language_ic("en") == pytest.approx(0.0655, abs=1e-4)
        assert language_ic("es") == pytest.approx(0.0743, abs=1e-4)

    def test_above_random(self):
        assert language_ic("en") > RANDOM_IC
        assert language_ic("es") > RANDOM_IC

    def test_unknown_language(self):
        with pytest.raises(ValueError):
            language_ic("fr")


class TestFindKeyLength:
    @pytest.mark.parametrize("key", ["LEMON", "CIPHER", "SECRETS", "QUANTUMKEY"])
    def test_english(self, key):
        assert find_key_length(encrypt(ENGLISH_TEXT, key)) == len(key)

    @pytest.mark.parametrize("key", ["CLAVE", "QUIJOTE", "MANCHAZ"])
    def test_spanish(self, key):
        assert find_key_length(encrypt(SPANISH_TEXT, key), language="es") == len(key)

    def test_not_a_multiple(self):
        # 6, 9, 12 are as high as 3, the rule has to pick the smallest
        assert find_key_length(encrypt(ENGLISH_TEXT, "KEY")) == 3

    def test_not_a_divisor(self):
        # CIPHER (6) gives a bump at 3, it must not be taken
        assert find_key_length(encrypt(ENGLISH_TEXT, "CIPHER")) == 6

    def test_plain_text_gives_one(self):
        assert find_key_length(ENGLISH_TEXT) == 1

    def test_fallback_to_highest_average(self):
        # A..Z twice: m = 2 gives 0.04, the rest are lower, and none reach the threshold
        text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 2
        assert coset_ic(text, 2) == pytest.approx(26 / 650)
        assert find_key_length(text, max_m=4) == 2
