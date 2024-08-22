from subprocess import PIPE, Popen
from statistics import stdev, mean
import time
import datetime
import threading


def pings(target, n, sleep=0.1):
    # Use powershell Test-Connection
    run = Popen(["pwsh", "-Command", f"1..{n}|Foreach-Object", "{(Test-Connection", str(
        target), "-Count", "1", ").Latency;", "Start-Sleep", str(sleep), "}",], stdout=PIPE, stderr=PIPE)
    out, err = run.communicate()
    # print(out.decode(),err.decode())
    res = list(map(int, out.decode().split()))
    return res


def ping_and_jit(data: list[int]):
    return (round(mean(data), 2), round(stdev(data), 2))


class ResultSequence(threading.Thread):
    def __init__(self, target, n, sleep=0.1, history=10000, delta=datetime.timedelta(seconds=10)):
        threading.Thread.__init__(self)
        self.arg = (target, n, sleep)
        self.res = []
        self.history = history
        self.range = delta

    def run(self):
        # start a test at every second
        def f():
            res = ping_and_jit(pings(*self.arg))
            self.res.append((datetime.datetime.now(), res))
            while len(self.res) > self.history:
                self.res.pop(0)
        while True:
            time.sleep(1-datetime.time().microsecond/1000000)
            threading.Thread(target=f).start()

    def get_res(self, start: datetime.datetime, end: datetime.datetime):
        start -= self.range
        end += self.range
        time.sleep(self.range.total_seconds())
        return [(r[0].strftime("%H:%M:%S"), r[1]) for r in self.res if start <= r[0] <= end]
