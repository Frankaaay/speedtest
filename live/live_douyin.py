import live_api
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import re

class DouyinLive(live_api.Live):
    def __init__(self, browser, room_id=None):
        super().__init__(browser)
        self.driver.implicitly_wait(0.2)
        if room_id is None:
            self.find_available_live()
        else:
            self.driver.get(f"https://live.douyin.com/{room_id}")

    def find_available_live(self):

        self.driver.implicitly_wait(5)
        self.driver.get("https://live.douyin.com/")
        url = self.driver.find_element(
            By.XPATH, '/html/body/div[2]/div[2]/div/main/div[3]/div/div/div/div[1]/div[1]/div[2]/div[1]/div/div/div/div[1]/a').get_attribute("href")
        room_id = re.findall(r'live.douyin.com/(\d+)', url)[0]
        self.driver.get(f"https://live.douyin.com/{room_id}")
        self.driver.implicitly_wait(0.2)

    def check(self) -> tuple[live_api.LiveResult, str | None]:
        # self.driver.switch_to.window(self.driver.window_handles[0])
        try:
            # 直播是否结束
            try:
                end_text = self.driver.find_element(
                    By.XPATH, '//*[@id="pip-anchor"]/div/pace-island[1]/div/span').text()
                if end_text == '直播已结束':
                    return (live_api.LiveResult.End, None)
            except exceptions.NoSuchElementException:
                pass

            # 直播是否卡顿
            try:
                self.driver.find_element(By.CLASS_NAME, "xgplayer-loading")
                return (live_api.LiveResult.Stuck, None)
            except exceptions.NoSuchElementException:
                return (live_api.LiveResult.Normal, None)

        except exceptions.WebDriverException as e:
            return (live_api.LiveResult.Error, str(e))
