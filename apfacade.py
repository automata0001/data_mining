import micronap.sdk as ap

import settings


class APFacade(object):
    def __init__(self, dev_name=None):
        if dev_name:
            self.dev_name = dev_name
        else:
            metrics = ap.QueryDeviceMetrics()
            self.dev_name = metrics[0].dev_name

        self.device = ap.Device()
        self.rto = None

    def setup(self):
        ap.ConfigureDevice(self.dev_name)
        self.device.OpenDevice(self.dev_name)
    
    def load(self, fsm):
        self.rto = self.device.Load(0, fsm) 

    def unload(self):
        if self.rto:
            self.rto.Unload()
            self.rto = None

    # TODO: support data as a file handle for more efficient memory usage/chunking
    # TODO: support async behavior, yield reports as they arrive
    def scan(self, data, chunk_size=settings.DEFAULT_CHUNK_SZ):
        reports = []
        i = 0
        flow = self.device.OpenFlow(self.rto)
        while i < len(data):
            chunk = data[i:i + chunk_size]
            wait = self.device.ScanFlows([ (flow, chunk) ])
            self.device.Wait(wait)
            reports += self.get_reports_()
            i += chunk_size
        return reports

    def get_reports_(self):
        erefs = []
        for reports in iter(self.device.GetMatches, []):
            for report in reports:
                erefs.append(report.report_alias.elementRef)
        return erefs

    def execute(self, fsm, data):
        self.load(fsm)
        reports = self.scan(data)
        self.unload()
        return reports


# vim: nu:et:ts=4:sw=4:fdm=indent
