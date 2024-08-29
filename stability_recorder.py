from common import *
import webpanel
import stable
import live
import sys
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

    def stop(self):
        super().stop()
        self.ping.stop()
        if self.device is not None:
            self.device.stop()


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
        self.file.write(
            f"Ping: {','.join([str(pings[self.targets[t]])+'ms' for t in self.target_name])}")
        self.file.write(
            f"State:{state.rsrp}, {state.sinr}, {state.band}\n")


class Main:
    def __init__(self, record_device: bool, device_ip: str, platform: str, room_id: str | None = None, ips: dict = dict()):
        if record_device:
            device = Sequence(webpanel.WebPanel_FM(device_ip),
                              interval=timedelta(seconds=2))
            device.start()
        else:
            device = None

        if len(room_id) == 0:
            room_id = None

        if platform == 'B站':
            living = live.BiliLive(room_id)
        elif platform == '抖音':
            living = live.DouyinLive(room_id)
        elif platform == '西瓜':
            living = live.Xigua(room_id)
        else:
            living = live.BiliLive(room_id)

        now = datetime.now().strftime("%Y-%m-%d_%H-%M")

        os.makedirs(f"log/{now}/", exist_ok=True)

        living.add_recorder(live.Reporter(
            open(f"log/{now}/stuck.csv", 'w', encoding='utf-8-sig'), threshold=1))
        living.add_recorder(live.Console(file=sys.stdout))
        # living = AutoFlush(living, timedelta(seconds=5))
        living = Sequence(living, interval=timedelta(seconds=0.2))
        living.start()

        log = PingAndState(stable.Pings(list(ips.values())), device)
        log = AutoFlush(log, timedelta(seconds=5))
        log.add_recorder(
            Log(open(f"log/{now}/ping.csv", 'w', encoding='utf-8-sig'), ips))
        log.add_recorder(Console(sys.stdout, ips))

        log = SequenceFullSecond(log, interval=timedelta(seconds=1))
        log.start()

        self.log = log
        self.living = living

    def stop(self):
        self.log.stop()
        self.living.stop()


# if __name__ == '__main__':
#     device = input(
#         f"记录设备{utils.which_is_device_ip()}状态 [Y/n] 默认启用:").lower() != 'n'

#     platform = input("平台 [b]站/[d]抖音/[x]西瓜/[a]爱奇艺:").lower()
#     room_id = input("房间号 (可不填):").strip()

#     platform = {'b': 'B站', 'd': '抖音', 'x': '西瓜',
#                 'a': '爱奇艺'}.get(platform, 'B站')

#     try:
#         obj = Main(device,
#                    utils.which_is_device_ip(),
#                    platform,
#                    room_id,
#                    {'ping_www': 'www.baidu.com',
#                     'ping_192': utils.which_is_device_ip()})
#     except KeyboardInterrupt:
#         pass
#     except Exception as e:
#         print(e)
#         raise e
#     finally:
#         obj.stop()
