from .api import Live, LiveState, timedelta, LONG_WAIT
import random
from selenium.webdriver.common.by import By
from selenium.common import exceptions as SEexceptions


class BiliLive(Live):
    def __init__(
        self, browser_name, room_id=None, interval=timedelta(seconds=0.1), proxy=None
    ):
        # if room_id is None:
        #     room_id = "31539256"
        super().__init__(
            browser_name,
            "https://live.bilibili.com/",
            room_id=room_id,
            interval=interval,
            proxy=proxy,
        )

    def find_available(self):
        i = random.randint(2, 5)
        super().find_available(
            lambda driver: driver.find_element(
                By.XPATH,
                f"/html/body/div[1]/div/div[5]/div[3]/div/div[2]/div[1]/div[1]/a[{i}]",
            ).get_attribute("href")
        )

    def update(self):
        super().update()
        if self.afk_check():
            return

        try:
            try:
                self.driver.implicitly_wait(LONG_WAIT.total_seconds())
                self.driver.find_element(By.XPATH, '//*[@id="live-player"]/video')
            except SEexceptions.WebDriverException:
                self.res = (LiveState.Error, "这似乎不是一个直播间")
                self.find_available()
            finally:
                self.driver.implicitly_wait(self.interval)

            # 直播是否结束
            try:
                self.driver.find_element(By.CLASS_NAME, "web-player-ending-panel")
                self.res = (LiveState.End, None)
                self.find_available()
            except SEexceptions.NoSuchElementException:
                pass

            # 直播是否断开

            # 直播是否卡顿
            try:
                self.driver.find_element(By.CLASS_NAME, "web-player-loading")
                self.res = (LiveState.Stuck, None)
            except SEexceptions.NoSuchElementException:
                self.res = (LiveState.Normal, None)

        except SEexceptions.WebDriverException as e:
            self.res = (LiveState.Error, str(e))
            self.find_available()

        except Exception:
            self.res = (LiveState.Error, "未知错误")
            self.find_available()
