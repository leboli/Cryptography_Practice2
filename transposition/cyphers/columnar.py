
def key_order(keyword: str) -> list[int]:
    order = [0] * len(keyword)
    sorted_indices = sorted(range(len(keyword)), key=lambda i: keyword[i])
    for rank, index in enumerate(sorted_indices, start=1):
        order[index] = rank
    return order

def encrypt(plaintext: str, keyword: str, pad: str = "X") -> str:
    plaintext = plaintext.replace(" ", "").upper()
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
    number_of_columns = len(keyword)
    number_of_rows = (len(ciphertext) + number_of_columns - 1) // number_of_columns

    matrix = [[''] * number_of_columns for _ in range(number_of_rows)]
    order = key_order(keyword)

    for rank in range(1, number_of_columns + 1):
        col_index = order.index(rank)
        for row in range(number_of_rows):
            matrix[row][col_index] = ciphertext[(rank - 1) * number_of_rows + row]

    plaintext = ""
    for row in range(number_of_rows):
        for col in range(number_of_columns):
            if matrix[row][col] is not None:
                plaintext += matrix[row][col]

    return plaintext.rstrip("X")

if __name__ == "__main__":
    # Example usage
    plaintext = "MYSECRETMESSAGE"
    keyword = "CIPHER"
    ciphertext = encrypt(plaintext, keyword)
    print(f"Ciphertext: {ciphertext}")
