import live_api
from selenium.webdriver.common.by import By
from selenium.common import exceptions


class BiliLive(live_api.Live):
    def __init__(self, browser, room_id=None):
        super().__init__(browser)
        self.driver.implicitly_wait(0.2)
        if room_id is None:
            self.find_available_live()
        else:
            self.driver.get(f"https://live.bilibili.com/{room_id}")

    def find_available_live(self):

        self.driver.implicitly_wait(5)
        self.driver.get("https://live.bilibili.com/")
        self.driver.find_element(
            By.XPATH, '/html/body/div[1]/div/div[5]/div[3]/div/div[2]/div[1]/div[1]/a[1]').click()
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.close()
        self.driver.implicitly_wait(0.2)

    def check(self) -> tuple[live_api.LiveResult, str | None]:
        self.driver.switch_to.window(self.driver.window_handles[0])
        try:

            # 网页正确打开
            # try:
            #     self.driver.find_element(By.CLASS_NAME, "live-logo")
            # except:
            #     return live.LiveResult.Error

            # 直播是否结束
            try:
                self.driver.find_element(
                    By.CLASS_NAME, "web-player-ending-panel")
                return (live_api.LiveResult.End, None)
            except exceptions.NoSuchElementException:
                pass

            # 直播是否卡顿
            try:
                self.driver.find_element(By.CLASS_NAME, "web-player-loading")
                return (live_api.LiveResult.Stuck, None)
            except exceptions.NoSuchElementException:
                return (live_api.LiveResult.Normal, None)

        except exceptions.WebDriverException as e:
            return (live_api.LiveResult.Error, str(e))
