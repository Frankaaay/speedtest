import threading
import socket
import re
import time
from datetime import datetime, timedelta  # noqa: F401
from selenium import webdriver
import random


def time_it(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(f"[耗时] {func.__name__} 耗时: {end - start:.2f}s")
        return res

    return wrapper


def web_driver(
    browser_name="Edge",
    headless: bool = False,
    proxy: None | str = None,
    disable_pic=False,
):
    print(f"[浏览器] Creating {browser_name=}, {headless=}, {proxy=}, {disable_pic=}")
    if browser_name == "Edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless")
        if disable_pic:
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.managed_default_content_settings.stylesheets": 2,
                "profile.managed_default_content_settings.popups": 2,
            }
            options.add_experimental_option("prefs", prefs)
        if proxy is not None:
            options.add_argument(f"--proxy-server={proxy}")
        options.add_argument("--log-level=3")
        return webdriver.Edge(options=options)

    elif browser_name == "Chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        if disable_pic:
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.managed_default_content_settings.stylesheets": 2,
                "profile.managed_default_content_settings.popups": 2,
            }
            options.add_experimental_option("prefs", prefs)
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        options.add_argument("--log-level=3")
        return webdriver.Chrome(options=options)

    elif browser_name == "Firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        if disable_pic:
            options.set_preference("permissions.default.stylesheet", 2)
            options.set_preference("permissions.default.image", 2)
            options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", "false")
        options.log.level = "fatal"
        if proxy:
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.http", proxy.split(":")[0])
            options.set_preference("network.proxy.http_port", int(proxy.split(":")[1]))
        return webdriver.Firefox(options=options)

    else:
        raise ValueError(f"{browser_name} is not supported")


# def web_driver(headless: bool = False, proxy_enable: bool = False):
#     return _web_driver(browser_name, headless, proxy_enable)


def wait_full_second(delta=1, now=time.time()):
    # Calculate the time until the next second
    next_second = int(now + delta)
    time_to_wait = next_second - now
    # Wait until the next second
    time.sleep(time_to_wait)


@time_it
def which_is_device_ip() -> str:
    hostname = socket.gethostname()
    ip_addresses = socket.getaddrinfo(hostname, None)
    ip_addresses = [ip[4][0] for ip in ip_addresses]
    ip_addresses = [
        ip for ip in ip_addresses if ip.startswith("192.") and not ip.endswith(".1")
    ]
    # 替换 .1
    ip_addresses = [re.sub(r"\.\d+$", ".1", ip) for ip in ip_addresses]
    if len(ip_addresses) > 0:
        ip = ".".join(
            map(
                str,
                min(list(map(lambda ip: list(map(int, ip.split("."))), ip_addresses))),
            )
        )
        print("[IP]", ip_addresses, "->", ip)
        return ip
    else:
        return "Not Detected"


@time_it
def which_is_my_ip(device_ip=None) -> str:
    # UDP连接到设备，返回本地ip
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((device_ip, 80))
            ip = s.getsockname()[0]
            print("[IP]", device_ip, "->", ip)
            return ip
    except Exception as e:
        print(f"[IP] 无法通过{device_ip}获取本机IP {e}")

        hostname = socket.gethostname()
        ip_addresses = socket.getaddrinfo(hostname, None)
        ip_addresses = [ip[4][0] for ip in ip_addresses]
        ip_addresses = [
            ip for ip in ip_addresses if ip.startswith("192.") and not ip.endswith(".1")
        ]
        # 不替换 .1
        if len(ip_addresses) > 0:
            ip = ".".join(
                map(
                    str,
                    min(
                        list(
                            map(lambda ip: list(map(int, ip.split("."))), ip_addresses)
                        )
                    ),
                )
            )
            print("[IP]", ip_addresses, "->", ip)
            return ip
        else:
            return "Not Detected"


class ThreadWithReturn(threading.Thread):
    def __init__(
        self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None
    ):
        super().__init__(
            group=group,
            target=target,
            name=name,
            args=args,
            kwargs=kwargs,
            daemon=daemon,
        )
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


def sanitize_filename(filename) -> str:
    # 替换非法字符为下划线
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # 去除前后空格
    sanitized = sanitized.strip()
    # 如果文件名为空，设置为默认值
    if not sanitized:
        sanitized = ""
    return sanitized


@time_it
def find_free_port() -> int:
    def port_occupied(address, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((address, port))
        sock.close()
        return result == 0

    res = random.randint(2000, 40000)
    while port_occupied("0.0.0.0", res):
        res = random.randint(2000, 40000)

    print(f"[IP]可用端口：{res}")

    return res
