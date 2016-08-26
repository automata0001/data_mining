import os
import unittest

from dataset import Dataset
from arm import ARM
import settings
import utils


class TestApplication(unittest.TestCase):
    def setUp(self):
        """"""
        test_name = self.id().split('.')[-1]
        ds_name = test_name.split('_', 1)[-1]

        self.dataset = Dataset(os.path.join(settings.DATA_PATH, '{}.dat'.format(ds_name)))
        self.dataset.parse_file()
        self.dataset.encode_data()

    def test_simple(self):
        """"""
        k = 3
        minsup = 2
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            arm.init_iteration(k)
            arm.execute_iteration(self.dataset.encoded_data)

        self.assertEquals(arm.items, set([1, 2, 3, 4]))

    def test_contextPasquier99(self):
        """"""
        k = 4
        minsup = 2
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            arm.init_iteration(k)
            arm.execute_iteration(self.dataset.encoded_data)

        self.assertEquals(arm.items, set([1, 2, 3, 5]))
        self.assertEquals(arm.itemsets, set([
            frozenset([1,]),
            frozenset([2,]),
            frozenset([3,]),
            frozenset([5,]), 
            frozenset([1, 2]),
            frozenset([1, 3]),
            frozenset([1, 5]),
            frozenset([2, 3]),
            frozenset([2, 5]),
            frozenset([3, 5]), 
            frozenset([1, 2, 3]),
            frozenset([1, 2, 5]),
            frozenset([1, 3, 5]),
            frozenset([2, 3, 5]), 
            frozenset([1, 2, 3, 5]),
        ]))

    def test_contextRelim(self):
        """"""
        k = 2
        minsup = 4
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            arm.init_iteration(k)
            arm.execute_iteration(self.dataset.encoded_data)

        self.assertEquals(arm.items, set([1, 2, 3, 4]))
        self.assertEquals(arm.itemsets, set([
            frozenset([1,]),
            frozenset([2,]),
            frozenset([3,]),
            frozenset([4,]),
            frozenset([1, 4]),
            frozenset([2, 4]),
        ]))

    def test_contextItemsetTree(self):
        """"""
        k = 3
        minsup = 2
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            arm.init_iteration(k)
            arm.execute_iteration(self.dataset.encoded_data)

        self.assertEquals(arm.items, set([1, 2, 4, 5]))
        self.assertEquals(arm.itemsets, set([
            frozenset([1,]),
            frozenset([2,]),
            frozenset([4,]),
            frozenset([5,]),
            frozenset([1, 2]),
            frozenset([1, 4]),
            frozenset([2, 4]),
            frozenset([2, 5]), 
            frozenset([1, 2, 4]),
        ]))

    def test_contextPFPM(self):
        """"""
        k = 2
        minsup = 3
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            arm.init_iteration(k)
            arm.execute_iteration(self.dataset.encoded_data)

        self.assertEquals(arm.items, set([1, 2, 3, 4, 5]))
        self.assertEquals(arm.itemsets, set([
            frozenset([1,]),
            frozenset([2,]),
            frozenset([3,]),
            frozenset([4,]),
            frozenset([5,]),
            frozenset([3, 4]),
            frozenset([3, 5]),
        ]))

    def test_double_precision_counter(self):
        """"""
        k = 3
        minsup = 3000
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            arm.init_iteration(k)
            arm.execute_iteration(self.dataset.encoded_data)

        self.assertEquals(arm.items, set([1, 2, 3]))
        self.assertEquals(arm.itemsets, set([
            frozenset([1,]),
            frozenset([2,]),
            frozenset([3,]), 
            frozenset([1, 2]),
            frozenset([1, 3]),
            frozenset([2, 3]),
            frozenset([1, 2, 3]),
        ]))

    def test_double_precision_remainder_counter(self):
        """"""
        k = 3
        minsup = 2053 # [2048, 1, 5]
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            arm.init_iteration(k)
            arm.execute_iteration(self.dataset.encoded_data)

        self.assertEquals(arm.items, set([1, 2, 3]))
        self.assertEquals(arm.itemsets, set([
            frozenset([1,]),
            frozenset([2,]),
            frozenset([3,]), 
            frozenset([1, 2]),
            frozenset([1, 3]),
            frozenset([2, 3]),
            frozenset([1, 2, 3]),
        ]))

    def test_large_ids(self):
        """"""
        k = 3
        minsup = 3
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup, num_id_bytes=self.dataset.num_id_bytes)
        
        for k in xrange(2, k+1):
            arm.init_iteration(k)
            arm.execute_iteration(self.dataset.encoded_data)

        self.assertEquals(arm.items, set([1, 10, 1000]))
        self.assertEquals(arm.itemsets, set([
            frozenset([1,]),
            frozenset([10,]),
            frozenset([1000,]), 
            frozenset([1, 10]),
            frozenset([1, 1000]),
            frozenset([10, 1000]),
            frozenset([1, 10, 1000]),
        ]))

    def test_multi_round(self):
        """"""
        k = 3
        minsup = 3000
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup, num_id_bytes=self.dataset.num_id_bytes)
        
        for k in xrange(2, k+1):
            arm.init_iteration(k)
            arm.execute_iteration(self.dataset.encoded_data)

        self.assertEquals(arm.items, set([7, 29, 34, 36, 40, 48, 52, 56, 58, 60, 62, 66]))
        self.assertEquals(arm.itemsets, set([
            frozenset([48, 58]),
            frozenset([60, 7]),
            frozenset([40, 7]),
            frozenset([40, 60, 7]),
            frozenset([58, 52, 62]),
            frozenset([56, 52]),
            frozenset([58, 29, 62]),
            frozenset([40, 58, 52]),
            frozenset([52, 58, 36]),
            frozenset([58]),
            frozenset([60, 52]),
            frozenset([56, 58, 29]),
            frozenset([29, 62]),
            frozenset([29]),
            frozenset([40, 34, 58]),
            frozenset([40, 29, 7]),
            frozenset([60, 66, 52]),
            frozenset([40, 58, 7]),
            frozenset([58, 60, 62]),
            frozenset([66, 60]),
            frozenset([40]),
            frozenset([60, 58, 36]),
            frozenset([66]),
            frozenset([34, 58, 29]),
            frozenset([40, 58, 29]),
            frozenset([58, 36]),
            frozenset([60, 58, 52]),
            frozenset([52, 36]),
            frozenset([66, 29]),
            frozenset([40, 58]),
            frozenset([56, 52, 29]),
            frozenset([40, 29]),
            frozenset([52, 62]),
            frozenset([40, 34, 29]),
            frozenset([56]),
            frozenset([48, 52]),
            frozenset([60, 52, 7]),
            frozenset([60]),
            frozenset([40, 62]),
            frozenset([34, 52, 29]),
            frozenset([40, 60]),
            frozenset([62]),
            frozenset([58, 60, 29]),
            frozenset([36, 29]),
            frozenset([56, 58]),
            frozenset([40, 52, 29]),
            frozenset([48, 58, 52]),
            frozenset([60, 52, 29]),
            frozenset([56, 29]),
            frozenset([52, 7]),
            frozenset([58, 36, 29]),
            frozenset([60, 29]),
            frozenset([66, 52]),
            frozenset([58, 60, 7]),
            frozenset([40, 52, 62]),
            frozenset([40, 60, 29]),
            frozenset([60, 52, 62]),
            frozenset([66, 60, 58]),
            frozenset([34, 58]),
            frozenset([40, 52, 7]),
            frozenset([66, 60, 29]),
            frozenset([60, 62]),
            frozenset([48]),
            frozenset([52, 29]),
            frozenset([40, 52, 36]),
            frozenset([40, 58, 36]),
            frozenset([40, 36, 29]),
            frozenset([40, 34]),
            frozenset([52, 29, 62]),
            frozenset([58, 29, 7]),
            frozenset([34]),
            frozenset([58, 52, 7]),
            frozenset([66, 58]),
            frozenset([29, 7]),
            frozenset([34, 29]),
            frozenset([40, 60, 36]),
            frozenset([40, 36]),
            frozenset([60, 36]),
            frozenset([40, 60, 52]),
            frozenset([58, 52]),
            frozenset([34, 52, 58]),
            frozenset([7]),
            frozenset([58, 29]),
            frozenset([52, 36, 60]),
            frozenset([66, 52, 29]),
            frozenset([66, 52, 58]),
            frozenset([52, 29, 7]),
            frozenset([66, 58, 29]),
            frozenset([58, 62]),
            frozenset([60, 29, 62]),
            frozenset([52, 36, 29]),
            frozenset([40, 52]),
            frozenset([40, 34, 52]),
            frozenset([58, 7]),
            frozenset([56, 58, 52]),
            frozenset([58, 60]),
            frozenset([52]),
            frozenset([40, 58, 60]),
            frozenset([60, 29, 7]),
            frozenset([34, 52]),
            frozenset([36]),
            frozenset([40, 29, 62]),
            frozenset([60, 36, 29]),
            frozenset([58, 52, 29]),
            frozenset([40, 58, 62]),
        ]))


# vim: nu:et:ts=4:sw=4:fdm=indent
