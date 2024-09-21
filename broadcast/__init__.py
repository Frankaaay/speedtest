import socket
from common import *

# 设定广播地址和端口

CONTENT = '''Quod est superius est sicut quod inferius, et quod inferius est sicut quod est superius.'''.encode()
# As above, so below
PORT = 62126


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
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        print(f"[邻居]启动!广播!")
        while not self.stopped:
            sock.sendto(CONTENT, ('<broadcast>', PORT))
            sleep(self.delta)
        print(f"[邻居]停止!广播!")

    def listen(self):
        while not self.stopped:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            try:
                sock.bind(('', PORT))
            except socket.error as e:
                print(f"[邻居] bind error: {e}")
                continue

            data, addr = sock.recvfrom(1024)
            if data != CONTENT:
                continue
            # print(f"[邻居] recv {addr[0]}{addr[1]}")
            self.neighbor[addr[0]] = time()
        

    def update(self):
        now = time()
        self.res = [ip for (ip, timestamp) in self.neighbor.items() if now - timestamp < self.delta]
        super().update()


def main():
    obj = Broadcast(delta=timedelta(seconds=1))
    obj.add_recorder(Recorder())
    obj = Sequence(obj, timedelta(seconds=0.5))
    obj.start()
    sleep(100)
    obj.stop()
