import itertools
import os

import micronap.sdk as ap

import settings
import utils


class ARM(object):
    def __init__(self, initial_items, min_support, num_id_bytes=1):
        """"""
        self.min_support = min_support
        self.num_id_bytes = num_id_bytes
        self.items = set(initial_items)
        self.itemsets = set([frozenset([x]) for x in self.items])

        self.k = None
        self.factors = utils.get_counter_factors(self.min_support)
        self.num_counters = len(self.factors)
        self.candidates = None
        self.fsm = None
        self.emap = None
        self.mdef = None

    def init_iteration(self, k):
        """"""
        self.k = k
        self.ick = 'i{}c{}k{}'.format(self.num_id_bytes, self.num_counters, k)

        self.restore_itemset_mdef_()
        self.restore_itemset_fsm_()
        self.restore_itemset_emap_()
        self.generate_candidates_()
        self.label_candidates_()

    def restore_itemset_mdef_(self):
        """"""
        path = os.path.join(settings.ANML_PATH, '{}.anml'.format(self.ick))
        anml = ap.Anml()
        self.mdef = anml.LoadAnmlMacro(path)

    def restore_itemset_fsm_(self):
        """"""
        path = os.path.join(settings.FSM_PATH, '{}.fsm'.format(self.ick))
        self.fsm = ap.Automaton()
        self.fsm.Restore(path)

    def restore_itemset_emap_(self):
        """"""
        path = os.path.join(settings.MAP_PATH, '{}.map'.format(self.ick))
        self.emap = ap.ElementMap()
        self.emap.RestoreElementMap(path)

    def generate_candidates_(self):
        """"""
        self.candidates = list(itertools.combinations(self.items, self.k))

    def label_candidates_(self):
        """"""
        symbol_chgs = []
        target_chgs = []

        for i, itemset in enumerate(self.candidates):
            mref = self.emap.GetElementRefFromElementId('arm_net_{}.mref{}'.format(self.ick, i))
            symbol_chgs += self.label_items_(mref, itemset)
            target_chgs += self.label_counter_(mref)

        self.fsm.SetSymbol(self.emap, symbol_chgs)
        self.fsm.SetCounterTarget(self.emap, target_chgs)

    def label_items_(self, mref, itemset):
        """"""
        changes = []
        for i, item in enumerate(sorted(itemset)):
            id_bytes = utils.to_base(item, settings.STE_ID_SPACE)
            id_bytes.reverse()
            num_zeroes = self.num_id_bytes - len(id_bytes)
            for j in xrange(self.num_id_bytes):
                param = self.mdef.GetMacroParamFromName('%i{}{}'.format(i, j))
                byte = 0
                if j >= num_zeroes: 
                    byte = id_bytes.pop()
                changes.append(ap.ap_symbol_change(mref, r'[\x{:02x}]'.format(byte), param))
        return changes

    # TODO: this should be done once per FSM as an initialization step, not every iteration
    def label_counter_(self, mref):
        """"""
        if self.num_counters == 1:
            return self.label_single_precision_counter_(mref)
        elif self.num_counters == 2:
            return self.label_double_precision_counter_(mref)
        else:
            return self.label_double_precision_remainder_counter_(mref)

    def label_single_precision_counter_(self, mref):
        """"""
        param = self.mdef.GetMacroParamFromName('%msp')
        return [ap.ap_counter_change(mref, self.min_support, param)]

    def label_double_precision_counter_(self, mref):
        """"""
        p_param = self.mdef.GetMacroParamFromName('%p_msp')
        q_param = self.mdef.GetMacroParamFromName('%q_msp')
        return [ap.ap_counter_change(mref, self.factors[0], p_param),
                ap.ap_counter_change(mref, self.factors[1], q_param)]

    def label_double_precision_remainder_counter_(self, mref):
        """"""
        p_param = self.mdef.GetMacroParamFromName('%p_msp')
        q_param = self.mdef.GetMacroParamFromName('%q_msp')
        r_param = self.mdef.GetMacroParamFromName('%r_msp')
        return [ap.ap_counter_change(mref, self.factors[0], p_param),
                ap.ap_counter_change(mref, self.factors[1], q_param),
                ap.ap_counter_change(mref, self.factors[2], r_param)]

    def process_reports(self, erefs):
        """"""
        for eref in erefs:
            itemset = self.candidates[eref - 1]
            for i in itemset: 
                self.items.add(i) 
            self.itemsets.add(frozenset(itemset))


# vim: nu:et:ts=4:sw=4:fdm=indent
