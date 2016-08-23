import os
import unittest

from apfacade import APFacade
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

        self.device = APFacade(dev_name=settings.DEV_NAME)
        self.device.setup()

    def tearDown(self):
        """"""
        self.device = None

    def test_simple(self):
        """"""
        k = 3
        minsup = 2
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            arm.init_iteration(k)
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

        self.assertEquals(arm.items, set([1, 2, 3, 4]))

    def test_contextPasquier99(self):
        """"""
        k = 4
        minsup = 2
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            arm.init_iteration(k)
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

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
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

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
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

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
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

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
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

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
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

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
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

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


# vim: nu:et:ts=4:sw=4:fdm=indent
