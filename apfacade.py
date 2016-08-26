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
        self.rtos = []
        self.flows = []

    def setup(self):
        ap.ConfigureDevice(self.dev_name)
        self.device.OpenDevice(self.dev_name)
    
    def load(self, fsms):
        try:
            for fsm in fsms:
                self.rtos.append(self.device.Load(0, fsm))
        except TypeError:
            self.rtos.append(self.device.Load(0, fsms))

    def unload(self):
        for rto in self.rtos:
            rto.Unload()
        self.rtos = []

    def open_flows(self):
        for rto in self.rtos:
            self.flows.append(self.device.OpenFlow(rto))

    def close_flows(self):
        for flow in self.flows:
            flow.Close()
        self.flows = []

    # TODO: support data as a file handle for more efficient memory usage/chunking
    def scan(self, data, chunk_size=settings.DEFAULT_CHUNK_SZ):
        reports = []
        i = 0
        while i < len(data):
            chunk = data[i:i + chunk_size]
            wait = self.device.ScanFlows([(x, chunk) for x in self.flows])
            i += chunk_size
        self.device.Wait(wait)
        return self.get_reports_()

    def get_reports_(self):
        reports = []
        for batch in iter(self.device.GetMatches, []):
            for report in batch:
                reports.append(report)
        return reports

    def execute(self, fsm, data):
        self.load(fsm)
        reports = self.scan(data)
        self.unload()
        return reports


# vim: nu:et:ts=4:sw=4:fdm=indent
