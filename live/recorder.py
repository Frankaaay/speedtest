from .api import LiveState
from common import Recorder, time, datetime, DATETIME_FORMAT
from time import strftime


class Console(Recorder):
    def __init__(self, file):
        super().__init__(file)

    def record(self, res: tuple[LiveState, str | None]):
        state, msg = res
        if msg is None:
            msg = ""
        time_str = strftime("%H:%M:%S")

        if state == LiveState.Normal:
            self.file.write(f"[直播]正常  {time_str} {msg}\n")
        elif state == LiveState.Afk:
            self.file.write(f"[直播]AFK! {time_str} {msg}\n")
        elif state == LiveState.Stuck:
            self.file.write(f"[直播]卡顿! {time_str} {msg}\n")
        elif state == LiveState.End:
            self.file.write(f"[直播]结束! {time_str} {msg}\n")
        elif state == LiveState.Error:
            self.file.write(f"[直播]错误! {time_str} {msg}\n")
        else:
            self.file.write(f"[直播]未知!!{time_str} {msg}\n")

        self.file.flush()


class Logger(Recorder):
    def __init__(self, file):
        super().__init__(file)
        self.file.write("count,time,result,message\n")
        self.start = None
        self.count = 0

    def record(self, res: tuple[LiveState, str | None]):
        state, msg = res
        if msg is None:
            msg = ""
        now = time()
        time_str = strftime("%H:%M:%S")

        if (
            state == LiveState.Normal
            or state == LiveState.Afk
            and self.start is not None
        ):
            self.file.write(f"{self.count},{time_str},结束,{now-self.start:.3f}\n")
            self.start = None
            self.count += 1

        elif state == LiveState.Stuck and self.start is None:
            self.start = now
            self.file.write(f"{self.count},{time_str},开始\n")

        elif state == LiveState.End:
            self.file.write(f"-,{time_str},结束,{repr(msg)}")

        elif state == LiveState.Error:
            if self.start is not None:
                self.file.write(f"-,{time_str},错误,{repr(msg)}\n")
                self.start = now


class MergeResult:
    def __init__(self, interval=5, threshold=5):
        """
        interval:  两次间隔小于interval会被合并记录
        threshold: 小于threshold的将不会被记录
        """
        self.start = None
        self.last_end = None
        self.count = 0

        self.INTERVAL = interval
        self.THRESHOLD = threshold

    def merge(
        self, res: tuple[LiveState, str | None]
    ) -> tuple[int, datetime, datetime] | None:
        now = datetime.now()
        state, msg = res
        if msg is None:
            msg = ""

        if state == LiveState.Normal or state == LiveState.Afk:
            if self.last_end is None:
                self.last_end = now

            if (
                self.start is not None
                and (now - self.last_end).total_seconds() > self.INTERVAL
            ):
                duration = (self.last_end - self.start).total_seconds()

                going_to_return = None

                if duration >= self.THRESHOLD:
                    going_to_return = (self.count, self.start, self.last_end)
                    self.count += 1

                self.start = None
                self.last_end = None

                return going_to_return

        elif state == LiveState.Stuck:
            self.last_end = None
            if self.start is None:
                self.start = now
        elif state == LiveState.End:
            pass
        elif state == LiveState.Error:
            pass


class StuckReporter(Recorder):
    def __init__(self, file, interval=5, threshold=5):
        super().__init__(file)
        self.file.write("start,end,duration\n")
        self.merger = MergeResult(interval, threshold)

    def record(self, res: tuple[LiveState, str | None]):
        res = self.merger.merge(res)
        if res is None:
            return

        count, start, end = res

        start_str = start.strftime(DATETIME_FORMAT)
        end_str = end.strftime(DATETIME_FORMAT)
        duration = (end - start).total_seconds()

        self.file.write(f"{start_str},{end_str},{duration:.1f}\n")
