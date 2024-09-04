from typing import Callable
from common import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import exceptions as SEexceptions
import utils
import re


class LiveState:
    Normal = 0,
    Stuck = 1,
    End = 2,
    Error = 3,


class Live(Producer):
    def __init__(self, base_url, room_id=None, interval=timedelta(seconds=0.1)):
        super().__init__()
        self.base_url = base_url
        self.driver = utils.web_driver()
        self.res: tuple[LiveState, str | None] = (
            LiveState.Error, "initializing")
        self.interval = interval.total_seconds()
        if room_id is None:
            self.find_available()
        else:
            self.goto_room(room_id)

        self.afk_since = time()
        self.set_default((LiveState.Error, "Not update for too long"))
        self.set_ttl(timedelta(minutes=1))

    def find_available(self, get_url: Callable[[webdriver.Edge], str]):
        print('finding available...')
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.implicitly_wait(5)
        self.driver.get(self.base_url)
        url: str = get_url(self.driver)
        room_id = re.findall(self.base_url + r'(\d+)', url)[0]
        self.driver.implicitly_wait(self.interval)
        self.goto_room(room_id)

    def goto_room(self, room_id: str):
        print("goto room", room_id)
        self.afk_since = time()
        self.driver.get(self.base_url + room_id)

    def refresh(self):
        print("refreshing...")
        self.afk_since = time()
        self.driver.refresh()

    def update(self):
        super().update()

    def afk_check(self) -> bool:
        if time() - self.afk_since > timedelta(minutes=20).total_seconds():
            self.refresh()  # refresh page to prevent afk
            self.afk_since = time()
            self.res = (LiveState.End, "anti afk")
            return True
        elif time() - self.afk_since < timedelta(seconds=15).total_seconds():
            self.res = (LiveState.Normal, "anti afk refreshing")
            return True
        return False

    def stop(self):
        self.res = (LiveState.End, "stopped")
        super().stop()
        self.driver.quit()
