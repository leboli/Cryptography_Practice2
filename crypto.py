import argparse
import sys

from substitution.cyphers import caesar, affine, monoalpha, vigenere
from substitution.breakers.break_caesar import break_caesar
from substitution.breakers.break_affine import break_affine
from substitution.breakers.break_vigenere import break_vigenere
from substitution.breakers.assist import report
from utils.basics import normalise


def build_parser() -> argparse.ArgumentParser:
    # --in, --out and --lang are shared by every command
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--in", dest="infile", help="input file (default: stdin)")
    common.add_argument("--out", dest="outfile", help="output file (default: stdout)")
    common.add_argument("--lang", choices=["en", "es"], default="en", help="language for the breakers")

    parser = argparse.ArgumentParser(prog="crypto.py", description="Substitution ciphers and their attacks")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("caesar", parents=[common], help="Caesar cipher")
    p.add_argument("mode", choices=["encrypt", "decrypt"])
    p.add_argument("--key", type=int, required=True, help="shift")

    p = sub.add_parser("affine", parents=[common], help="affine cipher")
    p.add_argument("mode", choices=["encrypt", "decrypt"])
    p.add_argument("--a", type=int, required=True, help="multiplier, coprime with 26")
    p.add_argument("--b", type=int, required=True, help="shift")

    p = sub.add_parser("mono", parents=[common], help="monoalphabetic substitution")
    p.add_argument("mode", choices=["encrypt", "decrypt"])
    key = p.add_mutually_exclusive_group(required=True)
    key.add_argument("--keyword", help="keyword used to build the key")
    key.add_argument("--key", help="full 26-letter permutation")

    p = sub.add_parser("vigenere", parents=[common], help="Vigenere cipher")
    p.add_argument("mode", choices=["encrypt", "decrypt"])
    p.add_argument("--key", required=True, help="keyword")

    p = sub.add_parser("break", parents=[common], help="recover the key from a ciphertext")
    p.add_argument("cipher", choices=["caesar", "affine", "vigenere"])
    p.add_argument("--m", type=int, help="key length (vigenere only)")

    sub.add_parser("assist", parents=[common], help="frequency report for a monoalphabetic ciphertext")

    return parser


def run(args, text: str) -> str:
    if args.command == "caesar":
        func = caesar.encrypt if args.mode == "encrypt" else caesar.decrypt
        return func(text, args.key)

    if args.command == "affine":
        func = affine.encrypt if args.mode == "encrypt" else affine.decrypt
        return func(text, args.a, args.b)

    if args.command == "mono":
        key = monoalpha.key_from_keyword(args.keyword) if args.keyword else args.key
        func = monoalpha.encrypt if args.mode == "encrypt" else monoalpha.decrypt
        return func(text, key)

    if args.command == "vigenere":
        func = vigenere.encrypt if args.mode == "encrypt" else vigenere.decrypt
        return func(text, args.key)

    if args.command == "break":
        if not normalise(text):
            raise ValueError("the ciphertext has no letters to break")
        if args.cipher == "caesar":
            key, plaintext = break_caesar(text, args.lang)
        elif args.cipher == "affine":
            (a, b), plaintext = break_affine(text, args.lang)
            key = f"a={a} b={b}"
        else:
            if args.m is None:
                raise ValueError("break vigenere needs the key length, use --m")
            key, plaintext = break_vigenere(text, args.m, args.lang)
        return f"key: {key}\n{plaintext}"

    return report(text, args.lang)


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.infile:
            with open(args.infile, encoding="utf-8") as f:
                text = f.read()
        else:
            text = sys.stdin.read()

        result = run(args, text)

        if args.outfile:
            with open(args.outfile, "w", encoding="utf-8") as f:
                f.write(result + "\n")
        else:
            print(result)
    except (ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
