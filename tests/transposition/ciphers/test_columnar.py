import pytest

from transposition.cyphers.columnar import encrypt, decrypt, key_order, encrypt_double, decrypt_double
from utils.basics import normalise

TEXT = "THEQUICKBROWNFOGJUMPSOVERTHELAZYDOGANDKEEPSRUNNINGAWAY"  # no X, so every X is a pad
KEYWORDS = ["A", "AB", "ROTOR", "CIPHER", "ENIGMA", "KASISKI", "BLETCHLEY"]


def padded(plaintext: str, n_cols: int, pad: str = "X") -> str:
    # what decrypt must give back: the plaintext with its last row filled
    rows = -(-len(plaintext) // n_cols)
    return plaintext.ljust(rows * n_cols, pad)


class TestKeyOrder:
    @pytest.mark.parametrize("keyword, order", [
        ("ENIGMA", [2, 6, 4, 3, 5, 1]),
        ("ROTOR", [3, 1, 5, 2, 4]),
        ("KASISKI", [4, 1, 6, 2, 7, 5, 3]),
        ("BLETCHLEY", [1, 6, 3, 8, 2, 5, 7, 4, 9]),
        ("ZEBRAS", [6, 3, 2, 4, 1, 5]),
    ])
    def test_handout_values(self, keyword, order):
        assert key_order(keyword) == order

    def test_ties_left_to_right(self):
        assert key_order("AAA") == [1, 2, 3]
        assert key_order("BAB") == [2, 1, 3]

    @pytest.mark.parametrize("keyword", KEYWORDS)
    def test_is_a_permutation(self, keyword):
        assert sorted(key_order(keyword)) == list(range(1, len(keyword) + 1))


class TestCheckValues:
    def test_handout_values(self):
        assert encrypt("MYSECRETMESSAGE", "CIPHER") == "MEACSXEEXYTGSMERSX"
        assert encrypt("THE INDEX OF COINCIDENCE", "KASISKI") == "HOIICEENETXCDICEFDNON"

    def test_decrypt_returns_padded_plaintext(self):
        # "Decryption of a padded ciphertext returns the padded plaintext"
        assert decrypt("MEACSXEEXYTGSMERSX", "CIPHER") == "MYSECRETMESSAGEXXX"
        assert decrypt("HOIICEENETXCDICEFDNON", "KASISKI") == "THEINDEXOFCOINCIDENCE"

    def test_double_handout_value(self):
        plaintext = "THESAMEKEYMUSTNEVERBEUSEDTWICE"
        ciphertext = "WCTEIHSTAEVREBEUTMNSUEEDSEEMYK"
        assert encrypt_double(plaintext, "ROTOR", "ENIGMA") == ciphertext
        assert decrypt_double(ciphertext, "ROTOR", "ENIGMA") == plaintext


class TestPadding:
    def test_pad_is_a_parameter(self):
        assert encrypt("MYSECRETMESSAGE", "CIPHER", pad="Q") == "MEACSQEEQYTGSMERSQ"
        assert decrypt("MEACSQEEQYTGSMERSQ", "CIPHER") == "MYSECRETMESSAGEQQQ"

    def test_no_padding_when_length_fits(self):
        assert "X" not in encrypt("ABCDEF", "CIPHER")

    def test_trailing_x_of_the_plaintext_is_kept(self):
        # stripping X's would turn SIX into SI
        assert decrypt(encrypt("SIX", "AB"), "AB") == "SIXX"
        assert decrypt(encrypt("SIXX", "AB"), "AB") == "SIXX"

    @pytest.mark.parametrize("keyword", KEYWORDS)
    def test_ciphertext_fills_the_grid(self, keyword):
        for length in range(1, 30):
            assert len(encrypt(TEXT[:length], keyword)) % len(keyword) == 0


class TestRoundTrip:
    @pytest.mark.parametrize("keyword", KEYWORDS)
    def test_every_length(self, keyword):
        for length in range(len(TEXT) + 1):
            plaintext = TEXT[:length]
            assert decrypt(encrypt(plaintext, keyword), keyword) == padded(plaintext, len(keyword))

    @pytest.mark.parametrize("keyword", KEYWORDS)
    def test_only_reorders_letters(self, keyword):
        assert sorted(encrypt(TEXT, keyword)) == sorted(padded(TEXT, len(keyword)))

    def test_input_is_normalised(self):
        assert encrypt("My secret, message!", "CIPHER") == "MEACSXEEXYTGSMERSX"
        assert encrypt("the quick brown fox", "cipher") == encrypt("THEQUICKBROWNFOX", "CIPHER")


class TestDouble:
    def test_padding_at_both_passes(self):
        # 12 -> 15 -> 18 letters, and the intermediate ends in a pad X from the first pass
        plaintext = "ATTACKATDAWN"
        assert encrypt(plaintext, "ROTOR") == "TANADXAKWCAXTTX"
        ciphertext = encrypt_double(plaintext, "ROTOR", "ENIGMA")
        assert ciphertext == "XXXTATACXNWXDAXAKT"
        assert decrypt_double(ciphertext, "ROTOR", "ENIGMA") == padded(plaintext, 5)

    def test_naive_decrypt_is_garbage(self):
        # 9 letters -> 9 -> 12: decrypting pass by pass leaves the 3 pad X's of the
        # second pass in, so the first grid is read with 4 rows instead of 3
        plaintext = "ATTACKNOW"
        ciphertext = encrypt_double(plaintext, "KEY", "CIPHER")
        naive = decrypt(decrypt(ciphertext, "CIPHER"), "KEY")
        assert not naive.startswith(plaintext)
        assert decrypt_double(ciphertext, "KEY", "CIPHER") == plaintext

    @pytest.mark.parametrize("kw1, kw2", [
        ("ROTOR", "ENIGMA"), ("ENIGMA", "ROTOR"), ("KASISKI", "CIPHER"),
        ("ZEBRAS", "BLETCHLEY"), ("AB", "KASISKI"), ("CIPHER", "CIPHER"),
    ])
    def test_every_length(self, kw1, kw2):
        for length in range(len(TEXT) + 1):
            plaintext = TEXT[:length]
            ciphertext = encrypt_double(plaintext, kw1, kw2)
            assert decrypt_double(ciphertext, kw1, kw2) == padded(plaintext, len(kw1))

    def test_length_multiple_of_neither_key(self):
        # 23 letters: not a multiple of 5 nor of 6 (handout, section 3)
        plaintext = TEXT[:23]
        ciphertext = encrypt_double(plaintext, "ROTOR", "ENIGMA")
        assert len(ciphertext) == 30
        assert decrypt_double(ciphertext, "ROTOR", "ENIGMA") == padded(plaintext, 5)

    def test_keeps_inner_x(self):
        plaintext = "XEROXTHEXRAYS"
        ciphertext = encrypt_double(plaintext, "KASISKI", "ROTOR")
        assert decrypt_double(ciphertext, "KASISKI", "ROTOR") == padded(plaintext, 7)

    def test_pad_is_a_parameter(self):
        ciphertext = encrypt_double("ATTACKATDAWN", "ROTOR", "ENIGMA", pad="Q")
        assert ciphertext == "XXXTATACXNWXDAXAKT".replace("X", "Q")

    def test_not_injective_with_x_padding(self):
        # with an X pad two different plaintexts can give the same ciphertext,
        # so decrypt_double cannot always know where the first-pass padding ends
        assert encrypt_double("AX", "A", "ABC") == encrypt_double("A", "A", "ABC") == "AXX"


class TestEdgeCases:
    def test_empty_input(self):
        assert encrypt("", "CIPHER") == ""
        assert decrypt("", "CIPHER") == ""
        assert encrypt_double("", "ROTOR", "ENIGMA") == ""
        assert decrypt_double("", "ROTOR", "ENIGMA") == ""

    def test_single_character(self):
        assert encrypt("a", "CIPHER") == "AXXXXX"
        assert decrypt("AXXXXX", "CIPHER") == "AXXXXX"

    def test_no_letters(self):
        assert encrypt("123 !?", "CIPHER") == ""

    def test_plaintext_shorter_than_key(self):
        ciphertext = encrypt("HI", "CIPHER")
        assert len(ciphertext) == 6
        assert decrypt(ciphertext, "CIPHER") == "HIXXXX"

    def test_one_letter_keyword_is_identity(self):
        assert encrypt("MYSECRETMESSAGE", "K") == "MYSECRETMESSAGE"

    @pytest.mark.parametrize("ciphertext", ["AB", "ABCDEFG"])
    def test_ciphertext_not_filling_the_grid(self, ciphertext):
        # shorter than the number of columns, or not a multiple of it
        with pytest.raises(ValueError):
            decrypt(ciphertext, "CIPHER")
