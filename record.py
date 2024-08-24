import live
import stable
import speedspider
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

def main():
    now = datetime.datetime.now().strftime("%m-%d_%H-%M")
    os.makedirs(f"log/{now}/",exist_ok=True)

    pings = Log(open(f"log/{now}/ping.csv",'w',encoding='utf-8-sig'))
    lives = live.Reporter(open(f"log/{now}/stuck.csv",'w',encoding='utf-8-sig'))

    living = live.BiliLive('Firefox',False)

    try: 
        while True:
            now = datetime.datetime.now()
            pings.record(now.strftime("%m-%d %H:%M:%S"),stable.ping('192.168.0.1'),stable.ping('www.baidu.com'))
            lives.record(*living.check())
            time.sleep(1 - (now.microsecond/1000000))
    except KeyboardInterrupt:
        pass
    finally:
        print("Exiting...")
        living.quit()
        lives.flush()
        pings.flush()
        
    

if __name__ == '__main__':
    main()