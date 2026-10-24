import pytest
from transposition.cyphers.columnar import encrypt, decrypt, key_order

class TestColumnar:

    def test_key_order(self):
        assert key_order("ZEBRAS") == [6, 3, 2, 4, 1, 5]
        assert key_order("AAA") == [1, 2, 3]
        assert key_order("ENIGMA") == [2, 6, 4, 3, 5, 1]
        assert key_order("ROTOR") == [3, 1, 5, 2, 4]
        assert key_order("KASISKI") == [4, 1, 6, 2, 7, 5, 3]
        assert key_order("BLETCHLEY") == [1, 6, 3, 8, 2, 5, 7, 4, 9]

    def test_encrypt(self):
        assert encrypt("MYSECRETMESSAGE", "CIPHER")  == "MEACSXEEXYTGSMERSX"
        assert encrypt("THE INDEX OF COINCIDENCE", "KASISKI") == "HOIICEENETXCDICEFDNON"

    def test_decrypt(self):
        assert decrypt("MEACSXEEXYTGSMERSX", "CIPHER") == "MYSECRETMESSAGE"
        assert decrypt("HOIICEENETXCDICEFDNON", "KASISKI") == "THEINDEXOFCOINCIDENCE"

    def test_corectness(self):
        plaintext = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        keyword = "CIPHER"
        ciphertext = encrypt(plaintext, keyword)
        decrypted_text = decrypt(ciphertext, keyword)
        assert decrypted_text == plaintext.replace(" ", "").upper()