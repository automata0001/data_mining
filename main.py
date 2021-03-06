#!/usr/bin/env python
from argparse import ArgumentParser
import itertools
import os
import sys

import micronap.sdk as ap

import settings
from macros import ItemsetMacro
from dataset import Dataset
from arm import ARM
import utils


def parse_args():
    """"""
    parser = ArgumentParser()
    parser.add_argument('--device', '-d', default=settings.DEV_NAME)
    parser.add_argument('--verbose', '-v', action='store_true', default=False)
    parser.add_argument('--max-k', '-k', type=int, required=True)
    parser.add_argument('--min-support', '-s', required=True, help='Minimum support threshold expressed as an exact value (n) or a percentage (n%%)')
    parser.add_argument('dataset_file')
    args = parser.parse_args()

    return args

def import_dataset(dataset_file):
    """"""
    ds = Dataset(dataset_file)
    ds.parse_file()    
    ds.encode_data()
    return ds

# TODO: write output to a file (add argument for filename)
def main():
    """"""
    args = parse_args()
    dataset = import_dataset(args.dataset_file)

    args.min_support = utils.normalize_minsup(args.min_support, len(dataset.data))
    if args.min_support > settings.MAX_DOUBLE_TARGET:
        sys.exit('{}: support must be <= {}!'.format(__file__, settings.MAX_DOUBLE_TARGET))

    arm = ARM(dataset.get_frequent_items(args.min_support), args.min_support, dataset.num_id_bytes, dev_name=args.device)
    for k in xrange(2, args.max_k + 1):
        if args.verbose: print 'Iteration k={}'.format(k)

        arm.init_iteration(k)
        arm.execute_iteration(dataset.encoded_data)
        if len(arm.itemsets) < 1:
            print '  zero {}-itemsets satisfy minsup {}'.format(arm.k, arm.min_support)
            break
        # Print survivors list
        if args.verbose: 
            for i in sorted(arm.itemsets, key=lambda x: len(x)):
                print '  {}'.format(sorted(list(i)))


if __name__ == '__main__':
    main()


# vim: nu:et:ts=4:sw=4:fdm=indent
