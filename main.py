#!/usr/bin/env python
from argparse import ArgumentParser
import itertools
import os
import sys

import micronap.sdk as ap

import settings
from apfacade import APFacade
from macros import ItemsetMacro
from dataset import Dataset
from arm import ARM


def parse_args():
    """"""
    parser = ArgumentParser()
    parser.add_argument('--device', '-d', default='/dev/frio0')
    parser.add_argument('--verbose', '-v', action='store_true', default=False)
    parser.add_argument('--max-k', '-k', type=int, required=True)
    parser.add_argument('--min-support', '-s', type=int, required=True)
    parser.add_argument('dataset_file')
    return parser.parse_args()

def import_dataset(dataset_file):
    """"""
    ds = Dataset(dataset_file)
    ds.parse_file()    
    ds.encode_data()
    return ds

def setup_device(dev_name):
    """"""
    dev = APFacade(dev_name=dev_name)
    dev.setup()
    return dev

def main():
    """"""
    args = parse_args()
    dataset = import_dataset(args.dataset_file)
    device = setup_device(args.device)
    arm = ARM(dataset.get_frequent_items(args.min_support), args.min_support)

    for k in xrange(2, args.max_k + 1):
        if args.verbose: print 'Iteration k={}'.format(k)

        arm.init_iteration(k)
        reports = device.execute(arm.fsm, dataset.encoded_data)
        if len(reports) < 1:
            print '  zero {}-itemsets satisfy minsup {}'.format(arm.k, arm.min_support)
            break
        arm.process_reports(reports)

        if args.verbose: 
            print '  survivors({}): {}'.format(len(arm.itemsets), arm.itemsets)


if __name__ == '__main__':
    main()


# vim: nu:et:ts=4:sw=4:fdm=indent
