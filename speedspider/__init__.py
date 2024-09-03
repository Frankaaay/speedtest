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
        return f"lag:{self.lag} jit:{self.jit} dl:{self.dl} ul:{self.ul}"


URLS = [
    "http://wsus.sjtu.edu.cn/speedtest/",
    # "http://speed.neu.edu.cn/", fuck stupid web always get 502
    "http://test.ustc.edu.cn/",
    "http://test.nju.edu.cn/",
    "http://speed.nuaa.edu.cn/",
]


class SpeedTester(Producer):
    def __init__(self, headless=True, timeout=timedelta(minutes=2), urls=URLS):
        super().__init__()
        self.headless = headless
        self.timeout = timeout.total_seconds()
        self.urls = urls

    def update(self):
        super().update()
        driver = web_driver(self.headless)
        driver.implicitly_wait(5)
        url = random.choice(self.urls)
        driver.get(url)
        startStopBtn = driver.find_element(By.ID, "startStopBtn")
        if startStopBtn.get_attribute("class") == "":
            startStopBtn.click()
        try:
            WebDriverWait(driver, self.timeout).until(
                lambda driver: int(driver.execute_script("return s.getState()")) == 4)
            lag = driver.find_element(By.ID, "pingText").text
            jit = driver.find_element(By.ID, "jitText").text
            dl = driver.find_element(By.ID, "dlText").text
            ul = driver.find_element(By.ID, "ulText").text
        except SEexceptions.NoSuchElementException:
            lag = jit = dl = ul = "nan"
        except SEexceptions.TimeoutException:
            lag = jit = dl = ul = "nan"
        except Exception as e:
            lag = jit = dl = ul = str(e)
        finally:
            driver.quit()

        try:
            self.res = SpeedTestResult(float(lag), float(jit), float(dl), float(ul))
        except ValueError:
            self.res = SpeedTestResult(lag, jit, dl, ul)
            

