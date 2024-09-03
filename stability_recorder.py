from common import *
import panel
import stable
import live
import sys
import os
import re


class PingAndState(Producer):
    def __init__(self, ping: stable.Pings, device: panel.Panel | None):
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
            empty = panel.PanelState()
            self.res = (now, self.ping.get(), empty)

    def stop(self):
        super().stop()
        self.ping.stop()
        if self.device is not None:
            self.device.stop()


class Reporter(Recorder):
    def __init__(self, file: TextIOWrapper, targets: dict[str, str]):
        super().__init__(file)
        # targets = {
        #     'ip_192':'192.168.0.1'
        # }
        self.targets = targets
        self.target_name = list(targets.keys())
        self.target_name.sort()
        self.file.write("time," + ','.join(self.target_name) +','+
                        ','.join(DEVICE_INFOS)+"\n")

    def record(self, data: tuple[datetime, dict[str, float], panel.PanelState]):
        time, pings, state = data
        time_str = time.strftime('%m-%d %H:%M:%S')
        self.file.write(time_str+","+
            ','.join([str(pings[self.targets[t]]) for t in self.target_name])+","+
            ','.join(state.get(i) for i in DEVICE_INFOS)+"\n")



PATH = './log/live'

def gen_live(platform: str, room_id: str | None = None,) -> Sequence:
    if len(room_id) == 0:
        room_id = None

    if platform != 'OFF':
        if platform == 'B站':
            living = live.BiliLive(room_id)
        elif platform == '抖音':
            living = live.DouyinLive(room_id)
        elif platform == '西瓜':
            living = live.Xigua(room_id)
        else:
            living = live.BiliLive(room_id)

    else:
        living = Producer()
        living.set_default((live.LiveState.Normal,'OFF'))
    return living

def gen_device(record_device: bool,device_ip: str) -> Sequence:
    if record_device:
        device = panel.Panel_FM(device_ip)
    else:
        device = Producer()
        device.set_default(panel.PanelState())
    return device

class Console(Recorder):
    def record(self, data: tuple[datetime, dict[str, float], panel.PanelState]):
        time, pings, state = data
        time_str = time.strftime('%m-%d %H:%M:%S')


class Main:
    def __init__(self, record_device: bool, device_ip: str, platform: str, room_id: str | None = None, ips: dict = dict(), stdout=sys.stdout):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        os.makedirs(f"{PATH}/{now}/", exist_ok=True)
        
        device = gen_device(record_device,device_ip)
        device.add_recorder(panel.Console(stdout))
        # device = AutoFlush(device, timedelta(minutes=5))
        device = SequenceFullSecond(device, timedelta(seconds=1))
        device.start()

        living = gen_live(platform, room_id)
        living.add_recorder(live.Reporter(
            open(f"{PATH}/{now}/stuck.csv", 'w', encoding='utf-8-sig'), threshold=1))
        living.add_recorder(live.Console(stdout))
        living = AutoFlush(living, timedelta(minutes=5))
        living = Sequence(living, interval=timedelta(seconds=0.3))
        living.start()


        ping_device = PingAndState(stable.Pings(list(ips.values())), device)
        ping_device = AutoFlush(ping_device, timedelta(minutes=5))
        ping_device.add_recorder(
            Reporter(open(f"{PATH}/{now}/ping.csv", 'w', encoding='utf-8-sig'), ips))
        ping_device.add_recorder(stable.Console(stdout, ips))

        ping_device = SequenceFullSecond(ping_device, interval=timedelta(seconds=1))
        ping_device.start()

        self.obj = ping_device
        self.living = living

    def flush(self):
        self.obj.flush()
        self.living.flush()
    
    def stop(self):
        self.obj.stop()
        self.living.stop()
