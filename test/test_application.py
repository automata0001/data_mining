import os
import unittest

from apfacade import APFacade
from dataset import Dataset
from arm import ARM
import create_fsms
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
        create_fsms.create_macro_defs(k, minsup)
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            create_fsms.compile_automaton(k, utils.ncr(4, k))
            arm.init_iteration(k)
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

        self.assertEquals(arm.items, set([1, 2, 3, 4]))

    def test_contextPasquier99(self):
        """"""
        k = 4
        minsup = 2
        create_fsms.create_macro_defs(k, minsup)
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            create_fsms.compile_automaton(k, utils.ncr(5, k))
            arm.init_iteration(k)
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

        self.assertEquals(arm.items, set([1, 2, 3, 5]))
        self.assertEquals(arm.itemsets, set([
            (1,), (2,), (3,), (5,), 
            (1, 2), (1, 3), (1, 5), (2, 3), (2, 5), (3, 5), 
            (1, 2, 3), (1, 2, 5), (1, 3, 5), (2, 3, 5), 
            (1, 2, 3, 5),
        ]))

    def test_contextRelim(self):
        """"""
        k = 2
        minsup = 4
        create_fsms.create_macro_defs(k, minsup)
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            create_fsms.compile_automaton(k, utils.ncr(4, k))
            arm.init_iteration(k)
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

        self.assertEquals(arm.items, set([1, 2, 3, 4]))
        self.assertEquals(arm.itemsets, set([
            (1,), (2,), (3,), (4,),
            (1, 4), (2, 4),
        ]))

    def test_contextItemsetTree(self):
        """"""
        k = 3
        minsup = 2
        create_fsms.create_macro_defs(k, minsup)
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            create_fsms.compile_automaton(k, utils.ncr(5, k))
            arm.init_iteration(k)
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

        self.assertEquals(arm.items, set([1, 2, 4, 5]))
        self.assertEquals(arm.itemsets, set([
            (1,), (2,), (4,), (5,),
            (1, 2), (1, 4), (2, 4), (2, 5), 
            (1, 2, 4),
        ]))

    def test_contextPFPM(self):
        """"""
        k = 2
        minsup = 3
        create_fsms.create_macro_defs(k, minsup)
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            create_fsms.compile_automaton(k, utils.ncr(5, k))
            arm.init_iteration(k)
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

        self.assertEquals(arm.items, set([1, 2, 3, 4, 5]))
        self.assertEquals(arm.itemsets, set([
            (1,), (2,), (3,), (4,), (5,),
            (3, 4), (3, 5),
        ]))

    def test_double_precision_counter(self):
        """"""
        k = 3
        minsup = 3000
        create_fsms.create_macro_defs(k, minsup)
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            create_fsms.compile_automaton(k, utils.ncr(3, k))
            arm.init_iteration(k)
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

        self.assertEquals(arm.items, set([1, 2, 3]))
        self.assertEquals(arm.itemsets, set([
            (1,), (2,), (3,), 
            (1, 2), (1, 3), (2, 3),
            (1, 2, 3),
        ]))

    def test_double_precision_remainder_counter(self):
        """"""
        k = 3
        minsup = 2053 # [2048, 1, 5]
        create_fsms.create_macro_defs(k, minsup)
        arm = ARM(self.dataset.get_frequent_items(minsup), minsup)
        
        for k in xrange(2, k+1):
            create_fsms.compile_automaton(k, utils.ncr(3, k))
            arm.init_iteration(k)
            reports = self.device.execute(arm.fsm, self.dataset.encoded_data)
            arm.process_reports(reports)

        self.assertEquals(arm.items, set([1, 2, 3]))
        self.assertEquals(arm.itemsets, set([
            (1,), (2,), (3,), 
            (1, 2), (1, 3), (2, 3),
            (1, 2, 3),
        ]))


# vim: nu:et:ts=4:sw=4:fdm=indent
