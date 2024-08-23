from tester import SpeedTester
import time
import datetime
from threading import Thread

class Sequence(Thread):
    def __init__(self, tester: SpeedTester, interval = datetime.timedelta(minutes=5)):
        super().__init__()
        self.tester = tester
        self.interval = interval
        self.last_run = datetime.datetime.now() - self.interval
        self.results = []
        self.stopped = False

    def run(self):
        while not self.stopped:
            if datetime.datetime.now() - self.last_run > self.interval:
                self.results.append(self.tester.speed_test())
                self.last_run = datetime.datetime.now()
            else:
                # don't let stop wait for too long!!!
                time.sleep(2)

    def __len__(self):
        return len(self.results)

    def consume(self):
        return  self.results.pop(0) if len(self.results)>0 else None

    def stop(self):
        self.stopped = True
        self.tester.close()
        time.sleep(1)
    
