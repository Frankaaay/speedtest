from common import *
from .api import *
from utils import web_driver, which_is_device_ip
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import lxml.etree


def login_FM(version: str | None = None,  user: str = 'admin', pwd: str = 'admin'):
    driver = web_driver(True)
    if version is None:
        try:
            print(f"尝试登录版本 1.3")
            login_FM_1_3(driver, user, pwd)
        except Exception as e:
            try:
                print(f"尝试登录版本 1.2")
                login_FM_1_2(driver, user, pwd)
            except Exception as e:
                print(f"无法登录设备,请手动操作")

    else:
        try:
            if version == '1.3':
                login_FM_1_3(driver, user, pwd)
            elif version == '1.2':
                login_FM_1_2(driver, user, pwd)
        except Exception as e:
            print(f"无法登录设备,请手动操作")
    driver.close()


def login_FM_1_3(driver: webdriver.Edge, user: str, password: str):
    driver.get(f"http://{which_is_device_ip()}")
    driver.implicitly_wait(3)
    usr = driver.find_element(
        By.XPATH, '//*[@id="app"]/div/div/div[1]/div/div/div[3]/form/div[1]/div[1]/div/div[1]/div[2]/input')
    usr.clear()
    usr.send_keys(user)
    pwd = driver.find_element(
        By.XPATH, '//*[@id="app"]/div/div/div[1]/div/div/div[3]/form/div[2]/div[1]/div/div[1]/div[2]/input')
    pwd.clear()
    pwd.send_keys(password)
    driver.find_element(
        By.XPATH, '//*[@id="app"]/div/div/div[1]/div/div/button').click()
    time.sleep(1)


def login_FM_1_2(driver: webdriver.Edge, user: str, password: str):
    driver.get(f"http://{which_is_device_ip()}")
    driver.implicitly_wait(3)
    usr = driver.find_element(By.ID, 'tbarouter_username')
    usr.clear()
    usr.send_keys(user)
    pwd = driver.find_element(By.ID, 'tbarouter_password')
    pwd.clear()
    pwd.send_keys(password)
    driver.find_element(By.ID, 'btnSignIn').click()
    time.sleep(1)


class WebPanel_FM(WebPanel):
    def __init__(self, timeout=timedelta(seconds=5)):
        print("请在*本*设备上任意浏览器手动登录web页")
        print("登录完成后，可关闭页面")
        # input("按回车继续")
        super().__init__(timeout)

    def update(self):
        super().update()
        params = {
            'method': 'get',
            'module': 'duster',
            'file': 'status1',
        }
        headers = {
            'Authorization': 'Digest username="admin", realm="Highwmg", nonce="57263", uri="/cgi/xml_action.cgi", response="7e50a2c227adae5b48fc3ceed4186fe0", qop=auth, nc=0000006D, cnonce="3624919b183e7e43"',
            'X-Requested-With': 'XMLHttpRequest',
        }
        try:
            try:
                res = requests.get(
                    f"http://{self.ip}/xml_action.cgi", params, headers=headers, timeout=self.timeout)
            except requests.exceptions.Timeout:
                print("连接到设备超时")
                return
            res = res.content.decode()
            self.tree = xml_to_dict(lxml.etree.fromstring(res))
            # print(self.tree)
            self.res = WebPanelState(
                rsrp=self.tree['wan']['lte_rsrp'],
                sinr=self.tree['wan']['lte_sinr'],
                band=self.tree['wan']['lte_band'],
            ).shrink_invalid()

        except Exception as e:
            print(e)
            print("无法连接到设备" + self.ip + "可能需要重新登录")
            print("正在重新登录")
            login_FM()

    def set_band(self, band=0):
        raise NotImplementedError()
        params = {
            'method': 'set',
            'module': 'duster',
            'file': 'wan'
        }
        data = f'<?xml version="1.0" encoding="US-ASCII"?> <RGW><wan><cellular><Prefer_Band>{
            band}</Prefer_Band><Prefer_Band_Action>1</Prefer_Band_Action></cellular><auto_apn_check>1</auto_apn_check></wan></RGW>'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Digest username="admin", realm="Highwmg", nonce="57263", uri="/cgi/xml_action.cgi", response="7e50a2c227adae5b48fc3ceed4186fe0", qop=auth, nc=0000006D, cnonce="3624919b183e7e43"',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-len': len(data),
        }

        res = requests.post(
            f"http://{self.ip}/xml_action.cgi", data, params, headers=headers)
        print(res.content)
        self.update()
