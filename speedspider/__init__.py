from common import *
from utils import web_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import exceptions as SEexceptions
import random


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
        return f"lag={self.lag} jit={self.jit} dl={self.dl} ul={self.ul}"


URLS = [
    "http://wsus.sjtu.edu.cn/speedtest/",
    "http://speed.neu.edu.cn/",
    "http://test.ustc.edu.cn/",
    "http://test.nju.edu.cn/",
    "http://speed.nuaa.edu.cn/",
]


class SpeedTester(Producer):
    def __init__(self, headless=True, timeout=timedelta(minutes=2), urls=URLS):
        super().__init__()
        self.driver = web_driver(headless)
        self.driver.implicitly_wait(5)
        self.timeout = timeout.total_seconds()
        self.urls = urls

    def update(self):
        super().update()
        url = random.choice(self.urls)
        self.driver.get(url)
        startStopBtn = self.driver.find_element(By.ID, "startStopBtn")
        if startStopBtn.get_attribute("class") == "":
            startStopBtn.click()
        try:
            WebDriverWait(self.driver, self.timeout).until(
                lambda driver: int(driver.execute_script("return s.getState()")) == 4)
            lag = self.driver.find_element(By.ID, "pingText").text
            jit = self.driver.find_element(By.ID, "jitText").text
            dl = self.driver.find_element(By.ID, "dlText").text
            ul = self.driver.find_element(By.ID, "ulText").text
        except SEexceptions.NoSuchElementException:
            lag = jit = dl = ul = "nan"
        except SEexceptions.TimeoutException:
            lag = jit = dl = ul = "nan"
        except Exception as e:
            lag = jit = dl = ul = str(e)

        try:
            self.res = SpeedTestResult(float(lag), float(jit), float(dl), float(ul))
        except ValueError:
            self.res = SpeedTestResult(lag, jit, dl, ul)
            

