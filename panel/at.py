from socket import socket, AF_INET, SOCK_STREAM, timeout

class AT:
    def __init__(self, device_ip, timeout:float):
        self.ip = device_ip
        self.timeout = timeout
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.settimeout(self.timeout)
        self.s.connect((self.ip, 8090))
    
    def sr1(self, cmd:str):
        self.s.sendall(cmd.encode())
        try:
            res = self.s.recv(80).decode().strip()
            # print(f"{cmd} -> {res}")
            return res
        except TimeoutError:
            return "ERR: AT command {cmd} timed out"
    
    
    def __del__(self):
        self.s.close()

