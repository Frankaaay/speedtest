import tkinter as tk
from tkinter import ttk
import utils
import stability_recorder

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

class LiveUI:
    def __init__(self, root: tk.Tk):
        try:
            self.root.title("直播稳定性检测")
        except:
            pass
        
        self.root = root
        self.create_widgets()

    def create_widgets(self):
    
        # 勾选项
        self.record_device = tk.BooleanVar(value=False)
        tk.Checkbutton(self.root, text="记录设备状态", variable=self.record_device).pack()

        # 输入框
        tk.Label(self.root, text="设备IP地址").pack()
        self.device_ip = tk.Entry(self.root)
        self.device_ip.insert(0, utils.which_is_device_ip())
        self.device_ip.pack()

        # 单选列表
        options = ["B站", "抖音", "西瓜", "OFF"]
        self.live_option = tk.StringVar()
        self.live_option.set(options[0])
        live_frame = ttk.Frame(self.root)
        for option in options:
            radio_button = ttk.Radiobutton(
                live_frame, text=option, value=option, variable=self.live_option)
            radio_button.pack(side="left")
        live_frame.pack()

        # 单选列表
        options = ["Edge", "Chrome", "Firefox"]
        self.browser_option = tk.StringVar()
        self.browser_option.set(options[0])
        browser_frame = ttk.Frame(self.root)
        for option in options:
            radio_button = ttk.Radiobutton(
                browser_frame, text=option, value=option, variable=self.browser_option)
            radio_button.pack(side="left")
        browser_frame.pack()

        # 可选输入框
        tk.Label(self.root, text="房间号（可不填）").pack()
        self.room_id = tk.Entry(self.root)
        self.room_id.pack()


        self.obj: stability_recorder.Main|None = None

        # 开始和停止按钮
        button_frame = ttk.Frame(self.root)

        start_button = tk.Button(button_frame, text="开始", command=self.start_button_clicked)
        start_button.pack(side=tk.LEFT)
        stop_button = tk.Button(button_frame, text="停止", command=self.stop_button_clicked)
        stop_button.pack(side=tk.RIGHT)

        button_frame.pack()

        # 创建一个滚动文本框
        output_text = tk.Text(self.root, wrap="word", height=20, width=100)
        output_text.pack()

        self.not_stdout = StdoutRedirector(output_text)
        
        # 重定向 stdout 和 stderr
        # sys.stdout = StdoutRedirector(output_text)
        # sys.stderr = StdoutRedirector(output_text)


    def start_button_clicked(self,):
        # 处理开始按钮点击事件
        if self.obj is not None:
            self.not_stdout.write("Already running! Flushing\n")
            self.obj.flush()
            return
        utils.browser_name = self.browser_option.get()

        self.obj = stability_recorder.Main(self.record_device.get(),
                                    self.device_ip.get(),
                                    self.live_option.get(),
                                    self.room_id.get(),
                                    {'ping_www': 'www.baidu.com',
                                    'ping_192': self.device_ip.get()},
                                    stdout=self.not_stdout,
                                    )


    def stop_button_clicked(self):
        # 处理停止按钮点击事件
        if self.obj is not None:
            self.not_stdout.write("Stopping\n")
            self.obj.stop()
            self.obj = None
        else:
            self.not_stdout.write("Not running!\n")

def main(root:tk.Tk):
    LiveUI(root)

if __name__ == "__main__":
    root = tk.Tk()
    LiveUI(root)
    root.mainloop()
