import os
import socket
import toml
import json
from common import *

def set_config(device_ip, id):
    cfg = {
        'tui': True ,
        'ipv6_first': False,
        'lookup' : f"127.0.0.1:{id+1}",
        'timeout' :{
            'connect' : 5000,
            'retry' :10000,
            'io' :  180000
        },
        'routing' : [
            {
                'id': id,
                'host': [f"127.0.0.1:{id}"],
                'pool': [device_ip],
            }
        ]
    }
    toml.dump(cfg, open('multi3.toml', 'w'))

def get_sciatic(id):
    stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        stream.connect(('127.0.0.1', id+1))
    except:
        print("[代理]无法连接到multi3!!")
        start_proxy()
        return None
    stream.send(str(id).encode())
    try:
        res =  json.loads(stream.recv(128).decode('utf-8'))
    except Exception as e:
        print(f"[代理]无法获取流量: {e}")
        return {'ul':0,'dl':0}
    return res



def start_proxy():
    print("[代理]启动!multi3!")
    os.system("start multi3.exe")

def stop_proxy():
    print("[代理]停止!multi3!")
    os.system("taskkill /f /im multi3.exe")

def is_running():
    return get_sciatic() is not None    


class ProxyResult:
    '''
    单位: Mbps
    单位: ms
    '''
    upload: float 
    download: float

    def __init__(self, upload, download):
        self.upload = upload
        self.download = download

class ProxySpeed(Producer):
    def __init__(self,device_ip,id):
        super().__init__()
        self.id = id
        set_config(device_ip,self.id)
        start_proxy()
        self.previous_time = time() -  1
        self.previous = {'ul':0,'dl':0}
        self.low_speed_since = None

    def update(self):
        res = get_sciatic(self.id)
        # 获取当前的上行和下行流量
        if res is None:
            return
        # 如果获取不到流量，则返回
        super().update()
        rate = {
            'ul' : round((res['ul'] - self.previous['ul']) / (time() - self.previous_time) * 8 / 1024 / 1024,3),
            'dl' : round((res['dl'] - self.previous['dl']) / (time() - self.previous_time) * 8 / 1024 / 1024,3),
        }
        # 计算当前的上行和下行流量速率
        if rate['ul'] + rate['dl'] < 0.2:
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
        self.res = ProxyResult(rate['ul'], rate['dl'])
        # 设置返回结果为当前的上行和下行流量速率
        # sleep(1)
    
    def stop(self):
        super().stop()
        stop_proxy()

        
class Console(Recorder):
    def __init__(self, file: TextIOWrapper):
        super().__init__(file)

    def record(self, data: ProxyResult):
        self.file.write(f"[网速] ⇧{data.upload}Mbps ⇩{data.download}Mbps\n")