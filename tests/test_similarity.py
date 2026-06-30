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

    def test_symmetric(self):
        a = [1, 0, 0, 0, 1]
        b = [1, 1, 0, 0, 0]
        self.assertEqual(jaccard(a, b), jaccard(b, a))

    def test_one_zero_one_nonzero(self):
        a = [0, 0, 0]
        b = [1, 1, 0]
        self.assertEqual(jaccard(a, b), 0.0)
        self.assertEqual(jaccard(b, a), 0.0)


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

    def test_one_zero_one_nonzero(self):
        a = [0, 0, 0]
        b = [1, 1, 0]
        self.assertEqual(dice(a, b), 0.0)

    def test_dice_similar_passwords_high_score(self):
        a = [1, 1, 1, 1, 0, 0]
        b = [1, 1, 1, 0, 1, 0]
        score = dice(a, b)
        self.assertGreater(score, 0.5)
        self.assertLess(score, 1.0)


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

    def test_one_zero_one_nonzero(self):
        a = [0, 0, 0]
        b = [1, 1, 0]
        self.assertEqual(cosine(a, b), 0.0)

    def test_cosine_similar_passwords_high_score(self):
        a = [1, 1, 1, 1, 0, 0]
        b = [1, 1, 1, 0, 1, 0]
        score = cosine(a, b)
        self.assertGreater(score, 0.5)
        self.assertLess(score, 1.0)


class TestDifferentLengthVectors(unittest.TestCase):

    def test_jaccard_a_longer_raises_indexerror(self):
        a = [1, 1, 1, 0, 1]
        b = [1, 1, 0, 0]
        with self.assertRaises(IndexError):
            jaccard(a, b)

    def test_jaccard_b_longer_silent(self):
        a = [1, 1, 0, 0]
        b = [1, 1, 0, 0, 1]
        result = jaccard(a, b)
        self.assertIsInstance(result, float)

    def test_dice_a_longer_raises_indexerror(self):
        a = [1, 1, 1, 0, 1]
        b = [1, 1, 0, 0]
        with self.assertRaises(IndexError):
            dice(a, b)

    def test_dice_b_longer_silent(self):
        a = [1, 1, 0, 0]
        b = [1, 1, 0, 0, 1]
        result = dice(a, b)
        self.assertIsInstance(result, float)

    def test_cosine_a_longer_raises_indexerror(self):
        a = [1, 1, 1, 0, 1]
        b = [1, 1, 0, 0]
        with self.assertRaises(IndexError):
            cosine(a, b)

    def test_cosine_b_longer_silent(self):
        a = [1, 1, 0, 0]
        b = [1, 1, 0, 0, 1]
        result = cosine(a, b)
        self.assertIsInstance(result, float)


if __name__ == '__main__':
    unittest.main()
