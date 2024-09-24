from common import Producer, timedelta, sleep
from utils import web_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import exceptions as SEexceptions
import random
import threading


class SpeedTestResult:
    lag: float
    jit: float
    dl: float
    ul: float

    def __init__(self, lag, jit, dl, ul):
        self.lag = lag
        self.jit = jit
        self.dl = dl
        self.ul = ul

    def __repr__(self) -> str:
        return f"lag:{self.lag} jit:{self.jit} ⇩:{self.dl} ⇧:{self.ul}"


URLS = [
    "http://wsus.sjtu.edu.cn/speedtest/",
    # "http://speed.neu.edu.cn/", # fuck stupid web always get 502
    "http://test.ustc.edu.cn/",
    # "http://test.nju.edu.cn/", # sometimes get Timeout
    "http://speed.nuaa.edu.cn/",
]


class SpeedTester(Producer):
    def __init__(
        self, browser_name: str, headless: bool, timeout: timedelta, urls: list[str]
    ):
        super().__init__()
        self.browser_name = browser_name
        self.headless = headless
        self.timeout = timeout.total_seconds()
        self.urls = urls if len(urls) > 0 else URLS
        self.asap = False

    def update(self):
        super().update()
        url = random.choice(self.urls)
        # 为了减少故障率，每次都重新打开一个浏览器
        driver = web_driver(
            browser_name=self.browser_name, headless=self.headless, disable_pic=True
        )
        driver.implicitly_wait(5)
        driver.get(url)
        try:
            startStopBtn = driver.find_element(By.ID, "startStopBtn")
            if startStopBtn.get_attribute("class") == "":
                startStopBtn.click()
            sleep(2)

            def afap(driver):
                try:
                    return (
                        int(driver.execute_script("return s.getState()")) == 4
                        or float(driver.find_element(By.ID, "ulText").text) > 0
                    )
                except ValueError:
                    return False

            WebDriverWait(driver, self.timeout).until(afap)
            self.asap = True
            WebDriverWait(driver, self.timeout).until(
                lambda driver: int(driver.execute_script("return s.getState()")) == 4
            )
            lag = driver.find_element(By.ID, "pingText").text
            jit = driver.find_element(By.ID, "jitText").text
            dl = driver.find_element(By.ID, "dlText").text
            ul = driver.find_element(By.ID, "ulText").text
        except SEexceptions.NoSuchElementException as e:
            lag = repr(e)
            jit = url
            dl = ul = "nan"
            print("[测速]NoSuchElementException")
            print(e)
        except SEexceptions.TimeoutException:
            lag = "SpeedTest Timeout"
            jit = url
            dl = ul = "nan"
            print("[测速]TimeoutException")
        except Exception as e:
            lag = repr(e)
            jit = url
            dl = ul = "nan"
        finally:
            self.asap = True
            threading.Thread(target=driver.quit).start()
            sleep(0.3)

        try:
            lag = float(lag)
            jit = float(jit)
            dl = float(dl)
            ul = float(ul)
            self.res = SpeedTestResult(float(lag), float(jit), float(dl), float(ul))
        except ValueError:
            self.res = SpeedTestResult(lag, jit, dl, ul)
        self.asap = False


class SpeedTester0Interval(Producer):
    """
    在第一个测速'上传'开始后开始第二个测速
    """

    def __init__(
        self, browser_name, headless=True, timeout=timedelta(minutes=2), urls=URLS
    ):
        super().__init__()
        self.headless = headless
        self.timeout = timeout.total_seconds()
        self.urls = urls
        self.jobs = []
        self.obj1 = SpeedTester(browser_name, headless, timeout, urls)
        self.obj2 = SpeedTester(browser_name, headless, timeout, urls)
        self.handle = threading.Thread(target=self.obj1.update)
        self.handle.start()

    def update(self):
        while self.handle.is_alive() and not self.obj1.asap:
            sleep(0.1)
        sleep(1.5)
        print("[测速]光速开始第二个测速")
        if not self.stopped:
            h = threading.Thread(target=self.obj2.update)
            h.start()

        try:
            self.handle.join()
        except Exception:
            print("[测速]handle not finish his job")
            pass
        self.res = self.obj1.get()

        if self.stopped:
            return
        self.handle = h
        tmp = self.obj1
        self.obj1 = self.obj2
        self.obj2 = tmp
