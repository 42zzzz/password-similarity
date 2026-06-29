from hash.hash_functions import sha256_hash, md5_hash

L = 1000
K = 20


def compute_atom(bigram: str) -> list[int]:
    f = sha256_hash(bigram)
    g = md5_hash(bigram)
    atom = [0] * L
    for i in range(K):
        atom[(f + i * g) % L] = 1
    return atom


def or_atoms(atoms: list[list[int]]) -> list[int]:
    result = [0] * L
    for atom in atoms:
        for i in range(L):
            if atom[i]:
                result[i] = 1
    return result
