from selenium import webdriver
from datetime import timedelta
class LiveResult:
    Normal = 0
    Stuck = 1
    End = 2
    Error = 3


class Live:
    driver: webdriver.Edge # OR any other browser
    option: webdriver.EdgeOptions # OR any other browser option

    def __init__(self, browser:str, headless:bool, room_id, detect_interval:timedelta):
        exec(f"self.option = webdriver.{browser}Options()")
        if headless: self.option.add_argument('--headless')
        exec(f"self.driver = webdriver.{browser}(options=self.option)")
        self.interval = detect_interval.total_seconds()
        if room_id is None:
            self.find_available_live()
        else:
            self.goto_room(room_id)
    
    def goto_room(self, room_id):
        raise "Overwrite me🥰"

    def find_available_live(self):
        raise "Overwrite me🥰"

    def check(self) -> tuple[LiveResult, str | None]:
        raise "Overwrite me🥰"

    def quit(self):
        self.driver.quit()
