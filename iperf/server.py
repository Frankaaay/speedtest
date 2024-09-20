import subprocess
import sys
import time
import threading
import io

IPERF_PATH = r'iperf3\iperf3.exe'

class Server:
    def __init__(self, port, output):
        self.port = port
        self.process = None
        self.output = output

    def start(self):
        self.process = subprocess.Popen([IPERF_PATH, '-s', '-p', str(self.port)])
        
        # threading.Thread(target=self.read_output).start()

    def read_output(self):
        while self.process.poll() is None:
            r = self.process.stdout.readline().decode()
            self.output.write(r)

    def stop(self):
        if self.process:
            self.process.kill()
            self.process.terminate()
            self.process.wait()
            print(f"Server stopped on port {self.port}")

class Servers:
    def __init__(self, ports, output):
        self.servers = [Server(port, output) for port in ports]

    def start(self):
        for server in self.servers:
            server.start()
            time.sleep(0.1)

    def stop(self):
        for server in self.servers:
            server.stop()

if __name__ == "__main__":
    ports = [5201]
    servers = Servers(ports, sys.stdout)
    servers.start()
    # 停止服务器
    # servers.stop()

