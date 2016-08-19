import unittest

import settings
from utils import *


class TestUtils(unittest.TestCase):
    def test_ncr(self):
        self.assertEquals(ncr(0, 0), 1)
        self.assertEquals(ncr(0, 1), 0)
        self.assertEquals(ncr(3, 3), 1)
        self.assertEquals(ncr(10, 5), 252)

    def test_get_prime_factors(self):
        self.assertEquals(get_prime_factors(1), [])
        self.assertEquals(get_prime_factors(2), [2])
        self.assertEquals(get_prime_factors(3), [3])
        self.assertEquals(get_prime_factors(4), [2, 2])
        self.assertEquals(get_prime_factors(5), [5])
        self.assertEquals(get_prime_factors(6), [2, 3])
        self.assertEquals(get_prime_factors(100), [2, 2, 5, 5])

    def test_get_counter_factors(self):
        for i in xrange(1, settings.MAX_SINGLE_TARGET+1):
            self.assertEquals(get_counter_factors(i), [i])

        self.assertEquals(get_counter_factors(2053), [2048, 1, 5])
        self.assertRaises(NotImplementedError, get_counter_factors, settings.MAX_DOUBLE_TARGET+1)

    def test_balanced_factor_pair(self):
        self.assertEquals(balanced_factor_pair(get_prime_factors(4096), 1, 1, 0), [64, 64])
        self.assertEquals(balanced_factor_pair(get_prime_factors(10000), 1, 1, 0), [100, 100])

    def test_normalize_minsup(self):
        self.assertEquals(normalize_minsup('0%', 0), 0)
        self.assertEquals(normalize_minsup('100%', 0), 0)
        self.assertEquals(normalize_minsup('0%', 1), 0)
        self.assertEquals(normalize_minsup('100%', 1), 1)
        self.assertEquals(normalize_minsup('100%', 50), 50)
        self.assertEquals(normalize_minsup('25%', 100), 25)
        self.assertEquals(normalize_minsup('25%', 101), 25)

        self.assertEquals(normalize_minsup('1', 0), 1)
        self.assertEquals(normalize_minsup('0', 0), 0)
        self.assertEquals(normalize_minsup('100', 0), 100)


# vim: nu:et:ts=4:sw=4:fdm=indent
