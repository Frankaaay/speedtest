import api
from datetime import timedelta
from selenium.webdriver.common.by import By
from selenium.common import exceptions


class BiliLive(api.Live):
    def __init__(self, browser:str, headless:bool=False, room_id=None, detect_interval=timedelta(milliseconds=200)):
        super().__init__(browser, headless, room_id, detect_interval)
        
    def goto_room(self, room_id):
        self.driver.get(f"https://live.bilibili.com/{room_id}")

    def find_available_live(self):

        self.driver.implicitly_wait(5)
        self.driver.get("https://live.bilibili.com/")
        self.driver.find_element(
            By.XPATH, '/html/body/div[1]/div/div[5]/div[3]/div/div[2]/div[1]/div[1]/a[1]').click()
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.close()
        self.driver.implicitly_wait(self.interval)

    def check(self) -> tuple[api.LiveResult, str | None]:
        self.driver.switch_to.window(self.driver.window_handles[0])
        try:

            # 直播是否结束
            try:
                self.driver.find_element(
                    By.CLASS_NAME, "web-player-ending-panel")
                self.find_available_live()
                return (api.LiveResult.End, None)
            except exceptions.NoSuchElementException:
                pass

            # 直播是否卡顿
            try:
                self.driver.find_element(By.CLASS_NAME, "web-player-loading")
                return (api.LiveResult.Stuck, None)
            except exceptions.NoSuchElementException:
                return (api.LiveResult.Normal, None)

        except exceptions.WebDriverException as e:
            return (api.LiveResult.Error, str(e))
