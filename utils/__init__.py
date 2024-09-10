import threading
import socket
import re
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy

browser_name = 'Edge'
proxy_socket = '127.0.0.1:6210'
SPEED_UP = True

def web_driver(browser_name=browser_name, headless: bool = False, proxy_enable = False):
    print(f"Creating {browser_name=}, {headless=}, {proxy_enable=}")
    if browser_name == "Edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless")
        if SPEED_UP:
            prefs = {
                'profile.managed_default_content_settings.images': 2,
                'profile.managed_default_content_settings.stylesheets':2,
                'profile.managed_default_content_settings.popups':2,
            }
            options.add_experimental_option("prefs", prefs)
        if proxy_enable:
            options.add_argument(f'--proxy-server={proxy_socket}')
        options.add_argument("--log-level=3")
        return webdriver.Edge(options=options)
    
    elif browser_name == "Chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        if SPEED_UP:
            prefs = {
                'profile.managed_default_content_settings.images': 2,
                'profile.managed_default_content_settings.stylesheets':2,
                'profile.managed_default_content_settings.popups':2,
            }
            options.add_experimental_option("prefs", prefs)
        if proxy_enable:
            options.add_argument(f'--proxy-server={proxy_socket}')
        options.add_argument("--log-level=3")
        return webdriver.Chrome(options=options)
    
    elif browser_name == "Firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        if SPEED_UP:
            options.set_preference('permissions.default.stylesheet', 2)
            options.set_preference('permissions.default.image', 2)
            options.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        options.log.level = 'fatal'
        if proxy_enable:
            options.set_preference('network.proxy.type', 1)
            options.set_preference('network.proxy.http', proxy_socket.split(':')[0])
            options.set_preference('network.proxy.http_port', int(proxy_socket.split(':')[1]))
        return webdriver.Firefox(options=options)

    else:
        raise ValueError(f"{browser_name} is not supported")


# def web_driver(headless: bool = False, proxy_enable: bool = False):
#     return _web_driver(browser_name, headless, proxy_enable)


def wait_full_second(delta=1, now=time.time()):
    # Calculate the time until the next second
    next_second = int(now + delta)
    time_to_wait = (next_second - now)
    # Wait until the next second
    time.sleep(time_to_wait)


def which_is_device_ip():
    hostname = socket.gethostname()
    ip_addresses = socket.getaddrinfo(hostname, None)
    ip_addresses = [ip[4][0] for ip in ip_addresses]
    ip_addresses = [ip for ip in ip_addresses if ip.startswith(
        '192.') and not ip.endswith('.1')]
    # 替换 .1
    ip_addresses = [re.sub(r'\.\d+$', '.1', ip) for ip in ip_addresses]
    if len(ip_addresses) > 0:
        ip = '.'.join(map(str,min(list(map(lambda ip:list(map(int,ip.split('.'))),ip_addresses)))))
        print(ip_addresses, "->", ip)
        return ip
    else: 
        return 'Not Detected'
    
def which_is_my_ip():
    hostname = socket.gethostname()
    ip_addresses = socket.getaddrinfo(hostname, None)
    ip_addresses = [ip[4][0] for ip in ip_addresses]
    ip_addresses = [ip for ip in ip_addresses if ip.startswith(
        '192.') and not ip.endswith('.1')]
    # 替换 .1
    # ip_addresses = [re.sub(r'\.\d+$', '.1', ip) for ip in ip_addresses]
    if len(ip_addresses) > 0:
        ip = '.'.join(map(str,min(list(map(lambda ip:list(map(int,ip.split('.'))),ip_addresses)))))
        print(ip_addresses, "->", ip)
        return ip
    else: 
        return '0.0.0.0'


class ThreadWithReturn(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name,
                         args=args, kwargs=kwargs, daemon=daemon)
        self._return = None

    def run(self):
        try:
            if self._target is not None:
                self._return = self._target(*self._args, **self._kwargs)
        finally:
            del self._target, self._args, self._kwargs

    def join(self, timeout=None):
        super().join(timeout)
        return self._return

def sanitize_filename(filename):
    # 替换非法字符为下划线
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 去除前后空格
    sanitized = sanitized.strip()
    # 如果文件名为空，设置为默认值
    if not sanitized:
        sanitized = 'default_filename'
    return sanitized