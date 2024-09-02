from common import *


def xml_to_dict(element):
    if len(element) == 0:
        return element.text
    return {child.tag: xml_to_dict(child) for child in element}


class WebPanelState:
    rsrp: str
    sinr: str
    band: str
    pci: str

    def __init__(self, rsrp='-',sinr='-', band='-',pci='-'):
        self.rsrp = rsrp
        self.sinr = sinr
        self.band = band
        self.pci = pci

    def __str__(self):
        return f"rsrp: {self.rsrp}, pci:{self.pci} sinr: {self.sinr}, band: {self.band}"

    def __eq__(self, value: object) -> bool:
        if isinstance(value, WebPanelState):
            return self.rsrp == value.rsrp and self.sinr == value.sinr and self.band == value.band and self.pci == value.pci
        return False

    def shrink_invalid(self):
        if self.rsrp is None:
            self.rsrp = '-'
        if self.sinr is None:
            self.sinr = '-'
        if self.band is None:
            self.band = '-'
        if self.pci is None:
            self.pci = '-'
        return self


class WebPanel(Producer):
    def __init__(self, device_ip, timeout=timedelta(seconds=5)):
        super().__init__()
        self.ip = device_ip
        self.tree: dict = None
        self.timeout = timeout.total_seconds()
        self.res = WebPanelState()

    def update(self):
        super().update()

    def set_band(self, band):
        pass

    def reboot(self):
        pass
