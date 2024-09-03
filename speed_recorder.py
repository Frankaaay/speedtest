import sys
from common import *
from speedspider import SpeedTester, SpeedTestResult
from webpanel import WebPanelState, WebPanel_FM


class Reporter(Recorder):
    def __init__(self, f):
        super().__init__(f)
        self.file.write("time,lag,jit,download,upload,rsrp,sinr,band,pci\n")

    def record(self, res: tuple[SpeedTestResult, WebPanelState]):
        now = datetime.now().strftime("%m-%d %H:%M:%S")
        speed_res, device_res = res
        self.file.write(
            f"{now},"
            f"{speed_res.lag},{speed_res.jit},{speed_res.dl},{speed_res.ul},"
            f"{device_res.rsrp},{device_res.sinr},{device_res.band},{device_res.pci}"
            "\n")


class Console(Recorder):
    def record(self, res: tuple[SpeedTestResult,WebPanelState]):
        speed_res, device_res = res
        self.file.write(f"{speed_res}\n")
        self.file.write(f"{device_res}\n")

class SpeedAndState(Producer):
    def __init__(self, speed: SpeedTester, device: WebPanel_FM):
        super().__init__()
        self.speed = speed
        self.device = device

    def update(self):
        super().update()
        self.device.update()
        self.speed.update()
        self.res: tuple[None, None] = (self.speed.get(), self.device.get())

def gen_device(record_device: bool,device_ip: str) -> Sequence:
    if record_device:
        device = WebPanel_FM(device_ip)
    else:
        device = Producer()
        device.res = WebPanelState()
    return device

PATH = './log/speed'
def Main(urls, record_device: bool, device_ip: str, save_log: bool, headless: bool, stdout) -> SpeedTester:
        device = gen_device(record_device,device_ip)
        speed = SpeedTester(headless,timedelta(minutes=2), urls)
        now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        obj = SpeedAndState(speed, device)
        obj.add_recorder(Console(stdout))

        if save_log:
            import os
            os.makedirs(f"{PATH}/{now}/", exist_ok=True)
            obj.add_recorder(
                Reporter(open(f"{PATH}/{now}/speed.csv", 'w', encoding='utf-8-sig')))
        return obj

