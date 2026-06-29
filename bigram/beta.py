import os

from bloom.bloom_beta import compute_atom, or_atoms, L


def compute_beta(password: str) -> list[int]:
    padded = " " + password + " "
    bigrams = [padded[i:i+2] for i in range(len(padded) - 1)]
    atoms = [compute_atom(bg) for bg in bigrams]
    return or_atoms(atoms)


def build_beta_dictionary(dataset_path: str = None) -> dict:
    if dataset_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dataset_path = os.path.join(base_dir, "data", "rockyou_subset_6.txt")

    beta_dict = {}
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            pwd = line.strip()
            if pwd and 8 <= len(pwd) <= 10:
                beta_dict[pwd] = compute_beta(pwd)
    return beta_dict


if __name__ == "__main__":
    all_betas = build_beta_dictionary()
    print(f"Loaded {len(all_betas)} passwords from dataset.\n")

    print("First 5 passwords:")
    for i, (pwd, beta) in enumerate(list(all_betas.items())[:5]):
        print(f"  {i+1}. {pwd}")

    items = list(all_betas.items())

    if len(items) >= 17:
        pwd_17, beta_17 = items[16]
        print(f"\n17th password: '{pwd_17}'")
        print(f"Beta (first 50 bits): {''.join(str(b) for b in beta_17[:50])}")
    else:
        print(f"\nOnly {len(items)} passwords in dataset – cannot get 17th yet.")

    if len(items) >= 55:
        pwd_55, beta_55 = items[54]
        print(f"\n55th password: '{pwd_55}'")
        print(f"Beta (first 50 bits): {''.join(str(b) for b in beta_55[:50])}")
    else:
        print(f"\nOnly {len(items)} passwords in dataset – cannot get 55th yet.")
