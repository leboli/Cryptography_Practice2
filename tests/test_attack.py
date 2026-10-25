import subprocess
import sys
from pathlib import Path

import pytest

from attack import run
from substitution.cyphers import monoalpha, vigenere
from transposition.cyphers import columnar
from utils.basics import normalise
from utils.constants import ENGLISH_TEXT, SPANISH_TEXT

ATTACK = Path(__file__).resolve().parent.parent / "attack.py"
PLAIN = normalise(ENGLISH_TEXT)[:300]


def test_columnar_without_cols():
    cipher = columnar.encrypt(PLAIN, "ZEBRAS")  # 300 letters, divisible by 2..6
    out = run(cipher)
    assert "Family:            transposition" in out
    assert "columns: 6" in out
    assert out.splitlines()[-1] == PLAIN


def test_columnar_with_cols():
    cipher = columnar.encrypt(PLAIN, "KEY")
    out = run(cipher, cols=3)
    assert "Column counts tried: [3]" in out
    assert out.splitlines()[-1] == PLAIN


def test_vigenere():
    out = run(vigenere.encrypt(PLAIN, "LEMON"))
    assert "polyalphabetic" in out
    assert "Key length: 5" in out
    assert out.splitlines()[-2:] == ["key: LEMON", PLAIN]


def test_vigenere_spanish():
    plain = normalise(SPANISH_TEXT)
    out = run(vigenere.encrypt(plain, "CLAVE"), language="es")
    assert out.splitlines()[-2:] == ["key: CLAVE", plain]


def test_monoalphabetic_prints_assistant():
    out = run(monoalpha.encrypt(PLAIN, monoalpha.key_from_keyword("CRYPTO")))
    assert "monoalphabetic" in out
    assert "FREQUENCY ASSISTANT REPORT" in out


def test_measurements_always_printed():
    for cipher in [columnar.encrypt(PLAIN, "KEY"), vigenere.encrypt(PLAIN, "KEY")]:
        out = run(cipher)
        assert "Index of coinc.:" in out
        assert "Chi-squared / n:" in out


@pytest.mark.parametrize("text", ["", "A", "123 !!"])
def test_too_short(text):
    with pytest.raises(ValueError):
        run(text)


def test_cols_not_a_divisor():
    with pytest.raises(ValueError):
        run(columnar.encrypt(PLAIN, "KEY"), cols=7)


def test_no_divisor_from_2_to_8():
    # 307 is prime, so no column count can be tried without --cols
    cipher = columnar.encrypt(normalise(ENGLISH_TEXT)[:307], "A")
    with pytest.raises(ValueError):
        run(cipher)


def test_cli(tmp_path):
    cipher = tmp_path / "cipher.txt"
    cipher.write_text(columnar.encrypt(PLAIN, "ZEBRAS"), encoding="utf-8")
    result = subprocess.run([sys.executable, str(ATTACK), "--in", str(cipher), "--cols", "6"],
                            capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout.splitlines()[-1] == PLAIN


def test_cli_error_exits_cleanly():
    result = subprocess.run([sys.executable, str(ATTACK)], input="1",
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert "error" in result.stderr
    assert "Traceback" not in result.stderr
