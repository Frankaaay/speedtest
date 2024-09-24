from common import (
    Producer,
    Recorder,
    Sequence,
    SequenceFullSecond,
    AutoFlush,
    datetime,
    timedelta,
    DEVICE_INFOS,
)
import panel
import stable
import live
import sys
import os
import utils
import multi3
import broadcast


class PingAndState(Producer):
    def __init__(
        self,
        ping: stable.Pings,
        device: panel.Panel | None,
        net_speed: multi3.ProxySpeed,
        live: live.Live,
        neighbor: broadcast.Broadcast,
    ):
        super().__init__()
        self.ping = ping
        self.device = device
        self.net_speed = net_speed
        self.neighbor = neighbor
        self.live = live
        self.res: tuple[
            datetime, dict[str, float], panel.PanelState, multi3.ProxyResult
        ]
        self.res = ["time", "ping", "device", multi3.ProxyResult(0.03, 3)]

    def update(self):
        super().update()
        now = datetime.now()
        self.ping.update()
        self.net_speed.update()
        self.neighbor.update()
        res = [
            now,
            self.ping.get(),
            self.device.get(),
            "speed",
            len(self.neighbor.get()),
        ]

        if (
            self.net_speed.low_speed_since is not None
            and self.net_speed.low_speed_since
            < (now - timedelta(minutes=2)).timestamp()
        ):
            print("[直播]长时间速度低，刷新直播")
            self.live.find_available()
            self.net_speed.low_speed_since = None

        if self.live.get()[0] == live.LiveState.Afk:
            res[3] = self.res[3]
        else:
            res[3] = self.net_speed.get()

        self.res = tuple(res)

    def stop(self):
        super().stop()
        self.ping.stop()
        self.device.stop()
        self.net_speed.stop()
        self.neighbor.stop()


class ReporterPingAndState(Recorder):
    def __init__(self, file, targets: dict[str, str]):
        super().__init__(file)
        # targets = {
        #     'ip_192':'192.168.0.1'
        # }
        self.targets = targets
        self.target_name = list(targets.keys())
        self.target_name.sort()
        self.file.write(
            "time," + ",".join(self.target_name) + "," + ",".join(DEVICE_INFOS) + ","
            "up,down,neighbor" + "\n"
        )

    def record(
        self,
        data: tuple[
            datetime, dict[str, float], panel.PanelState, multi3.ProxyResult, int
        ],
    ):
        time, pings, state, net_speed, neighbor = data
        time_str = time.strftime("%m-%d %H:%M:%S")
        self.file.write(
            time_str
            + ","
            + ",".join([str(pings[self.targets[t]]) for t in self.target_name])
            + ","
            + ",".join(state.get(i) for i in DEVICE_INFOS)
            + ","
            + str(net_speed.upload)
            + ","
            + str(net_speed.download)
            + ","
            + str(neighbor)
            + "\n"
        )


class ConsolePingAndState(Recorder):
    def __init__(self, file, targets: dict[str, str]):
        super().__init__(file)
        self.pings = stable.Console(file, targets)
        self.net_speed = multi3.Console(file)

    def record(
        self,
        data: tuple[
            datetime, dict[str, float], panel.PanelState, multi3.ProxyResult, int
        ],
    ):
        time, pings, state, net_speed, neighbor = data
        self.pings.record(pings)
        self.net_speed.record(net_speed)
        self.file.write(f"[组播] {neighbor}台设备正在运行\n")


PATH = "./log/live"


def gen_live(
    browser_name: str, platform: str, room_id: str | None, proxy_id: int | None
) -> live.Live:
    if len(room_id) == 0:
        room_id = None
    if proxy_id is not None:
        proxy = f"127.0.0.1:{proxy_id}"
    else:
        proxy = None
    if platform != "OFF":
        if platform == "B站":
            living = live.BiliLive(browser_name, room_id, proxy=proxy)
        elif platform == "抖音":
            living = live.DouyinLive(browser_name, room_id, proxy=proxy)
        elif platform == "西瓜":
            living = live.Xigua(browser_name, room_id, proxy=proxy)
        else:
            living = live.BiliLive(browser_name, room_id, proxy=proxy)
        living.set_ttl(timedelta(minutes=1))
    else:
        living = live.EmptyLive(browser_name, proxy=proxy)
    return living


def gen_device(record_device: bool, device_ip: str, stdout) -> panel.Panel:
    if record_device:
        device = panel.Panel_FM(device_ip, timeout=datetime(second=10), logger=stdout)
        device.set_ttl(timedelta(minutes=1))
    else:
        device = Producer()
    device.set_default(panel.PanelState())
    return device


class Main:
    def __init__(
        self,
        browser_name: str,
        record_device: bool,
        device_ip: str,
        save_log: bool,
        platform: str,
        room_id: str | None = None,
        ips: dict = dict(),  # {'ping_192':'192.168.0.1'}
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

        proxy_id = utils.find_free_port()

        network_speed = multi3.ProxySpeed(utils.which_is_my_ip(device_ip), proxy_id)
        living = gen_live(browser_name, platform, room_id, proxy_id)
        if save_log:
            living.add_recorder(
                live.StuckReporter(
                    open(
                        f"{PATH}/{now}#{folder_name}/stuck.csv",
                        "w",
                        encoding="utf-8-sig",
                    ),
                    interval=5,
                    threshold=0.5,
                )
            )
        living.add_recorder(live.Console(stdout))
        living_seq = AutoFlush(living, timedelta(minutes=5))
        living_seq = Sequence(living_seq, interval=timedelta(seconds=0.3))
        living_seq.start()

        broadcast_obj = broadcast.Broadcast(timedelta(seconds=2))

        ping_device = PingAndState(
            stable.Pings(list(ips.values()), timedelta(seconds=0.75)),
            device_seq,
            network_speed,
            living,
            broadcast_obj,
        )
        ping_device = AutoFlush(ping_device, timedelta(minutes=5))
        if save_log:
            ping_device.add_recorder(
                ReporterPingAndState(
                    open(
                        f"{PATH}/{now}#{folder_name}/ping.csv",
                        "w",
                        encoding="utf-8-sig",
                    ),
                    ips,
                )
            )
        ping_device.add_recorder(ConsolePingAndState(stdout, ips))

        ping_device = SequenceFullSecond(ping_device, interval=timedelta(seconds=1))
        ping_device.start()

        self.obj = ping_device
        self.living = living_seq

    def flush(self):
        self.obj.flush()
        self.living.flush()

    def stop(self):
        self.obj.stop()
        self.living.stop()
