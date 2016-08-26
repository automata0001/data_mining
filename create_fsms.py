#!/usr/bin/env python
from argparse import ArgumentParser
import os
import time

import micronap.sdk as ap

import settings
from macros import ItemsetMacro
import utils


def create_macro_def(k, id_bytes, num_counters):
    """"""
    macro = ItemsetMacro(ap.Anml(), k, id_bytes, num_counters)
    macro.compile()
    macro.export('i{}c{}k{}.anml'.format(id_bytes, num_counters, k))

def create_network(ick):
    """"""
    anml = ap.Anml()
    mdef = anml.LoadAnmlMacro(os.path.join(settings.ANML_PATH, '{}.anml'.format(ick)))
    network = anml.CreateAutomataNetwork(anmlId='arm_net_{}'.format(ick))
    return anml, mdef, network

def get_load_size(fsm):
    """"""
    try:
        return ap.CalcLoadSize(fsm)
    except ap.ApError:
        return float('inf')

def compile_automaton(k, id_bytes, num_counters, verbose=False):
    """"""
    ick = 'i{}c{}k{}'.format(id_bytes, num_counters, k)
    count = 1
    exp = 0
    block_size = 0
    elapsed = 0
    t0 = time.time()
    while block_size != settings.BLK_PER_RANK:
        anml, mdef, net = create_network(ick)
        mrefs = []
        for i in xrange(count):
            mrefs.append(net.AddMacroRef(mdef, anmlId='mref{}'.format(i)))
        fsm, emap = anml.CompileAnml(options=ap.CompileDefs.AP_OPT_MT)

        block_size = fsm.GetInfo().blocks_rect
        if verbose: print 'count={}, blocks={}, time={:.2f}'.format(count, block_size, time.time() - t0)

        if block_size > settings.BLK_PER_RANK or get_load_size(fsm) > 8:
            count -= 2**(exp-1) - 1
            exp = 1
        elif elapsed < settings.COMPILE_TIMEOUT:
            count += 2**exp
            exp += 1
        else:
            break
        elapsed = time.time() - t0

    fsm = label_automaton(k, id_bytes, mdef, mrefs, fsm, emap)
    save_automaton(fsm, emap, ick)
    return fsm, emap

def label_automaton(k, id_bytes, mdef, mrefs, fsm, emap):
    changes = []
    for mref in mrefs:
        for i in xrange(k):
            for x in xrange(id_bytes):
                param = mdef.GetMacroParamFromName('%i{}{}'.format(i, x))
                changes.append(ap.ap_symbol_change(mref, '[]', param))
    fsm.SetSymbol(emap, changes)
    return fsm

def save_automaton(fsm, emap, ick):
    """"""
    fsm.Save(os.path.join(settings.FSM_PATH, '{}.fsm'.format(ick)))
    emap.SaveElementMap(os.path.join(settings.MAP_PATH, '{}.map'.format(ick)))

def main():
    """"""

    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument('--max-k', '-k', type=int, required=True)
    parser.add_argument('--device', '-d', default=settings.DEV_NAME)
    parser.add_argument('--verbose', '-v', action='store_true', default=False)
    args = parser.parse_args()

    # Compile automata for each combination of:
    # - number of ID bytes
    # - number of counters
    # - max itemset size (k)
    # 
    for id_bytes in xrange(1, 3):
        for num_counters in xrange(1, 4):
            for k in xrange(2, args.max_k + 1):
                print 'Compiling FSM for i{}c{}k{}'.format(id_bytes, num_counters, k)
                create_macro_def(k, id_bytes, num_counters)
                fsm, _ = compile_automaton(k, id_bytes, num_counters, args.verbose)


if __name__ == '__main__':
    main()


# vim: nu:et:ts=4:sw=4:fdm=indent
