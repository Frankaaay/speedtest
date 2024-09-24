from .api import LiveState, Live, timedelta
import utils


class EmptyLive(Live):
    def __init__(
        self, browser_name, room_id=None, interval=timedelta(seconds=0.1), proxy=None
    ):
        super().__init__(
            browser_name,
            "http://localhost",
            room_id=room_id,
            interval=interval,
            disable_pic=False,
            proxy=proxy,
        )
        self.res = None
        self.set_default((LiveState.Normal, "OFF"))

    def find_available(self):
        # 如果当前没有打开任何窗口
        try:
            if not self.driver.current_window_handle:
                self.driver.quit()
                self.driver = utils.web_driver(
                    proxy_enable=True, disable_pic=self.driver_disable_pic
                )
        except Exception:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = utils.web_driver(
                proxy_enable=True, disable_pic=self.driver_disable_pic
            )
        pass

    def update(self):
        super().update()
        pass
