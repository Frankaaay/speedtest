from selenium import webdriver
from datetime import timedelta, datetime
class LiveResult:
    Normal = 0
    Stuck = 1
    End = 2
    Error = 3


class Live:
    driver: webdriver.Edge # OR any other browser
    option: webdriver.EdgeOptions # OR any other browser option

    def __init__(self, browser:str, headless:bool, room_id, detect_interval:timedelta):
        browser = browser.title()

        if browser == "Edge" or browser == "Chrome":
            exec(f"self.option = webdriver.{browser}Options()")
            self.option.add_argument('--log-level=off')
        elif browser == "Firefox":
            self.option = webdriver.FirefoxOptions()
            self.option.log.level = "off"
            
        if headless: self.option.add_argument('--headless')

        exec(f"self.driver = webdriver.{browser}(options=self.option)")
        self.interval = detect_interval
        if room_id is None:
            self.find_available_live()
        else:
            self.goto_room(room_id)
        
        self.anti_afk = self.last_ok = datetime.now()
    
    def goto_room(self, room_id):
        raise "Override me🥰"

    def find_available_live(self):
        raise "Override me🥰"

    def check(self) -> tuple[LiveResult, str | None]:
        raise "Override me🥰"

    def quit(self):
        self.driver.quit()
