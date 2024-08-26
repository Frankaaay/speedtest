from io import TextIOWrapper
from live import api
import sys
import datetime


class Recorder:
    def __init__(self, file: TextIOWrapper):
        self.file = file
    
    def record(self, res: api.LiveResult, message: str | None):
        raise "Override me🥰"

    def flush(self):
        if self.file is not None:
            self.file.flush()


class Console(Recorder):
    def __init__(self, file = sys.stderr):
        super().__init__(file)

    def record(self, res: api.LiveResult, message: str | None):
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        if res == api.LiveResult.Normal:
            self.file.write(f"{time_str} 正常\n")
        elif res == api.LiveResult.Stuck:
            self.file.write(f"{time_str} 直播卡顿\n")
        elif res == api.LiveResult.End:
            self.file.write(f"{time_str} 直播结束 {message}\n")
        elif res == api.LiveResult.Error:
            self.file.write(f"{time_str} 直播错误 {message}\n")


class Logger(Recorder):
    def __init__(self, file):
        super().__init__(file)
        self.file.write("count,time,result,message\n")
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

class MergeResult:
    def __init__(self, interval=5, threshold=5):
        '''
        interval:  两次间隔小于interval会被合并记录
        threshold: 小于threshold的将不会被记录
        '''
        self.start = None
        self.last_end = None
        self.count = 0

        self.INTERVAL = interval
        self.THRESHOLD = threshold

    def merge(self, res: api.LiveResult, message: str | None)  -> tuple[int, datetime.datetime, datetime.datetime] | None:
        now = datetime.datetime.now()

        if res == api.LiveResult.Normal:
            if self.last_end is None:
                self.last_end = now

            if self.start is not None and (now - self.last_end).total_seconds() > self.INTERVAL:
                duration = (self.last_end - self.start).total_seconds()
                
                going_to_return = None

                if duration >= self.THRESHOLD:
                    going_to_return = (self.count,self.start,self.last_end)
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



class Reporter(Recorder):

    def __init__(self, file, interval=5, threshold=5):
        super().__init__(file)
        self.file.write("start,end,duration\n")
        self.merge = MergeResult(interval, threshold)

    def record(self, res: api.LiveResult, message: str | None) :
        merged_res = self.merge.merge(res, message)
        if merged_res is None:
            return
        
        count,start,end = merged_res

        start_str = start.strftime("%m-%d %H:%M:%S")
        end_str = end.strftime("%m-%d %H:%M:%S")
        duration = (end - start).total_seconds()

        self.file.write(f"{start_str},{end_str},{duration:.3f}\n")
            
