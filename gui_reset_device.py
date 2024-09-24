from panel import Panel_FM
import common
from common import time, sleep, Producer
import ping3
import tkinter as tk
from tkinter import ttk
from datetime import timedelta
import utils
from gui_common import StdoutRedirector, StopCounter


class ResetDevice(Producer):
    def __init__(self, device_ip, timeout, logger):
        super().__init__()
        self.device_ip = device_ip
        self.timeout = timeout
        self.logger = logger

    def update(self):
        # 创建一个面板对象
        panel = Panel_FM(self.device_ip, self.timeout, self.logger)
        # 重置面板
        res = panel.reset()
        if res != "OK":
            self.logger.write("重置失败\n")
            self.res = ("Fail", res)
            super().update()
            return
        start = time()
        self.logger.write("重置\n")
        sleep(5)
        while True:
            res = ping3.ping(self.device_ip, self.timeout.total_seconds())
            if isinstance(res, float):
                break
            else:
                self.logger.write(f"等待设备上线...{time()-start:.1f}秒\n")
        device_up = time()
        self.logger.write(f"设备上线，耗时{device_up-start:.1f}秒\n")
        while True:
            res = ping3.ping("www.baidu.com", self.timeout.total_seconds())
            if isinstance(res, float):
                break
            else:
                self.logger.write(f"等待设备驻网...{time()-device_up:.1f}秒\n")
        device_online = time()
        self.logger.write(f"设备驻网，耗时{device_online-device_up:.1f}秒\n")

        self.res = (round(device_up - start), round(device_online - device_up))
        super().update()


IS_RUNNING: bool = False


class Result2Table(common.Recorder):
    def __init__(self, table: ttk.Treeview):
        super().__init__(None)
        self.table = table
        self.cnt = 0
        # self.len = 0

    def record(self, res: tuple[float, float]):
        start_time, online_time = res
        self.cnt += 1
        self.table.insert("", tk.END, values=(self.cnt, start_time, online_time))
        self.table.yview_moveto(1)


class ResetUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        try:
            root.title("重置捏~")
        except:  # noqa: E722
            pass

        self.root = root
        self.widgets = []
        self.create_widgets()

    def create_widgets(self):
        def f(x):
            self.widgets.append(x)
            return x

        no_name_frame_1 = ttk.Frame(self.root)

        no_name_frame_1_1 = ttk.Frame(no_name_frame_1)
        tk.Label(no_name_frame_1_1, text="设备IP地址").pack()
        self.device_ip = f(tk.Entry(no_name_frame_1_1))
        self.device_ip.insert(0, utils.which_is_device_ip())
        self.device_ip.pack()
        no_name_frame_1_1.pack(side=tk.LEFT)

        # no_name_frame_1_2 = ttk.Frame(no_name_frame_1)
        # self.save_log = tk.BooleanVar(value=True)
        # f(tk.Checkbutton(no_name_frame_1_2, text="保存结果到文件", variable=self.save_log)).pack()
        # tk.Label(no_name_frame_1_2, text="保存至：时间戳+[...]").pack()
        # self.folder_name_addon = f(tk.Entry(no_name_frame_1_2))
        # self.folder_name_addon.insert(0, '为你的设备命名')
        # self.folder_name_addon.pack()
        # no_name_frame_1_2.pack(side=tk.RIGHT)

        no_name_frame_1.pack()

        custom_frame = ttk.Frame(self.root)
        tk.Label(custom_frame, text="总共").pack(side=tk.LEFT)
        self.count_custom = f(tk.Entry(custom_frame, width=3))
        self.count_custom.insert(0, "∞")
        self.count_custom.pack(side=tk.LEFT)
        tk.Label(custom_frame, text="次").pack(side=tk.LEFT)
        custom_frame.pack()

        no_name_frame_3 = ttk.Frame(self.root)
        start_button = tk.Button(
            no_name_frame_3, text="开始", command=self.start_button_clicked
        )
        start_button.pack(side=tk.LEFT)
        stop_button = tk.Button(
            no_name_frame_3, text="停止", command=self.stop_button_clicked
        )
        stop_button.pack(side=tk.LEFT)
        self.count_label = tk.Label(no_name_frame_3, text="第0次")
        self.count_label.pack(side=tk.LEFT)
        copy_button = tk.Button(
            no_name_frame_3, text="复制选中", command=self.copy_selected_to_clipboard
        )
        copy_button.pack(side=tk.LEFT)
        clear_button = tk.Button(
            no_name_frame_3, text="清空历史", command=self.clear_tree
        )
        clear_button.pack(side=tk.LEFT)
        no_name_frame_3.pack()

        output_text = tk.Text(self.root, wrap="word", height=8)
        output_text.pack(expand=True, fill=tk.X)

        self.not_stdout = StdoutRedirector(output_text)

        columns = ("编号", "启动用时", "驻网用时")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill=tk.X)

        self.obj: common.Sequence | None = None

    def start_button_clicked(
        self,
    ):
        if self.obj is not None:
            self.not_stdout.write("已在运行! 刷新文件缓存\n")
            self.obj.flush()
            return
        else:
            self.not_stdout.write("Starting\n")

        try:
            count = int(self.count_custom.get())
        except ValueError:
            count = -1

        self.obj = ResetDevice(
            self.device_ip.get(), timedelta(seconds=1), self.not_stdout
        )

        self.obj.add_recorder(Result2Table(self.tree))
        self.obj.add_recorder(
            StopCounter(
                callback_each=lambda cnt: self.count_label.config(text=f"第{cnt}次"),
                callback_final=self.stop_button_clicked,
                target_cnt=count,
            )
        )
        # self.obj = common.AutoFlush(self.obj, timedelta(minutes=20))
        self.obj = common.Sequence(self.obj)
        self.obj.start()
        global IS_RUNNING
        IS_RUNNING = True
        self.disable_when_running()

    def stop_button_clicked(
        self,
    ):
        if self.obj is not None:
            self.not_stdout.write("正在停止…\n")
            self.obj.flush()
            self.obj.stop()
            self.obj = None
            global IS_RUNNING
            IS_RUNNING = False
            self.enable_when_stopped()
        else:
            self.not_stdout.write("未在运行!\n")

    def disable_when_running(
        self,
    ):
        for i in self.widgets:
            i.configure(state=tk.DISABLED)

    def enable_when_stopped(
        self,
    ):
        for i in self.widgets:
            i.configure(state=tk.NORMAL)

    def copy_selected_to_clipboard(
        self,
    ):
        selected_items: tuple[str, ...] = self.tree.selection()
        if selected_items:
            selected_data = []
            for item in selected_items:
                row = self.tree.item(item)["values"][1:]
                selected_data.append(row)

            # 将选中的数据转换为制表符分隔的字符串
            clipboard_text = ""
            for row in selected_data:
                clipboard_text += "\t".join(map(str, row)) + "\n"

            # 复制到剪贴板
            root.clipboard_clear()
            root.clipboard_append(clipboard_text)
            root.update()  # 更新剪贴板内容

            print("选中的数据已复制到剪贴板")

    def clear_tree(
        self,
    ):
        for item in self.tree.get_children():
            self.tree.delete(item)


def main(root: tk.Tk):
    return ResetUI(root)


if __name__ == "__main__":
    root = tk.Tk()
    ResetUI(root)
    root.mainloop()
