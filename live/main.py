from live_bili import BiliLive
import recorder
import sys

def main():
    if len(sys.argv) != 4:
        print("请提供三个参数: 备注名称, 浏览器, 房间号")
        return
    print("开始记录")
    name = sys.argv[1]
    browser = sys.argv[2].title()
    room_id = sys.argv[3]
    
    all_browser = ["Edge", "Chrome", "Firefox", "Ie", "Safari",]
    if browser not in all_browser:
        print(f"请使用以下浏览器之一: {all_browser}")
        return

    live = BiliLive(browser, room_id)
    logger = recorder.Logger(name)
    report = recorder.Reporter(name)
    try:
        while True:
            state = live.check()
            logger.record(state)
            report.record(state)
            logger.flush()
            report.flush()
    except KeyboardInterrupt:
        live.quit()
    except Exception as e:
        raise e
    finally:
        logger.flush()
        report.flush()
        print("结束记录")

if __name__ == "__main__":
    main()