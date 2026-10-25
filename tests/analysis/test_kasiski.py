import pytest

from analysis.kasiski import distances, factor_tally, repeats
from substitution.cyphers.vigenere import encrypt
from utils.constants import ENGLISH_TEXT

CHECK = """ELQYR JVQDR LXEGB ELQQV ALQFE PTQOG DEZRG SIDSC PEFGO PXDOL
ELQYR JXAOA LPKGV D"""


class TestCheckValues:
    def test_elq_positions(self):
        assert repeats(CHECK)["ELQ"] == [0, 15, 50]

    def test_longest_repeat(self):
        found = repeats(CHECK)
        longest = max(found, key=len)
        assert longest == "ELQYRJ"
        assert found[longest] == [0, 50]

    def test_distances(self):
        assert distances(CHECK) == [15, 35, 50]

    def test_factor_tally(self):
        tally = factor_tally(CHECK)
        assert tally[5] == 3
        assert tally[2] == 1
        assert tally[7] == 1
        assert tally[3] == 1
        assert tally[4] == 0


class TestRepeats:
    def test_every_repeat_listed(self):
        assert repeats(CHECK) == {
            "ELQ": [0, 15, 50],
            "LQY": [1, 51], "QYR": [2, 52], "YRJ": [3, 53],
            "ELQY": [0, 50], "LQYR": [1, 51], "QYRJ": [2, 52],
            "ELQYR": [0, 50], "LQYRJ": [1, 51],
            "ELQYRJ": [0, 50],
        }

    def test_min_len(self):
        found = repeats(CHECK, min_len=5)
        assert set(found) == {"ELQYR", "LQYRJ", "ELQYRJ"}

    def test_shorter_than_min_len_ignored(self):
        assert repeats("ABXAB") == {}
        assert repeats("ABXAB", min_len=2) == {"AB": [0, 3]}

    def test_overlapping_repeat(self):
        assert repeats("AAAA") == {"AAA": [0, 1]}

    def test_spaces_and_case_ignored(self):
        assert repeats("the cat, the dog")["THE"] == [0, 6]


class TestDistances:
    def test_all_pairs(self):
        assert distances("ABCxABCyyABC") == [4, 5, 9]

    def test_same_distance_counted_once(self):
        assert distances("ABCDEFABCDEF") == [6]


class TestFactorTally:
    def test_one_is_left_out(self):
        tally = factor_tally(CHECK, max_factor=6)
        assert list(tally) == [2, 3, 4, 5, 6]

    def test_counts(self):
        tally = factor_tally("ABCxABCyyABC", max_factor=10)
        assert tally[2] == 1
        assert tally[3] == 1
        assert tally[4] == 1
        assert tally[9] == 1
        assert tally[5] == 1
        assert tally[6] == 0

    @pytest.mark.parametrize("key", ["LEMON", "CIPHER", "SECRETS"])
    def test_vigenere_key_length_stands_out(self, key):
        tally = factor_tally(encrypt(ENGLISH_TEXT, key))
        top = max(tally.values())
        best = max(f for f in tally if tally[f] >= 0.8 * top)
        assert best == len(key)


class TestEdgeCases:
    def test_empty_input(self):
        assert repeats("") == {}
        assert distances("") == []
        assert factor_tally("") == {f: 0 for f in range(2, 21)}

    def test_no_repeats(self):
        assert repeats("ABCDEFGHIJ") == {}
        assert distances("ABCDEFGHIJ") == []
