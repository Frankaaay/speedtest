from io import TextIOWrapper
from threading import Thread
from time import sleep, time
from datetime import datetime, timedelta
from utils import wait_full_second
import sys

DEVICE_INFOS = ['rsrq','rsrp','sinr','band','pci','bar']
DEVICE_INFOS_UNIT = ['dB','dBm','dB','','','']

class StupidClassExistOnlyForDebug:
    _StupidClass_name = ""
    _StupidClass_debug = False

    def __get_caller(self):
        frame = sys._getframe(1)
        while frame.f_back and frame.f_back.f_code.co_name.startswith('__'):
            frame = frame.f_back
        return frame
    
    def __display_stack(self):
        f = self.__get_caller()
        print(f'    at "{f.f_code.co_filename}", line {f.f_lineno}, in {f.f_code.co_name}')

    def __init__(self) -> None:
        if self._StupidClass_debug:
            print(f"constructing {type(self).__name__} {self._StupidClass_name}")
            self.__display_stack()
            print()

    def __del__(self) -> None:
        if self._StupidClass_debug:
            print(f"destructing {type(self).__name__} {self._StupidClass_name}")
            # self.__display_stack()
            # print()

    def set_name(self, name: str=""):
        self._StupidClass_name = str(name)

class Recorder(StupidClassExistOnlyForDebug):
    def __init__(self, file: TextIOWrapper):
        super().__init__()
        self.file = file

    def record(self, res):
        if self.file is not None:
            self.file.write(f"{res}\n")

    def flush(self):
        if self.file is not None:
            self.file.flush()

    def close(self):
        if self.file is not None:
            self.file.close()
            self.file = None

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()
    

class Producer(StupidClassExistOnlyForDebug):
    def __init__(self):
        super().__init__()
        self.res = None
        self.recorders: list[Recorder] = []
        self.stopped = False
        self.ttl = float('inf')
        self.last_update = time()
        self.default = None

    def set_ttl(self, ttl: timedelta):
        self.ttl = ttl.total_seconds()
    
    def set_default(self, default):
        self.default = default
        if self.res is None:
            self.res = default

    def update(self):
        self.last_update = time()

    def get(self):
        if self.last_update + self.ttl < time():
            return self.default
        else:
            return self.res

    def consume(self):
        x = self.get()
        self.res = self.default
        return x

    def add_recorder(self, recorder: Recorder):
        self.recorders.append(recorder)

    def record(self):
        for recorder in self.recorders:
            recorder.record(self.get())

    def stop(self):
        self.stopped = True
        for recorder in self.recorders:
            recorder.close()

    def flush(self):
        for recorder in self.recorders:
            recorder.flush()
        
    


class AutoFlush(Producer):
    def __init__(self, obj: Producer, interval: timedelta):
        super().__init__()
        self.obj = obj
        self.interval = interval
        self.last_flush = time()
        self.res = obj.get()

    def update(self):
        super().update()
        self.obj.update()
        self.res = self.obj.get()
        if time() - self.last_flush > self.interval.total_seconds():
            self.flush()
            self.obj.flush()
            self.last_flush = time()

    def flush(self):
        super().flush()
        self.obj.flush()

    def stop(self):
        super().stop()
        self.obj.stop()

    def record(self):
        super().record()
        self.obj.record()


class Sequence(Thread, Producer, StupidClassExistOnlyForDebug):
    def __init__(self, obj: Producer, interval: timedelta):
        Thread.__init__(self)
        Producer.__init__(self)
        StupidClassExistOnlyForDebug.__init__(self)
        self.obj = obj
        self.interval = interval
        self.res = obj.get()
        self.stopped = False
        self.last_run = time()-self.interval.total_seconds()

    def update(self):
        super().update()
        self.res = self.obj.get()

    def run(self):
        try:
            while not self.stopped:
                now = time()
                if now < self.last_run + self.interval.total_seconds():
                    sleep(max(0, min(1, self.last_run + self.interval.total_seconds() - now)))
                    continue
                self.last_run = now
                self.obj.update()
                self.update()
                self.obj.record()
                # sleep(max(0, self.interval.total_seconds() - (now - now)))
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
            self.obj.stop()


    def flush(self):
        super().flush()
        self.obj.flush()

class SequenceFullSecond(Sequence):
    def run(self):
        try:
            while not self.stopped:
                now = time()
                if now >= self.last_run + self.interval.total_seconds():
                    pass
                elif now+1 >= self.last_run + self.interval.total_seconds():
                    wait_full_second(now=now)
                else:
                    sleep(max(0, self.last_run + self.interval.total_seconds() - now))
                    continue
                self.last_run = time()
                self.obj.update()
                self.update()
                self.obj.record()
                # sleep(max(0, self.interval.total_seconds() - (now - now)))
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
            self.obj.stop()

