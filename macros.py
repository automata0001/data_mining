import os
import micronap.sdk as ap

import settings
import utils

SYMSET_DELIM = r'[\x{:02x}]'.format(settings.DEFAULT_DELIM)
SYMSET_NOT_DELIM = r'[^\x{:02x}]'.format(settings.DEFAULT_DELIM)


class ItemsetMacro(object):
    def __init__(self, anml, k, id_bytes, num_counters):
        """Constructor.

        Args:
            anml: ANML workspace.
            k: Number of items in itemset.
            id_bytes: Number of bytes required to encode item IDs (1 or 2).
            num_counters: Number of counters required to encode min support (1-3). 
        """
        self.anml = anml
        self.k = k
        self.id_bytes = id_bytes
        self.num_counters = num_counters
        self.mdef = None
        self.create()

    def create(self):
        """"""
        self.mdef = self.anml.CreateMacroDef(anmlId='arm_macro_i{}c{}k{}'.format(self.id_bytes, self.num_counters, self.k))
        last_el = self.mdef.AddSTE(SYMSET_DELIM, startType=ap.AnmlDefs.ALL_INPUT)
        last_el = self.create_item_chain_(last_el)
        last_el = self.create_support_counter_(last_el)
        self.create_end_delimiters_(last_el)

    def create_item_chain_(self, prev):
        """"""
        if self.id_bytes == 1:
            return self.create_single_precision_item_chain_(prev)
        else:
            return self.create_double_precision_item_chain_(prev)

    def create_single_precision_item_chain_(self, prev):
        """"""
        symbols = [settings.DEFAULT_SYMBOL for _ in xrange(self.k)] + [SYMSET_DELIM]

        for i, sym in enumerate(symbols):
            item = self.mdef.AddSTE(sym) 
            hold = self.mdef.AddSTE(SYMSET_NOT_DELIM)
            if sym == settings.DEFAULT_SYMBOL:
                self.mdef.AddMacroParam('%i{}0'.format(i), item)

            self.mdef.AddAnmlEdge(prev, item)
            self.mdef.AddAnmlEdge(prev, hold)
            self.mdef.AddAnmlEdge(hold, item)
            self.mdef.AddAnmlEdge(hold, hold)

            prev = item

        return prev

    def create_double_precision_item_chain_(self, prev):
        """"""
        for i in xrange(self.k):
            item0 = self.mdef.AddSTE(settings.DEFAULT_SYMBOL)
            item1 = self.mdef.AddSTE(settings.DEFAULT_SYMBOL)
            self.mdef.AddMacroParam('%i{}0'.format(i), item0)
            self.mdef.AddMacroParam('%i{}1'.format(i), item1)

            hold0 = self.mdef.AddSTE(SYMSET_NOT_DELIM)
            hold1 = self.mdef.AddSTE(SYMSET_NOT_DELIM)

            self.mdef.AddAnmlEdge(prev, item0)
            self.mdef.AddAnmlEdge(prev, hold0)
            self.mdef.AddAnmlEdge(item0, item1)
            self.mdef.AddAnmlEdge(hold0, hold1)
            self.mdef.AddAnmlEdge(hold1, hold0)
            self.mdef.AddAnmlEdge(hold1, item0)

            prev = item1

        return prev

    def create_support_counter_(self, prev):
        """"""
        if self.num_counters == 1:
            return self.create_single_precision_counter_(prev)
        elif self.num_counters == 2:
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
        p_ctr = self.mdef.AddCounter(settings.DEFAULT_TARGET, mode=ap.CounterMode.STOP_PULSE)
        q_ctr = self.mdef.AddCounter(settings.DEFAULT_TARGET, mode=ap.CounterMode.STOP_HOLD)
        r_ctr = self.mdef.AddCounter(settings.DEFAULT_TARGET, mode=ap.CounterMode.STOP_HOLD)
        and_gate = self.mdef.AddBoolean(ap.BooleanMode.AND)
        pq_pad = self.mdef.AddSTE('*')
        post_q_pad = self.mdef.AddSTE('*')
        post_r_pad = self.mdef.AddSTE('*')
        post_and_pad = self.mdef.AddSTE('*')

        self.mdef.AddMacroParam('%p_msp', p_ctr)
        self.mdef.AddMacroParam('%q_msp', q_ctr)
        self.mdef.AddMacroParam('%r_msp', r_ctr)

        self.mdef.AddAnmlEdge(prev, p_ctr, ap.AnmlDefs.COUNT_ONE_PORT)
        self.mdef.AddAnmlEdge(prev, r_ctr, ap.AnmlDefs.COUNT_ONE_PORT)
        self.mdef.AddAnmlEdge(p_ctr, pq_pad)
        self.mdef.AddAnmlEdge(pq_pad, p_ctr, ap.AnmlDefs.RESET_PORT)
        self.mdef.AddAnmlEdge(pq_pad, q_ctr, ap.AnmlDefs.COUNT_ONE_PORT)
        self.mdef.AddAnmlEdge(pq_pad, r_ctr, ap.AnmlDefs.RESET_PORT)
        self.mdef.AddAnmlEdge(q_ctr, post_q_pad)
        self.mdef.AddAnmlEdge(r_ctr, post_r_pad)
        self.mdef.AddAnmlEdge(post_q_pad, and_gate)
        self.mdef.AddAnmlEdge(post_r_pad, and_gate)
        self.mdef.AddAnmlEdge(and_gate, post_and_pad)
        self.mdef.AddAnmlEdge(post_and_pad, p_ctr, ap.AnmlDefs.RESET_PORT)

        return and_gate

    def create_end_delimiters_(self, prev):
        """"""
        eod1 = self.mdef.AddSTE(SYMSET_DELIM)
        eod2 = self.mdef.AddSTE(SYMSET_DELIM, match=True)
        self.mdef.AddAnmlEdge(prev, eod1)
        self.mdef.AddAnmlEdge(eod1, eod2)

    def compile(self):
        """"""
        self.mdef.SetMacroDefToBeCompiled()
        self.anml.CompileMacros(options=ap.CompileDefs.AP_OPT_MT)

    def export(self, filename='itemset_macro.anml'):
        """"""
        self.mdef.ExportAnml(os.path.join(settings.ANML_PATH, filename))


# vim: nu:et:ts=4:sw=4:fdm=indent
