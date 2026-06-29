# =============================================================================
# bigram/beta.py
# Member 3 – Bigram Analysis & β(p) Computation
# CSCI262 Project – Section III.B (exactly as per rubric)
# =============================================================================

import os

# Constants from the project spec (III.A.1)
L = 1000   # Bloom filter length
K = 20     # number of hash functions

# -----------------------------------------------------------------------------
# INTERFACE WITH MEMBER 1 (Bloom Filter Core)
# -----------------------------------------------------------------------------
# Member 1 will create a function inside the 'bloom' folder.
# We will import it here once they give us the exact function name.
# For now, we use a placeholder so you can test your bigram logic.
# -----------------------------------------------------------------------------

from bloom.bloom_beta import compute_atom

# -----------------------------------------------------------------------------
# YOUR CORE LOGIC (Section III.B)
# -----------------------------------------------------------------------------

def compute_beta(password: str) -> list[int]:
    """
    Computes the Bloom filter β(p) for a single password.
    Steps (exactly as per III.B):
      1. Append a space at beginning and end.
      2. Extract all bigrams (sliding window, step 1).
      3. For each bigram, get its atom (Bloom filter for that bigram).
      4. OR all atoms together → β(p).
    """
    # Step 1: pad with spaces
    padded = " " + password + " "

    # Step 2: generate bigrams (sliding window of length 2)
    bigrams = []
    for i in range(len(padded) - 1):
        bigrams.append(padded[i:i+2])

    # Step 3 & 4: start with an empty filter (all zeros)
    beta = [0] * L

    # For each bigram, get its atom and OR it into beta
    for bg in bigrams:
        atom = compute_atom(bg)          # Member 1's function   # Member 1's function   # calls Member 1's function
        # Logical bitwise OR (element-wise)
        for j in range(L):
            beta[j] = beta[j] | atom[j]

    return beta


# -----------------------------------------------------------------------------
# BUILD THE DICTIONARY FOR THE ENTIRE DATASET
# -----------------------------------------------------------------------------

def build_beta_dictionary(dataset_path: str = None) -> dict:
    """
    Reads the provided password dataset and returns a dictionary:
    { password: beta_filter (list of 1000 bits) }
    This dictionary will be used by Member 4 to compute similarities.
    
    If no path is given, it looks for 'data/common_passwords.txt' by default.
    """
    if dataset_path is None:
        # Go up one level from 'bigram' folder to the repo root, then into 'data'
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dataset_path = os.path.join(base_dir, "data", "rockyou_subset_6.txt")
    
    beta_dict = {}
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            pwd = line.strip()
            if pwd:   # skip empty lines
                # The dataset should already have passwords of length 8-10,
                # but you can add an if check here if you want:
                # if 8 <= len(pwd) <= 10:
                beta_dict[pwd] = compute_beta(pwd)
    return beta_dict


# -----------------------------------------------------------------------------
# QUICK SELF-TEST – run this file directly to verify your logic
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Build beta dictionary from the real dataset
    all_betas = build_beta_dictionary()
    print(f"Loaded {len(all_betas)} passwords from dataset.\n")
    
    # Show first 5 passwords (just to verify)
    print("First 5 passwords:")
    for i, (pwd, beta) in enumerate(list(all_betas.items())[:5]):
        print(f"  {i+1}. {pwd}")
    
    # ----- For the screenshot requirement (Section 6) -----
    # Get the 17th password (index 16 because 0-based)
    items = list(all_betas.items())
    
    if len(items) >= 17:
        pwd_17, beta_17 = items[16]   # 17th password
        print(f"\n17th password: '{pwd_17}'")
        print(f"Beta (first 50 bits): {beta_17[:50]}")
        print(f"Beta (full 1000 bits): {beta_17}")
    else:
        print(f"\nOnly {len(items)} passwords in dataset – cannot get 17th yet.")
    
    # Get the 55th password (if exists)
    if len(items) >= 55:
        pwd_55, beta_55 = items[54]   # 55th password
        print(f"\n55th password: '{pwd_55}'")
        print(f"Beta (first 50 bits): {beta_55[:50]}")
        print(f"Beta (full 1000 bits): {beta_55}")
    else:
        print(f"\nOnly {len(items)} passwords in dataset – cannot get 55th yet.")