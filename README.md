# Password Similarity Detector

CSCI262 Spring 2026

Detecting password similarities using **Bloom filters** and **cryptographic hash functions**.

## Team

| # Member  | Role                              | Branch        |
| ---------- | --------------------------------- | ------------- |
| 1, Zaidan  | Bloom Filter Core                 | `bloom`       |
| 2, Roshni   | Hash Functions                    | `hash`        |
| 3, Sakina  | Bigram Similarity Engine          | `bigram`      |
| 4, Hafsa  | Threshold Justification & Testing | `threshold`   |
| 5, Manisha | Integration & Report              | `integration` |

## Setup

```bash
git clone https://github.com/42zzzz/password-similarity.git
cd password-similarity
```

## How to Run

No external dependencies are required — the project uses only the Python standard library.

**Launch the application:**

```bash
python main.py
```

Or:

```bash
python -m bloom.cli
```

**Run tests:**

```bash
python -m unittest discover tests
```

## Structure

```
bloom/
  __init__.py
  bloom_beta.py            # β(p) Bloom filter (bi-gram atoms, OR combination, precompute)
  cli.py                   # CLI with password input, length validation, JUSTIF table

main.py                    # Root entry point (python main.py)

hash/
  __init__.py
  hash_functions.py        # SHA-256, MD5, hash function factory (double hashing)

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
  rockyou_subset_6.txt       # 250 common passwords (testing data, length 8-10)
.gitignore
requirements.txt
README.md
```
