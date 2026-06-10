import hashlib


def sha256_hash(data: str) -> int:
    # f(x) from the project formula — SHA256 the bigram, convert to int
    # we need an integer not a hex string because Zaidan does (f + i*g) % 1000
    encoded_data = data.encode('utf-8')
    hash_obj = hashlib.sha256(encoded_data)
    hex_digest = hash_obj.hexdigest()
    return int(hex_digest, 16)


def md5_hash(data: str) -> int:
    # g(x) from the project formula — same idea as above but using MD5
    # the two together give Zaidan everything needed to compute all 20 h_i values
    encoded_data = data.encode('utf-8')
    hash_obj = hashlib.md5(encoded_data)
    hex_digest = hash_obj.hexdigest()
    return int(hex_digest, 16)


def get_hash_pair(bigram: str) -> tuple:
    # instead of calling sha256 and md5 separately every time,
    # just call this and get both back at once as (f, g)
    # Sakina can loop through bigrams and pass each one here directly
    return sha256_hash(bigram), md5_hash(bigram)


def load_passwords(filepath: str) -> list:
    # reads the common passwords dataset and filters by length
    # document says passwords must be between 8 and 10 characters (Section V.b)
    # Member 1 and Member 3 will use this list to build the bloom filters
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        passwords = [line.strip() for line in f if 8 <= len(line.strip()) <= 10]
    return passwords