import pytest

from substitution.cyphers.caesar import encrypt
from substitution.breakers.break_caesar import break_caesar, chi_squared, frequency_table
from utils.basics import normalise
from utils.constants import ENGLISH_TEXT, SPANISH_TEXT, ENGLISH_FREQUENCY_TABLE, SPANISH_FREQUENCY_TABLE
from tests.helpers import random_fragments

RELIABLE_LENGTH = 30  # from the C1 measurement


class TestChiSquared:
    def test_normalised_by_length(self):
        # the same text repeated has the same letter proportions, so the same score
        text = normalise(ENGLISH_TEXT)[:100]
        assert chi_squared(text, ENGLISH_FREQUENCY_TABLE) == pytest.approx(
            chi_squared(text * 5, ENGLISH_FREQUENCY_TABLE))

    def test_english_scores_better_with_english_table(self):
        assert chi_squared(ENGLISH_TEXT, ENGLISH_FREQUENCY_TABLE) < chi_squared(ENGLISH_TEXT, SPANISH_FREQUENCY_TABLE)

    def test_spanish_scores_better_with_spanish_table(self):
        assert chi_squared(SPANISH_TEXT, SPANISH_FREQUENCY_TABLE) < chi_squared(SPANISH_TEXT, ENGLISH_FREQUENCY_TABLE)

    def test_real_text_scores_better_than_shifted_text(self):
        assert chi_squared(ENGLISH_TEXT, ENGLISH_FREQUENCY_TABLE) < chi_squared(encrypt(ENGLISH_TEXT, 3), ENGLISH_FREQUENCY_TABLE)

    def test_no_letters_is_infinite(self):
        assert chi_squared("", ENGLISH_FREQUENCY_TABLE) == float("inf")
        assert chi_squared("123 !?", ENGLISH_FREQUENCY_TABLE) == float("inf")


class TestFrequencyTables:
    @pytest.mark.parametrize("language", ["en", "es"])
    def test_tables_cover_a_to_z_and_sum_to_one(self, language):
        table = frequency_table(language)
        assert sorted(table) == list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        assert sum(table.values()) == pytest.approx(1.0, abs=0.01)

    def test_unknown_language_rejected(self):
        with pytest.raises(ValueError):
            frequency_table("fr")
        with pytest.raises(ValueError):
            break_caesar("KHOOR", "fr")


class TestBreakCaesar:
    @pytest.mark.parametrize("text, language", [(ENGLISH_TEXT, "en"), (SPANISH_TEXT, "es")])
    def test_20_generated_ciphertexts_at_reliable_length(self, text, language):
        fragments = random_fragments(text, RELIABLE_LENGTH, count=20, seed=1)
        for i, fragment in enumerate(fragments):
            key = (i * 7 + 3) % 26  # different keys, including 0
            found_key, found_plaintext = break_caesar(encrypt(fragment, key), language)
            assert found_key == key
            assert found_plaintext == fragment

    def test_long_text_with_punctuation(self):
        plaintext = "Cryptography is the only branch of computing designed against an intelligent, adaptive opponent."
        found_key, found_plaintext = break_caesar(encrypt(plaintext, 6))
        assert found_key == 6
        assert found_plaintext == normalise(plaintext)

    def test_defaults_to_english(self):
        ciphertext = encrypt(ENGLISH_TEXT[:200], 11)
        assert break_caesar(ciphertext) == break_caesar(ciphertext, "en")

    def test_no_letters_does_not_crash(self):
        assert break_caesar("123 !?") == (0, "")
