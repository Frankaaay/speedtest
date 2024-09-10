import ping3
from common import *
from utils import ThreadWithReturn


def ping(target, timeout=timedelta(seconds=0.75)):
    try:
        delay = ping3.ping(target, unit='ms', timeout=timeout.total_seconds())
        delay = round(delay, 1) if isinstance(delay, float) else float('inf')
        # Why there is data like 10000ms ????
        if delay > timeout.total_seconds()*1000:
            delay = float('inf')
        return delay
    except ping3.errors.PingError:
        return float('inf')
    except Exception as e:
        print(e)
        return float('inf')


class Pings(Producer):
    def __init__(self, targets: list[str], timeout=timedelta(seconds=0.75)):
        super().__init__()
        self.target = targets
        self.res: dict[str, float] = {}
        self.timeout = timeout

    def add_target(self, target: str):
        self.target.append(target)

    def update(self):
        super().update()
        handles: dict[str, Thread] = {}
        for target in self.target:
            handles[target] = ThreadWithReturn(
                target=ping, args=(target, self.timeout))
            handles[target].start()

        res: dict[str, float] = {}
        for target, thread in handles.items():
            # Stupid method return None and I have to overwrite it
            res[target] = thread.join()

        self.res = res

class Console(Recorder):
    def __init__(self, file: TextIOWrapper, targets: dict[str, str]):
        super().__init__(file)
        self.targets = targets
        self.target_name = list(targets.keys())
        self.target_name.sort()

    def record(self, pings: dict[str, float]):
        self.file.write(
            f"Ping: {','.join([str(pings[self.targets[t]])+'ms' for t in self.target_name])}\n")
