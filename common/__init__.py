from io import TextIOWrapper
from threading import Thread
from time import sleep,time
from datetime import datetime, timedelta
from utils import wait_full_second

class Recorder:
    def __init__(self, file: TextIOWrapper):
        self.file = file
    
    def record(self, res):
        self.file.write(f"{res}\n")

    def flush(self):
        if self.file is not None:
            self.file.flush()
    
    def close(self):
        self.flush()
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

class Producer:
    def __init__(self):
        self.res = None
        self.recorders:list[Recorder] = []

    def update(self):
        pass

    def get(self):
        return self.res
    
    def consume(self):
        x = self.get()
        self.res = None
        return x
    
    def add_recorder(self, recorder: Recorder):
        self.recorders.append(recorder)

    def record(self):
        for recorder in self.recorders:
            recorder.record(self.get())
    
    def stop(self):
        for recorder in self.recorders:
            recorder.close()

    def flush(self):
        for recorder in self.recorders:
            recorder.flush()


class Sequence(Thread, Producer):
    def __init__(self, obj:Producer, interval:timedelta):
        super().__init__()
        Producer.__init__(self)
        self.obj = obj
        self.interval = interval
        self.res = obj.get()
        self.stopped = False

    def update(self):
        self.res = self.obj.get()

    def run(self):
        try:
            while not self.stopped:
                now = time()
                self.obj.update()
                self.update()
                self.obj.record()
                sleep(max(0, self.interval.total_seconds() - (time() - now)))
        except KeyboardInterrupt:
            self.stopped = True
        finally:
            self.obj.stop()

    def stop(self):
        self.stopped = True


class SequenceFullSecond(Sequence):
    def update(self):
        wait_full_second(self.interval)
        self.res = self.obj.get()

class SequenceConsumed(Sequence):
    def update(self):
        self.res = self.obj.consume()
    


        
    
