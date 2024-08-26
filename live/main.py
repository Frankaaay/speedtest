from live_bili import BiliLive
from live_douyin import DouyinLive
from api import LiveResult
import datetime
import os
import recorder
import sys


def main():

    print("开始记录")
    browser = "Firefox"
    room_id = None

    all_browser = ["Edge", "Chrome", "Firefox", "Ie", "Safari",]
    if browser not in all_browser:
        print(f"请使用以下浏览器之一: {all_browser}")
        return

    obj = BiliLive(browser,headless=False, room_id=room_id)
    
    time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(f"reports/", exist_ok=True)
    report_file = open(f"reports/{time_str}.csv", "a", encoding="utf-8-sig")
    
    console = recorder.Console()
    report = recorder.Reporter(report_file, interval=5, threshold=3)
    try:
        while True:
            state = obj.check()
            report.record(*state)
            console.record(*state)
            report.flush()

            if state[0] == LiveResult.Error:
                break

    except KeyboardInterrupt:
        pass
    except Exception as e:
        raise e
    finally:
        obj.quit()
        console.flush()
        report.flush()
        print("结束记录")


if __name__ == "__main__":
    main()
