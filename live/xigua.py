from .api import *
import random
from selenium.webdriver.common.by import By
from selenium.common import exceptions as SEexceptions


class Xigua(Live):
    def __init__(self,  season_id=None, interval=timedelta(seconds=0.1)):
        if season_id is None:
            season_id = '6562025890606219790'

        super().__init__('https://www.ixigua.com/', season_id, interval)

    def find_available(self):
        self.episode += 1
        self.driver.implicitly_wait(5)

        episodes = self.driver.find_elements(
            By.CLASS_NAME, 'playlist__panel__selectItem')
        episode_id = episodes[self.episode %
                              len(episodes)].get_attribute('href')
        get_attribute('href')

        room_id = re.findall(self.base_url + r'(\d+)', url)[0]
        self.driver.implicitly_wait(self.interval)
        self.goto_room(room_id)

    def update(self):
        if self.afk_check():
            return

        try:
            # 直播是否结束
            try:
                self.driver.find_element(
                    By.CLASS_NAME, "web-player-ending-panel")
                self.find_available()
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
