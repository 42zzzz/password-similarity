import unittest
import os
import tempfile

from bigram.beta import compute_beta, build_beta_dictionary
from bloom.bloom_beta import L


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


class TestBuildBetaDictionary(unittest.TestCase):

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

    def test_build_returns_dict(self):
        result = build_beta_dictionary(self.tmpfile)
        self.assertIsInstance(result, dict)

    def test_build_filters_by_length(self):
        result = build_beta_dictionary(self.tmpfile)
        self.assertIn("password", result)
        self.assertIn("123456789", result)
        self.assertIn("12345678", result)
        self.assertNotIn("123456", result)
        self.assertNotIn("tiny", result)

    def test_build_values_are_beta_lists(self):
        result = build_beta_dictionary(self.tmpfile)
        for pw, beta in result.items():
            self.assertEqual(len(beta), L)
            for bit in beta:
                self.assertIn(bit, (0, 1))

    def test_build_deterministic(self):
        r1 = build_beta_dictionary(self.tmpfile)
        r2 = build_beta_dictionary(self.tmpfile)
        for pw in r1:
            self.assertEqual(r1[pw], r2[pw])


if __name__ == '__main__':
    unittest.main()
