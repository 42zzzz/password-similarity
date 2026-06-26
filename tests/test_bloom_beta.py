import unittest
import os
import tempfile

from bloom.bloom_beta import L, K, compute_atom, compute_beta, precompute_dataset, filter_to_string


class TestComputeAtom(unittest.TestCase):

    def test_atom_length(self):
        atom = compute_atom("MU")
        self.assertEqual(len(atom), L)

    def test_atom_binary(self):
        atom = compute_atom("MU")
        for bit in atom:
            self.assertIn(bit, (0, 1))

    def test_atom_has_ones(self):
        atom = compute_atom("MU")
        self.assertGreater(sum(atom), 0)

    def test_atom_at_most_k_ones(self):
        atom = compute_atom("MU")
        self.assertLessEqual(sum(atom), K)

    def test_atom_deterministic(self):
        a1 = compute_atom("MU")
        a2 = compute_atom("MU")
        self.assertEqual(a1, a2)

    def test_atom_different_bigrams_differ(self):
        a1 = compute_atom("MU")
        a2 = compute_atom("UE")
        self.assertNotEqual(a1, a2)


class TestComputeBeta(unittest.TestCase):

    def test_beta_length(self):
        beta = compute_beta("MUELLER")
        self.assertEqual(len(beta), L)

    def test_beta_binary(self):
        beta = compute_beta("MUELLER")
        for bit in beta:
            self.assertIn(bit, (0, 1))

    def test_beta_has_ones(self):
        beta = compute_beta("MUELLER")
        self.assertGreater(sum(beta), 0)

    def test_beta_deterministic(self):
        b1 = compute_beta("MUELLER")
        b2 = compute_beta("MUELLER")
        self.assertEqual(b1, b2)

    def test_beta_different_passwords_differ(self):
        b1 = compute_beta("password")
        b2 = compute_beta("password1")
        self.assertNotEqual(b1, b2)

    def test_beta_similar_passwords_share_bits(self):
        b1 = compute_beta("password")
        b2 = compute_beta("passw0rd")
        overlap = sum(1 for i in range(L) if b1[i] == 1 and b2[i] == 1)
        self.assertGreater(overlap, 0)

    def test_beta_padded_with_spaces(self):
        beta = compute_beta("MUELLER")
        self.assertEqual(len(beta), L)

    def test_beta_min_length_password(self):
        beta = compute_beta("12345678")
        self.assertEqual(len(beta), L)
        self.assertGreater(sum(beta), 0)

    def test_beta_max_length_password(self):
        beta = compute_beta("1234567890")
        self.assertEqual(len(beta), L)
        self.assertGreater(sum(beta), 0)

    def test_beta_empty_string_returns_valid(self):
        beta = compute_beta("")
        self.assertEqual(len(beta), L)
        for bit in beta:
            self.assertIn(bit, (0, 1))


class TestPrecomputeDataset(unittest.TestCase):

    def setUp(self):
        self.tmpfile = os.path.join(tempfile.gettempdir(), '_test_passwords.txt')
        with open(self.tmpfile, 'w', encoding='utf-8') as f:
            f.write("123456\n")
            f.write("password\n")
            f.write("123456789\n")
            f.write("tiny\n")
            f.write("12345678\n")

    def tearDown(self):
        if os.path.exists(self.tmpfile):
            os.remove(self.tmpfile)

    def test_precompute_returns_dict(self):
        result = precompute_dataset(self.tmpfile)
        self.assertIsInstance(result, dict)

    def test_precompute_filters_by_length(self):
        result = precompute_dataset(self.tmpfile)
        self.assertIn("password", result)
        self.assertIn("123456789", result)
        self.assertIn("12345678", result)
        self.assertNotIn("123456", result)
        self.assertNotIn("tiny", result)

    def test_precompute_values_are_beta_lists(self):
        result = precompute_dataset(self.tmpfile)
        for pw, beta in result.items():
            self.assertEqual(len(beta), L)
            for bit in beta:
                self.assertIn(bit, (0, 1))

    def test_precompute_deterministic(self):
        r1 = precompute_dataset(self.tmpfile)
        r2 = precompute_dataset(self.tmpfile)
        for pw in r1:
            self.assertEqual(r1[pw], r2[pw])


class TestFilterToString(unittest.TestCase):

    def test_filter_to_string_length(self):
        beta = compute_beta("MUELLER")
        s = filter_to_string(beta)
        self.assertEqual(len(s), L)
        self.assertIsInstance(s, str)

    def test_filter_to_string_contents(self):
        beta = [0, 1, 0, 1, 1] + [0] * (L - 5)
        s = filter_to_string(beta)
        self.assertEqual(s[:5], "01011")
        self.assertEqual(s[5:], "0" * (L - 5))

    def test_filter_to_string_all_zeros(self):
        beta = [0] * L
        s = filter_to_string(beta)
        self.assertEqual(s, "0" * L)

    def test_filter_to_string_all_ones(self):
        beta = [1] * L
        s = filter_to_string(beta)
        self.assertEqual(s, "1" * L)


if __name__ == '__main__':
    unittest.main()
