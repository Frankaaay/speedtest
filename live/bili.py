from .api import *
import random
from selenium.webdriver.common.by import By
from selenium.common import exceptions as SEexceptions


class BiliLive(Live):
    def __init__(self, room_id=None, interval=timedelta(seconds=0.1)):
        if room_id is None:
            room_id = '31539256'
        super().__init__('https://live.bilibili.com/', room_id, interval)

    def find_available(self):
        i = random.randint(2, 5)
        super().find_available(lambda driver: driver.find_element(
            By.XPATH, f'/html/body/div[1]/div/div[5]/div[3]/div/div[2]/div[1]/div[1]/a[{i}]').get_attribute('href'))

    def update(self):
        super().update()
        if self.afk_check():
            return

        try:
            # 直播是否结束
            try:
                self.driver.find_element(
                    By.CLASS_NAME, "web-player-ending-panel")
                self.res = (LiveState.End, None)
                self.find_available()
            except SEexceptions.NoSuchElementException:
                pass

            # 直播是否断开
            self.driver.find_element(
                By.XPATH, '//*[@id="live-player"]/video')

            # 直播是否卡顿
            try:
                self.driver.find_element(By.CLASS_NAME, "web-player-loading")
                self.res = (LiveState.Stuck, None)
            except SEexceptions.NoSuchElementException:
                self.res = (LiveState.Normal, None)

        except SEexceptions.WebDriverException as e:
            self.res = (LiveState.Error, str(e))
            self.find_available()
        
        except Exception as e:
            self.res = (LiveState.Error, "未知错误"+repr(e))
            self.find_available()
