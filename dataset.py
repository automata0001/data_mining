import os

import settings


class Dataset(object):
    def __init__(self, datafile):
        if not os.path.isfile(datafile):
            raise ValueError('No such file: {}'.format(datafile))

        self.datafile = datafile
        self.data = []
        self.encoded_data = ''

    def parse_file(self):
        """"""
        with open(self.datafile) as fh:
            line = fh.readline()
            while line:
                items = map(int, line.strip().split(' '))
                self.data.append(items)
                line = fh.readline()

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
        to_encode = []
        for row in self.data:
            to_encode.append(settings.DEFAULT_DELIM)
            to_encode += row
        to_encode.append(settings.DEFAULT_DELIM)
        to_encode.append(settings.DEFAULT_DELIM)
        to_encode.append(settings.DEFAULT_DELIM)

        self.encoded_data = str(bytearray(to_encode))


# vim: nu:et:ts=4:sw=4:fdm=indent
