import subprocess
import sys
import json
from common import Producer

IPERF_PATH = "iperf3/iperf3.exe"


class ClientTcp(Producer):
    res: float

    def __init__(
        self,
        server_ip,
        server_port,
        duration,
        num_streams,
        reverse,
        bandwidth,
        output=sys.stderr,
        capture_output=False,
    ):
        self.server_ip = server_ip
        self.server_port = server_port
        self.duration = duration
        self.num_streams = num_streams
        self.reverse = reverse
        self.bandwidth = bandwidth
        self.f = output
        self.process = None
        self.capture_output = capture_output
        super().__init__()

    def repr(self):
        return f"TCP {'⬇️' if self.reverse else '⬆️'}"

    def update(self):
        cmd = [
            IPERF_PATH,
            "-c",
            self.server_ip,
            "-p",
            str(self.server_port),
            "-t",
            str(self.duration),
            "-P",
            str(self.num_streams),
        ]
        if len(self.bandwidth) > 0:
            cmd.append("-b")
            cmd.append(self.bandwidth)
        if self.reverse:
            cmd.append("-R")
        if self.capture_output:
            cmd.append("-J")
            self.f.write(f"[iperf]运行 {' '.join(cmd)}\n")
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = self.process.communicate()
            self.res = (self.repr(), self.parse_output(stdout))
            self.process.terminate()
        else:
            self.f.write(f"[iperf]运行 {' '.join(cmd)}\n")
            self.process = subprocess.Popen(cmd, text=True)
            self.res = (self.repr(), "不捕获输出")

    def parse_output(self, output):
        try:
            result = json.loads(output)
            try:
                return (
                    result["end"]["sum_received"]["bits_per_second"] / 1e6
                )  # 转换为Mbps
            except KeyError:
                self.f.write(f"[iperf]错误 {result['error']}\n")
        except (json.JSONDecodeError, KeyError) as e:
            self.f.write(f"[iperf]错误 Json: {e}\n")
            return None


class ClientUdp(Producer):
    res: float

    def __init__(
        self,
        server_ip,
        server_port,
        duration,
        num_streams,
        reverse,
        bandwidth,
        output=sys.stderr,
        capture_output=False,
    ):
        self.server_ip = server_ip
        self.server_port = server_port
        self.duration = duration
        self.num_streams = num_streams
        self.reverse = reverse
        self.bandwidth = bandwidth
        self.f = output
        self.process = None
        self.capture_output = capture_output
        super().__init__()

    def repr(self):
        return f"UDP {'⬇️' if self.reverse else '⬆️'}"

    def update(self):
        cmd = [
            IPERF_PATH,
            "-c",
            self.server_ip,
            "-p",
            str(self.server_port),
            "-t",
            str(self.duration),  # '-P', str(self.num_streams),
            "-u",
            "-b",
            str(self.bandwidth),
        ]
        if self.reverse:
            cmd.append("-R")
        if self.capture_output:
            cmd.append("-J")
            self.f.write(f"[iperf]运行 {' '.join(cmd)}\n")
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = self.process.communicate()
            self.res = (self.repr(), self.parse_output(stdout))
            self.process.terminate()
        else:
            self.f.write(f"[iperf]运行 {' '.join(cmd)}\n")
            self.process = subprocess.Popen(cmd, text=True)
            self.res = (self.repr(), "不捕获输出")

    def parse_output(self, output):
        try:
            result = json.loads(output)
            try:
                return result["end"]["sum"]["bits_per_second"] / 1e6  # 转换为Mbps
            except KeyError:
                self.f.write(f"[iperf]错误 {result['error']}\n")
        except (json.JSONDecodeError, KeyError) as e:
            self.f.write(f"[iperf]错误 Json {e}\n")
            return None


# 示例使用
if __name__ == "__main__":
    tcp_client = ClientTcp("127.0.0.1", 5201, 4, 4, True)
    tcp_result = tcp_client.update()
    print(f"TCP Test Result: {tcp_result} Mbps")

    # udp_client = ClientUdp('127.0.0.1', 5201, 4, 4, '1M')
    # udp_result = udp_client.update()
    # print(f"UDP Test Result: {udp_result} Mbps")
