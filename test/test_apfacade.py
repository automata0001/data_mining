import unittest

import micronap.sdk as ap

from apfacade import APFacade


class TestAPFacade(unittest.TestCase):
    def setUp(self):
        anml = ap.Anml()
        network = anml.CreateAutomataNetwork()
        network.AddSTE('*', startType=ap.AnmlDefs.ALL_INPUT, match=True)
        fsm, emap = anml.CompileAnml()
        self.fsm = fsm
        self.emap = emap

    def test_init_nodev(self):
        apf = APFacade()
        self.assertEquals(isinstance(apf.device, ap.Device), True)

    def test_init_withdev(self):
        apf = APFacade(dev_name='/dev/frio0')
        self.assertEquals(isinstance(apf.device, ap.Device), True)

    def test_load_without_setup(self):
        apf = APFacade()
        self.assertRaises(ap.ApError, apf.load, self.fsm)

    def test_load_with_setup(self):
        apf = APFacade()
        apf.setup()
        apf.load(self.fsm)
        self.assertEquals(isinstance(apf.rto, ap.RTO), True)

    def test_unload_without_load(self):
        apf = APFacade()
        apf.setup()
        apf.unload()
        self.assertEquals(apf.rto, None)

    def test_unload_with_load(self):
        apf = APFacade()
        apf.setup()
        apf.load(self.fsm)
        self.assertEquals(isinstance(apf.rto, ap.RTO), True)
        apf.unload()
        self.assertEquals(apf.rto, None)

    def test_scan_without_load(self):
        apf = APFacade(dev_name='//simulator/frio0')
        apf.setup()
        self.assertRaises(TypeError, apf.scan, 'foobar')

    def test_scan_with_load(self):
        apf = APFacade(dev_name='//simulator/frio0')
        apf.setup()
        apf.load(self.fsm)
        reports = apf.scan('foo')
        self.assertEquals(reports, [1, 1, 1])
	

# vim: nu:et:ts=4:sw=4:fdm=indent
