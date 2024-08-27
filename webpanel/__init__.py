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

    def __eq__(self, value: object) -> bool:
        if isinstance(value, WebPanelResult):
            return self.rsrp == value.rsrp and self.sinr == value.sinr and self.band == value.band
        return False

class WebPanel_FM:
    def __init__(self):
        print("请在*本*设备上任意浏览器手动登录web页")
        print("登录完成后，可关闭页面")
        self.ip = which_is_fm_ip()
        print(f"设备IP: {self.ip}")
        self.tree: dict = None
        self.res = WebPanelResult('nan', 'nan', 'nan')

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
            try:
                try:
                    res = requests.get(f"http://{self.ip}/xml_action.cgi", params, headers=headers,timeout=1)
                    # print(res.content)
                except requests.exceptions.Timeout:
                    print("连接到设备超时")
                    return
                res = res.content.decode()
                self.tree = xml_to_dict(lxml.etree.fromstring(res))
                self.res = WebPanelResult(
                    rsrp=self.tree['wan']['lte_rsrp'],
                    sinr=self.tree['wan']['lte_sinr'],
                    band=self.tree['wan']['lte_band'],
                )

            except:
                print("无法连接到设备" + self.ip + "可能需要重新登录")
                print("正在重新登录")
                login_FM()
                self.update()


    def get(self): 
        if self.tree is None:
            self.update()
        return self.res
    
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

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login_FM(version:str=None,user:str='admin',pwd:str='admin'):
    if version is None:
        try:
            print(f"尝试登录版本 1.3")
            login_FM_1_3(user,pwd)
        except Exception as e:
            try: 
                print(f"尝试登录版本 1.2")
                login_FM_1_2(user,pwd)
            except Exception as e: 
                print(f"无法登录设备,请手动操作")
                
    else:
        if version == '1.3':
            login_FM_1_3(user,pwd)
        elif version == '1.2':
            login_FM_1_2(user,pwd)

def login_FM_1_3(user:str,password:str):
    option = webdriver.EdgeOptions()
    option.add_argument('--headless')
    device = webdriver.Edge(options=option)
    device.get(f"http://{which_is_fm_ip()}")
    device.implicitly_wait(3)
    usr = device.find_element(By.XPATH,'//*[@id="app"]/div/div/div[1]/div/div/div[3]/form/div[1]/div[1]/div/div[1]/div[2]/input')
    usr.clear()
    usr.send_keys(user)
    pwd = device.find_element(By.XPATH,'//*[@id="app"]/div/div/div[1]/div/div/div[3]/form/div[2]/div[1]/div/div[1]/div[2]/input')
    pwd.clear()
    pwd.send_keys(password)
    device.find_element(By.XPATH,'//*[@id="app"]/div/div/div[1]/div/div/button').click()
    time.sleep(1)
    device.close()

def login_FM_1_2(user:str,password:str):
    option = webdriver.EdgeOptions()
    option.add_argument('--headless')
    device = webdriver.Edge(options=option)
    device.get(f"http://{which_is_fm_ip()}")
    device.implicitly_wait(3)
    usr = device.find_element(By.ID,'tbarouter_username')
    usr.clear()
    usr.send_keys(user)
    pwd = device.find_element(By.ID,'tbarouter_password')
    pwd.clear()
    pwd.send_keys(password)
    device.find_element(By.ID,'btnSignIn').click()
    time.sleep(1)
    device.close()
