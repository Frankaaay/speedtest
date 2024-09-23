import socket
import struct
from common import *

# 设定广播地址和端口

# 组播地址和端口
MULTICAST_GROUP = '239.11.45.14'
PORT = 62126
CONTENT = '''Quod est superius est sicut quod inferius, et quod inferius est sicut quod est superius.'''.encode()
# As above, so below


class Broadcast(Producer):
    def __init__(self, delta:timedelta):
        super().__init__()
        self.delta = delta.total_seconds()
        self.neighbor: dict[str, float] = {}
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
            ttl = struct.pack('b', 5)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
            print(f"[组播]启动!")
            while not self.stopped:
                s.sendto(CONTENT, (MULTICAST_GROUP, PORT))
                sleep(self.delta / 2)
        print(f"[组播]停止!")

    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', PORT))
            mreq = struct.pack('4sl', socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            while not self.stopped:
                data, addr = s.recvfrom(1024)
                if data == CONTENT:
                    # print(f"recv from {addr}")
                    self.neighbor[addr] = time()


    def update(self):
        now = time()
        self.res = [ip for (ip, timestamp) in self.neighbor.items() if now - timestamp < self.delta * 2]
        super().update()


def main():
    obj = Broadcast(delta=timedelta(seconds=1))
    obj.add_recorder(Recorder())
    obj = Sequence(obj, timedelta(seconds=0.5))
    obj.start()
    sleep(100)
    obj.stop()
