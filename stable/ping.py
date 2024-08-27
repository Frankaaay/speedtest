import ping3
from statistics import stdev, mean
import time
import datetime
import threading


def ping(target):
    delay = ping3.ping(target, unit='ms', timeout=0.8)
    delay = round(delay,1) if isinstance(delay, float) else float('inf')
    # Why there is data like 10000ms ????
    if delay > 0.8:  delay = float('inf')
    return delay

class ResultsAtRange:
    def __init__(self, history = 10000):
        self.history = history
        self.results = []
    
    def append(self, result):
        self.results.append((datetime.datetime.now(),result))
        if len(self.results) > self.history:
            self.results.pop(0)
        
    def get_range(self, start, end, delta = 0):
        start -= delta
        end += delta
        return [r[1] for r in self.results if start <= r[0] <= end]