from . import api
from datetime import timedelta, datetime
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import threading
import random 
import time
import re
class BiliLive(api.Live):
    def __init__(self, browser:str, headless:bool=False, room_id=None, detect_interval=timedelta(milliseconds=100)):
        super().__init__(browser, headless, room_id, detect_interval)
        
    def goto_room(self, room_id):
        self.driver.get(f"https://live.bilibili.com/{room_id}")
        self.anti_afk = datetime.now()

    def find_available_live(self):
        self.driver.implicitly_wait(5)
        self.driver.get("https://live.bilibili.com/")
        i = random.randint(2,5)
        url = self.driver.find_element(
            By.XPATH, f'/html/body/div[1]/div/div[5]/div[3]/div/div[2]/div[1]/div[1]/a[{i}]').get_attribute('href')
        room_id = re.findall(r'live.bilibili.com/(\d+)', url)[0]
        self.goto_room(room_id)
        self.driver.implicitly_wait(self.interval.total_seconds())

    def check(self) -> tuple[api.LiveResult, str | None]:
        # self.driver.switch_to.window(self.driver.window_handles[0])

        now = datetime.now()
        if now - self.anti_afk > timedelta(minutes=20):
            self.anti_afk = now
            threading.Thread(target=self.driver.refresh).start()
            return (api.LiveResult.End, "anti afk")
        
        if now - self.anti_afk < timedelta(seconds=5):
            time.sleep(self.interval.total_seconds())
            return (api.LiveResult.Normal, None)
        
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
