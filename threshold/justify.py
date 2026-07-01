# This file is for threshold testing and report justification
# Not used during app runtime; run it to recompute FAR/FRR evidence

import random
from bigram.beta import build_beta_dictionary, compute_beta
from bigram.similarity import jaccard


SAMPLE_SIZE = 60


def generate_similar_passwords(passwords, limit=SAMPLE_SIZE):
    # Similar passwords are small edits of real dataset passwords
    leet = {'a': '@', 'o': '0', 'i': '1', 'e': '3', 's': '$'}
    dataset_passwords = set(passwords)
    similar = []

    for password in passwords:
        if len(similar) >= limit:
            break
        if not password:
            continue

        for index, character in enumerate(password):
            replacement = leet.get(character.lower())
            if replacement is None:
                continue

            candidate = password[:index] + replacement + password[index + 1:]
            if (
                8 <= len(candidate) <= 10
                and candidate not in dataset_passwords
                and candidate not in similar
            ):
                similar.append(candidate)
                break
        else:
            candidate = password[0].upper() + password[1:]
            if (
                candidate != password
                and 8 <= len(candidate) <= 10
                and candidate not in dataset_passwords
                and candidate not in similar
            ):
                similar.append(candidate)
            elif len(password) < 10:
                candidate = password + '1'
                if (
                    8 <= len(candidate) <= 10
                    and candidate not in dataset_passwords
                    and candidate not in similar
                ):
                    similar.append(candidate)

    return similar


def generate_dissimilar_pass(n=SAMPLE_SIZE, seed=42):
    # Fixed seed keeps FAR/FRR results reproducible for the report
    rng = random.Random(seed)
    chars = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ2357'
    dissimilar = []

    while len(dissimilar) < n:
        length = rng.randint(8, 10)
        candidate = ''.join(rng.choices(chars, k=length))
        if candidate not in dissimilar:
            dissimilar.append(candidate)

    return dissimilar


def _max_jaccard_scores(passwords, dataset_betas):
    # Each test password is judged by its closest dataset match
    scores = []
    betas = list(dataset_betas.values())

    for password in passwords:
        beta = compute_beta(password)
        if betas:
            scores.append(max(jaccard(beta, item) for item in betas))
        else:
            scores.append(0.0)

    return scores


def _far_frr_from_scores(similar_scores, dissimilar_scores, threshold):
    # Similar passwords should be rejected; dissimilar passwords should be accepted
    false_accepts = sum(1 for score in similar_scores if score < threshold)
    false_rejects = sum(1 for score in dissimilar_scores if score >= threshold)

    far = false_accepts / len(similar_scores) if similar_scores else 0.0
    frr = false_rejects / len(dissimilar_scores) if dissimilar_scores else 0.0

    return round(far, 4), round(frr, 4)


def compute_far_frr(dataset_betas, similar_pass, dissimilar_pass, threshold):
    similar_scores = _max_jaccard_scores(similar_pass, dataset_betas)
    dissimilar_scores = _max_jaccard_scores(dissimilar_pass, dataset_betas)
    return _far_frr_from_scores(similar_scores, dissimilar_scores, threshold)


def find_optimal_threshold(dataset_betas, similar_pass, dissimilar_pass, steps=100):
    # Precompute scores once; only the threshold changes during the sweep
    similar_scores = _max_jaccard_scores(similar_pass, dataset_betas)
    dissimilar_scores = _max_jaccard_scores(dissimilar_pass, dataset_betas)

    results = []
    for i in range(1, steps):
        threshold = round(i / steps, 2)
        far, frr = _far_frr_from_scores(similar_scores, dissimilar_scores, threshold)
        results.append((threshold, far, frr))

    zero_error_rows = [row for row in results if row[1] == 0.0 and row[2] == 0.0]
    if zero_error_rows:
        selected_row = zero_error_rows[0]
    else:
        selected_row = min(results, key=lambda row: abs(row[1] - row[2]))
    return results, selected_row[0]


def print_far_frr_table(results, selected_threshold=None):
    # Print changed rows only, plus the selected threshold
    print(f'\n{"Threshold":<12} {"FAR":<10} {"FRR":<10} {"Note"}')
    print('-' * 44)

    last_printed = None

    for i, (threshold, far, frr) in enumerate(results):
        first_row = i == 0
        last_row = i == len(results) - 1
        selected_row = threshold == selected_threshold

        prev_row = results[i - 1] if i > 0 else None
        next_row = results[i + 1] if i < len(results) - 1 else None

        changed_from_prev = prev_row is None or (far, frr) != (prev_row[1], prev_row[2])
        changes_next = next_row is not None and (far, frr) != (next_row[1], next_row[2])

        if first_row or last_row or selected_row or changed_from_prev or changes_next:
            if last_printed is not None and i - last_printed == 2:
                threshold2, far2, frr2 = results[last_printed + 1]
                print(f'{threshold2:<12.2f} {far2:<10.4f} {frr2:<10.4f} ')
            elif last_printed is not None and i - last_printed > 2:
                print(f'{"...":<12} {"...":<10} {"...":<10}')

            note = '<-- first zero-error, selected' if selected_row else ''
            print(f'{threshold:<12.2f} {far:<10.4f} {frr:<10.4f} {note}')
            last_printed = i


if __name__ == '__main__':
    # Recompute the report evidence from the dataset
    print('Loading dataset...')
    dataset_betas = build_beta_dictionary()
    print(f'Loaded {len(dataset_betas)} passwords.\n')

    similar_pass = generate_similar_passwords(list(dataset_betas.keys()))
    dissimilar_pass = generate_dissimilar_pass()
    print(f'{len(similar_pass)} similar | '
          f'{len(dissimilar_pass)} dissimilar test passwords')

    results, first_zero_threshold = find_optimal_threshold(
        dataset_betas,
        similar_pass,
        dissimilar_pass,
    )

    selected_far, selected_frr = compute_far_frr(
        dataset_betas,
        similar_pass,
        dissimilar_pass,
        first_zero_threshold,
    )

    print_far_frr_table(results, first_zero_threshold)
    print(f'\nSelected threshold: {first_zero_threshold:.2f}')
    print(f'FAR: {selected_far} | FRR: {selected_frr}')
