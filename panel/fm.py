from common import *
from .api import *
from socket import socket, AF_INET, SOCK_STREAM

class AT:
    def __init__(self, device_ip, timeout:float):
        self.ip = device_ip
        self.timeout = timeout
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.settimeout(self.timeout)
        self.s.connect((self.ip, 8090))
    
    def sr1(self, cmd:str):
        self.s.sendall(cmd.encode())
        res = self.s.recv(80).decode().strip()
        # print(f"{cmd} -> {res}")
        return res
    
    def get(self):
        res = {}
        x = self.sr1('AT*BANDIND?')[len('*BANDIND: '):].split(',')
        res['band'] = x[1].strip()
        x = self.sr1('AT*CESQ')[len('*CESQ: '):].split(',')
        res['sinr'] = x[-1]
        x = self.sr1('AT+RSRP?')[len('+RSRP: '):].split(',')
        res['pci'] = x[0]
        res['earfcn'] = x[1]
        res['rsrp'] = x[2]
        return PanelState(res)
    
    def __del__(self):
        self.s.close()



class Panel_FM(Panel):
    def __init__(self, device_ip, timeout=timedelta(seconds=10)):
        super().__init__(device_ip, timeout)

    def update(self):
        self.res = AT(self.ip,self.timeout).get()

    def set_band(self, band=0):
        raise NotImplementedError()
    
    def reboot(self):
        raise NotImplementedError()
