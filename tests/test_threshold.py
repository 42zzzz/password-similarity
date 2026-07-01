import unittest
import tempfile
import os

from threshold.evaluate import evaluate, DEFAULT_THRESHOLD
from threshold.justify import (
    _far_frr_from_scores,
    generate_similar_passwords,
    generate_dissimilar_pass,
    SAMPLE_SIZE,
)


class TestEvaluate(unittest.TestCase):

    def test_empty_list_returns_accept(self):
        decision, j, d, c, pw = evaluate([])
        self.assertEqual(decision, 'ACCEPT')
        self.assertEqual(j, 0.0)
        self.assertEqual(d, 0.0)
        self.assertEqual(c, 0.0)
        self.assertIsNone(pw)

    def test_all_below_threshold_accepts(self):
        rows = [(0.1, 0.1, 0.1, 'pass1'), (0.2, 0.2, 0.2, 'pass2')]
        decision, j, d, c, pw = evaluate(rows, threshold=0.26)
        self.assertEqual(decision, 'ACCEPT')
        self.assertEqual(pw, 'pass2')
        self.assertEqual(j, 0.2)
        self.assertEqual(d, 0.2)
        self.assertEqual(c, 0.2)

    def test_all_above_threshold_rejects(self):
        rows = [(0.3, 0.3, 0.3, 'pass1'), (0.5, 0.5, 0.5, 'pass2')]
        decision, j, d, c, pw = evaluate(rows, threshold=0.26)
        self.assertEqual(decision, 'REJECT')
        self.assertEqual(pw, 'pass2')
        self.assertEqual(j, 0.5)
        self.assertEqual(d, 0.5)
        self.assertEqual(c, 0.5)

    def test_exactly_at_threshold_rejects(self):
        rows = [(0.26, 0.3, 0.3, 'pass1')]
        decision, j, d, c, pw = evaluate(rows, threshold=0.26)
        self.assertEqual(decision, 'REJECT')
        self.assertEqual(j, 0.26)

    def test_mixed_scores_finds_highest(self):
        rows = [(0.1, 0.1, 0.1, 'low'), (0.5, 0.5, 0.5, 'high'), (0.3, 0.3, 0.3, 'mid')]
        decision, j, d, c, pw = evaluate(rows, threshold=0.26)
        self.assertEqual(decision, 'REJECT')
        self.assertEqual(pw, 'high')
        self.assertEqual(j, 0.5)
        self.assertEqual(d, 0.5)
        self.assertEqual(c, 0.5)

    def test_below_threshold_with_some_above(self):
        rows = [(0.5, 0.5, 0.5, 'high'), (0.1, 0.1, 0.1, 'low')]
        decision, j, d, c, pw = evaluate(rows, threshold=0.26)
        self.assertEqual(decision, 'REJECT')

    def test_custom_threshold(self):
        rows = [(0.15, 0.15, 0.15, 'pw1')]
        decision, j, d, c, pw = evaluate(rows, threshold=0.1)
        self.assertEqual(decision, 'REJECT')
        decision, j, d, c, pw = evaluate(rows, threshold=0.2)
        self.assertEqual(decision, 'ACCEPT')

    def test_single_row_accept(self):
        rows = [(0.01, 0.01, 0.01, 'pw1')]
        decision, j, d, c, pw = evaluate(rows)
        self.assertEqual(decision, 'ACCEPT')
        self.assertEqual(pw, 'pw1')
        self.assertEqual(j, 0.01)
        self.assertEqual(d, 0.01)
        self.assertEqual(c, 0.01)

    def test_single_row_reject(self):
        rows = [(0.99, 0.99, 0.99, 'pw1')]
        decision, j, d, c, pw = evaluate(rows)
        self.assertEqual(decision, 'REJECT')
        self.assertEqual(pw, 'pw1')
        self.assertEqual(j, 0.99)
        self.assertEqual(d, 0.99)
        self.assertEqual(c, 0.99)

    def test_default_threshold_is_positive(self):
        self.assertGreater(DEFAULT_THRESHOLD, 0)

    def test_default_threshold_far_from_one(self):
        self.assertLess(DEFAULT_THRESHOLD, 0.99)


class TestFarFrrFromScores(unittest.TestCase):

    def test_all_correct_zero_errors(self):
        similar_scores = [0.8, 0.9, 0.95]
        dissimilar_scores = [0.1, 0.05, 0.01]
        far, frr = _far_frr_from_scores(similar_scores, dissimilar_scores, threshold=0.26)
        self.assertEqual(far, 0.0)
        self.assertEqual(frr, 0.0)

    def test_all_wrong_max_errors(self):
        similar_scores = [0.1, 0.05, 0.0]
        dissimilar_scores = [0.9, 0.8, 0.7]
        far, frr = _far_frr_from_scores(similar_scores, dissimilar_scores, threshold=0.26)
        self.assertEqual(far, 1.0)
        self.assertEqual(frr, 1.0)

    def test_one_third_errors(self):
        similar_scores = [0.9, 0.1, 0.8]
        dissimilar_scores = [0.01, 0.3, 0.01]
        far, frr = _far_frr_from_scores(similar_scores, dissimilar_scores, threshold=0.26)
        self.assertAlmostEqual(far, 1.0 / 3, places=4)
        self.assertAlmostEqual(frr, 1.0 / 3, places=4)

    def test_empty_scores(self):
        far, frr = _far_frr_from_scores([], [], threshold=0.26)
        self.assertEqual(far, 0.0)
        self.assertEqual(frr, 0.0)

    def test_only_similar_errors(self):
        similar_scores = [0.1, 0.2]
        dissimilar_scores = [0.01, 0.05]
        far, frr = _far_frr_from_scores(similar_scores, dissimilar_scores, threshold=0.26)
        self.assertEqual(far, 1.0)
        self.assertEqual(frr, 0.0)

    def test_returns_rounded_values(self):
        similar_scores = [0.9, 0.1]
        dissimilar_scores = [0.01, 0.5]
        far, frr = _far_frr_from_scores(similar_scores, dissimilar_scores, threshold=0.26)
        self.assertIsInstance(far, float)
        self.assertIsInstance(frr, float)
        self.assertLessEqual(far, 1.0)
        self.assertLessEqual(frr, 1.0)


class TestGenerateSimilarPasswords(unittest.TestCase):

    def test_returns_correct_count(self):
        passwords = ['password', 'sunshine', 'princess', 'michael1', 'andrew14']
        result = generate_similar_passwords(passwords, limit=3)
        self.assertEqual(len(result), 3)

    def test_generated_not_in_original(self):
        passwords = ['password', 'sunshine', 'princess']
        result = generate_similar_passwords(passwords, limit=3)
        for pw in result:
            self.assertNotIn(pw, passwords)

    def test_all_have_valid_length(self):
        passwords = ['password', 'sunshine', 'princess', 'michael1', 'andrew14']
        result = generate_similar_passwords(passwords, limit=5)
        for pw in result:
            self.assertGreaterEqual(len(pw), 8)
            self.assertLessEqual(len(pw), 10)

    def test_empty_input_returns_empty(self):
        result = generate_similar_passwords([], limit=10)
        self.assertEqual(result, [])

    def test_limit_respected(self):
        passwords = ['password', 'sunshine', 'princess', 'michael1', 'andrew14',
                     'babygirl', 'football', 'baseball', 'hockey11', 'soccer07']
        result = generate_similar_passwords(passwords, limit=3)
        self.assertLessEqual(len(result), 3)

    def test_no_duplicates_in_output(self):
        passwords = ['password', 'sunshine', 'princess', 'michael1', 'andrew14']
        result = generate_similar_passwords(passwords, limit=5)
        self.assertEqual(len(result), len(set(result)))


class TestGenerateDissimilarPass(unittest.TestCase):

    def test_returns_correct_count(self):
        result = generate_dissimilar_pass(n=10, seed=42)
        self.assertEqual(len(result), 10)

    def test_all_have_valid_length(self):
        result = generate_dissimilar_pass(n=50, seed=42)
        for pw in result:
            self.assertGreaterEqual(len(pw), 8)
            self.assertLessEqual(len(pw), 10)

    def test_deterministic_with_same_seed(self):
        r1 = generate_dissimilar_pass(n=10, seed=42)
        r2 = generate_dissimilar_pass(n=10, seed=42)
        self.assertEqual(r1, r2)

    def test_different_seed_different_results(self):
        r1 = generate_dissimilar_pass(n=10, seed=42)
        r2 = generate_dissimilar_pass(n=10, seed=99)
        self.assertNotEqual(r1, r2)

    def test_no_duplicates(self):
        result = generate_dissimilar_pass(n=60, seed=42)
        self.assertEqual(len(result), len(set(result)))

    def test_uses_restricted_charset(self):
        result = generate_dissimilar_pass(n=10, seed=42)
        allowed = set('bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ2357')
        for pw in result:
            for ch in pw:
                self.assertIn(ch, allowed)

    def test_default_n(self):
        result = generate_dissimilar_pass(seed=42)
        self.assertEqual(len(result), SAMPLE_SIZE)

    def test_custom_n(self):
        result = generate_dissimilar_pass(n=5, seed=42)
        self.assertEqual(len(result), 5)


if __name__ == '__main__':
    unittest.main()
