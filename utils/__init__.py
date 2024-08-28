import threading
import socket
import re
import time
from datetime import datetime, timedelta
from selenium import webdriver


def web_driver(browser_name: str, headless: bool = False):
    browser_name = browser_name.title()

    if browser_name == "Edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--log-level=3")
        return webdriver.Edge(options=options)
    elif browser_name == "Chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--log-level=3")
        return webdriver.Chrome(options=options)
    elif browser_name == "Firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        options.log.level = 'fatal'
        return webdriver.Firefox(options=options)

    else:
        raise ValueError(f"{browser_name} is not supported")


def wait_full_second(delta=timedelta(seconds=1), now=datetime.now()):
    # Calculate the time until the next second
    next_second = (now + delta).replace(microsecond=0)
    time_to_wait = (next_second - now).total_seconds()
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
    ip = min(ip_addresses)
    print(f"设备IP: {ip}")
    return ip


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
