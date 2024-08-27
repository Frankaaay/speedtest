from selenium import webdriver
from datetime import timedelta, datetime

class LiveResult:
    Normal = 0
    Stuck = 1
    End = 2
    Error = 3

from io import TextIOWrapper
class Recorder:
    def __init__(self, file: TextIOWrapper):
        self.file = file
    
    def record(self, res: LiveResult, message: str | None):
        raise "Override me🥰"

    def flush(self):
        if self.file is not None:
            self.file.flush()

class Live:
    driver: webdriver.Edge # OR any other browser
    option: webdriver.EdgeOptions # OR any other browser option

    def __init__(self, browser:str, headless:bool, room_id, detect_interval:timedelta):
        browser = browser.title()

        if browser == "Edge":
            option = webdriver.EdgeOptions()
            option.add_argument('--log-level=off')
        elif browser == "Chrome":
            option = webdriver.ChromeOptions()
            option.add_argument('--log-level=off')
        elif browser == "Firefox":
            option = webdriver.FirefoxOptions()
            option.log.level = "fatal"
            
        if headless: option.add_argument('--headless')

        if browser == "Edge":
            self.driver = webdriver.Edge(options=option)
        elif browser == "Chrome":
            self.driver = webdriver.Chrome(options=option)
        elif browser == "Firefox":
            self.driver = webdriver.Firefox(options=option)

        self.interval = detect_interval
        if room_id is None:
            self.find_available_live()
        else:
            self.goto_room(room_id)
        
        self.anti_afk = datetime.now()
        self.recorders:list[Recorder] = []
    
    def goto_room(self, room_id):
        pass

    def find_available_live(self):
        pass

    def check(self) -> tuple[LiveResult, str | None]:
        pass

    def check_and_record(self):
        result, msg = self.check()
        for recorder in self.recorders:
            recorder.record(result, msg)
        return result, msg

    def flush(self):
        for recorder in self.recorders:
            recorder.flush()
    
    def add_recorder(self, recorder:Recorder):
        self.recorders.append(recorder)
    

    def quit(self):
        self.driver.quit()
