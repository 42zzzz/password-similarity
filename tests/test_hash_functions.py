import unittest
import hashlib
import os
import tempfile

from hash.hash_functions import sha256_hash, md5_hash, get_hash_pair, create_hashes, load_passwords


class TestSHA256(unittest.TestCase):

    def test_returns_int(self):
        result = sha256_hash("MU")
        self.assertIsInstance(result, int)

    def test_deterministic(self):
        self.assertEqual(sha256_hash("MU"), sha256_hash("MU"))

    def test_different_inputs_differ(self):
        self.assertNotEqual(sha256_hash("MU"), sha256_hash("UE"))

    def test_matches_hardcoded_value(self):
        expected = int(hashlib.sha256("MU".encode('utf-8')).hexdigest(), 16)
        self.assertEqual(sha256_hash("MU"), expected)

    def test_non_ascii(self):
        result = sha256_hash("caf\u00e9")
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_empty_string(self):
        result = sha256_hash("")
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_case_sensitive(self):
        self.assertNotEqual(sha256_hash("mu"), sha256_hash("MU"))


class TestMD5(unittest.TestCase):

    def test_returns_int(self):
        result = md5_hash("MU")
        self.assertIsInstance(result, int)

    def test_deterministic(self):
        self.assertEqual(md5_hash("MU"), md5_hash("MU"))

    def test_different_inputs_differ(self):
        self.assertNotEqual(md5_hash("MU"), md5_hash("UE"))

    def test_matches_hardcoded_value(self):
        expected = int(hashlib.md5("MU".encode('utf-8')).hexdigest(), 16)
        self.assertEqual(md5_hash("MU"), expected)

    def test_non_ascii(self):
        result = md5_hash("caf\u00e9")
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_empty_string(self):
        result = md5_hash("")
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_md5_and_sha256_differ(self):
        self.assertNotEqual(sha256_hash("MU"), md5_hash("MU"))


class TestGetHashPair(unittest.TestCase):

    def test_returns_tuple(self):
        pair = get_hash_pair("MU")
        self.assertIsInstance(pair, tuple)
        self.assertEqual(len(pair), 2)

    def test_first_is_sha256(self):
        f, g = get_hash_pair("MU")
        self.assertEqual(f, sha256_hash("MU"))

    def test_second_is_md5(self):
        f, g = get_hash_pair("MU")
        self.assertEqual(g, md5_hash("MU"))

    def test_deterministic(self):
        self.assertEqual(get_hash_pair("MU"), get_hash_pair("MU"))


class TestCreateHashes(unittest.TestCase):

    def test_creates_correct_number(self):
        hashes = create_hashes(20, 1000)
        self.assertEqual(len(hashes), 20)

    def test_custom_k(self):
        hashes = create_hashes(5, 1000)
        self.assertEqual(len(hashes), 5)

    def test_each_returns_int(self):
        hashes = create_hashes(20, 1000)
        for hf in hashes:
            result = hf("MU")
            self.assertIsInstance(result, int)

    def test_results_in_range(self):
        L = 1000
        hashes = create_hashes(20, L)
        for hf in hashes:
            result = hf("MU")
            self.assertGreaterEqual(result, 0)
            self.assertLess(result, L)

    def test_custom_L(self):
        L = 500
        hashes = create_hashes(10, L)
        for hf in hashes:
            result = hf("MU")
            self.assertGreaterEqual(result, 0)
            self.assertLess(result, L)

    def test_different_i_differ(self):
        hashes = create_hashes(20, 1000)
        results = [hf("MU") for hf in hashes]
        for i in range(1, len(results)):
            self.assertNotEqual(results[0], results[i])

    def test_deterministic(self):
        h1 = create_hashes(20, 1000)
        h2 = create_hashes(20, 1000)
        for i in range(20):
            self.assertEqual(h1[i]("MU"), h2[i]("MU"))


class TestLoadPasswords(unittest.TestCase):

    def setUp(self):
        self.tmpfile = os.path.join(tempfile.gettempdir(), '_test_load.txt')
        with open(self.tmpfile, 'w', encoding='utf-8') as f:
            f.write("123456\n")
            f.write("password\n")
            f.write("123456789\n")
            f.write("a\n")
            f.write("12345678\n")

    def tearDown(self):
        if os.path.exists(self.tmpfile):
            os.remove(self.tmpfile)

    def test_filters_by_length(self):
        result = load_passwords(self.tmpfile)
        self.assertIn("password", result)
        self.assertIn("123456789", result)
        self.assertIn("12345678", result)
        self.assertNotIn("123456", result)
        self.assertNotIn("a", result)

    def test_returns_list(self):
        result = load_passwords(self.tmpfile)
        self.assertIsInstance(result, list)

    def test_all_results_valid_length(self):
        result = load_passwords(self.tmpfile)
        for pw in result:
            self.assertGreaterEqual(len(pw), 8)
            self.assertLessEqual(len(pw), 10)

    def test_empty_file(self):
        empty_path = os.path.join(tempfile.gettempdir(), '_test_empty.txt')
        with open(empty_path, 'w', encoding='utf-8') as f:
            pass
        result = load_passwords(empty_path)
        self.assertEqual(result, [])
        os.remove(empty_path)

    def test_no_valid_lengths(self):
        short_path = os.path.join(tempfile.gettempdir(), '_test_short.txt')
        with open(short_path, 'w', encoding='utf-8') as f:
            f.write("a\nbb\nccc\n")
        result = load_passwords(short_path)
        self.assertEqual(result, [])
        os.remove(short_path)


if __name__ == '__main__':
    unittest.main()
