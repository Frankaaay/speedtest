import tkinter as tk
from tkinter import ttk
import utils
import stability_recorder
import time

IS_RUNNING: bool = False

class StdoutRedirector:
    def __init__(self, text_widget:tk.Text):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.config(state="normal")  # 允许编辑
        self.text_widget.insert(tk.END, message)  # 在文本框末尾插入消息
        self.text_widget.see(tk.END)
        # 删除多余的行
        lines = self.text_widget.get("1.0", tk.END).split("\n")
        if len(lines) > 100:
            self.text_widget.delete("1.0", f"{len(lines) - 100}.0")
        self.text_widget.config(state="disabled")  # 禁止编辑

    def flush(self):
        pass

    def close(self):
        pass

class LiveUI:
    def __init__(self, root: tk.Tk):
        try:
            root.title("测速捏~")
        except:
            pass
        
        self.root = root
        self.create_widgets()

    def create_widgets(self):
        no_name_frame_1 = ttk.Frame(self.root)

        no_name_frame_1_1 = ttk.Frame(no_name_frame_1)
        self.record_device = tk.BooleanVar(value=False)
        tk.Checkbutton(no_name_frame_1_1, text="记录设备状态", variable=self.record_device).pack()
        tk.Label(no_name_frame_1_1, text="设备IP地址").pack()
        self.device_ip = tk.Entry(no_name_frame_1_1)
        self.device_ip.insert(0, utils.which_is_device_ip())
        self.device_ip.pack()
        no_name_frame_1_1.pack(side=tk.LEFT)

        no_name_frame_1_2 = ttk.Frame(no_name_frame_1)
        self.save_log = tk.BooleanVar(value=True)
        tk.Checkbutton(no_name_frame_1_2, text="保存结果到文件", variable=self.save_log).pack()
        tk.Label(no_name_frame_1_2, text="保存至：时间戳+[...]").pack()
        self.folder_name_addon = tk.Entry(no_name_frame_1_2)
        self.folder_name_addon.insert(0, '为你的设备命名')
        self.folder_name_addon.pack()
        no_name_frame_1_2.pack(side=tk.RIGHT)

        no_name_frame_1.pack()

        
        # 可选输入框
        no_name_frame_2 = ttk.Frame(self.root)
        no_name_frame_2_1 = ttk.Frame(no_name_frame_2)
        tk.Label(no_name_frame_2_1, text="房间号").pack()
        self.room_id = tk.Entry(no_name_frame_2_1)
        self.room_id.pack()
        no_name_frame_2_1.pack(side=tk.LEFT)

        no_name_frame_2_2 = ttk.Frame(no_name_frame_2)
        # 计时器显示
        tk.Label(no_name_frame_2_2, text="测试时长").pack()
        self.timer_h = tk.Entry(no_name_frame_2_2, width=6)
        self.timer_h.insert(0, '00')
        self.timer_h.pack(side=tk.LEFT)
        tk.Label(no_name_frame_2_2, text=":").pack(side=tk.LEFT)
        self.timer_m = tk.Entry(no_name_frame_2_2, width=4)
        self.timer_m.insert(0, '00')
        self.timer_m.pack(side=tk.LEFT)
        tk.Label(no_name_frame_2_2, text=":").pack(side=tk.LEFT)
        self.timer_s = tk.Entry(no_name_frame_2_2, width=4)
        self.timer_s.insert(0, '00')
        self.timer_s.pack(side=tk.LEFT)
        no_name_frame_2_2.pack(side=tk.LEFT)
        
        no_name_frame_2.pack()

    

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

        self.obj: stability_recorder.Main|None = None

        # 开始和停止按钮
        button_frame = ttk.Frame(self.root)

        start_button = tk.Button(button_frame, text="开始", command=self.start_button_clicked)
        start_button.pack(side=tk.LEFT)

        self.timer_label = tk.Label(button_frame, text="--:--:--")
        self.timer_label.pack(side=tk.LEFT)

        stop_button = tk.Button(button_frame, text="停止", command=self.stop_button_clicked)
        stop_button.pack(side=tk.LEFT)
        
        button_frame.pack()

        # 创建一个滚动文本框
        output_text = tk.Text(self.root, wrap="word", height=25, width=60)
        output_text.pack(expand=True, fill=tk.X)

        self.not_stdout = StdoutRedirector(output_text)
        
        # 重定向 stdout 和 stderr


    def start_button_clicked(self,):
        # 处理开始按钮点击事件
        if self.obj is not None:
            self.not_stdout.write("Already running! Flushing\n")
            self.obj.flush()
            return
        global IS_RUNNING
        IS_RUNNING = True
        self.start_time = time.time()
        try:
            h = float(self.timer_h.get())
            m = float(self.timer_m.get())
            s = float(self.timer_s.get())
            total_seconds = h * 3600 + m * 60 + s
        except:
            total_seconds = 0
        self.obj = stability_recorder.Main(
                                    self.browser_option.get(),
                                    self.record_device.get(),
                                    self.device_ip.get(),
                                    self.save_log.get(),
                                    self.live_option.get(),
                                    self.room_id.get(),
                                    {'ping_www': 'www.baidu.com',
                                    'ping_192': self.device_ip.get()},
                                    self.not_stdout,
                                    self.folder_name_addon.get()
                                    )
        self.update_timer(total_seconds>0, time.time(), total_seconds)


    def stop_button_clicked(self):
        # 处理停止按钮点击事件
        if self.obj is not None:
            self.not_stdout.write("Stopping\n")
            self.obj.flush()
            self.obj.stop()
            self.obj = None
            global IS_RUNNING
            IS_RUNNING = False
        else:
            self.not_stdout.write("Not running!\n")

    def update_timer(self, countdown:bool,start_time:float, t:float):
        if self.obj is not None:
            if countdown:
                time_to_display = t - (time.time() - start_time)
                if time_to_display < 1:
                    self.stop_button_clicked()
            else:
                time_to_display = time.time() - start_time
            hours, remainder = divmod(time_to_display, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_label.config(text=f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}")
            self.root.after(900, self.update_timer,countdown,start_time,t)  # 每秒更新一次

def main(root:tk.Tk):
    return LiveUI(root)

if __name__ == "__main__":
    root = tk.Tk()
    LiveUI(root)
    root.mainloop()
