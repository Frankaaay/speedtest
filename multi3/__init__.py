import os
import socket
import toml
import json
from common import Recorder, Producer, time

# https://github.com/epiglottis-cartilage/multi3 at branch FM
"""
通过代理获取浏览器的流量
此为与multi3通信的接口
"""


def set_config(device_ip, id):
    cfg = {
        "tui": True,  # terminal user interface
        "ipv6_first": False,  # that is ipv4 first, None is default
        "lookup": f"127.0.0.1:{id+1}",  # lookup address return how many bytes has been proxied
        "timeout": {"connect": 5000, "retry": 10000, "io": 180000},
        "routing": [
            {
                "id": id,
                "host": [f"127.0.0.1:{id}"],
                "pool": [device_ip],
            }
        ],
    }
    toml.dump(cfg, open("multi3.toml", "w"))


def get_sciatic(id) -> None | dict[str, int]:
    stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        stream.connect(("127.0.0.1", id + 1))
    except Exception:
        print("[代理]无法连接到multi3!!")
        return None
    stream.send(str(id).encode())
    try:
        res = json.loads(stream.recv(128).decode("utf-8"))
    except Exception as e:
        print(f"[代理]无法获取流量: {e}")
        return None
    return res


def start_proxy() -> None:
    print("[代理]启动!multi3!")
    os.system("start multi3.exe")


def stop_proxy(id) -> None:
    print("[代理]停止!multi3!")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as stream:
            stream.connect(("127.0.0.1", id + 1))
            stream.send("KILL".encode())
    except Exception:
        print("[代理]无法连接到multi3!!")
        os.system("taskkill /f /im multi3.exe")
        # 反正有重启机制
        # 传奇耐kill王


def is_running():
    return get_sciatic() is not None


class ProxyResult:
    """
    单位: Mb/s
    单位: ms
    """

    upload: float
    download: float

    def __init__(self, upload, download):
        self.upload = upload
        self.download = download


class ProxySpeed(Producer):
    def __init__(self, device_ip, id):
        super().__init__()
        self.device_ip = device_ip
        self.id = id
        set_config(self.device_ip, self.id)
        start_proxy()
        self.previous_time = time() - 1
        self.previous = {"ul": 0, "dl": 0}
        self.low_speed_since = None

    def update(self):
        res = get_sciatic(self.id)
        # 获取当前的上行和下行流量
        if res is None:
            set_config(self.device_ip, self.id)
            start_proxy()
            return
        # 如果获取不到流量，则返回
        super().update()
        rate = {
            "ul": round(
                (res["ul"] - self.previous["ul"])
                / (time() - self.previous_time)
                * 8
                / 1024
                / 1024,
                2,
            ),
            "dl": round(
                (res["dl"] - self.previous["dl"])
                / (time() - self.previous_time)
                * 8
                / 1024
                / 1024,
                2,
            ),
        }
        # 计算当前的上行和下行流量速率
        if rate["ul"] + rate["dl"] < 0.2:
            if self.low_speed_since is None:
                self.low_speed_since = time()
        else:
            self.low_speed_since = None

        # 如果当前的上行和下行流量速率之和小于0.2，则设置low_speed_since为当前时间
        # 否则，将low_speed_since设置为None
        self.previous_time = time()
        # 设置上一次的时间为当前时间
        self.previous = res

        # 设置上一次的上行和下行流量为当前流量
        self.res = ProxyResult(rate["ul"], rate["dl"])
        # 设置返回结果为当前的上行和下行流量速率
        # sleep(1)

    def stop(self):
        super().stop()
        stop_proxy(self.id)


class Console(Recorder):
    def __init__(self, file):
        super().__init__(file)

    def record(self, data: ProxyResult):
        self.file.write(f"[网速] ⇧{data.upload}Mbps ⇩{data.download}Mbps\n")
