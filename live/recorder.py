import api
import datetime
from selenium.common.exceptions import WebDriverException
import os


class Recorder:
    file = None
    
    def record(self, res: api.LiveResult, message: str | None):
        raise "Override me🥰"

    def flush(self):
        if self.file is not None:
            self.file.flush()


class Console(Recorder):
    def record(self, res: api.LiveResult, message: str | None):
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        if res == api.LiveResult.Normal:
            print(f"{time_str} 正常")
        elif res == api.LiveResult.Stuck:
            print(f"{time_str} 直播卡顿")
        elif res == api.LiveResult.End:
            print(f"{time_str} 直播结束 {message}")
        elif res == api.LiveResult.Error:
            print(f"{time_str} 错误 {message}")


class Logger(Recorder):
    def __init__(self, name):
        time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(f"logs/{name}", exist_ok=True)
        self.file = open(
            f"logs/{name}/{time_str}.csv","a", encoding="utf-8-sig")
        self.start = None
        self.count = 0

    def record(self, res: api.LiveResult, message: str | None):
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")

        if res == api.LiveResult.Normal and self.start is not None:
            self.file.write(
                f"{self.count},{time_str},结束,{(now-self.start).total_seconds():.3f}\n")
            self.start = None
            self.count += 1

        elif res == api.LiveResult.Stuck and self.start is None:
            self.start = now
            self.file.write(f"{self.count},{time_str},开始\n")

        elif res == api.LiveResult.End:
            self.file.write(f"-,{time_str},结束,{repr(message)}")

        elif res == api.LiveResult.Error:
            if self.start is not None:
                self.file.write(f"-,{time_str},错误,{repr(message)}\n")
                self.start = now

class MergeResult(Recorder):
    def __init__(self, name, interval=5, threshold=5):
        '''
        interval:  两次间隔小于interval会被合并记录
        threshold: 小于threshold的将不会被记录
        '''
        time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(f"reports/{name}", exist_ok=True)
        self.file = open(
            f"reports/{name}/{time_str}.csv", "a", encoding="utf-8-sig")
        self.start = None
        self.last_end = None
        self.count = 0

        self.INTERVAL = interval
        self.THRESHOLD = threshold

    def record(self, res: api.LiveResult, message: str | None) :
        now = datetime.datetime.now()

        if res == api.LiveResult.Normal:
            if self.last_end is None:
                self.last_end = now

            if self.start is not None and (now - self.last_end).total_seconds() > self.INTERVAL:
                start_str = self.start.strftime("%H:%M:%S")
                end_str = self.last_end.strftime("%H:%M:%S")
                duration = (self.last_end - self.start).total_seconds()

                going_to_return = None

                if duration >= self.THRESHOLD:
                    going_to_return = (self.count,start_str,end_str)
                    self.count += 1

                self.start = None
                self.last_end = None
                
                return going_to_return


        elif res == api.LiveResult.Stuck:
            self.last_end = None
            if self.start is None:
                self.start = now

        elif res == api.LiveResult.End:
            pass

        elif res == api.LiveResult.Error:
            pass



class Reporter(MergeResult):

    def __init__(self, name, interval=5, threshold=5):
        super().__init__(name, interval, threshold)
        time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(f"reports/{name}", exist_ok=True)
        self.file = open(
            f"reports/{name}/{time_str}.csv", "a", encoding="utf-8-sig")

    def record(self, res: api.LiveResult, message: str | None) :
        merged = super().record(res, message)
        if merged is not None:
            count,start,end = merged

            start_str = start.strftime("%H:%M:%S")
            end_str = end.strftime("%H:%M:%S")
            duration = (end - start).total_seconds()

            self.file.write(f"{count},{start_str},{end_str},{duration:.3f}\n")
            
