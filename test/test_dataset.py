import os
import shutil
import tempfile
import unittest

from dataset import Dataset


class TestDataset(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.tmpfile = os.path.join(self.tmpdir, 'emptyfile')
        open(self.tmpfile, 'w').close()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_init_with_badfile(self):
        self.assertRaises(ValueError, Dataset, 'fakefile')

    def test_init(self):
        ds = Dataset(self.tmpfile)

    def test_parse_file_empty(self):
        ds = Dataset(self.tmpfile)
        ds.parse_file()

    def test_parse_file(self):
        fn = os.path.join(self.tmpdir, 'foo')
        with open(fn, 'w') as fh:
            fh.write('1 2 3 4 5')
        ds = Dataset(fn)
        ds.parse_file()
        self.assertEquals(ds.data, [[1, 2, 3, 4, 5]])

    def test_get_frequent_items_without_parse_file(self):
        fn = os.path.join(self.tmpdir, 'foo')
        with open(fn, 'w') as fh:
            fh.write('1 2 3 4 5')
        ds = Dataset(fn)
        self.assertEquals(ds.get_frequent_items(1), [])

    def test_get_frequent_items_one_txn(self):
        fn = os.path.join(self.tmpdir, 'foo')
        with open(fn, 'w') as fh:
            fh.write('1 2 3 4 5')
        ds = Dataset(fn)
        ds.parse_file()
        self.assertEquals(ds.get_frequent_items(1), [1, 2, 3, 4, 5])
        self.assertEquals(ds.get_frequent_items(2), [])

    def test_get_frequent_items_oneitem_txns(self):
        fn = os.path.join(self.tmpdir, 'foo')
        with open(fn, 'w') as fh:
            fh.write('1\n')
            fh.write('2\n')
            fh.write('3\n')
            fh.write('4\n')
            fh.write('5\n')
        ds = Dataset(fn)
        ds.parse_file()
        self.assertEquals(ds.get_frequent_items(1), [1, 2, 3, 4, 5])
        self.assertEquals(ds.get_frequent_items(2), [])

    def test_encode_data(self):
        pass
	

# vim: nu:et:ts=4:sw=4:fdm=indent

