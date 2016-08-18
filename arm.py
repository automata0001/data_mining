import itertools
import os

import micronap.sdk as ap

import settings
import utils


class ARM(object):
    def __init__(self, initial_items, min_support):
        """"""
        self.min_support = min_support
        self.items = set(initial_items)
        self.itemsets = set([(x,) for x in self.items])

        self.k = None
        self.candidates = None
        self.fsm = None
        self.emap = None
        self.mdef = None

    def init_iteration(self, k):
        """"""
        self.k = k
        self.restore_itemset_mdef_()
        self.restore_itemset_fsm_()
        self.restore_itemset_emap_()
        self.generate_candidates_()
        self.label_candidates_()

    def restore_itemset_mdef_(self):
        """"""
        path = os.path.join(settings.ANML_PATH, 'k{}.anml'.format(self.k))
        anml = ap.Anml()
        self.mdef = anml.LoadAnmlMacro(path)

    def restore_itemset_fsm_(self):
        """"""
        path = os.path.join(settings.FSM_PATH, 'k{}.fsm'.format(self.k))
        self.fsm = ap.Automaton()
        self.fsm.Restore(path)

    def restore_itemset_emap_(self):
        """"""
        path = os.path.join(settings.MAP_PATH, 'k{}.map'.format(self.k))
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
            mref = self.emap.GetElementRefFromElementId('arm_net_k{}.mref{}'.format(self.k, i))
            symbol_chgs += self.label_items_(mref, itemset)
            target_chgs += self.label_counter_(mref)

        self.fsm.SetSymbol(self.emap, symbol_chgs)
        self.fsm.SetCounterTarget(self.emap, target_chgs)

    def label_items_(self, mref, itemset):
        """"""
        changes = []
        for j, item in enumerate(itemset):
            param = self.mdef.GetMacroParamFromName('%i{}'.format(j))
            changes.append(ap.ap_symbol_change(mref, r'[\x{:02x}]'.format(item), param))
        return changes

    # TODO: this should be done once per FSM as an initialization step, not every iteration
    def label_counter_(self, mref):
        """"""
        factors = utils.get_counter_factors(self.min_support)

        if len(factors) == 1:
            return self.label_single_precision_counter_(mref)
        elif len(factors) == 2:
            return self.label_double_precision_counter_(mref, factors)
        else:
            return self.label_double_precision_remainder_counter_(mref, factors)

    def label_single_precision_counter_(self, mref):
        """"""
        param = self.mdef.GetMacroParamFromName('%msp')
        return [ap.ap_counter_change(mref, self.min_support, param)]

    def label_double_precision_counter_(self, mref, factors):
        """"""
        p_param = self.mdef.GetMacroParamFromName('%p_msp')
        q_param = self.mdef.GetMacroParamFromName('%q_msp')
        return [ap.ap_counter_change(mref, factors[0], p_param),
                ap.ap_counter_change(mref, factors[1], q_param)]

    def label_double_precision_remainder_counter_(self, mref, factors):
        """"""
        p_param = self.mdef.GetMacroParamFromName('%p_msp')
        q_param = self.mdef.GetMacroParamFromName('%q_msp')
        r_param = self.mdef.GetMacroParamFromName('%r_msp')
        return [ap.ap_counter_change(mref, factors[0], p_param),
                ap.ap_counter_change(mref, factors[1], q_param),
                ap.ap_counter_change(mref, factors[2], r_param)]

    def process_reports(self, erefs):
        """"""
        for eref in erefs:
            itemset = self.candidates[eref - 1]
            for i in itemset: 
                self.items.add(i) 
            self.itemsets.add(itemset)


# vim: nu:et:ts=4:sw=4:fdm=indent
