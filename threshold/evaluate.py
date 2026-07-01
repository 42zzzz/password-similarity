# Default threshold: first zero-error value found by threshold/justify.py
DEFAULT_THRESHOLD = 0.26


def evaluate(scored_rows, threshold=DEFAULT_THRESHOLD):
    # Reuse precomputed JUSTIF rows: (jaccard, dice, cosine, password)
    if not scored_rows:
        return 'ACCEPT', 0.0, None

    # Jaccard is the metric used for the accept/reject threshold
    closest = max(scored_rows, key=lambda row: row[0])
    max_score = closest[0]
    closest_password = closest[-1]

    decision = 'REJECT' if max_score >= threshold else 'ACCEPT'
    return decision, max_score, closest_password
