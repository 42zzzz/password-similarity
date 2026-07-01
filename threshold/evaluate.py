# Derived from threshold/justify.py: first zero-error threshold (FAR=0, FRR=0)
# using 60 similar + 60 dissimilar test passwords against the full dataset.
# Run: python -m threshold.justify
DEFAULT_THRESHOLD = 0.26


def evaluate(scored_rows, threshold=DEFAULT_THRESHOLD):
    if not scored_rows:
        return 'ACCEPT', 0.0, 0.0, 0.0, None

    closest = max(scored_rows, key=lambda row: row[0])
    j, d, c, pw = closest

    decision = 'REJECT' if j >= threshold else 'ACCEPT'
    return decision, j, d, c, pw
