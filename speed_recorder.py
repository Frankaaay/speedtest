import sys
from common import *
from speedspider import SpeedTester, SpeedTestResult
from panel import PanelState, Panel_FM
import utils


class Reporter(Recorder):
    def __init__(self, f):
        super().__init__(f)
        self.file.write("time,lag,jit,download,upload,"+
                        ','.join(DEVICE_INFOS)+"\n")

    def record(self, res: tuple[SpeedTestResult, PanelState]):
        now = datetime.now().strftime("%m-%d %H:%M:%S")
        speed, state = res
        self.file.write(now+","+
            f"{speed.lag},{speed.jit},{speed.dl},{speed.ul},"+
            ','.join(state.get(i) for i in DEVICE_INFOS)+"\n")


class Console(Recorder):
    def record(self, res: tuple[SpeedTestResult,PanelState]):
        speed_res, device_res = res
        self.file.write(f"{speed_res}\n")
        self.file.write(f"{device_res}\n")

class SpeedAndState(Producer):
    def __init__(self, speed: SpeedTester, device: Panel_FM):
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
        device = Panel_FM(device_ip)
        device.set_ttl(timedelta(minutes=5))
    else:
        device = Producer()
    device.set_default(PanelState())
    return device

PATH = './log/speed'
def Main(urls: list[str], 
         record_device: bool, 
         device_ip: str, 
         save_log: bool, 
         headless: bool, 
         stdout=sys.stdout,
         folder_name: str = "",
         ) -> SpeedTester:
        folder_name = utils.sanitize_filename(folder_name)
        device = gen_device(record_device,device_ip)
        speed = SpeedTester(headless,timedelta(minutes=2), urls)
        now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        obj = SpeedAndState(speed, device)
        obj.add_recorder(Console(stdout))
        if save_log:
            import os
            os.makedirs(f"{PATH}/{now}#{folder_name}/", exist_ok=True)
            obj.add_recorder(
                Reporter(open(f"{PATH}/{now}#{folder_name}/speed.csv", 'w', encoding='utf-8-sig')))
        return obj

