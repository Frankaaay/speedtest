import live
import stable
import speedspider
import webpanel
import datetime
import time
import os

class Log:
    def __init__(self,file):
        self.f = file
        self.f.write(f"time,ping192,pingwww\n")

    def record(self, time,pin192,pingwww):
        self.f.write(f"{time},{pin192},{pingwww}\n")

    def flush(self):
        self.f.flush()

ip_192 = webpanel.which_is_fm_ip()
ip_www = "www.baidu.com"

def main():
    now = datetime.datetime.now().strftime("%m-%d_%H-%M")
    os.makedirs(f"log/{now}/",exist_ok=True)

    ping_log = Log(open(f"log/{now}/ping.csv",'w',encoding='utf-8-sig'))
    live_console = live.Console()
    live_log = live.Reporter(open(f"log/{now}/stuck.csv",'w',encoding='utf-8-sig'),threshold=3)

    browser = "Edge".title()
    platform = input("平台？ [b]站/[d]抖音/[x]西瓜/[a]爱奇艺").lower()
    room_id = input("房间号：？ (可不填)").strip()

    if len(room_id) == 0:
        room_id = None

    if platform == 'b':
        living = live.BiliLive(browser, False, room_id)
    elif platform == 'd':
        living = live.DouyinLive(browser, False, room_id)
    else:
        living = live.BiliLive(browser, False, room_id)
    

    try: 
        while True:
            now = datetime.datetime.now()
            res,msg = living.check()
            ping_log.record(now.strftime("%m-%d %H:%M:%S"),stable.ping(ip_192),stable.ping(ip_www))
            live_console.record(res,msg)
            live_log.record(res,msg)

            time.sleep(1 - (now.microsecond/1000000))

            if now.second == 0 or res!=live.api.LiveResult.Normal:
                live_log.flush()
                ping_log.flush()
    except KeyboardInterrupt:
        pass
    finally:
        print("Exiting...")
        live_log.flush()
        ping_log.flush()
        living.quit()
        
    

if __name__ == '__main__':
    main()