from .api import *
import random
from selenium.webdriver.common.by import By
from selenium.common import exceptions as SEexceptions

class BiliLive(Live):
    def __init__(self, browser_name: str = 'Edge', room_id = None, interval = timedelta(seconds=0.1)):
        super().__init__(browser_name,'https://live.bilibili.com/', room_id, interval)

    def find_available_live(self):
        i = random.randint(2, 5)
        super().find_available_live(lambda driver : driver.find_element(
            By.XPATH, f'/html/body/div[1]/div/div[5]/div[3]/div/div[2]/div[1]/div[1]/a[{i}]').get_attribute('href'))
    
    def update(self):
        if self.afk_check():
            return 
        
        try:
            # 直播是否结束
            try:
                self.driver.find_element(
                    By.CLASS_NAME, "web-player-ending-panel")
                self.find_available_live()
                self.res = (LiveState.End, None)
            except SEexceptions.NoSuchElementException:
                pass

            # 直播是否卡顿
            try:
                self.driver.find_element(By.CLASS_NAME, "web-player-loading")
                self.res = (LiveState.Stuck, None)
            except SEexceptions.NoSuchElementException:
                self.res = (LiveState.Normal, None)

        except SEexceptions.WebDriverException as e:
            self.res = (LiveState.Error, str(e))

        except Exception as e:
            self.res = (LiveState.Error, str(e))