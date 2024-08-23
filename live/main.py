from live_bili import BiliLive
from live_douyin import DouyinLive
from api import LiveResult
import recorder
import sys


def main():

    print("开始记录")
    name = "any"
    browser = "Firefox"
    room_id = None

    try:
        name = sys.argv[1]
        browser = sys.argv[2].title()
        room_id = sys.argv[3]
    except Exception as e:
        pass

    all_browser = ["Edge", "Chrome", "Firefox", "Ie", "Safari",]
    if browser not in all_browser:
        print(f"请使用以下浏览器之一: {all_browser}")
        return

    obj = DouyinLive(browser, room_id)
    console = recorder.Console()
    # logger = recorder.Logger(name)
    report = recorder.Reporter(name, interval=5, threshold=3)
    try:
        while True:
            state = obj.check()
            # logger.record(*state)
            report.merge(*state)
            console.record(*state)
            # logger.flush()
            report.flush()
            if state[0] == LiveResult.End:
                obj.find_available_live()

    except KeyboardInterrupt:
        obj.quit()
    except Exception as e:
        # logger.flush()
        report.flush()
        raise e
    finally:
        # logger.flush()
        report.flush()
        print("结束记录")


if __name__ == "__main__":
    main()
