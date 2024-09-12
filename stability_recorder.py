from common import *
import panel
import stable
import live
import sys
import os
import utils
import multi3


class PingAndState(Producer):
    def __init__(self, ping: stable.Pings, device: panel.Panel | None, net_speed: multi3.ProxySpeed, live:live.Live):
        super().__init__()
        self.ping = ping
        self.device = device
        self.net_speed = net_speed
        self.live = live
        self.res:tuple[datetime, dict[str, float], panel.PanelState, multi3.ProxyResult]
        self.res = ['time', 'ping', 'device', multi3.ProxyResult(0.03,3)]

    def update(self):
        super().update()
        now = datetime.now()
        self.ping.update()
        self.net_speed.update()
        res = [now, self.ping.get(),self.device.get(),'speed']

        if self.net_speed.low_speed_since is not None and\
        self.net_speed.low_speed_since < (now - timedelta(minutes=2)).timestamp():
            print('[直播]长时间速度低，刷新直播')
            self.live.find_available()

        if self.live.get()[0] == live.LiveState.Afk:
            res[3] = self.res[3]
        else:
            res[3] = self.net_speed.get()
        
        self.res = tuple(res)

    def stop(self):
        super().stop()
        self.ping.stop()
        if self.device is not None:
            self.device.stop()
        self.net_speed.stop()


class ReporterPingAndState(Recorder):
    def __init__(self, file: TextIOWrapper, targets: dict[str, str]):
        super().__init__(file)
        # targets = {
        #     'ip_192':'192.168.0.1'
        # }
        self.targets = targets
        self.target_name = list(targets.keys())
        self.target_name.sort()
        self.file.write("time," + ','.join(self.target_name) +','+
                        ','.join(DEVICE_INFOS)+','\
                        'up,down'+"\n")

    def record(self, data: tuple[datetime, dict[str, float], panel.PanelState, multi3.ProxyResult]):
        time, pings, state,net_speed = data
        time_str = time.strftime('%m-%d %H:%M:%S')
        self.file.write(time_str+","+
            ','.join([str(pings[self.targets[t]]) for t in self.target_name])+","+
            ','.join(state.get(i) for i in DEVICE_INFOS)+','+
            str(net_speed.upload)+','+str(net_speed.download)+"\n")

class ConsolePingAndState(stable.Console):
    def __init__(self, file: TextIOWrapper, targets: dict[str, str]):
        super().__init__(file,targets)

    def record(self, data: tuple[datetime, dict[str, float], panel.PanelState, multi3.ProxyResult]):
        time, pings, state,net_speed = data
        super().record(pings)
        self.file.write(f"[网速] ⇧{net_speed.upload}Mbps ⇩{net_speed.download}Mbps\n")


PATH = './log/live'

def gen_live(platform: str, room_id: str | None = None,) -> live.Live:
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
        living.set_ttl(timedelta(minutes=1))
    else:
        living = Producer()
        living.set_default((live.LiveState.Normal,'OFF'))
    return living

def gen_device(record_device: bool,device_ip: str, stdout) -> panel.Panel:
    if record_device:
        device = panel.Panel_FM(device_ip, logger=stdout)
        device.set_ttl(timedelta(minutes=1))
    else:
        device = Producer()
    device.set_default(panel.PanelState())
    return device

class Main:
    def __init__(self, 
                 record_device: bool, 
                 device_ip: str, 
                 save_log: bool, 
                 platform: str, 
                 room_id: str | None = None, 
                 ips: dict = dict(), #{'ping_192':'192.168.0.1'}
                 stdout=sys.stdout,
                 folder_name: str = "",
                 ):
        folder_name = utils.sanitize_filename(folder_name)
        now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        if save_log:
            os.makedirs(f"{PATH}/{now}#{folder_name}/", exist_ok=True)
        
        device = gen_device(record_device, device_ip, stdout)
        device.add_recorder(panel.Console(stdout))
        # device = AutoFlush(device, timedelta(minutes=5))
        device_seq = SequenceFullSecond(device, timedelta(seconds=1))
        device_seq.start()

    
        network_speed = multi3.ProxySpeed(utils.proxy_socket,utils.which_is_my_ip())
        living = gen_live(platform, room_id)
        if save_log:
            living.add_recorder(live.Reporter(
                open(f"{PATH}/{now}#{folder_name}/stuck.csv", 'w', encoding='utf-8-sig'), interval=5, threshold=1))
        living.add_recorder(live.Console(stdout))
        living_seq = AutoFlush(living, timedelta(minutes=5))
        living_seq = Sequence(living_seq, interval=timedelta(seconds=0.33))
        living_seq.start()


        ping_device = PingAndState(stable.Pings(list(ips.values())), device, network_speed, living)
        ping_device = AutoFlush(ping_device, timedelta(minutes=5))
        if save_log:
            ping_device.add_recorder(
                ReporterPingAndState(open(f"{PATH}/{now}#{folder_name}/ping.csv", 'w', encoding='utf-8-sig'), ips))
        ping_device.add_recorder(ConsolePingAndState(stdout, ips))

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
