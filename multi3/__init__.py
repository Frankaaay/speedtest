import os
import socket
import toml
import json
from common import *

LOOK_UP_PORT = 7878

def set_config(proxy_socket, device_ip):
    cfg = {
        'tui': True ,
        'ipv6_first': False,
        'lookup' : f"127.0.0.1:{LOOK_UP_PORT}",
        'timeout' :{
            'connect' : 5000,
            'retry' :10000,
            'io' :  180000
        },
        'routing' : [
            {
                'id': 0,
                'host': [proxy_socket],
                'pool': [device_ip],
            }
        ]
    }
    toml.dump(cfg, open('multi3.toml', 'w'))

def get_sciatic():
    stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        stream.connect(('127.0.0.1', LOOK_UP_PORT))
    except:
        print("无法连接到multi3!!")
        start_proxy()
        return None
    stream.send(b'0')
    res = stream.recv(128).decode('utf-8')
    return json.loads(res)



def start_proxy():
    os.system("start multi3.exe")

def stop_proxy():
    os.system("taskkill /f /im multi3.exe")

def is_running():
    return get_sciatic() is not None    

class ProxySpeed(Producer):
    def __init__(self, proxy_socket, device_ip):
        super().__init__()
        set_config(proxy_socket, device_ip)
        start_proxy()
        self.previous_time = time() -  1
        self.previous = {'ul':0,'dl':0}

    def update(self):
        super().update()
        res = get_sciatic()

        rate = {
            'ul' : round((res['ul'] - self.previous['ul']) / (time() - self.previous_time) / 1024,2),
            'dl' : round((res['dl'] - self.previous['dl']) / (time() - self.previous_time) / 1024,2),
        }

        self.previous_time = time()
        self.previous = res

        self.res = rate
        # sleep(1)
    
    def stop(self):
        super().stop()
        stop_proxy()

        
