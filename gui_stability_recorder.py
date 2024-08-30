import tkinter as tk
from tkinter import ttk
import utils
import sys
import stability_recorder

def main():
    root = tk.Tk()
    root.title("直播稳定性检测")

    # 勾选项
    record_device = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="记录设备状态", variable=record_device).pack()

    # 输入框
    tk.Label(root, text="设备IP地址").pack()
    device_ip = tk.Entry(root)
    device_ip.insert(0, utils.which_is_device_ip())
    device_ip.pack()

    # 单选列表
    options = ["B站", "抖音", "西瓜", "Youtube"]
    live_option = tk.StringVar()
    live_option.set(options[0])
    live_frame = ttk.Frame(root)
    for option in options:
        radio_button = ttk.Radiobutton(
            live_frame, text=option, value=option, variable=live_option)
        radio_button.pack(side="left")
    live_frame.pack()

    # 单选列表
    options = ["Edge", "Chrome", "Firefox"]
    browser_option = tk.StringVar()
    browser_option.set(options[0])
    browser_frame = ttk.Frame(root)
    for option in options:
        radio_button = ttk.Radiobutton(
            browser_frame, text=option, value=option, variable=browser_option)
        radio_button.pack(side="left")
    browser_frame.pack()

    # 可选输入框
    tk.Label(root, text="房间号（可不填）").pack()
    room_id = tk.Entry(root)
    room_id.pack()


    obj = None


    def start_button_clicked():
        # 处理开始按钮点击事件
        nonlocal obj
        if obj is not None:
            return

        nonlocal record_device, device_ip, live_option, browser_option, room_id
        utils.browser_name = browser_option.get()

        obj = stability_recorder.Main(record_device.get(),
                                    device_ip.get(),
                                    live_option.get(),
                                    room_id.get(),
                                    {'ping_www': 'www.baidu.com',
                                    'ping_192': device_ip.get()}
                                    )


    def stop_button_clicked():
        # 处理停止按钮点击事件
        nonlocal obj
        if obj is not None:
            print("Stopping")
            obj.stop()
            obj = None


    # 开始和停止按钮
    button_frame = ttk.Frame(root)

    start_button = tk.Button(button_frame, text="开始", command=start_button_clicked)
    start_button.pack(side=tk.LEFT)
    stop_button = tk.Button(button_frame, text="停止", command=stop_button_clicked)
    stop_button.pack(side=tk.RIGHT)

    button_frame.pack()

    # 创建一个滚动文本框
    output_text = tk.Text(root, wrap="word", height=20, width=64)
    output_text.pack()


    class StdoutRedirector:
        def __init__(self, text_widget):
            self.text_widget = text_widget

        def write(self, message):
            self.text_widget.config(state="normal")  # 允许编辑
            self.text_widget.insert(tk.END, message)  # 在文本框末尾插入消息
            self.text_widget.see(tk.END)
            self.text_widget.config(state="disabled")  # 禁止编辑

        def flush(self):
            pass

        def close(self):
            pass


    # 重定向 stdout 和 stderr
    sys.stdout = StdoutRedirector(output_text)
    sys.stderr = StdoutRedirector(output_text)

    root.mainloop()

if __name__ == '__main__':
    main()