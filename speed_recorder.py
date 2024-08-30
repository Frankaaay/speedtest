import sys
from common import *
from speedspider import SpeedTester, SpeedTestResult


class Reporter(Recorder):
    def __init__(self, f):
        super().__init__(f)
        self.file.write("time,lag,jit,download,upload\n")

    def record(self, res: SpeedTestResult):
        now = datetime.now().strftime("%m-%d %H:%M:%S")
        self.file.write(
            f"{now},{res.lag},{res.jit},{res.dl},{res.ul}\n")


class Console(Recorder):
    def record(self, res: SpeedTestResult):
        self.file.write(f"{res}\n")




def Main(urls, save_log: bool) -> SpeedTester:
        obj = SpeedTester(headless=False, urls=urls)
        now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        obj.add_recorder(Console(sys.stderr))

        if save_log:
            import os
            os.makedirs(f"log/", exist_ok=True)
            obj.add_recorder(
                Reporter(open(f"log/{now}-speed.csv", 'w', encoding='utf-8-sig')))
        return obj

