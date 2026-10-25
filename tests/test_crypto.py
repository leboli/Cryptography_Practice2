import subprocess
import sys
from pathlib import Path

CRYPTO = Path(__file__).resolve().parent.parent / "crypto.py"
TEXT = "Attack at dawn! The enemy will not expect us to come through the forest this early in the morning, so be ready and bring enough water for the whole day."
PLAIN = "ATTACKATDAWNTHEENEMYWILLNOTEXPECTUSTOCOMETHROUGHTHEFORESTTHISEARLYINTHEMORNINGSOBEREADYANDBRINGENOUGHWATERFORTHEWHOLEDAY"


def cli(*args, stdin=""):
    return subprocess.run([sys.executable, str(CRYPTO), *args], input=stdin,
                          capture_output=True, text=True)


def test_caesar_stdin_stdout():
    result = cli("caesar", "encrypt", "--key", "3", stdin="MYSECRETMESSAGE")
    assert result.returncode == 0
    assert result.stdout.strip() == "PBVHFUHWPHVVDJH"


def test_affine_files(tmp_path):
    message, cipher, plain = tmp_path / "message.txt", tmp_path / "cipher.txt", tmp_path / "plain.txt"
    message.write_text(TEXT, encoding="utf-8")
    assert cli("affine", "encrypt", "--a", "5", "--b", "8", "--in", str(message), "--out", str(cipher)).returncode == 0
    assert cli("affine", "decrypt", "--a", "5", "--b", "8", "--in", str(cipher), "--out", str(plain)).returncode == 0
    assert plain.read_text(encoding="utf-8").strip() == PLAIN


def test_mono_keyword():
    result = cli("mono", "encrypt", "--keyword", "CRYPTO", stdin="ABC")
    assert result.stdout.strip() == "CRY"


def test_vigenere():
    result = cli("vigenere", "encrypt", "--key", "LEMON", stdin="attackatdawn")
    assert result.stdout.strip() == "LXFOPVEFRNHR"


def test_break_caesar():
    cipher = cli("caesar", "encrypt", "--key", "7", stdin=TEXT).stdout
    result = cli("break", "caesar", stdin=cipher)
    assert result.stdout.split() == ["key:", "7", PLAIN]


def test_break_affine():
    cipher = cli("affine", "encrypt", "--a", "5", "--b", "8", stdin=TEXT).stdout
    result = cli("break", "affine", stdin=cipher)
    assert result.stdout.splitlines() == ["key: a=5 b=8", PLAIN]


def test_break_vigenere():
    cipher = cli("vigenere", "encrypt", "--key", "KEY", stdin=TEXT).stdout
    result = cli("break", "vigenere", "--m", "3", stdin=cipher)
    assert result.stdout.splitlines() == ["key: KEY", PLAIN]


def test_assist():
    result = cli("assist", stdin="QATNTYSMHQ")
    assert result.returncode == 0
    assert "FREQUENCY ASSISTANT REPORT" in result.stdout


def test_railfence():
    result = cli("railfence", "encrypt", "--rails", "3", stdin="MYSECRETMESSAGE")
    assert result.stdout.strip() == "MCMAYERTESGSESE"
    result = cli("railfence", "decrypt", "--rails", "3", stdin="MCMAYERTESGSESE")
    assert result.stdout.strip() == "MYSECRETMESSAGE"


def test_columnar_files(tmp_path):
    message, cipher = tmp_path / "message.txt", tmp_path / "cipher.txt"
    message.write_text("MYSECRETMESSAGE", encoding="utf-8")
    assert cli("columnar", "encrypt", "--key", "CIPHER", "--in", str(message), "--out", str(cipher)).returncode == 0
    assert cipher.read_text(encoding="utf-8").strip() == "MEACSXEEXYTGSMERSX"
    result = cli("columnar", "decrypt", "--key", "CIPHER", "--in", str(cipher))
    assert result.stdout.strip() == "MYSECRETMESSAGEXXX"


def test_measure():
    assert cli("measure", "ic", stdin="CRYPTANALYSIS").stdout.strip() == "0.0385"
    assert cli("measure", "classify", stdin=TEXT).stdout.strip() == "transposition"
    kasiski = cli("measure", "kasiski",
                  stdin="ELQYRJVQDRLXEGBELQQVALQFEPTQOGDEZRGSIDSCPEFGOPXDOLELQYRJXAOALPKGVD").stdout
    assert "ELQ: [0, 15, 50]" in kasiski
    assert "distances: [15, 35, 50]" in kasiski


def test_invalid_inputs_exit_cleanly():
    cases = [
        cli("affine", "encrypt", "--a", "13", "--b", "1", stdin=TEXT),
        cli("mono", "encrypt", "--key", "ABC", stdin=TEXT),
        cli("vigenere", "encrypt", "--key", "L3", stdin=TEXT),
        cli("break", "vigenere", stdin=TEXT),
        cli("break", "caesar", stdin="123 !!"),
        cli("caesar", "encrypt", "--key", "3", "--in", "does_not_exist.txt"),
        cli("caesar", "encrypt", "--key", "x", stdin=TEXT),
    ]
    for result in cases:
        assert result.returncode != 0
        assert "error" in result.stderr
        assert "Traceback" not in result.stderr
