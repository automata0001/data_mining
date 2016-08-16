import os
import micronap.sdk as ap

import settings

SYMSET_DELIM = r'[\x{:02x}]'.format(settings.DEFAULT_DELIM)
SYMSET_NOT_DELIM = r'[^\x{:02x}]'.format(settings.DEFAULT_DELIM)


# TODO: add support for itemset IDs > 255 (multi-STE items)
# TODO: add support for support values > 2048 (multi-counter values)
#
class ItemsetMacro(object):
    def __init__(self, anml, k):
        """Constructor.

        Args:
            anml: ANML workspace.
            k: Number of items in itemset.
        """
        self.anml = anml
        self.k = k
        self.mdef = None
        self.create()

    def create(self):
        """"""
        self.mdef = self.anml.CreateMacroDef(anmlId='arm_macro_k{}'.format(self.k))

        # Create the item chain
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

        # Add the support counter 
        ctr = self.mdef.AddCounter(settings.DEFAULT_TARGET, mode=ap.CounterMode.STOP_HOLD)
        self.mdef.AddMacroParam('%msp', ctr)
        self.mdef.AddAnmlEdge(prev, ctr, ap.AnmlDefs.COUNT_ONE_PORT)

        # Add the end-of-data delimiters
        eod1 = self.mdef.AddSTE(SYMSET_DELIM)
        eod2 = self.mdef.AddSTE(SYMSET_DELIM, match=True)
        self.mdef.AddAnmlEdge(ctr, eod1)
        self.mdef.AddAnmlEdge(eod1, eod2)

    def compile(self):
        """"""
        self.mdef.SetMacroDefToBeCompiled()
        self.anml.CompileMacros(options=ap.CompileDefs.AP_OPT_MT)

    def export(self, filename='itemset_macro.anml'):
        """"""
        self.mdef.ExportAnml(os.path.join(settings.ANML_PATH, filename))


# vim: nu:et:ts=4:sw=4:fdm=indent
