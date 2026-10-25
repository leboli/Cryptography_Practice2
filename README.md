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

Transposition ciphers and measurements:

```
python crypto.py railfence encrypt --rails 3  --in message.txt
python crypto.py railfence decrypt --rails 3  --in cipher.txt
python crypto.py columnar  encrypt --key CIPHER [--pad X] --in message.txt
python crypto.py columnar  decrypt --key CIPHER --in cipher.txt
python crypto.py measure ic       --in cipher.txt
python crypto.py measure classify --in cipher.txt [--lang es]
python crypto.py measure kasiski  --in cipher.txt
```

## Automatic attack (`attack.py`, Part D)

```
python attack.py --in cipher.txt [--lang en|es] [--cols N]
```

It prints the measurements it used (length, index of coincidence, chi-squared against its threshold, family, and then the IC threshold, coset table or bigram scores) followed by the result.

Commands can also be chained through pipes, for example:

```
echo "Attack at dawn" | python crypto.py caesar encrypt --key 7 | python crypto.py break caesar
```

On invalid input (a non-invertible `a`, a key that is not a permutation, a Vigenere key with non-letters, a missing `--m`, a file that does not exist, a ciphertext with no letters to break...) the program prints `error: <reason>` to standard error and exits with status 1. Wrong or missing arguments are reported by `argparse` with exit status 2. No stack traces reach the user.

**Note on accents through stdin.** Files are read as UTF-8, so `--in` handles `ñ` and accented letters correctly. When piping text on Windows, the console may use another encoding and letters like `ñ` can arrive broken (for example PowerShell turns them into `?`, which is then removed). For Spanish text with accents, use `--in`.

## Measurements and tests

```
python -m experiments.measure_break_caesar     # Practice 1 C1 table
python -m experiments.measure_break_affine     # Practice 1 C2 table
python -m experiments.measure_break_vigenere   # Practice 1 C3 tables
python -m experiments.measure_assist           # Practice 1 C4 report on the given cryptogram
python -m experiments.measure_index            # B1 index of coincidence vs length
python -m experiments.measure_classify         # B2 cipher family classifier, X pad vs random pad
python -m experiments.measure_attack_vigenere  # C2 automatic Vigenere attack, key and key length
python -m experiments.measure_break_columnar   # C3 columnar breaker table and search time (~3 min)
python -m experiments.measure_pipeline         # D mono / poly decision, midpoint vs clear-peak threshold
python -m pytest -v                            # all the tests
```

On Windows, `py` can be used instead of `python`. Every measurement uses a fixed seed, so running it again gives the same numbers as the tables below.

# Tests

From the root run (`pytest.ini` puts the project root on the import path, so both work):

```
python -m pytest -v
pytest -v
```

Every cipher test file follows the same structure: the check values published in the handout, round-trip `decrypt(encrypt(m, k), k) == normalised m`, rejection of invalid keys, and edge cases (empty input, a single character, input with no letters, and for Vigenere input shorter than the key). `tests/test_crypto.py` runs `crypto.py` as a real process and checks every command, both input/output modes, and that invalid input exits with an error and no stack trace.

Practice 2 tests:

- `tests/transposition/ciphers/`: the rail fence and columnar check values, round trips for every length and several keys, padding kept by `decrypt`, the double transposition check value and round trips at every length, including plaintexts whose length is a multiple of neither key (and a test showing that the naive double decryption fails). Edge cases: empty input, a single character, no letters, a plaintext shorter than the key and a ciphertext that does not fill the grid.
- `tests/analysis/`: the two B1 index values, the B2 classifier on transpositions and substitutions, the B3 Kasiski check values (positions of `ELQ`, longest repeat `ELQYRJ`, distances 15, 35, 50, factor tally), and `coset_ic` / `find_key_length`, including multiples and divisors of the key length.
- Part C attacks on 20 generated ciphertexts per case, at lengths where the measurements say they are reliable: `find_key_length` and the automatic Vigenère `attack` for m = 3, 5, 7, 9 (300, 200, 300, 400 letters) in English and Spanish, and the columnar breaker for 4 to 7 columns.
- `tests/test_attack.py`: the Part D pipeline on columnar, Vigenère (en and es) and monoalphabetic ciphertexts, the measurements printed in every case, too-short input, a `--cols` that does not divide the length, and a length with no divisor from 2 to 8.

The Practice 1 breakers are tested on 20 generated ciphertexts per language as before (Caesar 30 letters, affine 60, Vigenère ~40 letters per coset).

# Deviations from the handout

- In the handout it says we can assume the input is normalized. My functions don't assume the input is already normalised: the ciphers, measurements (`index_of_coincidence`, `classify`, Kasiski, `coset_ic`), breakers and `attack.py` all normalise it themselves, so they accept raw text with spaces, lowercase letters and punctuation. I did this so I could use the reference texts as they are in the experiments and tests, and to make the code more robust: a caller that forgets to normalise gets the same result instead of a wrong one. The exception is `columnar.decrypt` (and so `decrypt_double`), which takes the ciphertext exactly as `encrypt` produced it.
- `railfence` also accepts 1 rail (and any number of rails at least the text length), which leaves the text unchanged. 0 or fewer rails raise `ValueError`.
- `columnar.decrypt` raises `ValueError` when the ciphertext length is not a multiple of the keyword length, since such a ciphertext cannot come from `encrypt`.
- `decrypt_double` has an extra optional `pad` argument (default `"X"`), so it can undo an `encrypt_double` made with another pad letter.
- `find_key_length` returns the `m` with the highest average when no `m` reaches the threshold (very short texts), instead of failing.
- `attack.py` stops with an error if the ciphertext has fewer than two letters, if `--cols` does not divide the length, or if no column count from 2 to 8 divides it (then `--cols` has to be given).

# Report

## A : Transposition ciphers

### A3: Double transposition

The check plaintext is 30 letters, which is a multiple of both 5 (`ROTOR`) and 6 (`ENIGMA`), so no padding is added in either pass and decrypting twice just works.

**What does `decrypt_double` have to do differently when the length is not a multiple of both, and why does a naive implementation return garbage?**

When the length doesn't fit, both passes add `X`s, but in different places. Pass 1 pads the plaintext up to a multiple of `len(kw1)`, and those `X`s get shuffled into the intermediate text with everything else (one can also land at the end). Pass 2 pads the intermediate text up to a multiple of `len(kw2)`, and when pass 2 is undone those `X`s are back at the end of the intermediate text. To undo a pass you need the exact length of its input, because that decides how many rows the grid has.

So `decrypt_double` first undoes pass 2 with `decrypt`, which keeps the padding. The result is the intermediate text followed by fewer than `len(kw2)` pad letters. Then it cuts the text back to the length it had after pass 1: the shortest length that is a multiple of `len(kw1)`, is less than `len(kw2)` letters shorter, and where everything cut off is pad. Finally it undoes pass 1 with `decrypt`, which returns the padded plaintext.

The naive version, `decrypt(decrypt(c, kw2), kw1)`, passes the pass 2 padding into the first-pass decryption. For example, `ATTACKATDAWN` with `ROTOR` gives `TANADXAKWCAXTTX` (15 letters), and `ENIGMA` then gives `XXXTATACXNWXDAXAKT` (18). Undoing pass 2 gives `TANADXAKWCAXTTXXXX`: the 15 letters of the intermediate text plus the 3 pads of pass 2. 18 is not a multiple of 5, so the naive call fails straight away (`decrypt` raises an error). It is worse when the extra length happens to be a multiple of `len(kw1)`, because then there is no error. `ATTACKNOW` with `KEY` then `CIPHER` goes 9 → 9 → 12 letters, so the naive call reads the first grid with 4 rows instead of 3. Every column is cut in the wrong place and the whole text comes out scrambled, not just the end (`test_naive_decrypt_is_garbage`). The check value never shows this because with 30 letters there is no padding.

One thing this can't fix: `X` is also the pad letter, so when the intermediate text itself ends in `X`s, the cut is ambiguous. That needs real `X`s in the plaintext that pass 1 happens to move to the end, and room for a shorter cut (a second key longer than the first). For example, `IXE` with `AB` becomes `IEXX` after pass 1 and `IEXXXXX` after `KASISKI`. `decrypt_double` cuts it back to `IE` and returns `IE`, so the real `X` is lost. In the extreme case, `encrypt_double("AX", "A", "ABC")` and `encrypt_double("A", "A", "ABC")` both give `AXX`, so no decryption can tell them apart. A plaintext that just ends in `X` is usually fine: `ATTACKATDAWNX`, `RELAX` and `BOX` all come back correctly with `ROTOR`/`ENIGMA`, `KEY`/`CIPHER` and `AB`/`KASISKI`. Over 570 short plaintexts containing an `X`, with those three key pairs, 7 lost a letter.


## B: Measuring a ciphertext

### B1: Index of coincidence

**CRYPTANALYSIS is an English word whose index equals that of uniformly random letters. State the shortest text length at which you would trust this measurement, and how you decided.**

CRYPTANALYSIS has 13 letters, and only A, S and Y appear twice, so its IC is 6 / (13 x 12) = 1/26 ~ 0.0385, the value for random letters. For English the expected value is about 0.066 (the sum of the squared frequencies in the table).

To find the length, I ran an experiment (`py -m experiments.measure_index`). For each length it takes 1000 random fragments of the English reference text and 1000 strings of uniformly random letters, computes the IC of each, and labels it "English" if it is above the midpoint between the two values (0.052). 

| len | EN mean | EN std | random mean | random std | EN correct | random correct |
|-----|---------|--------|-------------|------------|------------|----------------|
| 13  | 0.0631 | 0.0281 | 0.0380 | 0.0221 | 51.7%  | 83.0%  |
| 20  | 0.0665 | 0.0205 | 0.0380 | 0.0141 | 77.1%  | 82.3%  |
| 30  | 0.0669 | 0.0149 | 0.0385 | 0.0090 | 85.9%  | 91.4%  |
| 40  | 0.0675 | 0.0117 | 0.0386 | 0.0069 | 93.7%  | 96.1%  |
| 50  | 0.0683 | 0.0095 | 0.0386 | 0.0052 | 97.6%  | 98.8%  |
| 60  | 0.0688 | 0.0085 | 0.0385 | 0.0048 | 100%   | 98.9%  |
| 80  | 0.0690 | 0.0066 | 0.0385 | 0.0034 | 100%   | 99.9%  |
| 100 | 0.0692 | 0.0055 | 0.0385 | 0.0029 | 100%   | 100%   |

The averages are already right at 13 letters, so the problem is not bias but spread. At 13 letters the standard deviation of English fragments (0.028) is bigger than the whole gap between English and random (0.027), so a single short text can land almost anywhere. Only half of the 13-letter English fragments look like English, and CRYPTANALYSIS is one of the ones that doesn't.

I would trust the measurement from about **50 letters**: it is the first length where both English and random text are classified correctly at least 95% of the time, and from 60 letters it is around 99-100%.

### B2: Cipher family classifier

`classify` computes the chi-squared distance between the ciphertext and the language table with the scoring function from Practice 1 (`chi_squared`, which already divides by the number of letters). A transposition keeps the letters of the plaintext, so its distance is small. A substitution replaces them, so it is large. If the score is at most `CHI_THRESHOLD` the answer is "transposition", otherwise "substitution".

*Setup* (`py -m experiments.measure_classify`). Samples are random fragments of the English reference text (1033 letters). The length is the number of plaintext letters, so a columnar ciphertext can be a few letters longer because of padding. Columnar keys are random keywords of 4 to 10 distinct letters (so 0 to 9 pad characters) and monoalphabetic keys are random permutations of the alphabet. There are 150 columnar and 150 monoalphabetic samples per length.

**Choosing the threshold:** I generated a separate calibration set (seed 1, X padding, same sizes, 1200 samples), tried every cut point between two consecutive scores, and kept the one with the fewest errors: **2.214** (24 errors out of 1200). The error tables below come from new samples (seed 42), so the threshold is not measured on the data that chose it. I calibrated with X because it is the default pad of `encrypt`.

Scores on the calibration set:

| len | transposition max (pad X) | transposition max (random pad) | substitution min |
|-----|---------------------------|--------------------------------|------------------|
| 60  | 3.206 | 0.627 | 0.865 |
| 120 | 1.625 | 0.400 | 1.742 |
| 250 | 0.438 | 0.214 | 1.858 |
| 400 | 0.195 | 0.117 | 1.370 |

*Error rates.* For the second table I changed only the `pad` argument: for every message, one letter is drawn with the English frequencies and passed as `pad`, instead of `X`. Same threshold in both.

| len | pad X: trans | pad X: subs | pad X: total | random pad: trans | random pad: subs | random pad: total |
|-----|------|------|------|------|------|------|
| 60  | 4.7% | 2.7% | 3.7% | 0.0% | 2.0% | 1.0% |
| 120 | 0.0% | 4.0% | 2.0% | 0.0% | 5.3% | 2.7% |
| 250 | 0.0% | 4.7% | 2.3% | 0.0% | 3.3% | 1.7% |
| 400 | 0.0% | 7.3% | 3.7% | 0.0% | 5.3% | 2.7% |

("trans" is the share of transpositions called substitution, "subs" the share of substitutions called transposition.)

**At which lengths does the classifier work, and at which does it fail?**

The total error is below 4% at every length, but the two kinds of error behave differently.

- Transpositions are only misclassified at 60 letters with X padding (4.7%). With random padding no transposition was misclassified at any length.
- Substitutions have an error of 2-7% that does not go down with length. For a substitution, the normalised score tends to a fixed value that depends on the key, not on the length. Some random keys happen to send frequent letters to other frequent letters, and their score settles below 2.214 (the lowest substitution score was 0.865 at 60 letters and still 1.370 at 400). Longer text doesn't help with these keys. What would help is a lower threshold, and with random padding one could be used: every transposition scored below 0.63. The threshold is 2.214 because the short X-padded transpositions, which go up to 3.2, push it up.

So the classifier works from about 120 letters. At 60 letters it fails on transpositions when they are padded with `X`. And the high threshold that X padding forces adds a few percent of substitution errors at every length.

**Changing only the pad character moves the error rate substantially. Explain the mechanism.**

Chi-squared divides each squared difference by the *expected* count, so a letter that should be rare weighs a lot. `X` has frequency 0.002, so a 60-letter English text is expected to contain 0.12 X's. A columnar ciphertext with `k` pad X's adds a term of about k² / (N² · 0.002) to the normalised score, which grows with the square of the number of pads and falls with the square of the length. In the worst case of my setup (9 pads):

| len | 9 X pads alone add |
|-----|--------------------|
| 60  | 8.47 |
| 120 | 2.42 |
| 250 | 0.60 |
| 400 | 0.24 |

At 60 letters the padding alone is several times the threshold. At 400 it disappears into the noise. That is why the transposition errors are all at the short length.

A pad drawn from the English distribution is, most of the time, a common letter whose expected count is already large, so a few more copies barely change the score. For example, 6 `E`s added to 60 letters add only about 0.05, while 6 `Z`s would add about 13.8. The ciphertext then keeps the shape of English, and the transposition scores stay tight (max 0.63 at 60 letters instead of 3.2).

**Compute, for a 66-letter ciphertext containing 6 pad characters, how much the pad alone contributes to the chi-squared statistic. Compare that number with your threshold.**

Expected number of X's in 66 English letters: 0.002 × 66 = 0.132. With 6 pad X's (and no real X), that term of the sum is
(6 − 0.132)² / 0.132 = 34.43 / 0.132 ≈ 260.9, and normalised by the length, 260.9 / 66 ≈ **3.95**.

That is 1.8 times the threshold of 2.214. The padding alone, before counting any of the 60 real letters, is enough for the classifier to call a transposition a substitution.

**State the design rule this implies for anyone building a cipher that needs padding.**

Padding must not change the statistics of the text. Don't pad with a fixed character, and especially not with a rare one. Draw the pad letters at random from the letter distribution of the language, so they look like the rest of the message. A constant pad is a recognisable pattern that leaks information about the cipher (here it gives away the cipher family) and gets worse the shorter the message is.

### B3: Kasiski examination

`repeats` finds every sequence of at least `min_len` letters that appears more than once, with all its positions. `distances` takes every pair of positions of every repeat and returns the distinct distances, sorted. `factor_tally` counts, for each factor from 2 to `max_factor`, how many of those distances it divides (1 is left out because it divides everything).

On the check ciphertext, `ELQ` is at 0, 15 and 50, and the longest repeat is `ELQYRJ` at 0 and 50. There are 10 repeats in total, because every piece of `ELQYRJ` (`LQY`, `ELQYR`, ...) also repeats at distance 50. These all give the same gap, and since `distances` keeps each distance once, the result is `[15, 35, 50]`. The tally is:

| factor | 2 | 3 | 4 | 5 | 6 | 7 | 8..20 |
|--------|---|---|---|---|---|---|-------|
| count  | 1 | 1 | 0 | **3** | 0 | 1 | 0 (except 10 → 1, 15 → 1) |

5 divides all three distances, and no larger factor divides more than one.

**The gcd of those three distances is 5, which is the right answer. Explain why `factor_tally` must not be replaced by a gcd, and give the condition under which the gcd silently fails.**

A repeat in a Vigenère ciphertext can come from two things. Either the same plaintext was encrypted at the same position of the key, and then the distance is a multiple of the key length. Or two different pieces of plaintext happened to give the same ciphertext letters, and then the distance can be anything. The ciphertext alone can't tell these apart.

The gcd needs every distance to be a multiple of the key length. One accidental distance is enough to ruin it: gcd(15, 35, 50, 52) = 1. It doesn't give a warning or a "maybe", it just returns a wrong number (usually 1 or a small divisor of the real length). The tally only counts, so an accidental distance adds 1 to a few wrong factors and the real key length still has the highest count among the large factors. You look for the largest factor that still divides most of the distances, not all of them.

This happens with real text. Encrypting the English reference text with `LEMON` gives 98 distinct distances. 70 of them are multiples of 5, and the gcd of all 98 is **1**. The tally still points at 5 (70 distances), well ahead of 10 (36) and 15 (22). The same happens with `CIPHER` (6) and `SECRETS` (7) in the tests.

**Condition under which the gcd silently fails:** whenever at least one distance is not a multiple of the key length, that is, whenever there is a single accidental repeat. The longer the ciphertext, the more accidental repeats there are, so the gcd gets worse with more data, the opposite of what you'd expect from a statistical test. It also fails the other way when all the distances happen to share an extra factor (for example they are all multiples of 10 when the key length is 5): then it returns a multiple of the key length. That one is less of a problem, since with more repeats the extra factor usually disappears.

## C: Breaking

### C1: Key length

`coset_ic` splits the ciphertext into `m` cosets (letters `i, i+m, i+2m, ...`) and returns the average of their indices of coincidence. If `m` is the key length (or a multiple of it), every coset was shifted by a single letter of the key, so it keeps the index of the language. Otherwise each coset mixes several shifts and its index drops towards random.

**What "clearly above the baseline" means:** The baseline is random text, 1/26 ≈ 0.0385. The target is the index of the language, Σp² over the frequency table: 0.0655 for English, 0.0743 for Spanish. An average counts as clearly above the baseline when it gets at least **3/4 of the way** from random to the language:

| language | random | language IC | threshold |
|----------|--------|-------------|-----------|
| en       | 0.0385 | 0.0655      | **0.0588** |
| es       | 0.0385 | 0.0743      | **0.0653** |

`find_key_length` returns the smallest `m` from 1 to `max_m` whose average reaches the threshold. Taking the largest average would be wrong, because multiples of the key length are just as high (sometimes a bit higher by chance). If no `m` reaches it, which happens with very short texts, it returns the `m` with the highest average as a best guess.

Why 3/4 and not halfway: divisors of the key length also rise above random. With a key of length 6, `m = 3` puts two key letters in each coset, which is already noticeably less flat than random. Halfway (0.052 in English) is low enough for those divisor bumps to get past it on short texts.

Table for the English reference text (1033 letters) encrypted with `CIPHER`, true key length 6:

| m  | coset_ic | | m  | coset_ic | |
|----|----------|-|----|----------|-|
| 1  | 0.0448 | divisor | 9  | 0.0545 | |
| 2  | 0.0487 | divisor | 10 | 0.0474 | |
| 3  | 0.0547 | divisor | 11 | 0.0450 | |
| 4  | 0.0491 | | 12 | **0.0694** | multiple ✓ |
| 5  | 0.0438 | | 13 | 0.0448 | |
| 6  | **0.0691** | **true length** ✓ | 14 | 0.0487 | |
| 7  | 0.0446 | | 15 | 0.0531 | |
| 8  | 0.0493 | | 16 | 0.0498 | |

✓ = reaches the threshold 0.0588. Only 6 and its multiple 12 pass, and 12 (0.0694) is slightly higher than 6 (0.0691), so "take the maximum" would have returned 12. The smallest-passing rule returns 6.

The divisors 2 and 3 stand above the floor of about 0.044, and 3 is higher than 2, since each of its cosets mixes only two shifts. The same effect explains 8, 9, 15, 16 and others: they share a factor with 6 (2 or 3), so their cosets also mix fewer shifts than a completely unrelated `m` like 5, 7, 11 or 13. All of them stay below the threshold.

### C2: Automatic Vigenère attack

`attack` chains what was already there: `find_key_length` (C1) gives `m`, and `break_vigenere` from Practice 1 splits the text into `m` cosets, breaks each one with the Caesar breaker and puts the shifts together as the key.

**Measurement** (`experiments/measure_attack_vigenere.py`, seed 42). For each cell, 100 trials: a random fragment of the reference text, encrypted with a random key of length `m` (letters drawn independently, so repeats are allowed).

Complete key recovered:

| length | m=3 | m=5 | m=7 | m=9 | | m=3 | m=5 | m=7 | m=9 |
|--------|-----|-----|-----|-----|-|-----|-----|-----|-----|
|        | **en** | | | | | **es** | | | |
| 100    | 74% | 70% | 32% | 7%  | | 96% | 86% | 47% | 18% |
| 150    | 94% | 95% | 84% | 38% | | 99% | 95% | 96% | 85% |
| 200    | 94% | 100% | 97% | 78% | | 99% | 100% | 100% | 99% |
| 300    | 96% | 100% | 100% | 97% | | 99% | 100% | 100% | 100% |
| 400    | 97% | 100% | 100% | 100% | | 100% | 100% | 100% | 100% |

Key length correct:

| length | m=3 | m=5 | m=7 | m=9 | | m=3 | m=5 | m=7 | m=9 |
|--------|-----|-----|-----|-----|-|-----|-----|-----|-----|
|        | **en** | | | | | **es** | | | |
| 100    | 74% | 88% | 76% | 84% | | 96% | 92% | 85% | 87% |
| 150    | 94% | 95% | 98% | 90% | | 99% | 95% | 100% | 98% |
| 200    | 94% | 100% | 100% | 98% | | 99% | 100% | 100% | 99% |
| 300    | 96% | 100% | 100% | 98% | | 99% | 100% | 100% | 100% |
| 400    | 97% | 100% | 100% | 100% | | 100% | 100% | 100% | 100% |

Spanish does better everywhere, because its index (0.0743) is further from random than English (0.0655), so both the key length and each Caesar shift stand out more.

**Why m=3 doesn't reach 100%.** In every m=3 cell, the failures of the two tables are the same: when the key length is right, the key is right too. The failures come from `find_key_length` returning 1. With only three shifts mixed, the whole text is less flat than with seven or nine (about 0.05 instead of 0.044 in English), so it sits close to the threshold 0.0588 and noise can push it over. It is worst when two key letters are equal (`HUU`, `XKX`): then two thirds of the text has the same shift and m=1 passes even on 400 letters. About 11% of random 3-letter keys have a repeated letter, while for longer keys a repeat matters much less. With distinct letters only, m=3 in English gets the length right 97% of the time at 200 letters and 99.4% at 300. This is the price of the "smallest m that passes" rule: it never confuses multiples, but a key with few, similar shifts can look like m=1.

**The two tables degrade at very different rates. Which quantity governs each?**

- **Complete key: the letters per coset, n/m.** Each shift is found by a Caesar break on a coset of only n/m letters, and the key is only right if all m of them are right. The cells line up by n/m and not by n: around 40 letters per coset (200/5, 300/7, 400/9) is 97–100%, around 22 (200/9, 150/7) is 78–84%, around 14 (100/7) is 32% and 11 (100/9) is 7%. The Caesar breaker on its own needs about 25–30 letters (measured on 2000 English fragments: 97% at 20–22 letters, 99% at 25, 100% at 30), and with m of them in a row the small per-coset error multiplies.
- **Key length: the total length n.** `coset_ic` averages over all m cosets, so it always uses every letter of the text, and the average is much less noisy than any single coset. At n=100 the column barely changes with m (88%, 76%, 84% for m=5, 7, 9), while the key table falls from 70% to 7% on the same ciphertexts. The only clear exception is m=3 (see above).

**Your attack succeeds on 200 letters with a 5-letter key and fails with a 9-letter key. Why?**

The key length is found in both cases (100% and 98%), so the difference is in the Caesar step. With m=5 each coset has 200/5 = 40 letters, well above what the Caesar breaker needs, so all five shifts are right. With m=9 each coset has only 200/9 ≈ 22 letters. At that length a single Caesar break is right about 97% of the time, and all nine must be right: 0.97⁹ ≈ 0.76, close to the 78% measured. The text is the same length, but each Caesar break sees about half as many letters, and there are almost twice as many breaks that all have to succeed.

**Rule of thumb: how much ciphertext is needed?**

  **n ≥ 40 · m** letters for English (**n ≥ 25 · m** for Spanish), where m is the longest key length you want to cover.

That gives each coset the ~30–40 letters the Caesar breaker needs, with a margin for having m of them in a row. For short keys, also keep n ≥ ~200 (300 for m=3 in English), since then the key-length step, not the Caesar step, is the limit.

### C3: Columnar transposition breaker

`attack` tries all n! column orders. For each one it decrypts with the existing columnar `decrypt` (the order is turned into a keyword with the same `key_order`, e.g. `(2, 1, 3)` → `"BAC"`), scores the result and keeps the best. The order it returns is in the same format as `key_order`, and the plaintext keeps its padding, like `decrypt`.

**Scoring and corpus.** The score is the bigram log-probability, the sum of log p(xy) over every pair of adjacent letters. The tables are built from two books from Project Gutenberg that are not used anywhere else in the project, so the test fragments are never part of the training text:

| language | corpus | letters |
|----------|--------|---------|
| en | *The Adventures of Sherlock Holmes*, Arthur Conan Doyle (`data/english_corpus.txt`) | 431,477 |
| es | *Marianela*, Benito Pérez Galdós (`data/spanish_corpus.txt`) | 227,775 |

The text is normalised the same way as the ciphertext (A–Z only, no spaces), so pairs across word boundaries count too, as they do in the ciphertext. A pair that never appears in the corpus gets half a count instead of 0, so its log is very negative but finite. The most frequent pairs come out as TH, HE, IN for English and EN, ES, DE for Spanish.

**Why single-letter frequencies are useless here.** A transposition only changes the order of the letters, so every candidate decryption has exactly the same letter counts and gets the same single-letter score, which can't tell them apart.

**Measurement** (`experiments/measure_break_columnar.py`, seed 42). For each cell, 100 trials: a random fragment of the reference text, encrypted with a random keyword of n different letters and `X` padding. A trial counts only if the plaintext comes back exactly (with its padding).

| length | n=4 | n=5 | n=6 | n=7 | | n=4 | n=5 | n=6 | n=7 |
|--------|-----|-----|-----|-----|-|-----|-----|-----|-----|
|        | **en** | | | | | **es** | | | |
| 60     | 100% | 97% | 96% | 95% | | 100% | 100% | 100% | 98% |
| 120    | 100% | 100% | 100% | 100% | | 100% | 100% | 100% | 100% |
| 200    | 100% | 100% | 100% | 100% | | 100% | 100% | 100% | 100% |

Bigrams are a much stronger signal than the letter or coset statistics in C2. Even 60 letters is almost always enough. The few failures are at 60 letters with more columns, where there are only 9–12 rows. Typically the order found is the true one shifted by a column, for example `(6, 5, 1, 4, 2, 3)` found as `(5, 1, 4, 2, 3, 6)`. That gives almost the same text and only changes the pairs where one row runs into the next. With so few rows, a handful of pairs decide, and the wrong text can score a little higher (−326.4 against −327.5 in that example).

**Largest n under ten seconds.** Time for one attack on 200 letters (same script):

| n | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|
| orders (n!) | 24 | 120 | 720 | 5,040 | 40,320 | 362,880 |
| time | 0.00 s | 0.01 s | 0.04 s | 0.25 s | 1.95 s | 22.9 s |

The largest n under ten seconds is **n = 8**. Each extra column multiplies the time by about n, so n = 9 already takes over 20 s and n = 10 would take about 4 minutes.

**One approach to push the limit (not implemented): score column pairs instead of whole plaintexts.** Almost every bigram of the plaintext is made of a letter of some column i and the letter in the same row of the column j that goes right after it. So the score of an order is (almost exactly) the sum of the scores of its adjacent column pairs. You can compute an n × n table "how good is column j right after column i" once, and then an order is just a path that visits every column once, scored with n − 1 table lookups. That is the travelling salesman problem, which can be solved exactly with the Held–Karp dynamic programming in about 2ⁿ · n² steps instead of n! full decryptions: for n = 15 that is about 7 million steps instead of 1.3 · 10¹² orders. The pairs where one row wraps into the next add one correction term for the first and last column. For even larger n, the same table can be used with a local search (start from a greedy order and keep swapping columns while the score improves).

## D: The pipeline

`attack.py` decides in two steps:

1. **Family.** `classify` from B2: chi-squared per letter against the language table, with the threshold measured there (2.214). A transposition keeps the language's letter counts, so it falls below.
2. **Mono or poly.** For a substitution, the index of coincidence is compared with the same "clearly above the baseline" threshold as C1: 3/4 of the way from random text (1/26 = 0.0385) to the language (sum of p², 0.0655 for English), so 0.0588. A monoalphabetic cipher only renames the letters, so its index stays at the language value; a Vigenère cipher mixes several alphabets and pulls it down towards random. In other words, "monoalphabetic" means key length 1 already passes. I first tried the midpoint between random and the language (0.0520 en, 0.0564 es), but a 2-letter key has an expected index of exactly that midpoint, so the decision for it was a coin flip. Above the threshold it prints the C4 frequency assistant; below it, it prints the coset IC table for m = 1..16, picks the key length with `find_key_length` (C1) and runs `break_vigenere`.

For a transposition it runs the C3 breaker for `--cols`, or for every divisor of the length from 2 to 8, and keeps the result with the highest bigram log-probability. All candidates decrypt the same letters, so they have the same number of bigrams and their scores can be compared directly.

**Measurement** (`experiments/measure_pipeline.py`, seed 1). For each length, 300 random fragments encrypted with a random monoalphabetic key and 300 with a random Vigenère key of each length m. The table gives how often the index lands on the wrong side of the threshold: "mono" is a monoalphabetic text read as polyalphabetic, the m columns are Vigenère texts read as monoalphabetic.

| length | mono | m=2 | m=3 | m=5 | | mono | m=2 | m=3 | m=5 |
|--------|------|-----|-----|-----|-|------|-----|-----|-----|
| **midpoint** | **en** | | | | | **es** | | | |
| 100    | 0.0% | 57.0% | 30.3% | 6.7% | | 0.0% | 35.0% | 12.7% | 1.0% |
| 200    | 0.0% | 64.3% | 27.3% | 4.0% | | 0.0% | 30.3% | 8.0% | 0.3% |
| 300    | 0.0% | 68.3% | 20.0% | 1.3% | | 0.0% | 36.3% | 9.3% | 0.3% |
| **clear-peak (used)** | **en** | | | | | **es** | | | |
| 100    | 1.0% | 23.0% | 8.0% | 0.3% | | 7.3% | 8.0% | 0.7% | 0.0% |
| 200    | 0.0% | 19.0% | 4.7% | 0.0% | | 0.0% | 4.7% | 0.7% | 0.0% |
| 300    | 0.0% | 13.0% | 0.7% | 0.0% | | 0.0% | 3.7% | 0.0% | 0.0% |

The midpoint never misreads a monoalphabetic text, but it lets through more than half of the 2-letter keys and a fifth of the 3-letter ones in English. The clear-peak threshold trades a few monoalphabetic errors at 100 letters (1% en, 7.3% es) for far fewer Vigenère errors, and from 200 letters the only real problem left is m = 2. Even there 13–19% of English 2-letter keys still read as monoalphabetic: the index of a 2-alphabet mix depends on how much the two shifted distributions overlap, and for some pairs of shifts it stays close to plain English. One number cannot separate those cases. Keys of 5 or more letters are practically never misread.

**The single number behind the first decision.** Before trying any attack, the pipeline commits to a family based on one number: the length-normalised chi-squared distance between the ciphertext's letter counts and the language table. That number depends on only one property of the cipher: **whether it keeps the plaintext's single-letter frequency distribution**. It does not look at the order of the letters or at which letter became which. A transposition keeps the distribution, and a substitution normally moves it, but the classifier only sees the result, not the mechanism. A cipher that would defeat it entirely is a homophonic substitution built to match the language's frequencies: each plaintext letter is replaced by one of several ciphertext letters, with the choices weighted so that the ciphertext as a whole has the letter frequencies of English. Its chi-squared distance is as low as a transposition's, so it is classified as "transposition", and the columnar breaker returns nonsense. Its index of coincidence is also close to English, so even if the first step were skipped, the second would call it monoalphabetic. The opposite mistake is just as easy: a transposition applied to text that was first substituted (the idea behind ADFGVX) has a very high chi-squared distance, so it is classified as "substitution", and the transposition is never looked for.

## What does not work

- **The pipeline only breaks columnar transpositions.** A rail fence (or double transposition) ciphertext is correctly classified as a transposition, but then the columnar breaker runs on it and prints garbage. There is no rail fence or double transposition breaker.
- **Column counts.** Without `--cols`, a ciphertext whose length has no divisor from 2 to 8 (for example a prime length) is rejected. With `--cols` 9 or more the exhaustive search is slow (about 23 s for 9 columns, minutes for 10), and the breaker needs the full padded ciphertext: a ciphertext whose padding was removed cannot be decrypted at all.
- **Pad letter equal to a real letter.** When real `X`s of the plaintext end up at the end of the intermediate text, `decrypt_double` cannot tell them from padding and can cut them (see A3; 7 of 570 short test plaintexts containing an `X`).
- **Short or unlucky inputs.** At 60 letters, 4.7% of `X`-padded transpositions are classified as substitutions, and 2–7% of monoalphabetic substitutions are classified as transpositions at every length tested (B2). In the pipeline, 13–19% of English 2-letter Vigenère keys are read as monoalphabetic even at 200–300 letters. 3-letter keys with a repeated letter can be read as key length 1 (C2). At 60 letters with 5–7 columns, 3–5% of columnar ciphertexts come back with the order shifted by one column (C3).
- **Monoalphabetic ciphers are not solved automatically.** The pipeline prints the frequency assistant, as the handout allows.
- **Accented letters through stdin on Windows** can arrive broken. Use `--in` for Spanish text.

# Use of LLM assistants

For this project I used Claude Code for the following:

- **Tests:** generating tests for the ciphers, measurements, attacks and pipeline.
- **Code:** fixing bugs and making the code more robust (edge cases, input validation, clear errors instead of crashes).
- **README:** helping me write the answers to the report questions.
- **Review:** checking the finished submission against the handout to find missing items.

I reviewed and edited all the generated tests, code and text before including them, and I ran the tests and the measurement scripts myself to check that they work and that the numbers in this report are the ones they produce.
