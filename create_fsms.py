#!/usr/bin/env python
from argparse import ArgumentParser
import os
import sys

import micronap.sdk as ap

import settings
from macros import ItemsetMacro
import utils


def get_counters_per_rank(device):
    """"""
    metrics = ap.QueryDeviceMetrics(device)
    return settings.CTR_PER_BLK * settings.BLK_PER_DEV * (metrics.devs_per_rank - 1)

def create_macro_def(k, id_bytes, num_counters):
    """"""
    macro = ItemsetMacro(ap.Anml(), k, id_bytes, num_counters)
    macro.compile()
    macro.export('i{}c{}k{}.anml'.format(id_bytes, num_counters, k))

def compile_automaton(k, id_bytes, num_counters, macro_count):
    """"""
    ick = 'i{}c{}k{}'.format(id_bytes, num_counters, k)

    anml = ap.Anml()
    mdef = anml.LoadAnmlMacro(os.path.join(settings.ANML_PATH, '{}.anml'.format(ick)))
    network = anml.CreateAutomataNetwork(anmlId='arm_net_{}'.format(ick))

    mrefs = []
    for i in xrange(macro_count):
        mrefs.append(network.AddMacroRef(mdef, anmlId='mref{}'.format(i)))
    fsm, emap = anml.CompileAnml(options=ap.CompileDefs.AP_OPT_MT)

    changes = []
    for mref in mrefs:
        for i in xrange(k):
            for x in xrange(id_bytes):
                param = mdef.GetMacroParamFromName('%i{}{}'.format(i, x))
                changes.append(ap.ap_symbol_change(mref, '[]', param))
    fsm.SetSymbol(emap, changes)

    fsm.Save(os.path.join(settings.FSM_PATH, '{}.fsm'.format(ick)))
    emap.SaveElementMap(os.path.join(settings.MAP_PATH, '{}.map'.format(ick)))

    return fsm, emap

def main():
    """"""

    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument('--max-k', '-k', type=int, required=True)
    parser.add_argument('--macro-count', '-m', type=int)
    parser.add_argument('--device', '-d', default=settings.DEV_NAME)
    parser.add_argument('--verbose', '-v', action='store_true', default=False)
    args = parser.parse_args()

    if args.macro_count:
        macro_count = args.macro_count
    else:
        macro_count = get_counters_per_rank(args.device)

    # Compile automata for each combination of:
    # - number of ID bytes
    # - number of counters
    # - max itemset size (k)
    # 
    for id_bytes in xrange(1, 3):
        for num_counters in xrange(1, 4):
            for k in xrange(2, args.max_k + 1):
                create_macro_def(k, id_bytes, num_counters)
                fsm, _ = compile_automaton(k, id_bytes, num_counters, macro_count)
                print 'Compiled FSM for i{}c{}k{}, blk={}'.format(id_bytes, num_counters, k, fsm.GetInfo().blocks_rect)


if __name__ == '__main__':
    main()


# vim: nu:et:ts=4:sw=4:fdm=indent
