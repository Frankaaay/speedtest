from common import *
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
        return f"lag:{self.lag} jit:{self.jit} dl:{self.dl} ul:{self.ul}"


URLS = [
    "http://wsus.sjtu.edu.cn/speedtest/",
    # "http://speed.neu.edu.cn/", fuck stupid web always get 502
    "http://test.ustc.edu.cn/",
    "http://test.nju.edu.cn/",
    "http://speed.nuaa.edu.cn/",
]

class SpeedTester(Producer):
    def __init__(self, headless=True, timeout=timedelta(minutes=1), urls=URLS):
        super().__init__()
        self.headless = headless
        self.timeout = timeout.total_seconds()
        self.urls = urls
        self.afap = False

    def update(self):
        super().update()
        url = random.choice(self.urls)
        driver = web_driver(headless=self.headless,proxy_enable=False)
        driver.implicitly_wait(5)
        driver.get(url)
        
        try:
            # 
            startStopBtn = driver.find_element(By.ID, "startStopBtn")
            if startStopBtn.get_attribute("class") == "":
                startStopBtn.click()
            sleep(2)

            def afap(driver):
                try:
                    return int(driver.execute_script("return s.getState()")) == 4 or\
                           float(driver.find_element(By.ID, "ulText").text) > 0
                except ValueError: 
                    return False
                
            WebDriverWait(driver, self.timeout).until(afap)
            self.afap = True
            print("afap is set!!!")
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
            lag = repr(e)
            jit = dl = ul = "nan"
        finally:
            threading.Thread(target=driver.quit).start()

        try:
            lag = float(lag)
            jit = float(jit)
            dl = float(dl)
            ul = float(ul)
            if lag == 0 and jit == 0 and dl == 0 and ul == 0:
                lag = jit = dl = ul = float("nan")
            self.res = SpeedTestResult(float(lag), float(jit), float(dl), float(ul))
        except ValueError:
            self.res = SpeedTestResult(lag, jit, dl, ul)
        self.afap = False
    
class SpeedTester0Interval(Producer):
    '''
    在第一个测速'上传'开始后开始第二个测速
    '''
    def __init__(self, headless=True, timeout=timedelta(minutes=2), urls=URLS):
        super().__init__()
        self.headless = headless
        self.timeout = timeout.total_seconds()
        self.urls = urls
        self.jobs = []
        self.obj1 = SpeedTester(headless, timeout, urls)
        self.obj2 = SpeedTester(headless, timeout, urls)
        self.handle = threading.Thread(target=self.obj1.update)
        self.handle.start()

    def update(self):

        while not self.obj1.afap:
            sleep(0.1)
        sleep(2)
        h = threading.Thread(target=self.obj2.update)
        h.start()

        self.handle.join()
        self.res = self.obj1.get()

        self.handle = h
        tmp = self.obj1
        self.obj1 = self.obj2
        self.obj2 = tmp

