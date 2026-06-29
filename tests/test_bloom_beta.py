import unittest

from bloom.bloom_beta import L, K, compute_atom, or_atoms


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


class TestOrAtoms(unittest.TestCase):

    def test_or_single_atom(self):
        atom = compute_atom("MU")
        result = or_atoms([atom])
        self.assertEqual(result, atom)

    def test_or_two_atoms_combines_ones(self):
        a1 = compute_atom("MU")
        a2 = compute_atom("UE")
        result = or_atoms([a1, a2])
        for i in range(L):
            expected = 1 if a1[i] == 1 or a2[i] == 1 else 0
            self.assertEqual(result[i], expected)

    def test_or_all_zeros(self):
        zeros = [[0] * L for _ in range(5)]
        result = or_atoms(zeros)
        self.assertEqual(result, [0] * L)

    def test_or_empty_list(self):
        result = or_atoms([])
        self.assertEqual(result, [0] * L)

    def test_or_deterministic(self):
        a1 = compute_atom("MU")
        a2 = compute_atom("UE")
        r1 = or_atoms([a1, a2])
        r2 = or_atoms([a1, a2])
        self.assertEqual(r1, r2)


if __name__ == '__main__':
    unittest.main()
