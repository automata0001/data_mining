import unittest

import settings
from utils import *


class TestUtils(unittest.TestCase):
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
