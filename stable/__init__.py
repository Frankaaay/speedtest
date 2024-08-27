import ping3
from common import *


def ping(target, timeout = timedelta(seconds=0.75)):
    try:
        delay = ping3.ping(target, unit='ms', timeout=timeout.total_seconds())
        delay = round(delay,1) if isinstance(delay, float) else float('inf')
        # Why there is data like 10000ms ????
        if delay > timeout.total_seconds()*1000:  delay = float('inf')
        return delay
    except ping3.errors.PingError:
        return float('inf')
    
class PingSingle(Thread):
    def __init__(self, target, timeout = timedelta(seconds=0.75)):
        super().__init__()
        self.target = target
        self.timeout = timeout
    def run(self) -> None:
        self._return = ping(self.target, self.timeout)

    def join(self) -> float:
        super().join()
        return self._return
    
class Pings(Producer):
    def __init__(self, targets:list[str], timeout = timedelta(seconds=0.7)):
        super().__init__()
        self.target = targets
        self.res:dict[str,float] = {}
        self.timeout = timeout
        
    def add_target(self, target:str):
        self.target.append(target)

    def update(self):
        super().update()
        handles: dict[str, Thread] = {}
        for target in self.target:
            handles[target] = PingSingle(target,self.timeout)
            handles[target].start()

        res: dict[str, float] = {}
        for target, thread in handles.items():
            # Stupid method return None and I have to overwrite it
            res[target] = thread.join()
            
        
        self.res = res