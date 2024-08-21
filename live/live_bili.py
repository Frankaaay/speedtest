import live
from selenium.webdriver.common.by import By
from selenium.common import exceptions


class BiliLive(live.Live):
    def __init__(self, browser, room_id):
        super().__init__(browser)
        self.driver.implicitly_wait(0.2)
        self.driver.get(f"https://live.bilibili.com/{room_id}")

    def find_avaliable_live()->int:
        pass

    def check(self) -> tuple[live.LiveResult, str|None]:
        self.driver.switch_to.window(self.driver.window_handles[0])
        # 捕获未知错误
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
                return (live.LiveResult.End,None)
            except exceptions.NoSuchElementException:
                pass

            # 直播是否卡顿
            try:
                self.driver.find_element(By.CLASS_NAME, "web-player-loading")
                return (live.LiveResult.Stuck,None)
            except exceptions.NoSuchElementException:
                return (live.LiveResult.Normal,None)

        except exceptions.WebDriverException as e:
            return (live.LiveResult.Error,str(e))
