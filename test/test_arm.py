import unittest

import micronap.sdk as ap

from arm import ARM
import create_fsms
import utils


class TestARM(unittest.TestCase):
    def test_init(self):
        arm = ARM([], 1)

    def test_init_iteration(self):
        arm = ARM([], 1)
        arm.init_iteration(2) 
        self.assertTrue(isinstance(arm.mdef, ap.anml.AnmlMacroDef))
        self.assertTrue(isinstance(arm.fsm, ap.Automaton))
        self.assertTrue(isinstance(arm.emap, ap.ElementMap))

    def test_generate_candidates(self):
        k = 2
        minsup = 1
        create_fsms.create_macro_defs(k, minsup)
        create_fsms.compile_automaton(k, utils.ncr(3, 2))
        arm = ARM([1, 2, 3], minsup)
        arm.init_iteration(k)
        self.assertEqual(arm.candidates, [(1, 2), (1, 3), (2, 3)])

    def test_process_reports(self):
        k = 2
        minsup = 1
        create_fsms.create_macro_defs(k, minsup)
        create_fsms.compile_automaton(k, utils.ncr(3, 2))
        arm = ARM([1, 2, 3], minsup)
        arm.init_iteration(k)

        arm.process_reports([1, 2, 3])
        self.assertEqual(arm.items, set([1, 2, 3]))
	

# vim: nu:et:ts=4:sw=4:fdm=indent
