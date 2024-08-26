import socket
import lxml.etree
import requests
import re
import lxml

def xml_to_dict(element):
    if len(element) == 0:
        return element.text
    return {child.tag: xml_to_dict(child) for child in element}

def which_is_fm_ip():
    hostname = socket.gethostname()
    ip_addresses = socket.getaddrinfo(hostname, None)
    ip_addresses = [ip[4][0] for ip in ip_addresses]
    ip_addresses = [ip for ip in ip_addresses if ip.startswith('192.') and not ip.endswith('.1')]
    # 替换 .1
    ip_addresses = [re.sub(r'\.\d+$', '.1', ip) for ip in ip_addresses]
    return min(ip_addresses)

if __name__ == "__main__":
    print(which_is_fm_ip())

class WebPanelResult:
    rsrp: str
    sinr: str
    band: str

    def __init__(self, rsrp, sinr, band):
        self.rsrp = rsrp
        self.sinr = sinr
        self.band = band

    def __str__(self):
        return f"rsrp: {self.rsrp}, sinr: {self.sinr}, band: {self.band}"

class WebPanel_FM:
    def __init__(self):
        print("请在*本*设备上任意浏览器手动登录web页")
        print("登录完成后，可关闭页面")
        input("等待登录 (Enter)")
        self.ip = which_is_fm_ip()
        print(f"设备IP: {self.ip}")
        self.tree :dict = None

    def update(self):
        params ={
            'method': 'get',
            'module': 'duster',
            'file': 'status1'
        }
        headers = {
            'Authorization':'Digest username="admin", realm="Highwmg", nonce="57263", uri="/cgi/xml_action.cgi", response="7e50a2c227adae5b48fc3ceed4186fe0", qop=auth, nc=0000006D, cnonce="3624919b183e7e43"',
            'X-Requested-With': 'XMLHttpRequest'
        }
        res = requests.get(f"http://{self.ip}/xml_action.cgi", params, headers=headers)
        # print(res.content)
        try:
            res = res.content.decode()
            self.tree = xml_to_dict(lxml.etree.fromstring(res))
        except:
            raise "无法连接到设备" + self.ip + "可能需要重新登录"

    def get(self): 
        if self.tree is None:
            self.update()
        return WebPanelResult(
            rsrp=self.tree['wan']['lte_rsrp'],
            sinr=self.tree['wan']['lte_sinr'],
            band=self.tree['wan']['lte_band'],
        )
    
    def set_band(self, band=0):
        raise "不可用"
        params ={
            'method': 'set',
            'module': 'duster',
            'file': 'wan'
        }
        data = f'<?xml version="1.0" encoding="US-ASCII"?> <RGW><wan><cellular><Prefer_Band>{band}</Prefer_Band><Prefer_Band_Action>1</Prefer_Band_Action></cellular><auto_apn_check>1</auto_apn_check></wan></RGW>'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization':'Digest username="admin", realm="Highwmg", nonce="57263", uri="/cgi/xml_action.cgi", response="7e50a2c227adae5b48fc3ceed4186fe0", qop=auth, nc=0000006D, cnonce="3624919b183e7e43"',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-len': len(data),
        }
        
        res = requests.post(f"http://{self.ip}/xml_action.cgi", data, params, headers=headers)
        print(res.content)
        self.update()

import time
import datetime
from threading import Thread

class Sequence(Thread):
    def __init__(self, obj: WebPanel_FM, interval = datetime.timedelta(seconds=1)):
        super().__init__()
        self.obj = obj
        self.interval = interval
        self.res = obj.get()
        self.stopped = False

    def run(self):
        while not self.stopped:
            self.obj.update()
            self.res = self.obj.get()
            time.sleep(1 - (datetime.datetime.now().microsecond/1000000))

    def stop(self):
        self.stopped = True
        time.sleep(self.interval.total_seconds())
    