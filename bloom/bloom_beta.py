from hash.hash_functions import create_hashes

L = 1000
K = 20

_hashes = create_hashes(K, L)


def compute_atom(bigram: str) -> list[int]:
    atom = [0] * L
    for hf in _hashes:
        atom[hf(bigram)] = 1
    return atom


def compute_beta(password: str) -> list[int]:
    padded = ' ' + password + ' '
    bigrams = [padded[i:i+2] for i in range(len(padded) - 1)]
    beta = [0] * L
    for bg in bigrams:
        atom = compute_atom(bg)
        for i in range(L):
            if atom[i]:
                beta[i] = 1
    return beta


def precompute_dataset(filepath: str) -> dict:
    from hash.hash_functions import load_passwords
    return {pw: compute_beta(pw) for pw in load_passwords(filepath)}


def filter_to_string(beta: list) -> str:
    return ''.join(str(b) for b in beta)
