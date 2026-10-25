import pytest

from analysis.measure import classify, index_of_coincidence
from substitution.cyphers.caesar import encrypt as caesar
from substitution.cyphers.monoalpha import encrypt as mono
from transposition.cyphers.columnar import encrypt as columnar
from transposition.cyphers.railfence import encrypt as railfence
from utils.basics import ALPHABET
from utils.constants import ENGLISH_TEXT, SPANISH_TEXT


class TestCheckValues:
    def test_handout_values(self):
        # exact fractions from the definition, with the n(n - 1) denominator
        assert index_of_coincidence("CRYPTANALYSIS") == pytest.approx(6 / 156)
        assert index_of_coincidence("THEINDEXOFCOINCIDENCE") == pytest.approx(34 / 420)

    def test_not_n_squared(self):
        # with n^2 it would be 4/16 = 0.25
        assert index_of_coincidence("AABB") == pytest.approx(4 / 12)


class TestValues:
    def test_one_repeated_letter(self):
        assert index_of_coincidence("AAAAAAAAAA") == 1.0

    def test_all_letters_different(self):
        assert index_of_coincidence(ALPHABET) == 0.0

    def test_uniform_text_close_to_random(self):
        assert index_of_coincidence(ALPHABET * 40) == pytest.approx(1 / 26, abs=0.001)

    def test_english_text(self):
        assert 0.060 < index_of_coincidence(ENGLISH_TEXT) < 0.075

    @pytest.mark.parametrize("rails", [2, 3, 5])
    def test_unchanged_by_transposition(self, rails):
        # a transposition only moves letters, so the counts stay the same
        assert index_of_coincidence(railfence(ENGLISH_TEXT, rails)) == pytest.approx(
            index_of_coincidence(ENGLISH_TEXT))


class TestNormalisation:
    def test_spaces_and_case_ignored(self):
        assert index_of_coincidence("the index of coincidence") == pytest.approx(34 / 420)

    def test_punctuation_ignored(self):
        assert index_of_coincidence("Crypt-analysis!") == pytest.approx(6 / 156)


class TestEdgeCases:
    def test_empty_input(self):
        assert index_of_coincidence("") == 0.0

    def test_single_character(self):
        assert index_of_coincidence("A") == 0.0

    def test_no_letters(self):
        assert index_of_coincidence("123 !?") == 0.0

    def test_one_letter_after_normalising(self):
        assert index_of_coincidence("A!") == 0.0


class TestClassify:
    @pytest.mark.parametrize("keyword", ["ZEBRAS", "CRYPTO", "KEY"])
    def test_columnar_is_transposition(self, keyword):
        assert classify(columnar(ENGLISH_TEXT, keyword)) == "transposition"

    def test_railfence_is_transposition(self):
        assert classify(railfence(ENGLISH_TEXT, 3)) == "transposition"

    def test_plaintext_is_transposition(self):
        # the plaintext is the identity transposition
        assert classify(ENGLISH_TEXT) == "transposition"

    def test_monoalphabetic_is_substitution(self):
        assert classify(mono(ENGLISH_TEXT, "QWERTYUIOPASDFGHJKLZXCVBNM")) == "substitution"

    @pytest.mark.parametrize("shift", [1, 3, 13])
    def test_caesar_is_substitution(self, shift):
        assert classify(caesar(ENGLISH_TEXT, shift)) == "substitution"

    def test_spanish(self):
        assert classify(railfence(SPANISH_TEXT, 4), "es") == "transposition"
        assert classify(caesar(SPANISH_TEXT, 5), "es") == "substitution"

    def test_unknown_language(self):
        with pytest.raises(ValueError):
            classify(ENGLISH_TEXT, "fr")
