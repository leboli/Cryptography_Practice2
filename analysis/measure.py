def index_of_coincidence(text: str) -> float:
    if len(text) < 2:
        return 0.0
    
    text = text.upper().strip()
    unique_letters = set(text)

    index_of_coincidence = 0.0
    for letter in unique_letters:
        index_of_coincidence += text.count(letter) * (text.count(letter) - 1)
    return index_of_coincidence / (len(text) * (len(text) - 1))