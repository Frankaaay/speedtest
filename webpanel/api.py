from common import *


def xml_to_dict(element):
    if len(element) == 0:
        return element.text
    return {child.tag: xml_to_dict(child) for child in element}


class WebPanelState:
    rsrp: str
    sinr: str
    band: str

    def __init__(self, rsrp, sinr, band):
        self.rsrp = rsrp
        self.sinr = sinr
        self.band = band

    def __str__(self):
        return f"rsrp: {self.rsrp}, sinr: {self.sinr}, band: {self.band}"

    def __eq__(self, value: object) -> bool:
        if isinstance(value, WebPanelState):
            return self.rsrp == value.rsrp and self.sinr == value.sinr and self.band == value.band
        return False

    def shrink_invalid(self):
        if self.rsrp is None:
            self.rsrp = '-'
        if self.sinr is None:
            self.sinr = '-'
        if self.band is None:
            self.band = '-'
        return self


class WebPanel(Producer):
    def __init__(self, device_ip, timeout=timedelta(seconds=5)):
        super().__init__()
        self.ip = device_ip
        self.tree: dict = None
        self.timeout = timeout.total_seconds()
        self.res = WebPanelState('0', '0', '0')

    def update(self):
        super().update()

    def set_band(self, band):
        pass
