# Password Similarity Detector

CSCI262 Spring 2026

Detecting password similarities using **Bloom filters** and **cryptographic hash functions**.

## Team

| # Memeber  | Role                              | Branch        |
| ---------- | --------------------------------- | ------------- |
| 1, Zaidan  | Bloom Filter Core                 | `bloom`       |
| 2, Hafsa   | Hash Functions                    | `hash`        |
| 3, Sakina  | Bigram Similarity Engine          | `bigram`      |
| 4, Roshni  | Threshold Justification & Testing | `threshold`   |
| 5, Manisha | Integration & Report              | `integration` |

## Setup

```bash
git clone https://github.com/42zzzz/password-similarity.git
cd password-similarity
python integration/checker.py data/banned_passwords.txt
```

## Structure

```
bloom/
  __init__.py
  bloom_filter.py          # BloomFilter class (m-bit array, insert, check, FP rate)

hash/
  __init__.py
  hash_functions.py        # SHA-256, MurmurHash, hash function factory

bigram/
  __init__.py
  similarity.py            # Bigram extraction, Dice/Jaccard similarity

threshold/
  __init__.py
  evaluate.py              # FAR/FRR calculation, optimal threshold search

integration/
  __init__.py
  checker.py               # CLI/REPL wiring everything together

data/
  top10k_rockyou.txt       # Top 10,000 rockyou.txt passwords for testing
.gitignore
requirements.txt
README.md
```
