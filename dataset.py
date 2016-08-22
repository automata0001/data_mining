import math
import os
import struct

import settings
import utils


class Dataset(object):
    def __init__(self, datafile):
        if not os.path.isfile(datafile):
            raise ValueError('No such file: {}'.format(datafile))

        self.datafile = datafile
        self.data = []
        self.encoded_data = ''
        self.num_id_bytes = 0

    def parse_file(self):
        """"""
        max_id = 0
        with open(self.datafile) as fh:
            line = fh.readline()
            while line:
                items = map(int, line.strip().split(' '))
                max_id = max(max_id, max(items))
                self.data.append(items)
                line = fh.readline()
        self.calc_num_id_bytes_(max_id)

    def calc_num_id_bytes_(self, max_id):
        """"""
        try:
            self.num_id_bytes = int(math.ceil(math.log(max_id, settings.STE_ID_SPACE)))
        except ValueError:
            pass

    def get_frequent_items(self, threshold):
        """"""
        freq = {}
        for row in self.data:
            for item in row:
                try:
                    freq[item] += 1
                except KeyError:
                    freq[item] = 1

        return [x for x in freq.keys() if freq[x] >= threshold]

    def encode_data(self):
        """"""
        data = []
        for row in self.data:
            # Add the leading transaction delimiter
            data.append(struct.pack('B', settings.DEFAULT_DELIM))
            for item in row:
                id_bytes = utils.to_base(item, settings.STE_ID_SPACE)

                # Prepend any leading ID zeroes
                for _ in xrange(self.num_id_bytes - len(id_bytes)):
                    data.append(struct.pack('B', 0))

                # Add the ID bytes
                for i in id_bytes: 
                    data.append(struct.pack('B', i))

        # Add the end-of-data delimiters
        data.append(struct.pack('B', settings.DEFAULT_DELIM))
        data.append(struct.pack('B', settings.DEFAULT_DELIM))
        data.append(struct.pack('B', settings.DEFAULT_DELIM))

        self.encoded_data = ''.join(data)


# vim: nu:et:ts=4:sw=4:fdm=indent
