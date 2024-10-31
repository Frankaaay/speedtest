import sys
from common import (
    Recorder,
    Producer,
    Sequence,
    DEVICE_INFOS,
    datetime,
    timedelta,
    DATETIME_FORMAT,
)
import utils
from speedspider import SpeedTester, SpeedTestResult, SpeedTester0Interval
from panel import PanelState, Panel_FM


class Reporter(Recorder):
    def __init__(self, f):
        super().__init__(f)
        self.file.write("time,lag,jit,download,upload," + ",".join(DEVICE_INFOS) + "\n")

    def record(self, res: tuple[SpeedTestResult, PanelState]):
        now = datetime.now().strftime(DATETIME_FORMAT)
        speed, state = res
        self.file.write(
            now
            + ","
            + f"{speed.lag},{speed.jit},{speed.dl},{speed.ul},"
            + ",".join(state.get(i) for i in DEVICE_INFOS)
            + "\n"
        )


class Console(Recorder):
    def record(self, res: tuple[SpeedTestResult, PanelState]):
        speed_res, device_res = res
        self.file.write("[时间]" + datetime.now().strftime("%H:%M:%S") + "\n")
        self.file.write(f"[网速]{speed_res}\n")
        self.file.write(f"[设备]{device_res}\n")


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


def gen_device(record_device: bool, device_ip: str, stdout) -> Sequence:
    if record_device:
        device = Panel_FM(device_ip, logger=stdout)
        device.set_ttl(timedelta(minutes=3))
    else:
        device = Producer()
    device.set_default(PanelState())
    return device


PATH = "./log/speed"


def Main(
    browser_name: str,
    urls: list[str],
    record_device: bool,
    device_ip: str,
    save_log: bool,
    headless: bool,
    stdout=sys.stdout,
    folder_name: str = "",
    faster_version: bool = False,
) -> SpeedTester:
    folder_name = utils.sanitize_filename(folder_name)

    device = gen_device(record_device, device_ip, stdout)
    if faster_version:
        speed = SpeedTester0Interval(browser_name, headless, timedelta(minutes=1), urls)
    else:
        speed = SpeedTester(browser_name, headless, timedelta(minutes=1), urls)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M")

    obj = SpeedAndState(speed, device)
    obj.add_recorder(Console(stdout))
    if save_log:
        import os

        os.makedirs(f"{PATH}/{now}#{folder_name}/", exist_ok=True)
        obj.add_recorder(
            Reporter(
                open(f"{PATH}/{now}#{folder_name}/speed.csv", "w", encoding="utf-8-sig")
            )
        )
    return obj


if __name__ == "__main__":
    utils.browser_name = "Firefox"
    obj = SpeedTester0Interval(headless=False)
    while True:
        obj.update()
        print(obj.get())
