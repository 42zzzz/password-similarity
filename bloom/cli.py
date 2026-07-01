import os
import sys

from bigram.beta import compute_beta, build_beta_dictionary
from bigram.similarity import jaccard, dice, cosine
from threshold.evaluate import evaluate, DEFAULT_THRESHOLD
from bloom.bloom_beta import L

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'rockyou_subset_6.txt')


def validate_length(password: str) -> bool:
    if 8 <= len(password) <= 10:
        return True
    print(f'Error: Password must be between 8 and 10 characters (got {len(password)}).')
    return False


def main():
    data_path = os.path.abspath(DATA_FILE)
    if not os.path.exists(data_path):
        print(f'Error: Dataset not found at {data_path}')
        print('Ensure data/rockyou_subset_6.txt is present.')
        sys.exit(1)

    print('Loading dataset and precomputing beta filters...')
    dataset = build_beta_dictionary(data_path)
    print(f'Loaded {len(dataset)} passwords (length 8-10).')
    print()

    print('=== Password Similarity Checker ===')
    print()

    while True:
        try:
            user_pw = input('Enter a password (8-10 characters) or "quit": ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_pw.lower() == 'quit':
            break

        if not validate_length(user_pw):
            print('Please try again.')
            print()
            continue

        beta_user = compute_beta(user_pw)
        ones = sum(beta_user)
        print(f'beta({user_pw}) computed: {L} bits, {ones} ones.')
        print()

        print('JUSTIF Table - Similarity between UserP and each password in dataset:')
        print(f'{"Password":<15} {"Jaccard":<10} {"Dice":<10} {"Cosine":<10}')
        print('-' * 45)

        scored = []
        for pw, beta_pw in dataset.items():
            j = jaccard(beta_user, beta_pw)
            d = dice(beta_user, beta_pw)
            c = cosine(beta_user, beta_pw)
            scored.append((j, d, c, pw))

        scored.sort(key=lambda x: x[1], reverse=True)

        for i, (j, d, c, pw) in enumerate(scored):
            if i >= 10:
                remaining = len(scored) - 10
                if remaining > 0:
                    print(f'{"...":<15} {"...":<10} {"...":<10} {"...":<10}')
                    print(f'(Table truncated. {remaining} more passwords not shown.)')
                break
            print(f'{pw:<15} {j:<10.4f} {d:<10.4f} {c:<10.4f}')

        decision, j, d, c, closest_pw = evaluate(scored)
        print(f'Decision for "{user_pw}": {decision}')
        if closest_pw:
            print(f'Closest match: "{closest_pw}" (Jaccard={j:.4f}, Dice={d:.4f}, Cosine={c:.4f})')
            print(f'Threshold: {DEFAULT_THRESHOLD} (derived from FAR/FRR analysis)')
        print()

    print('Quitting...')


if __name__ == '__main__':
    main()
