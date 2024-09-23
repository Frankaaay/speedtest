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
    Afk = 4,


class Live(Producer):
    # 初始化函数，设置直播的基本参数
    def __init__(self, browser_name, base_url, room_id=None, interval=timedelta(seconds=0.1), disable_pic=True, proxy=None):
        # 打印启动信息
        print('[直播]启动！',base_url)
        # 调用父类的初始化函数
        super().__init__()
        self.create_web_driver = lambda :utils.web_driver(browser_name, headless=False, proxy=proxy, disable_pic=disable_pic)
        # 设置直播的基本参数
        self.base_url = base_url
        self.driver_browser_name = browser_name
        self.driver_disable_pic = disable_pic
        # 创建浏览器驱动
        self.driver = self.create_web_driver()
        # 设置直播状态和错误信息
        self.res: tuple[LiveState, str | None] = (LiveState.Error, "initializing")
        # 设置直播的时间间隔
        self.interval = interval.total_seconds()
        # 设置直播的房间ID
        self.room_id = room_id
        # 如果房间ID为空，则查找可用的房间
        if room_id is None:
            self.find_available()
        # 否则，跳转到指定的房间
        else:
            self.goto_room(room_id)

        # 设置直播的卡住时间
        self.stuck_since = None
        # 设置直播的离开时间
        self.afk_since = time()
        # 设置默认的直播状态和错误信息
        self.set_default((LiveState.Error, "Not update for too long"))

        # 设置当前房间离开时间内的错误次数
        self.error_this_room_since_afk = 0

    def find_available(self, get_url: Callable[[webdriver.Edge], str]):
        print('[直播]寻找可用房间')
        try:
            # 切换到第一个窗口
            self.driver.switch_to.window(self.driver.window_handles[0])
        except:
            try:
                # 如果切换窗口失败，则关闭浏览器
                self.driver.quit()
            except:
                pass
            # 重新打开浏览器
            self.driver = self.create_web_driver()
            self.driver.get(self.base_url)

        # 获取当前页面的房间ID
        room_id = re.findall(self.base_url + r'(\d+)', self.driver.current_url)
        if len(room_id) > 0:
            room_id = room_id[0]
            # 如果房间ID发生变化，则切换到新的直播间
            if room_id != self.room_id:
                print(f'[直播]检测到更换直播间 {room_id}')
                self.error_this_room_since_afk = 0
                self.goto_room(room_id)
                return

        # 如果房间ID不为空，且错误次数小于等于1，且直播状态不为结束，则继续使用之前的直播间
        if self.room_id is not None and\
        self.error_this_room_since_afk <= 1 and\
        self.get()[0] != LiveState.End:

            print(f'[直播]继续使用之前的直播间 {self.room_id}')
            self.error_this_room_since_afk += 1
            self.goto_room(self.room_id)
            return
        
        # 如果房间ID为空，或者错误次数大于1，或者直播状态为结束，则寻找新的直播间
        print('[直播]寻找新的直播间')
        self.error_this_room_since_afk = 0

        # 设置隐式等待时间为8秒
        self.driver.implicitly_wait(8)
        self.driver.get(self.base_url)
        # 获取新的直播间URL
        url: str = get_url(self.driver)
        # 获取新的直播间ID
        room_id = re.findall(self.base_url + r'(\d+)', url)[0]
        # 设置隐式等待时间为原来的间隔时间
        self.driver.implicitly_wait(self.interval)
        # 切换到新的直播间
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
        if self.res[0] == LiveState.Stuck and self.stuck_since is None:
            self.stuck_since = time()
        elif self.res[0] == LiveState.Normal or self.res[0] == LiveState.Afk:
            self.stuck_since = None


    def afk_check(self) -> bool:
        # 检查是否卡顿超过120秒
        if self.stuck_since is not None and time() - self.stuck_since > 120:
            self.refresh()  # refresh page to prevent afk
            self.refresh()  # 刷新页面以防止挂机
            self.afk_since = time()
            self.stuck_since = None
            self.res = (LiveState.Error, "stuck for too long")
            print("[直播]卡顿时间过长，刷新页面")
            return True
        # 检查是否挂机超过15分钟
        if time() - self.afk_since > timedelta(minutes=15).total_seconds():
            self.refresh()  # refresh page to prevent afk
            self.refresh()  # 刷新页面以防止挂机
            self.afk_since = time()
            self.res = (LiveState.Afk, "anti afk")
            print("[直播]防止挂机检测，刷新页面")
            return True
        # 检查是否在刷新页面
        elif time() - self.afk_since < timedelta(seconds=8).total_seconds():
            self.res = (LiveState.Afk, "anti afk refreshing")
            return True
        return False

    def stop(self):
        self.res = (LiveState.End, "stopped")
        super().stop()
        self.driver.quit()
