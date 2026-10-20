import pytest
from transposition.cyphers.railfence import encrypt, decrypt

class TestRailFence:

    def test_encrypt(self):
        assert encrypt("MYSECRETMESSAGE", 2) == "MSCEMSAEYERTESG"
        assert encrypt("MYSECRETMESSAGE", 3) == "MCMAYERTESGSESE"
        assert encrypt("MYSECRETMESSAGE", 4) == "MEAYRTSGSCMSEEE"

    def test_decrypt(self):
        assert decrypt("MSCEMSAEYERTESG", 2) == "MYSECRETMESSAGE"
        assert decrypt("MCMAYERTESGSESE", 3) == "MYSECRETMESSAGE"
        assert decrypt("MEAYRTSGSCMSEEE", 4) == "MYSECRETMESSAGE"

    def test_round_trip(self):
        plaintext = "Cryptography is the only branch of computing designed against an intelligent opponent!"
        for rails in range(1, 10):
            ciphertext = encrypt(plaintext, rails)
            decrypted = decrypt(ciphertext, rails)
            assert decrypted == plaintext

    def test_invalid_rails(self):
        with pytest.raises(ValueError):
            encrypt("MYSECRETMESSAGE", 0)
        with pytest.raises(ValueError):
            decrypt("MYSECRETMESSAGE", 0)
        with pytest.raises(ValueError):
            encrypt("MYSECRETMESSAGE", -1)
        with pytest.raises(ValueError):
            decrypt("MYSECRETMESSAGE", -1)

    def test_edge_cases(self):
        assert encrypt("", 5) == ""
        assert decrypt("", 5) == ""
        assert encrypt("a", 1) == "a"
        assert decrypt("a", 1) == "a"
        assert encrypt("abcde", 5) == "abcde"
        assert decrypt("abcde", 5) == "abcde"
