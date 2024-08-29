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
        try:
            episode = self.driver.find_elements(
                By.XPATH, '//a[contains(@class, "playlist__panel__selectItem")]')
            url = episode[self.episode].get_attribute('href')[1:]
            self.driver.implicitly_wait(self.interval)
            self.goto_room(url)
        except:
            seasons = self.driver.find_elements(
                By.XPATH, '//a[@class="HorizontalFeedCard__coverWrapper" and not(descendant::div[contains(@class, "component-episodeTag")])]')
            seasons_id = random.choice(seasons).get_attribute('href')[1:]
            self.driver.implicitly_wait(self.interval)
            self.goto_room(seasons_id)

    def afk_check(self) -> bool:
        if time() - self.afk_since > timedelta(hours=5).total_seconds():
            self.refresh()  # refresh page to prevent afk
            self.afk_since = time()
            self.res = (LiveState.End, "anti afk")
            return True
        elif time() - self.afk_since < timedelta(seconds=5).total_seconds():
            self.res = (LiveState.Normal, "anti afk refreshing")
            return True
        return False

    def update(self):
        if self.afk_check():
            return

        try:
            player = self.driver.find_element(By.ID, 'player_default')
            player_classes = player.get_attribute('class')
            # 是否结束
            if 'not-allow-autoplay' in player_classes:
                self.driver.find_element(
                    By.CLASS_NAME, 'xgplayer-start').click()
                self.res = (LiveState.Normal, "autoplay is not allowed")
            elif 'xgplayer-ended' in player_classes:
                self.res = (LiveState.End, None)
                self.find_available()
            elif "xgplayer-isloading" in player_classes:
                self.res = (LiveState.Stuck, None)
            else:
                self.res = (LiveState.Normal, None)

        except SEexceptions.WebDriverException as e:
            self.res = (LiveState.Error, str(e))

        except Exception as e:
            self.res = (LiveState.Error, str(e))
