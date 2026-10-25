from utils.basics import normalise


def key_order(keyword: str) -> list[int]:
    order = [0] * len(keyword)
    sorted_indices = sorted(range(len(keyword)), key=lambda i: keyword[i])
    for rank, index in enumerate(sorted_indices, start=1):
        order[index] = rank
    return order

def encrypt(plaintext: str, keyword: str, pad: str = "X") -> str:
    plaintext = normalise(plaintext)
    keyword = keyword.upper()
    number_of_columns = len(keyword)
    number_of_rows = (len(plaintext) + number_of_columns - 1) // number_of_columns
    matrix = [[''] * number_of_columns for _ in range(number_of_rows)]
    padded_plaintext = plaintext.ljust(number_of_rows * number_of_columns, pad)

    for row in range(number_of_rows):
        for col in range(number_of_columns):
            matrix[row][col] = padded_plaintext[row * number_of_columns + col]

    order = key_order(keyword)
    ciphertext = ""

    for rank in range(1, number_of_columns + 1):
        col_index = order.index(rank)
        for row in range(number_of_rows):
            ciphertext += matrix[row][col_index]

    return ciphertext

def decrypt(ciphertext: str, keyword: str) -> str:
    keyword = keyword.upper()
    number_of_columns = len(keyword)
    if len(ciphertext) % number_of_columns != 0:
        raise ValueError(f"Ciphertext length {len(ciphertext)} is not a multiple of the key length {number_of_columns}")
    number_of_rows = len(ciphertext) // number_of_columns

    matrix = [[''] * number_of_columns for _ in range(number_of_rows)]
    order = key_order(keyword)

    for rank in range(1, number_of_columns + 1):
        col_index = order.index(rank)
        for row in range(number_of_rows):
            matrix[row][col_index] = ciphertext[(rank - 1) * number_of_rows + row]

    plaintext = ""
    for row in range(number_of_rows):
        for col in range(number_of_columns):
            plaintext += matrix[row][col]

    # the padding is kept: decrypt returns the padded plaintext
    return plaintext

def encrypt_double(plaintext: str, kw1: str, kw2: str, pad: str = "X") -> str:
    intermediate = encrypt(plaintext, kw1, pad)
    return encrypt(intermediate, kw2, pad)

def decrypt_double(ciphertext: str, kw1: str, kw2: str, pad: str = "X") -> str:
    intermediate = decrypt(ciphertext, kw2)
    # The second pass padded the intermediate with fewer than len(kw2) pads, and the
    # real intermediate is a full first grid (a multiple of len(kw1)). Those pads must
    # be removed before the first decryption, or the first grid gets the wrong number
    # of rows. Take the shortest length that fits both conditions.
    for length in range(max(0, len(intermediate) - len(kw2) + 1), len(intermediate) + 1):
        if length % len(kw1) == 0 and intermediate[length:].strip(pad) == "":
            return decrypt(intermediate[:length], kw1)
    raise ValueError("Ciphertext was not produced by encrypt_double with these keywords")
