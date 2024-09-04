from .api import *
import random
from selenium.webdriver.common.by import By
from selenium.common import exceptions as SEexceptions


class DouyinLive(Live):
    def __init__(self, room_id=None, interval=timedelta(seconds=0.1)):
        super().__init__('https://live.douyin.com/', room_id, interval)

    def find_available(self):
        i = random.randint(2, 5)
        super().find_available(lambda driver: driver.find_element(
            By.XPATH, '//*[@id="player_div"]/div[1]/div/div/div//a').get_attribute("href"))
        # Stupid path that is different in Edge and Firefox

    def update(self):
        if self.afk_check():
            return

        try:
            # 直播是否结束
            player = self.driver.find_element(By.XPATH,"//div[(contains(@class,'basicPlayer'))]")
            player_class = player.get_attribute("class")

            if 'xgplayer-nostart' in player_class:
                self.res = (LiveState.End, None)
                self.find_available()
            elif 'xgplayer-is-error' in player_class:
                self.res = (LiveState.Error, None)
                self.find_available()
            elif 'xgplayer-isloading' in player_class:
                self.res = (LiveState.Stuck, None)
            else:
                self.res = (LiveState.Normal, None)
            
            # try:
            #     end_text = self.driver.find_element(
            #         By.XPATH, '//*[@data-anchor-id="living-basic-player"]/div/div/pace-island[1]/div/span').text
            #     if end_text == '直播已结束':
            #         self.res = (LiveState.End, None)
            #         self.find_available()
            # except SEexceptions.NoSuchElementException:
            #     pass

            # # 直播是否卡顿
            # loading = self.driver.find_element(
            #     By.CLASS_NAME, "xgplayer-loading")
            # if loading.is_displayed():
            #     self.res = (LiveState.Stuck, None)
            # else:
            #     self.res = (LiveState.Normal, None)

        except SEexceptions.WebDriverException as e:
            self.res = (LiveState.Error, str(e))
            self.find_available()

        except Exception as e:
            self.res = (LiveState.Error, "未知错误"+repr(e))
            self.find_available()