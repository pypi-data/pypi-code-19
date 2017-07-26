import unittest
import numpy as np
from scipy.stats import binom
from roulette_wheels import LinearScan, BinarySearch, StochasticAcceptance


N_SAMPLE = 10000
MIN_P = 0.001  # Fail approx 2 times (two-tailed) every 1000 iterations.


class TestAlgorithms(unittest.TestCase):

    def setUp(self):
        self.freqs = np.array([10.0, 20, 30])
        self.after_freqs = np.array([10.0, 50, 30])

    def assert_in_dist(self, algo, n, expected_freqs, p_min):
        sample = algo.sample_counts(n)
        normalized = expected_freqs / expected_freqs.sum()

        for i, p in enumerate(normalized):
            rv = binom(n, p)
            lower_bound, upper_bound = rv.ppf([p_min, 1 - p_min])
            msg = "i={} p={}".format(i, p)
            self.assertGreaterEqual(sample[i], lower_bound, msg)
            self.assertLessEqual(sample[i], upper_bound, msg)

    def test_iterable(self):
        algo = LinearScan(self.freqs)
        sample_set = {i for _, i in zip(range(100), algo)}
        self.assertEqual(sample_set, {0, 1, 2})

    def test_linear_scan(self):
        algo = LinearScan(self.freqs)
        self.assert_in_dist(algo, N_SAMPLE, self.freqs, MIN_P)

        algo.update(1, 50.0)
        self.assertEqual(algo.freqs[1], 50.0)
        self.assertEqual(algo.total, 90.0)

        self.assert_in_dist(algo, N_SAMPLE, self.after_freqs, MIN_P)

    def test_binary_search(self):
        algo = BinarySearch(self.freqs)
        self.assert_in_dist(algo, N_SAMPLE, self.freqs, MIN_P)

        self.assertEqual(algo.total, 60.0)
        algo.update(1, 50.0)
        algo.rebuild_registers()
        self.assertEqual(algo.freqs[1], 50.0)
        self.assertEqual(algo.total, 90.0)

        self.assert_in_dist(algo, N_SAMPLE, self.after_freqs, MIN_P)

    def test_stochastic_acceptance(self):
        algo = StochasticAcceptance(self.freqs)
        self.assert_in_dist(algo, N_SAMPLE, self.freqs, MIN_P)

        self.assertEqual(algo.max_value, 30.0)
        algo.update(1, 50.0)
        algo.rebuild_registers()
        self.assertEqual(algo.freqs[1], 50.0)
        self.assertEqual(algo.max_value, 50.0)

        self.assert_in_dist(algo, N_SAMPLE, self.after_freqs, MIN_P)


if __name__ == '__main__':
    unittest.main()
