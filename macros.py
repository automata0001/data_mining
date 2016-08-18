import os
import micronap.sdk as ap

import settings
import utils

SYMSET_DELIM = r'[\x{:02x}]'.format(settings.DEFAULT_DELIM)
SYMSET_NOT_DELIM = r'[^\x{:02x}]'.format(settings.DEFAULT_DELIM)


# TODO: add support for itemset IDs > 255 (multi-STE items)
class ItemsetMacro(object):
    def __init__(self, anml, k, min_support):
        """Constructor.

        Args:
            anml: ANML workspace.
            k: Number of items in itemset.
            min_support: Minimum support value.
        """
        self.anml = anml
        self.k = k
        self.min_support = min_support
        self.mdef = None
        self.create()

    def create(self):
        """"""
        self.mdef = self.anml.CreateMacroDef(anmlId='arm_macro_k{}'.format(self.k))
        last_ste = self.create_item_chain_()
        counter = self.create_support_counter_(last_ste)
        self.create_end_delimiters_(counter)

    def create_item_chain_(self):
        """"""
        prev = self.mdef.AddSTE(SYMSET_DELIM, startType=ap.AnmlDefs.ALL_INPUT)
        symbols = [settings.DEFAULT_SYMBOL for _ in xrange(self.k)] + [SYMSET_DELIM]

        for i, sym in enumerate(symbols):
            item = self.mdef.AddSTE(sym) 
            hold = self.mdef.AddSTE(SYMSET_NOT_DELIM)
            if sym == settings.DEFAULT_SYMBOL:
                self.mdef.AddMacroParam('%i{}'.format(i), item)

            self.mdef.AddAnmlEdge(prev, item)
            self.mdef.AddAnmlEdge(prev, hold)
            self.mdef.AddAnmlEdge(hold, item)
            self.mdef.AddAnmlEdge(hold, hold)

            prev = item

        return prev

    def create_support_counter_(self, prev):
        """"""
        factors = utils.get_counter_factors(self.min_support)
        if len(factors) == 1:
            return self.create_single_precision_counter_(prev)
        elif len(factors) == 2:
            return self.create_double_precision_counter_(prev)
        else:
            return self.create_double_precision_remainder_counter_(prev)

    def create_single_precision_counter_(self, prev):
        """"""
        ctr = self.mdef.AddCounter(settings.DEFAULT_TARGET, mode=ap.CounterMode.STOP_HOLD)
        self.mdef.AddMacroParam('%msp', ctr)
        self.mdef.AddAnmlEdge(prev, ctr, ap.AnmlDefs.COUNT_ONE_PORT)
        return ctr

    def create_double_precision_counter_(self, prev):
        """"""
        p_ctr = self.mdef.AddCounter(settings.DEFAULT_TARGET, mode=ap.CounterMode.STOP_PULSE)
        q_ctr = self.mdef.AddCounter(settings.DEFAULT_TARGET, mode=ap.CounterMode.STOP_HOLD)
        pad_ste = self.mdef.AddSTE('*')

        self.mdef.AddMacroParam('%p_msp', p_ctr)
        self.mdef.AddMacroParam('%q_msp', q_ctr)

        self.mdef.AddAnmlEdge(prev, p_ctr, ap.AnmlDefs.COUNT_ONE_PORT)
        self.mdef.AddAnmlEdge(p_ctr, pad_ste)
        self.mdef.AddAnmlEdge(pad_ste, p_ctr, ap.AnmlDefs.RESET_PORT)
        self.mdef.AddAnmlEdge(pad_ste, q_ctr, ap.AnmlDefs.COUNT_ONE_PORT)

        return q_ctr

    def create_double_precision_remainder_counter_(self, prev):
        """"""
        raise NotImplementedError()

    def create_end_delimiters_(self, counter):
        """"""
        eod1 = self.mdef.AddSTE(SYMSET_DELIM)
        eod2 = self.mdef.AddSTE(SYMSET_DELIM, match=True)
        self.mdef.AddAnmlEdge(counter, eod1)
        self.mdef.AddAnmlEdge(eod1, eod2)

    def compile(self):
        """"""
        self.mdef.SetMacroDefToBeCompiled()
        self.anml.CompileMacros(options=ap.CompileDefs.AP_OPT_MT)

    def export(self, filename='itemset_macro.anml'):
        """"""
        self.mdef.ExportAnml(os.path.join(settings.ANML_PATH, filename))


# vim: nu:et:ts=4:sw=4:fdm=indent
