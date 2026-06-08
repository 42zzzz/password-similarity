import unittest
import math
import random
import os

from bloom.bloom_filter import BloomFilter


DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'top10k_rockyou.txt')


class TestBloomFilterCore(unittest.TestCase):

    def test_add_and_check(self):
        bf = BloomFilter(1024, None)
        items = ['hello', 'world', 'password123']
        for item in items:
            bf.add(item)
        for item in items:
            self.assertTrue(bf.check(item))

    def test_absent(self):
        bf = BloomFilter(1024, None)
        bf.add('present')
        false_positives = 0
        for _ in range(1000):
            rnd = str(random.randint(0, 100000))
            if rnd != 'present' and bf.check(rnd):
                false_positives += 1
        self.assertLess(false_positives, 50)

    def test_empty_filter(self):
        bf = BloomFilter(1024, None)
        self.assertFalse(bf.check('anything'))
        self.assertFalse(bf.check(''))
        self.assertFalse(bf.check('123456'))

    def test_fp_rate_empty(self):
        bf = BloomFilter(1024, None)
        self.assertEqual(bf.false_positive_rate, 0.0)

    def test_fp_rate_full(self):
        bf = BloomFilter(64, None)
        for i in range(1000):
            bf.add(str(i))
        self.assertGreater(bf.false_positive_rate, 0.9)

    def test_fp_rate_monotonic(self):
        bf = BloomFilter(4096, None)
        rates = []
        for i in range(1, 200):
            bf.add(str(i))
            rates.append(bf.false_positive_rate)
        for i in range(1, len(rates)):
            self.assertGreaterEqual(rates[i], rates[i - 1])

    def test_count_increments(self):
        bf = BloomFilter(1024, None)
        self.assertEqual(bf.count, 0)
        bf.add('a')
        self.assertEqual(bf.count, 1)
        bf.add('b')
        self.assertEqual(bf.count, 2)

    def test_custom_hash_functions(self):
        def h1(x):
            return 0 if x == 'anything' else 1
        def h2(x):
            return 1 if x == 'anything' else 2
        bf = BloomFilter(8, hash_functions=[h1, h2])
        bf.add('anything')
        self.assertTrue(bf.check('anything'))
        self.assertFalse(bf.check('other'))


class TestBloomFilterFactory(unittest.TestCase):

    def test_for_capacity_basic(self):
        bf = BloomFilter.for_capacity(1000, fp_rate=0.01)
        self.assertIsInstance(bf, BloomFilter)
        self.assertGreater(bf.size, 0)
        self.assertGreater(len(bf.hash_functions), 0)

    def test_for_capacity_fp_rate_below_target(self):
        bf = BloomFilter.for_capacity(10000, fp_rate=0.01)
        for i in range(5000):
            bf.add(str(i))
        self.assertLess(bf.false_positive_rate, 0.011)

    def test_for_capacity_default_fp_rate(self):
        bf = BloomFilter.for_capacity(10000)
        for i in range(10000):
            bf.add(str(i))
        self.assertAlmostEqual(bf.false_positive_rate, 0.009, delta=0.003)

    def test_for_capacity_custom_hashes(self):
        bf = BloomFilter.for_capacity(100, fp_rate=0.1, hash_functions=[lambda x: 42])
        self.assertEqual(len(bf.hash_functions), 1)


class TestBloomFilterWithRealData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(DATA_FILE):
            raise unittest.SkipTest(f'{DATA_FILE} not found')
        with open(DATA_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            cls.passwords = [l.strip() for l in f if l.strip()]
        cls.bf = BloomFilter.for_capacity(len(cls.passwords), fp_rate=0.01)
        for pw in cls.passwords:
            cls.bf.add(pw)

    def test_no_false_negatives(self):
        missing = [pw for pw in self.passwords if not self.bf.check(pw)]
        self.assertEqual(len(missing), 0, f'{len(missing)} passwords not found')

    def test_empirical_fp_rate_below_one_percent(self):
        unseen = [str(random.randint(10000000, 99999999)) for _ in range(10000)]
        fp = sum(1 for pw in unseen if self.bf.check(pw))
        rate = fp / len(unseen)
        self.assertLess(rate, 0.01, f'Empirical FP rate {rate:.4f} >= 0.01')


if __name__ == '__main__':
    unittest.main()
