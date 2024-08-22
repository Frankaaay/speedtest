import ping
import datetime
import time
targets = [
    '192.168.0.1',
    'www.baidu.com',
    'www.bing.cn',
    'www.bilibili.com',
    'www.douyin.com',
    'ustc.edu.cn',
]

def main():
    ping_obj = ping.ResultSequence('ustc.edu.cn',5,0,100,datetime.timedelta(seconds=5))
    ping_obj.start()
    while True:
        now = datetime.datetime.now()
        print(list(ping_obj.get_res(now, now)))
        time.sleep(3)



if __name__ == '__main__':
    main()