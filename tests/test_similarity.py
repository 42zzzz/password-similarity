import unittest

from bigram.similarity import jaccard, dice, cosine


class TestJaccard(unittest.TestCase):

    def test_identical(self):
        a = [1, 0, 1, 0]
        self.assertEqual(jaccard(a, a), 1.0)

    def test_no_overlap(self):
        a = [1, 1, 0, 0]
        b = [0, 0, 1, 1]
        self.assertEqual(jaccard(a, b), 0.0)

    def test_partial(self):
        a = [1, 1, 0, 0]
        b = [1, 0, 1, 0]
        inter = 1
        uni = 3
        self.assertEqual(jaccard(a, b), inter / uni)

    def test_all_zeros(self):
        a = [0, 0, 0]
        b = [0, 0, 0]
        self.assertEqual(jaccard(a, b), 0.0)

    def test_all_ones(self):
        a = [1, 1, 1]
        b = [1, 1, 1]
        self.assertEqual(jaccard(a, b), 1.0)


class TestDice(unittest.TestCase):

    def test_identical(self):
        a = [1, 0, 1, 0]
        self.assertEqual(dice(a, a), 1.0)

    def test_no_overlap(self):
        a = [1, 1, 0, 0]
        b = [0, 0, 1, 1]
        self.assertEqual(dice(a, b), 0.0)

    def test_partial(self):
        a = [1, 1, 0, 0]
        b = [1, 0, 1, 0]
        inter = 1
        total = 2 + 2
        self.assertEqual(dice(a, b), 2.0 * inter / total)

    def test_all_zeros(self):
        a = [0, 0, 0]
        b = [0, 0, 0]
        self.assertEqual(dice(a, b), 0.0)

    def test_symmetric(self):
        a = [1, 0, 0, 0]
        b = [1, 1, 0, 0]
        self.assertEqual(dice(a, b), dice(b, a))


class TestCosine(unittest.TestCase):

    def test_identical(self):
        a = [1, 0, 1, 0]
        self.assertEqual(cosine(a, a), 1.0)

    def test_no_overlap(self):
        a = [1, 1, 0, 0]
        b = [0, 0, 1, 1]
        self.assertEqual(cosine(a, b), 0.0)

    def test_partial(self):
        a = [1, 1, 0, 0]
        b = [1, 0, 1, 0]
        inter = 1
        mag_a = 2
        mag_b = 2
        self.assertEqual(cosine(a, b), inter / (mag_a * mag_b) ** 0.5)

    def test_all_zeros(self):
        a = [0, 0, 0]
        b = [0, 0, 0]
        self.assertEqual(cosine(a, b), 0.0)

    def test_symmetric(self):
        a = [1, 0, 0, 0]
        b = [1, 1, 0, 0]
        self.assertEqual(cosine(a, b), cosine(b, a))


if __name__ == '__main__':
    unittest.main()
