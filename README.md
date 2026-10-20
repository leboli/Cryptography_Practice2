# Practice 2 

20357 Cryptography - Bachelor in Data Science and Engineering - Universidad CEU San Pablo, 2026/27

**Author:** Lucia Eboli Courreges

**Repository:** https://github.com/leboli/Cryptography_Practice2.git

# How to run it

Everything runs with Python 3.11+ and the standard library. The only extra is `pytest` for the tests (`pip install pytest`). Run every command from the project root.

## Command-line interface (`crypto.py`)

```
python crypto.py <cipher> <mode> [key arguments] [--in FILE] [--out FILE] [--lang en|es]
```

- `--in FILE` reads the input from a file. Without it, the input comes from standard input.
- `--out FILE` writes the result to a file. Without it, the result goes to standard output.
- `--lang en|es` picks the frequency table for `break` and `assist` (default `en`).
- `python crypto.py -h` or `python crypto.py <command> -h` shows the help.

Encrypt and decrypt:

```
python crypto.py caesar   encrypt --key 3            --in message.txt
python crypto.py caesar   decrypt --key 3            --in cipher.txt
python crypto.py affine   encrypt --a 5 --b 8        --in message.txt --out cipher.txt
python crypto.py affine   decrypt --a 5 --b 8        --in cipher.txt --out plain.txt
python crypto.py mono     encrypt --keyword CRYPTO   --in message.txt
python crypto.py mono     decrypt --key MNBVCXZASDFGHJKLPOIUYTREWQ --in cipher.txt
python crypto.py vigenere encrypt --key LEMON        --in message.txt
python crypto.py vigenere decrypt --key LEMON        --in cipher.txt
```

For `mono`, give either `--keyword` (the key is built with `key_from_keyword`) or `--key` (the full 26-letter permutation).

Break a ciphertext (the first line of the output is the recovered key, the second the plaintext):

```
python crypto.py break caesar      --in cipher.txt --lang es
python crypto.py break affine      --in cipher.txt
python crypto.py break vigenere --m 5 --in cipher.txt
```

Frequency report for a monoalphabetic ciphertext (C4):

```
python crypto.py assist --in cipher.txt
```

Commands can also be chained through pipes, for example:

```
echo "Attack at dawn" | python crypto.py caesar encrypt --key 7 | python crypto.py break caesar
```

On invalid input (a non-invertible `a`, a key that is not a permutation, a Vigenere key with non-letters, a missing `--m`, a file that does not exist, a ciphertext with no letters to break...) the program prints `error: <reason>` to standard error and exits with status 1. Wrong or missing arguments are reported by `argparse` with exit status 2. No stack traces reach the user.

**Note on accents through stdin.** Files are read as UTF-8, so `--in` handles `ñ` and accented letters correctly. When piping text on Windows, the console may use another encoding and letters like `ñ` can arrive broken (for example PowerShell turns them into `?`, which is then removed). For Spanish text with accents, use `--in`.

## Measurements and tests

```
py -m experiments.measure_break_caesar     # C1 table
py -m experiments.measure_break_affine     # C2 table
py -m experiments.measure_break_vigenere   # C3 tables
py -m experiments.measure_assist           # C4 report on the given cryptogram
py -m pytest -v                         # all the tests
```

Every measurement uses a fixed seed, so running it again gives the same numbers as the tables below.

# Tests

From the root run (`pytest.ini` puts the project root on the import path, so both work):

```
py -m pytest -v
pytest -v
```

Every cipher test file follows the same structure: the check values published in the handout, round-trip `decrypt(encrypt(m, k), k) == normalised m`, rejection of invalid keys, and edge cases (empty input, a single character, input with no letters, and for Vigenere input shorter than the key). `tests/test_crypto.py` runs `crypto.py` as a real process and checks every command, both input/output modes, and that invalid input exits with an error and no stack trace. Each breaker is tested on 20 generated ciphertexts per language at the length where the measurements below say it is reliable (Caesar 30 letters, affine 60, Vigenere ~40 letters per coset).

# Deviations from the handout

- **Folder layout.** The modules are grouped in folders instead of sitting at the root (only `crypto.py` is at the root): `utils/basics.py`, `substitution/cyphers/{caesar,affine,monoalpha,vigenere}.py`, `substitution/breakers/{break_caesar,break_affine,break_vigenere,assist}.py`, `experiments/measure_*.py`. Function names and signatures are exactly the ones in the handout.
- **Accents are folded, not dropped.** Input is normalised to uppercase A-Z as required, but accented letters are first reduced to their base letter (`É -> E`, `Ñ -> N`) instead of being removed, so Spanish text keeps all its letters. Because of this, the frequency of Ñ is added to N in the Spanish table.
- **Unknown languages are rejected.** Any `language` other than `"en"` or `"es"` raises `ValueError`.

# Key spaces

| Cipher | Key | Key space | ~bits |
|--------|-----|-----------|-------|
| Caesar | shift k in 0..25 | 26 | 4.7 |
| Affine | (a, b), gcd(a, 26) = 1 | 12 x 26 = 312 | 8.3 |
| Monoalphabetic | permutation of A-Z | 26! ~ 4.03 x 10^26 | 88.4 |
| Vigenere | keyword of length m | 26^m | 4.7 m |

- **Caesar.** Any integer works as a key, but shifts are taken mod 26, so `k` and `k + 26` encrypt the same way. That leaves 26 different keys, and one of them (`k = 0`) does nothing, so only 25 are actually useful.
- **Affine.** `E(x) = (a x + b) mod 26`. For decryption `a` needs an inverse mod 26, which only exists when `gcd(a, 26) = 1`. Since 26 = 2 x 13, that rules out every even number and 13, leaving phi(26) = 12 values of `a` (1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25). `b` can be any of the 26 shifts. So `valid_keys()` returns **312** pairs. Values of `a` or `b` outside 0..25 are the same keys again after reducing mod 26, so they don't add new ones. Note that the 26 pairs with `a = 1` are just the Caesar keys.
- **Monoalphabetic.** The key is any ordering of the 26 letters. The first letter can go to 26 places, the second to 25, and so on, so there are 26! ~ 4.03 x 10^26 keys (about 2^88). `key_from_keyword` only reaches a small part of these (the tail of the key is always in alphabetical order), but the cipher itself accepts any permutation.
- **Vigenere.** Each of the m key letters is an independent shift, so there are 26^m keys of length m. If the attacker doesn't know m, it's the sum over all lengths up to some maximum. Some of these keys are repeats (for example `ABAB` is the same key as `AB`), so the real count is a little lower, but 26^m is the usual figure.

# C - Breakers

## C1 - Caesar breaker

Run the measurements:

```
py -m experiments.measure_break_caesar
```

Recovery rate (200 fragments per length, fixed seed):

| len | EN/EN | EN/ES | ES/ES | ES/EN |
|-----|-------|-------|-------|-------|
| 20  | 95.0% | 65.0% | 99.0% | 57.0% |
| 30  | 100%  | 62.5% | 100%  | 77.5% |
| 40  | 100%  | 68.5% | 100%  | 83.0% |
| 60  | 100%  | 68.5% | 100%  | 93.5% |
| 100 | 100%  | 65.5% | 100%  | 100%  |

(EN/EN = english text with english table, EN/ES = english text with spanish table, ES/ES = spanish text with spanish table, ES/EN = spanish text with english table)

1) **At which length does the breaker become reliable?**

   From 20 letters it's already above 90% with the right table, and by 30 letters it's basically always right (100% in my runs). Below that there just isn't enough text for chi-squared to tell the real key apart from the other 25 shifts.

2) **How much does the wrong language table cost you?**

   It depends on which table is wrong. Using the English table on Spanish text starts off costly for short texts (35% worse at 20 letters) but that gap almost disappears by 100 letters, so more ciphertext fixes it. Using the Spanish table on English text is worse and doesn't get better with length, it stays wrong a lot of the time even at 100 letters. Looking at the failures at 100 letters, about two thirds of them pick the key off by exactly 13: under that wrong shift the common English letters N, R and H land on A, E and U, which are exactly the letters Spanish uses most, so the wrong decryption genuinely looks more Spanish than the right one. That is a systematic error, not noise, which is why more ciphertext doesn't fix it, and why guessing the wrong table isn't equally bad in both directions.

## Frequency tables and reference texts

All tables are in `utils/constants.py`:

- English letter frequencies: https://es.sttmedia.com/frecuencias-de-letras-ingles
- Spanish letter frequencies: https://es.sttmedia.com/frecuencias-de-letras-espanol (the frequency of Ñ is added to N, see Deviations)
- English bigrams and trigrams (for the C4 report): https://en.wikipedia.org/wiki/Bigram and https://en.wikipedia.org/wiki/Trigram
- Spanish bigrams and trigrams (for the C4 report): https://elladodelmal.com (accents removed)

The measurement fragments are taken from public-domain texts: the start of *Pride and Prejudice* (Jane Austen) plus the Gettysburg Address for English (1033 letters), and the start of *Don Quijote* (Cervantes) without accents for Spanish (853 letters).

## C2 - Affine breaker

Run the measurements:

```
py -m experiments.measure_break_affine
```

Recovery rate (200 fragments per length, fixed seed):

| len | EN/EN | EN/ES | ES/ES | ES/EN |
|-----|-------|-------|-------|-------|
| 20  | 84.0% | 34.0% | 89.0% | 44.0% |
| 30  | 96.5% | 35.5% | 99.5% | 49.5% |
| 40  | 99.5% | 33.0% | 99.5% | 61.0% |
| 60  | 100%  | 40.0% | 100%  | 68.0% |
| 100 | 100%  | 41.0% | 100%  | 86.5% |

(EN/EN = english text with english table, EN/ES = english text with spanish table, ES/ES = spanish text with spanish table, ES/EN = spanish text with english table)

1) **How many candidates did you test, and why is that the right number?**

   312 candidates per call: 12 valid values of `a` times 26 values of `b`. The valid `a` values are exactly the integers in 1..25 that are coprime with 26 (1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25) . Any `a` sharing a factor with 26 isn't invertible mod 26, so it can't be a real affine key and decrypting with it would just be wrong. That's the whole key space, so testing all 312 is both necessary and sufficient. There's no valid key outside this set, and skipping any of them risks missing the real one.

2) **What's the shortest length at which recovery is reliable, and how does that compare to C1?**

   With the right table, affine only gets to 100% at 60 letters, versus 30 letters for the Caesar breaker in C1 (twice as much text needed). 
   
   The reason is the size of the key space: Caesar only has to pick the right answer out of 26 shifts, while affine has to pick it out of 312 (a, b) pairs. With a short, noisy fragment, chi-squared scores for the wrong keys are close together, and a bigger haystack of wrong keys means a higher chance that some wrong one scores lower than the true key just by luck. More ciphertext narrows the score gaps enough for the true key to win, so affine simply needs more letters to reach the same reliability.

## C3 - Vigenere breaker

Run the measurements:

```
py -m experiments.measure_break_vigenere
```

Recovery rate (100 fragments per combination, fixed seed), each own-language text with its own table:

**m = 3**

| len | EN    | ES    | ~coset len |
|-----|-------|-------|------------|
| 60  | 89.0% | 91.0% | 20.0       |
| 120 | 100%  | 100%  | 40.0       |
| 200 | 100%  | 100%  | 66.7       |
| 300 | 100%  | 100%  | 100.0      |

**m = 5**

| len | EN    | ES    | ~coset len |
|-----|-------|-------|------------|
| 60  | 49.0% | 55.0% | 12.0       |
| 120 | 93.0% | 96.0% | 24.0       |
| 200 | 100%  | 100%  | 40.0       |
| 300 | 100%  | 100%  | 60.0       |

**m = 7**

| len | EN    | ES    | ~coset len |
|-----|-------|-------|------------|
| 60  | 13.0% | 17.0% | 8.6        |
| 120 | 72.0% | 77.0% | 17.1       |
| 200 | 95.0% | 100%  | 28.6       |
| 300 | 100%  | 100%  | 42.9       |

(`~coset len` = the average number of letters each individual Caesar sub-problem gets)

1) **What actually governs whether this works: total ciphertext length, or something else?**

   It's the coset length (len / m), not the total length. Look at len=60 with m=3 (coset len 20, 89-91% recovery) versus len=120 with m=7 (coset len 17.1, 72-77% recovery): the second one has *twice* the total ciphertext but does worse, because it's split across more cosets. Meanwhile len=200,m=7 (coset len 28.6, 95-100%) beats len=60,m=3 (coset len 20, 89-91%) despite having a longer key, simply because each coset still gets more letters. Rows with similar coset lengths land at similar recovery rates regardless of m or total length, which is the giveaway that coset length is the real variable, matching the same length-vs-reliability curve I saw for plain Caesar in C1.

2) **Why does a longer key make Vigenere stronger even though the cipher itself hasn't changed?**

   Breaking Vigenere with a known key length is just running the C1 Caesar attack m times, once per coset, and each coset only gets roughly 1/m of the ciphertext's letters. Chi-squared needs enough letters to tell the true shift's frequency profile apart from the other 25 by more than sampling noise; the same weakness reflected in C1. A longer key doesn't touch how any individual position is encrypted (it's still a Caesar shift), but it thins out how much evidence the attacker gets per key position, since the same ciphertext now has to cover more independent shifts. So the extra strength isn't in the encryption step, it's that a longer key starves each subproblem of the sample size cryptanalysis needs. Given enough ciphertext this advantage disappears (as the 300-length column shows, everything reaches 100% eventually), so "longer key = stronger" really means "stronger per unit of ciphertext available to the attacker."

## C4 - Frequency assistant for monoalphabetic substitution

Run it on the given cryptogram (and check the mapping against the real key):

```
py -m experiments.measure_assist
```

The cryptogram (110 letters, 22 distinct):

```
QATNT YSMHQ XJOCY HKATM FSNQI TUTMP TKTIP JIDTT KHIGQ ATCEG
JMHQA FNTYM TQRTY CSNTJ IEXQA TDTXY CIRTY ACIGT PVATI HQHNY
JFKMJ FHNTP
```

It decodes to a paraphrase of Kerckhoffs's principle: *"The security of a cipher must never depend on keeping the algorithm secret, because only the key can be changed when it is compromised."*

1) **How many of the 22 distinct letters does the suggested mapping get right?**

   3 out of 22 (T→E, U→V, X→Y).

2) **What's the single most useful line in the whole report for a human solver?**

   The repeated trigram line: `QAT: count=3, positions=[1, 45, 74]`. A trigram repeating 3 times in 110 letters, right at the start of the text, is almost certainly "THE", and that guess doesn't depend on this short sample's letters matching the language's long-run frequencies the way rank alignment does. It pins down 3 letters (Q, A, T) at once, and the top bigrams `AT` and `QA` immediately confirm it as "HE" and "TH".

3) **Why does rank alignment alone not solve the cipher, and what does?**

   Rank alignment assumes this one 110-letter sample's letter frequencies fall in the same order as the language's long-run average. They don't, T is the cipher's most frequent letter at 18.2%, well above English E's usual 12.6%, and several letters tie or sit close enough that sampling noise reorders them. Matching cipher-rank-i to language-rank-i is therefore often wrong, which is exactly why only 3 of 22 letters land correctly.

   What actually solves it is what a human solver does: treat the frequency ranking as a rough starting point only, then confirm or correct each letter with structural evidence the ranking ignores, repeated trigrams/bigrams matched to common words ("THE", "HE", "TH"), doubled letters, and propagating each confirmed letter into the other words it appears in until the partially-decoded text starts reading as real English.

# Why 26! keys is not enough (and AES-128 is)

The monoalphabetic cipher has 26! ~ 4 x 10^26 keys (more than an 88-bit key), yet a human can break it in minutes with the C4 report, while AES-128 has fewer keys and nothing like that works. The difference is that key-space size only measures how expensive brute force is. The real security of a cipher is the cost of the best attack, and that depends on its structure, not on the number of keys. 

A monoalphabetic cipher always maps the same plaintext letter to the same ciphertext letter, one letter at a time, so everything statistical about the plaintext survives in the ciphertext: letter frequencies, common bigrams and trigrams, doubled letters, repeated words (Structure). On top of that, the key can be found piece by piece. Each of the 26 letter mappings can be guessed and checked on its own, and a partly correct key already gives partly readable text, which tells the solver whether the last guess was right. So instead of searching 26! keys at once, the attacker solves around 26 small problems of at most 26 options each, a few hundred checks in total. 

AES-128 is built so that neither of these things happens. It works on 128-bit blocks instead of single letters, and after 10 rounds of a non-linear S-box (confusion) plus ShiftRows/MixColumns (diffusion) with the key mixed in every round, every output bit depends on every plaintext bit and every key bit. The output has no letter statistics to count, and knowing part of the key (even 127 of the 128 bits) doesn't give partly readable plaintext. A wrong key gives random-looking output no matter how close it is to the right one, so there's nothing to "climb" towards. The best known attack on AES-128 (biclique cryptanalysis) still needs about 2^126 operations, basically brute force, and 2^128 is far out of reach. In short: substitution is weak because it leaks structure and lets the key be attacked in pieces, not because its key space is small.

# Limitations

Things that don't work, or only work partially:

- **Short texts.** The breakers are statistical, so they fail on short ciphertexts. From my measurements: Caesar is not fully reliable below ~30 letters, affine below ~60, and Vigenere needs roughly 25-40 letters per coset (ciphertext length / m). Below those lengths the returned key is often wrong, and the program has no way to tell you.
- **No confidence score.** The breakers always return the best-scoring key, even when the text is too short or in the wrong language for that key to mean anything.
- **Wrong language table.** Using the Spanish table on English text stays at only 60-70% for Caesar (around 40% for affine) even at 100 letters, and more ciphertext doesn't fix it (see C1). The program does not detect the language by itself; the user has to pass `--lang`.
- **Vigenere needs m.** `break_vigenere` only works when the key length is given. There's no Kasiski examination or index of coincidence yet, so a wrong `m` just returns a wrong key. With `m` larger than the text, the extra cosets are empty and get the letter `A` in the key.
- **Empty input in the library functions.** Called directly, `break_caesar("")` returns `(0, "")`, `break_affine("")` returns `((1, 0), "")` and `break_vigenere("", m)` returns `A * m`. These look like real keys but they're just the first candidate. The CLI checks for this and gives an error instead.
- **C4 is not a solver.** `assist.py` only does the bookkeeping. Its suggested mapping (plain rank alignment) got only 3 of 22 letters right on the given cryptogram, so a human still has to finish the job.
- **Accents.** Accented letters are reduced to their base letter (`Ñ -> N`) instead of being removed (see Deviations), so Ñ can't be told apart from N after encryption. On Windows, text with accents piped through stdin can arrive broken because of the console encoding; `--in` with a UTF-8 file works fine.
- **Small reference texts.** The measurement fragments come from ~1000 letters of English and ~850 of Spanish, so many fragments overlap. The percentages describe these two texts; other kinds of text (lists, names, technical text) could behave differently.

# Use of LLM assistants

For this project I used Claude Code for the following:

- Generating tests.
- Refining the code for encryption and decryption in order to support text with spaces, punctuation and other characters. 
- Fixing a bug in the Vigenere coset reassembly and a mismatch between how the key index advances on encryption/decryption vs how cosets were split.
- Creating a measure base file for all the algorithms' breakers.
- Generating english and spanish text.
- Fixing a bug in the monoalphabetic cipher where decrypting lowercase/mixed-case ciphertext (or using a lowercase key) silently returned it unchanged instead of decrypting it.
- Recovering the real key for the C4 cryptogram (used only in `measure_assist.py`, to grade the suggested mapping) with a quadgram-based hill-climbing/simulated-annealing search against public-domain English text, to know the ground truth for the report-task questions.
- Redacting answers and this file.
- Writing the Part D tests (`tests/test_crypto.py`) and the "How to run it" section of this file.
- Reviewing the whole project against the handout: renaming functions to the handout names, stricter key validation (non A-Z letters in keys, empty XOR key, unknown language), and rewriting the tests so every part has check values, round-trips, invalid keys, edge cases and 20 generated ciphertexts per breaker. Measurements were re-run afterwards. 
