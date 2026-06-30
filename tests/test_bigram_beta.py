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

    def test_beta_non_string_raises_error(self):
        with self.assertRaises(Exception):
            compute_beta(12345)

    def test_beta_none_raises_error(self):
        with self.assertRaises(Exception):
            compute_beta(None)

    def test_beta_special_chars(self):
        beta = compute_beta("pass_word!")
        self.assertEqual(len(beta), L)
        self.assertGreater(sum(beta), 0)

    def test_beta_case_sensitive(self):
        lower = compute_beta("password")
        upper = compute_beta("PASSWORD")
        self.assertNotEqual(lower, upper)

    def test_beta_whitespace_in_password(self):
        beta = compute_beta("pass word")
        self.assertEqual(len(beta), L)
        self.assertGreater(sum(beta), 0)

    def test_beta_very_long_password(self):
        beta = compute_beta("a" * 100)
        self.assertEqual(len(beta), L)
        self.assertGreater(sum(beta), 0)


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

    def test_build_empty_file_returns_empty(self):
        empty_file = os.path.join(tempfile.gettempdir(), '_empty_test.txt')
        try:
            with open(empty_file, 'w', encoding='utf-8') as f:
                pass
            result = build_beta_dictionary(empty_file)
            self.assertEqual(result, {})
        finally:
            if os.path.exists(empty_file):
                os.remove(empty_file)

    def test_build_all_invalid_lengths_returns_empty(self):
        invalid_file = os.path.join(tempfile.gettempdir(), '_invalid_test.txt')
        try:
            with open(invalid_file, 'w', encoding='utf-8') as f:
                f.write("abc\n")
                f.write("1234567\n")
                f.write("12345678901\n")
            result = build_beta_dictionary(invalid_file)
            self.assertEqual(result, {})
        finally:
            if os.path.exists(invalid_file):
                os.remove(invalid_file)

    def test_build_skips_blank_lines(self):
        blank_file = os.path.join(tempfile.gettempdir(), '_blank_test.txt')
        try:
            with open(blank_file, 'w', encoding='utf-8') as f:
                f.write("password\n")
                f.write("\n")
                f.write("12345678\n")
                f.write("   \n")
            result = build_beta_dictionary(blank_file)
            self.assertIn("password", result)
            self.assertIn("12345678", result)
        finally:
            if os.path.exists(blank_file):
                os.remove(blank_file)

    def test_build_leading_trailing_whitespace(self):
        ws_file = os.path.join(tempfile.gettempdir(), '_ws_test.txt')
        try:
            with open(ws_file, 'w', encoding='utf-8') as f:
                f.write("  password  \n")
                f.write("\t12345678\t\n")
            result = build_beta_dictionary(ws_file)
            self.assertIn("password", result)
            self.assertIn("12345678", result)
        finally:
            if os.path.exists(ws_file):
                os.remove(ws_file)

    def test_build_large_dataset_returns_all(self):
        large_file = os.path.join(tempfile.gettempdir(), '_large_test.txt')
        try:
            with open(large_file, 'w', encoding='utf-8') as f:
                for i in range(100):
                    f.write(f"p{i:08d}\n")
            result = build_beta_dictionary(large_file)
            self.assertEqual(len(result), 100)
        finally:
            if os.path.exists(large_file):
                os.remove(large_file)


if __name__ == '__main__':
    unittest.main()
