import sys
import live
import stable
import webpanel
import speedspider
import threading
import webpanel
import datetime
import time
import os

class Log:
    def __init__(self,file):
        self.f = file
        self.f.write(f"time,ping192,pingwww,rsrp,sinr,band\n")

    def record(self, time,pin192,pingwww,device:webpanel.WebPanelResult):
        self.f.write(f"{time},{pin192},{pingwww},{device.rsrp},{device.sinr},{device.band}\n")

    def flush(self):
        self.f.flush()

ip_192 = webpanel.which_is_fm_ip()
ip_www = "www.baidu.com"

def main():

    device = None
    if input("记录设备状态 [Y/n] 默认启用:").lower() != 'n':
        device = webpanel.Sequence(webpanel.WebPanel_FM(),interval=datetime.timedelta(seconds=3))
        device.start()
    
    browser = "Edge".title()
    platform = input("平台 [b]站/[d]抖音/[x]西瓜/[a]爱奇艺:").lower()
    room_id = input("房间号 (可不填):").strip()

    if len(room_id) == 0:
        room_id = None

    if platform == 'b':
        living = live.BiliLive(browser, False, room_id)
    elif platform == 'd':
        living = live.DouyinLive(browser, False, room_id)
    else:
        living = live.BiliLive(browser, False, room_id)

    now = datetime.datetime.now().strftime("%m-%d_%H-%M")
    os.makedirs(f"log/{now}/",exist_ok=True)
    ping_log = Log(open(f"log/{now}/ping.csv",'w',encoding='utf-8-sig'))

    living.add_recorder(live.Reporter(open(f"log/{now}/stuck.csv",'w',encoding='utf-8-sig'),threshold=3))
    living.add_recorder(live.Console())
    
    def record_live():
        try: 
            while True:
                now = datetime.datetime.now()

                res,msg = living.check_and_record()

                if now.second == 0 or res!=live.LiveResult.Normal:
                    living.flush()
        except KeyboardInterrupt:
            pass
        finally:
            print("Exiting(2/2)")
            living.flush()
            time.sleep(3)
            sys.exit()


    live_thread = threading.Thread(target=record_live)
    live_thread.start()
    try: 
        while True:
            now = datetime.datetime.now()
            time.sleep(1 - (now.microsecond/1000000))
            device_info = device.res if device is not None else webpanel.WebPanelResult('-','-','-')
            ping_log.record(now.strftime("%m-%d %H:%M:%S"),stable.ping(ip_192),stable.ping(ip_www),device_info)
            print(device_info)
            if now.second == 0:
                ping_log.flush()
    except KeyboardInterrupt:
        pass
    finally:
        print("Exiting(1/2)")
        ping_log.flush()
        if device is not None: device.stop()
        live_thread.join()

        
    

if __name__ == '__main__':
    main()