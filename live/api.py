from selenium import webdriver


class LiveResult:
    Normal = 0
    Stuck = 1
    End = 2
    Error = 3


class Live:
    driver: webdriver.Edge # OR any other browser

    def __init__(self, browser):
        exec(f"self.driver = webdriver.{browser}()")

    def find_available_live(self):
        raise "Overwrite me🥰"

    def check(self) -> tuple[LiveResult, str | None]:
        raise "Overwrite me🥰"

    def quit(self):
        self.driver.quit()
