#!/usr/bin/env python
from argparse import ArgumentParser
import os
import sys

import micronap.sdk as ap

import settings
from macros import ItemsetMacro


def get_counters_per_rank(device):
    """"""
    metrics = ap.QueryDeviceMetrics(device)
    return settings.CTR_PER_BLK * settings.BLK_PER_DEV * (metrics.devs_per_rank - 1)

def create_macro_defs(max_k, min_support):
    """"""
    for k in xrange(1, max_k + 1):
        macro = ItemsetMacro(ap.Anml(), k, min_support)
        macro.compile()
        macro.export('k{}.anml'.format(k))

def compile_automaton(k, ctr_max):
    """"""
    anml = ap.Anml()
    mdef = anml.LoadAnmlMacro(os.path.join(settings.ANML_PATH, 'k{}.anml'.format(k)))
    network = anml.CreateAutomataNetwork(anmlId='arm_net_k{}'.format(k))

    mrefs = []
    for i in xrange(ctr_max):
        mrefs.append(network.AddMacroRef(mdef, anmlId='mref{}'.format(i)))
    fsm, emap = anml.CompileAnml(options=ap.CompileDefs.AP_OPT_MT)

    changes = []
    for mref in mrefs:
        for j in xrange(k):
            param = mdef.GetMacroParamFromName('%i{}'.format(j))
            changes.append(ap.ap_symbol_change(mref, '[]', param))
    fsm.SetSymbol(emap, changes)

    fsm.Save(os.path.join(settings.FSM_PATH, 'k{}.fsm'.format(k)))
    emap.SaveElementMap(os.path.join(settings.MAP_PATH, 'k{}.map'.format(k)))

    return fsm, emap

def main():
    """"""

    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument('--max-k', '-k', type=int, required=True)
    parser.add_argument('--min-support', '-s', type=int, required=True)
    parser.add_argument('--macro-count', '-m', type=int)
    parser.add_argument('--device', '-d', default=settings.DEV_NAME)
    parser.add_argument('--verbose', '-v', action='store_true', default=False)
    args = parser.parse_args()

    if args.min_support > settings.MAX_DOUBLE_TARGET:
        sys.exit('{}: support must be <= {}!'.format(__file__, settings.MAX_DOUBLE_TARGET))

    # Build all 1-k itemset macros
    create_macro_defs(args.max_k, args.min_support)

    # Compile automata for each k-itemset macro
    if args.macro_count:
        ctr_max = args.macro_count
    else:
        ctr_max = get_counters_per_rank(args.device)
    for k in xrange(2, args.max_k + 1):
        fsm, emap = compile_automaton(k, ctr_max)
        print 'Compiled FSM for k={}, blk={}'.format(k, fsm.GetInfo().blocks_rect)


if __name__ == '__main__':
    main()


# vim: nu:et:ts=4:sw=4:fdm=indent
