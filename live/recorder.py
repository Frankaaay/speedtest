import live
import datetime
from selenium.common.exceptions import WebDriverException
import os

class Recorder:
    file = None
    def record(self, res: live.LiveResult, message:str|None):
        pass
    def flush(self):
        if self.file is not None: self.file.flush()

class Console(Recorder):
    def record(self, res: live.LiveResult, message: str | None):
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        if res == live.LiveResult.Normal:
            print(f"{time_str} 正常")
        elif res == live.LiveResult.Stuck:
            print(f"{time_str} 直播卡顿")
        elif res == live.LiveResult.End:
            print(f"{time_str} 直播结束 {message}")
        elif res == live.LiveResult.Error:
            print(f"{time_str} 错误 {message}")

            

class Logger(Recorder):
    def __init__(self, name):
        time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(f"logs/{name}", exist_ok=True)
        self.file = open(f"logs/{name}/{time_str}.csv","a",encoding="utf-8-sig")
        self.start = None
        self.count = 0

    def record(self, res: live.LiveResult, message:str|None):
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        
        if res == live.LiveResult.Normal and self.start is not None:
            self.file.write(f"{self.count},{time_str},结束,{(now-self.start).total_seconds():.3f}\n")
            self.start = None
            self.count += 1

        elif res == live.LiveResult.Stuck and self.start is None:
            self.start = now
            self.file.write(f"{self.count},{time_str},开始\n")

        elif res == live.LiveResult.End:
            self.file.write(f"-,{time_str},结束,{repr(message)}")
            
        elif res == live.LiveResult.Error:
            if self.start is not None:
                self.file.write(f"-,{time_str},错误,{repr(message)}\n")
                self.start = now


class Reporter(Recorder):

    def __init__(self, name, interval = 5, threshold = 5):
        '''
        interval:  两次间隔小于interval会被合并记录
        threshold: 小于threshold的将不会被记录
        '''
        time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(f"reports/{name}", exist_ok=True)
        self.file = open(f"reports/{name}/{time_str}.csv","a",encoding="utf-8-sig")
        self.start = None
        self.last_end = None
        self.count = 0

        self.INTERVAL = interval
        self.THRESHOLD = threshold

    def record(self, res: live.LiveResult, message:str|None):
        now = datetime.datetime.now()
        
        if res == live.LiveResult.Normal:
            if self.last_end is None:
                self.last_end = now
            
            if self.start is not None and (self.last_end-self.start).total_seconds() > self.INTERVAL:
                start_str = self.start.strftime("%H:%M:%S")
                end_str = self.last_end.strftime("%H:%M:%S")
                duration = (self.last_end - self.start).total_seconds()

                if duration >= self.THRESHOLD:
                    print(f"{self.count},{start_str},{end_str},{duration:.3f}\n")
                    self.file.write(f"{self.count},{start_str},{end_str},{duration:.3f}\n")
                    self.count += 1

                self.start = None
                self.last_end = None

        elif res == live.LiveResult.Stuck:
            self.last_end = None
            if self.start is None:
                self.start = now

        elif res == live.LiveResult.End:
            pass

        elif res == live.LiveResult.Error:
            pass