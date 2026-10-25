import random

import pytest

from transposition.breakers.break_columnar import attack, bigram_log_table, bigram_score, order_to_keyword
from transposition.cyphers.columnar import encrypt, key_order
from utils.basics import ALPHABET, normalise
from utils.constants import ENGLISH_TEXT, SPANISH_TEXT
from tests.helpers import random_fragments


def padded(plaintext: str, n_cols: int, pad: str = "X") -> str:
    rows = -(-len(plaintext) // n_cols)
    return plaintext.ljust(rows * n_cols, pad)


class TestBigramTable:
    def test_every_pair_present(self):
        assert len(bigram_log_table("en")) == 26 * 26
        assert len(bigram_log_table("es")) == 26 * 26

    def test_most_common_pair(self):
        en = bigram_log_table("en")
        es = bigram_log_table("es")
        assert max(en, key=en.get) == "TH"
        assert max(es, key=es.get) == "EN"

    def test_common_beats_rare(self):
        table = bigram_log_table("en")
        assert table["TH"] > table["QZ"]

    def test_unknown_language(self):
        with pytest.raises(ValueError):
            bigram_log_table("fr")


class TestBigramScore:
    def test_text_beats_its_shuffle(self):
        text = normalise(ENGLISH_TEXT)[:200]
        shuffled = "".join(random.Random(0).sample(text, len(text)))
        assert bigram_score(text) > bigram_score(shuffled)

    def test_sum_over_adjacent_pairs(self):
        table = bigram_log_table("en")
        assert bigram_score("THE") == pytest.approx(table["TH"] + table["HE"])
        assert bigram_score("T") == 0


class TestOrderToKeyword:
    @pytest.mark.parametrize("keyword", ["CIPHER", "ENIGMA", "KASISKI", "BLETCHLEY"])
    def test_same_order_as_keyword(self, keyword):
        order = tuple(key_order(keyword))
        assert key_order(order_to_keyword(order)) == list(order)


class TestAttack:
    @pytest.mark.parametrize("n_cols", [4, 5, 6, 7])
    @pytest.mark.parametrize("text, language", [(ENGLISH_TEXT, "en"), (SPANISH_TEXT, "es")])
    def test_20_generated_ciphertexts(self, text, language, n_cols):
        # 120 letters: 100% in the C3 measurement
        rng = random.Random(n_cols)
        for fragment in random_fragments(text, 120, count=20, seed=n_cols):
            keyword = "".join(rng.sample(ALPHABET, n_cols))
            order, plaintext = attack(encrypt(fragment, keyword), n_cols, language)
            assert order == tuple(key_order(keyword))
            assert plaintext == padded(fragment, n_cols)

    def test_padding_is_kept(self):
        plaintext = "Four score and seven years ago our fathers brought forth on this continent"
        order, found = attack(encrypt(plaintext, "ZEBRAS"), 6)
        assert order == (6, 3, 2, 4, 1, 5)
        assert found == padded(normalise(plaintext), 6)
        assert found.endswith("XX")

    def test_spaces_and_case_ignored(self):
        ciphertext = encrypt(ENGLISH_TEXT[:200], "ROTOR").lower()
        assert attack(" ".join(ciphertext), 5)[0] == (3, 1, 5, 2, 4)

    def test_one_column(self):
        assert attack("HELLO", 1) == ((1,), "HELLO")

    def test_length_not_a_multiple(self):
        with pytest.raises(ValueError):
            attack("ABCDEFG", 3)
