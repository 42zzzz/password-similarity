import os
import sys

from bloom.bloom_beta import compute_beta, precompute_dataset, filter_to_string, L

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
    dataset = precompute_dataset(data_path)
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

        row_count = 0
        for pw, beta_pw in dataset.items():
            print(f'{pw:<15} {"---":<10} {"---":<10} {"---":<10}')
            row_count += 1
            if row_count >= 10:
                remaining = len(dataset) - 10
                if remaining > 0:
                    print(f'{"...":<15} {"...":<10} {"...":<10} {"...":<10}')
                    print(f'(Table truncated. {remaining} more passwords not shown.)')
                break

        print()
        print('Note: Jaccard, Dice, and Cosine values will be filled by Member 3')
        print('      (bigram/similarity.py). Accept/reject logic will be completed')
        print('      by Members 4 and 5 (threshold evaluation and integration).')
        print()

        decision = 'PENDING'
        print(f'Decision for "{user_pw}": {decision}')
        print('(Accept/reject justification requires similarity metrics from Member 3')
        print(' and threshold analysis from Member 4.)')
        print()

    print('Goodbye.')


if __name__ == '__main__':
    main()
