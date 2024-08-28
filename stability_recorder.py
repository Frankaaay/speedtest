import sys
from common import *
import utils
import live
import webpanel
import stable
import os


class PingAndState(Producer):
    def __init__(self, ping: Producer, device: Producer | None):
        super().__init__()
        self.ping = ping
        self.device = device

    def update(self):
        super().update()
        now = datetime.now()
        self.ping.update()
        if self.device is not None:
            self.device.update()
            self.res = (now, self.ping.get(), self.device.get())
        else:
            empty = webpanel.WebPanelState('-', '-', '-')
            self.res = (now, self.ping.get(), empty)


class Log(Recorder):
    def __init__(self, file: TextIOWrapper, targets: dict[str, str]):
        super().__init__(file)
        # targets = {
        #     'ip_192':'192.168.0.1'
        # }
        self.targets = targets
        self.target_name = list(targets.keys())
        self.target_name.sort()
        self.file.write("time," + ','.join(self.target_name) +
                        ',rsrp,sinr,band\n')

    def record(self, data: tuple[datetime, dict[str, float], webpanel.WebPanelState]):
        time, pings, state = data
        time_str = time.strftime('%m-%d %H:%M:%S')
        self.file.write(f"{time_str},{','.join([str(pings[self.targets[t]]) for t in self.target_name])},{
                        state.rsrp},{state.sinr},{state.band}\n")


class Console(Recorder):
    def __init__(self, file: TextIOWrapper, targets: dict[str, str]):
        super().__init__(file)
        self.targets = targets
        self.target_name = list(targets.keys())
        self.target_name.sort()

    def record(self, data: tuple[datetime, dict[str, float], webpanel.WebPanelState]):
        time, pings, state = data
        time_str = time.strftime('%m-%d %H:%M:%S')
        self.file.write(f"Ping:          {', '.join(
            [str(pings[self.targets[t]])+'ms' for t in self.target_name])} {state.rsrp}, {state.sinr}, {state.band}\n")


ips = {
    'ping_192': utils.which_is_device_ip(),
    'ping_www': 'www.baidu.com',
}


def main():

    device = None

    if input("记录设备状态 [Y/n] 默认启用:").lower() != 'n':
        device = Sequence(webpanel.WebPanel_FM(),
                          interval=timedelta(seconds=3))
        device.start()

    browser = "Edge".title()
    platform = input("平台 [b]站/[d]抖音/[x]西瓜/[a]爱奇艺:").lower()
    room_id = input("房间号 (可不填):").strip()

    if len(room_id) == 0:
        room_id = None

    if platform == 'b':
        living = live.BiliLive(browser, room_id)
    elif platform == 'd':
        living = live.DouyinLive(browser, room_id)
    else:
        living = live.BiliLive(browser, room_id)

    now = datetime.now().strftime("%Y-%m-%d_%H-%M")

    os.makedirs(f"log/{now}/", exist_ok=True)

    living.add_recorder(live.Reporter(
        open(f"log/{now}/stuck.csv", 'w', encoding='utf-8-sig'), threshold=1))
    living.add_recorder(live.Console())
    living = Sequence(living, interval=timedelta(seconds=0.2))
    living.start()

    log = PingAndState(stable.Pings(list(ips.values())), device)
    log.add_recorder(
        Log(open(f"log/{now}/ping.csv", 'w', encoding='utf-8-sig'), ips))
    log.add_recorder(Console(sys.stderr, ips))

    log = SequenceFullSecond(log, interval=timedelta(seconds=1))
    log.start()

    try:
        while True:
            sleep(60)
            log.flush()
            living.flush()
    except KeyboardInterrupt:
        pass
    finally:
        print("Exiting ...")
        # sleep(3)
        living.stop()
        log.stop()
        if device is not None:
            device.stop()


if __name__ == '__main__':
    main()
