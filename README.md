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
py -m experiments.measure_index            # B1 index of coincidence vs length
py -m experiments.measure_classify         # B2 cipher family classifier, X pad vs random pad
py -m experiments.measure_attack_vigenere  # C2 automatic Vigenere attack, key and key length
py -m experiments.measure_break_columnar   # C3 columnar breaker table and search time (~3 min)
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

[complete later]

# Key spaces

[complete later]

# Report

## A : Transposition ciphers

### A3: Double transposition

The check plaintext is 30 letters, which is a multiple of both 5 (`ROTOR`) and 6 (`ENIGMA`), so no padding is added in either pass and decrypting twice just works.

**What does `decrypt_double` have to do differently when the length is not a multiple of both, and why does a naive implementation return garbage?**

When the length doesn't fit, both passes add `X`s, but in different places. The `X`s from the second pass end up at the end of the intermediate text, while the ones from the first pass are mixed inside it (and one of them can also be at the end). To undo a pass you need the exact length of its input, because that's what decides the shape of the grid.

So `decrypt_double` first undoes pass 2 without removing any `X` (`strip_pad=False`). Then it cuts the text back to the length it had after pass 1: the shortest length that is a multiple of `len(kw1)`, is less than `len(kw2)` letters shorter, and where everything cut off is `X`. Finally it undoes pass 1 with a normal `decrypt`, which removes the remaining padding.

The naive version, `decrypt(decrypt(c, kw2), kw1)`, removes every `X` at the end after the first step, including the ones from pass 1. For example, `ATTACKATDAWN` with `ROTOR` and `ENIGMA` gives `TANADXAKWCAXTTX` (15 letters) after pass 1. After undoing pass 2 and stripping, only `TANADXAKWCAXTT` (14 letters) is left, so the pass 1 grid has the wrong shape. My first version crashed with that input, and a version that allows short columns puts the letters in the wrong columns, so the whole text comes out scrambled, not just the end. The check value never shows this because with 30 letters there is no padding.

One thing this can't fix: `X` is also the pad letter, so a plaintext that ends in a real `X` loses it.


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



# Use of LLM assistants

For this project I used Claude Code for the following:
