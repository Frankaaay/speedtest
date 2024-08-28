from .api import *
import random
from selenium.webdriver.common.by import By
from selenium.common import exceptions as SEexceptions


class DouyinLive(Live):
    def __init__(self, browser_name: str = 'Edge', room_id=None, interval=timedelta(seconds=0.1)):
        super().__init__(browser_name, 'https://live.douyin.com/', room_id, interval)

    def find_available_live(self):
        i = random.randint(2, 5)
        super().find_available_live(lambda driver: driver.find_element(
            By.XPATH, '/html/body/div[2]/div[2]/div/main/div[3]/div/div/div/div[1]/div[1]/div[2]/div[1]/div/div/div/div[1]/a').get_attribute("href"))

    def update(self):
        if self.afk_check():
            return

        try:
            # 直播是否结束
            try:
                end_text = self.driver.find_element(
                    By.XPATH, '//*[@id="pip-anchor"]/div/pace-island[1]/div/span').text()
                if end_text == '直播已结束':
                    self.find_available_live()
                    self.res = (LiveState.End, None)
            except SEexceptions.NoSuchElementException:
                pass

            # 直播是否卡顿
            loading = self.driver.find_element(
                By.CLASS_NAME, "xgplayer-loading")
            if loading.is_displayed():
                self.res = (LiveState.Stuck, None)
            else:
                self.res = (LiveState.Normal, None)

        except SEexceptions.WebDriverException as e:
            self.res = (LiveState.Error, str(e))
