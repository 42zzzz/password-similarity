def generate_bigrams(text):
    # Ignore upper/lower case differences
    text = text.lower()

    bigrams = []

    # Loop through every pair of consecutive characters
    for i in range(len(text) - 1):
        bigram = text[i:i+2]
        bigrams.append(bigram)

    return bigrams
