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
    # ping_obj_192 = ping.ResultSequence(
    #     '192.168.0.1', 5, 0, 100, datetime.timedelta(seconds=5))
    # ping_obj_192.start()
    ping_obj_bili = ping.ResultSequence(
        'live.bilibili.com', 5, 0, 100, datetime.timedelta(seconds=5))
    ping_obj_bili.start()
    while True:
        now = datetime.datetime.now()
        print(list(ping_obj_bili.get_res(now, now)))
        time.sleep(3)


if __name__ == '__main__':
    main()
