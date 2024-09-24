import socket
import struct
from common import Producer, timedelta, sleep, time, Thread, Recorder, Sequence

# 设定广播地址和端口

# 组播地址和端口
MULTICAST_GROUP = "239.11.45.14"
PORT = 62126
CONTENT = """Quod est superius est sicut quod inferius, et quod inferius est sicut quod est superius.""".encode()
# As above, so below


class Broadcast(Producer):
    def __init__(self, delta: timedelta):
        super().__init__()
        self.delta = delta.total_seconds()
        self.neighbor: dict[str, float] = {}
        self.neighbor_pre: list[str] = []
        self.server = None
        self.handles = [
            Thread(target=self.broadcast),
            Thread(target=self.listen),
        ]
        for handle in self.handles:
            handle.daemon = True
            handle.start()

    def broadcast(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            ttl = struct.pack("b", 5)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
            print("[组播]启动!")
            while not self.stopped:
                s.sendto(CONTENT, (MULTICAST_GROUP, PORT))
                sleep(self.delta / 2)
        print("[组播]停止!")

    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", PORT))
            mreq = struct.pack(
                "4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY
            )
            s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            while not self.stopped:
                data, addr = s.recvfrom(1024)
                if data == CONTENT:
                    # ip, port = addr
                    # addr = f"{ip}:{port}"
                    # print(f"recv from {addr}")
                    self.neighbor[addr] = time()
                # 对比前后两次的邻居列表，输出新增/减少的设备
                if self.neighbor.keys() != self.neighbor_pre:
                    addon = self.neighbor.keys() - self.neighbor_pre
                    delete = self.neighbor_pre - self.neighbor.keys()
                    if addon:
                        print(f"[组播]新增设备: {addon}")
                    if delete:
                        print(
                            f"[组播]减少设备: {self.neighbor_pre - self.neighbor.keys()}"
                        )
                    print(
                        f"[组播]当前{len(self.neighbor)}, {list(self.neighbor.keys())}"
                    )
                    self.neighbor_pre = self.neighbor.keys()

    def update(self):
        now = time()
        self.neighbor = {
            addr: timestamp
            for (addr, timestamp) in self.neighbor.items()
            if now - timestamp < self.delta * 2
        }
        self.res = list(self.neighbor.keys())
        super().update()


def main():
    obj = Broadcast(delta=timedelta(seconds=1))
    obj.add_recorder(Recorder())
    obj = Sequence(obj, timedelta(seconds=0.5))
    obj.start()
    sleep(100)
    obj.stop()
