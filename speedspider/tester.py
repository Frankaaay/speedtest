from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        return f"lag={self.lag}, jit={self.jit}, dl={self.dl}, ul={self.ul}"

urls = [
            "http://wsus.sjtu.edu.cn/speedtest/",
            "http://speed.neu.edu.cn/",
            "http://test.ustc.edu.cn/",
            "http://test.nju.edu.cn/",
            "http://speed.nuaa.edu.cn/"
        ]

class SpeedTester:
    def __init__(self, browser='Edge', headless=True):
        self.driver: webdriver.Edge = None
        self.option: webdriver.EdgeOptions = None

        exec(f"self.option = webdriver.{browser}Options()")
        if headless : self.option.add_argument('--headless')
        exec(f"self.driver = webdriver.{browser}(options=self.option)")

        self.driver.implicitly_wait(5)
    
    def speed_test(self, url=None) -> SpeedTestResult:
        if url is None:
            url = random.choice(urls)
        self.driver.get(url)
        startStopBtn = self.driver.find_element(By.ID,"startStopBtn")
        if startStopBtn.get_attribute("class") == "" : startStopBtn.click()
        WebDriverWait(self.driver, 60).until(
            lambda driver:int(driver.execute_script("return s.getState()")) == 4)

        lag = self.driver.find_element(By.ID,"pingText").text
        jit = self.driver.find_element(By.ID,"jitText").text
        dl = self.driver.find_element(By.ID,"dlText").text
        ul = self.driver.find_element(By.ID,"ulText").text
        return SpeedTestResult(float(lag), float(jit), float(dl), float(ul))
    
    def close(self):
        self.driver.close()