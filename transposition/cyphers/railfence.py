
from utils.basics import normalise


def encrypt(plaintext: str, rails: int) -> str:
    if rails < 1:
        raise ValueError(f"Number of rails must be at least 1, got {rails}")
    plaintext = normalise(plaintext)
    if rails == 1 or rails >= len(plaintext):
        return plaintext

    period = 2 * rails - 2
    lines = [''] * rails

    for i, c in enumerate(plaintext):
        line = i % period
        if line >= rails:
            line = period - line
        lines[line] += c

    return ''.join(lines)


def decrypt(ciphertext: str, rails: int) -> str:
    if rails < 1:
        raise ValueError(f"Number of rails must be at least 1, got {rails}")
    ciphertext = normalise(ciphertext)
    if rails == 1 or rails >= len(ciphertext):
        return ciphertext

    period = 2 * rails - 2
    # Calculate the number of characters in each rail
    rail_lengths = [0] * rails
    for i in range(len(ciphertext)):
        line = i % period
        if line >= rails:
            line = period - line
        rail_lengths[line] += 1

    # Fill the rails with the corresponding characters from the ciphertext
    rails_list = []
    start = 0
    for i in range(rails):
        rails_list.append(ciphertext[start:start + rail_lengths[i]])
        start += rail_lengths[i]

    # Reconstruct the plaintext by reading the rails in zig-zag order
    plaintext = ""
    rail_indices = [0] * rails
    for i in range(len(ciphertext)):
        line = i % period
        if line >= rails:
            line = period - line
        plaintext += rails_list[line][rail_indices[line]]
        rail_indices[line] += 1
    
    return plaintext
