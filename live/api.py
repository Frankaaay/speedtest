from typing import Callable
from common import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import exceptions as SEexceptions
import utils
import re


class LiveState:
    '''
    注意在一些情况下End的等级可能高于Error，
    Error表示可能恢复的错误，
    而End表示不可恢复的错误。
    '''
    Normal = 0,
    Stuck = 1,
    End = 2,
    Error = 3,


class Live(Producer):
    def __init__(self, base_url, room_id=None, interval=timedelta(seconds=0.1)):
        print('[直播]启动！',base_url)
        super().__init__()
        self.base_url = base_url
        self.driver = utils.web_driver(proxy_enable=True)
        self.res: tuple[LiveState, str | None] = (LiveState.Error, "initializing")
        self.interval = interval.total_seconds()
        self.room_id = room_id
        if room_id is None:
            self.find_available()
        else:
            self.goto_room(room_id)

        self.stuck_since = None
        self.afk_since = time()
        self.set_default((LiveState.Error, "Not update for too long"))

        self.error_this_room_since_afk = 0

    def find_available(self, get_url: Callable[[webdriver.Edge], str]):
        print('[直播]寻找可用房间')
        try:
            self.driver.switch_to.window(self.driver.window_handles[0])
        except:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = utils.web_driver()
            self.driver.get(self.base_url)

        room_id = re.findall(self.base_url + r'(\d+)', self.driver.current_url)
        if len(room_id) > 0:
            room_id = room_id[0]
            if room_id != self.room_id:
                print(f'[直播]检测到更换直播间 {room_id}')
                self.error_this_room_since_afk = 0
                self.goto_room(room_id)
                return

        if self.room_id is not None and\
        self.error_this_room_since_afk < 3 and\
        self.get()[0] != LiveState.End:

            print(f'[直播]继续使用之前的直播间 {self.room_id}')
            self.error_this_room_since_afk += 1
            self.goto_room(self.room_id)
            return
        
        print('[直播]寻找新的直播间')
        self.error_this_room_since_afk = 0

        self.driver.implicitly_wait(8)
        self.driver.get(self.base_url)
        url: str = get_url(self.driver)
        room_id = re.findall(self.base_url + r'(\d+)', url)[0]
        self.driver.implicitly_wait(self.interval)
        self.goto_room(room_id)

    def goto_room(self, room_id: str):
        print("[直播]来到房间", room_id)
        self.room_id = room_id
        self.afk_since = time()
        self.driver.get(self.base_url + room_id)

    def refresh(self):
        print("[直播]刷新中")
        self.afk_since = time()
        self.driver.refresh()

    def update(self):
        super().update()
        if self.res[0] != LiveState.Normal and self.stuck_since is None:
            self.stuck_since = time()


    def afk_check(self) -> bool:
        if self.stuck_since is not None and time() - self.stuck_since > 120:
            self.refresh()  # refresh page to prevent afk
            self.afk_since = time()
            self.stuck_since = None
            self.res = (LiveState.Error, "stuck for too long")
            print("[直播]卡顿时间过长，刷新页面")
            return True
        if time() - self.afk_since > timedelta(minutes=20).total_seconds():
            self.refresh()  # refresh page to prevent afk
            self.afk_since = time()
            self.res = (LiveState.Normal, "anti afk")
            print("[直播]防止挂机检测，刷新页面")
            return True
        elif time() - self.afk_since < timedelta(seconds=10).total_seconds():
            self.res = (LiveState.Normal, "anti afk refreshing")
            return True
        return False

    def stop(self):
        self.res = (LiveState.End, "stopped")
        super().stop()
        self.driver.quit()
