import tkinter as tk
from tkinter import ttk
import speedspider
import common
from datetime import timedelta
import utils
import panel
import recorder_speed
from gui_common import StdoutRedirector, StopCounter

IS_RUNNING: bool = False


class Result2Table(common.Recorder):
    def __init__(self, table: ttk.Treeview):
        super().__init__(None)
        self.table = table
        # self.len = 0

    def record(self, res: tuple[speedspider.SpeedTestResult, panel.PanelState]):
        res_speed, res_device = res
        # if self.len > 8:
        #     self.table.delete(self.table.get_children()[0])
        # else:
        #     self.len += 1
        self.table.insert(
            "",
            tk.END,
            values=(res_speed.lag, res_speed.jit, res_speed.dl, res_speed.ul),
        )
        self.table.yview_moveto(1)


class SpeedUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        try:
            root.title("测速捏~")
        except:  # noqa: E722
            pass

        self.root = root
        self.widgets = []
        self.create_widgets()

    def create_widgets(self):
        def f(x):
            self.widgets.append(x)
            return x

        self.headless = tk.BooleanVar(value=True)
        f(tk.Checkbutton(self.root, text="浏览器无头", variable=self.headless)).pack()

        no_name_frame_1 = ttk.Frame(self.root)

        no_name_frame_1_1 = ttk.Frame(no_name_frame_1)
        self.record_device = tk.BooleanVar(value=False)
        f(
            tk.Checkbutton(
                no_name_frame_1_1, text="记录设备状态", variable=self.record_device
            )
        ).pack()
        tk.Label(no_name_frame_1_1, text="设备IP地址").pack()
        self.device_ip = f(tk.Entry(no_name_frame_1_1))
        self.device_ip.insert(0, utils.which_is_device_ip())
        self.device_ip.pack()
        no_name_frame_1_1.pack(side=tk.LEFT)

        no_name_frame_1_2 = ttk.Frame(no_name_frame_1)
        self.save_log = tk.BooleanVar(value=True)
        f(
            tk.Checkbutton(
                no_name_frame_1_2, text="保存结果到文件", variable=self.save_log
            )
        ).pack()
        tk.Label(no_name_frame_1_2, text="保存至：时间戳+[...]").pack()
        self.folder_name_addon = f(tk.Entry(no_name_frame_1_2))
        self.folder_name_addon.insert(0, "为你的设备命名")
        self.folder_name_addon.pack()
        no_name_frame_1_2.pack(side=tk.RIGHT)

        no_name_frame_1.pack()

        # 创建默认项列表
        tk.Label(self.root, text="测速网站").pack()
        self.url_listbox = tk.Listbox(
            self.root, selectmode=tk.SINGLE, width=50, height=8
        )
        for item in speedspider.URLS:
            self.url_listbox.insert(tk.END, item)
        self.url_listbox.pack()

        # 输入框和按钮
        no_name_frame_2 = ttk.Frame(self.root)
        self.add_url = f(tk.Entry(no_name_frame_2, width=38))
        self.add_url.pack(side=tk.LEFT)
        add_button = f(tk.Button(no_name_frame_2, text="添加", command=self.add_item))
        add_button.pack(side=tk.LEFT)
        delete_button = f(
            tk.Button(no_name_frame_2, text="删除", command=self.delete_item)
        )
        delete_button.pack(side=tk.LEFT)
        no_name_frame_2.pack()

        # 单选列表
        options = ["Edge", "Chrome", "Firefox"]
        self.browser_option = tk.StringVar()
        self.browser_option.set(options[0])
        browser_frame = ttk.Frame(self.root)
        for option in options:
            radio_button = f(
                ttk.Radiobutton(
                    browser_frame,
                    text=option,
                    value=option,
                    variable=self.browser_option,
                )
            )
            radio_button.pack(side="left")
        browser_frame.pack()

        custom_frame = ttk.Frame(self.root)
        tk.Label(custom_frame, text="每隔").pack(side=tk.LEFT)
        self.delta_custom = f(tk.Entry(custom_frame, width=3))
        self.delta_custom.insert(0, "5")
        self.delta_custom.pack(side=tk.LEFT)
        tk.Label(custom_frame, text="分钟").pack(side=tk.LEFT)
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

        columns = ("延迟", "抖动", "下载", "上传")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill=tk.X)

        self.obj: common.Sequence | None = None

    def add_item(
        self,
    ):
        item = self.add_url.get()
        if item:
            self.url_listbox.insert(tk.END, item)
            self.add_url.delete(0, tk.END)
        else:
            self.not_stdout.write("输入要添加的网站\n")
            pass
            # messagebox.showwarning("警告", "请输入要添加的项！")

    def delete_item(
        self,
    ):
        selected_index = self.url_listbox.curselection()
        if selected_index:
            self.url_listbox.delete(selected_index)
        else:
            self.not_stdout.write("选择要删除的网站\n")
            pass
            # messagebox.showwarning("警告", "请选择要删除的项！")

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
            interval = float(self.delta_custom.get())
        except ValueError:
            interval = 0

        try:
            count = int(self.count_custom.get())
        except ValueError:
            count = -1

        utils.Browser_name = self.browser_option.get()

        delta = timedelta(minutes=max(0, interval), microseconds=1)
        self.obj = recorder_speed.Main(
            self.browser_option.get(),
            self.url_listbox.get(0, tk.END),
            self.record_device.get(),
            self.device_ip.get(),
            self.save_log.get(),
            self.headless.get(),
            self.not_stdout,
            self.folder_name_addon.get(),
            faster_version=interval < 0,
        )

        self.obj.add_recorder(Result2Table(self.tree))
        self.obj.add_recorder(
            StopCounter(
                callback_each=lambda cnt: self.count_label.config(text=f"第{cnt}次"),
                callback_final=self.stop_button_clicked,
                target_cnt=count,
            )
        )
        self.obj = common.AutoFlush(self.obj, timedelta(minutes=20))
        self.obj = common.Sequence(self.obj, delta)
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
                row = self.tree.item(item)["values"]
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
    return SpeedUI(root)


if __name__ == "__main__":
    root = tk.Tk()
    SpeedUI(root)
    root.mainloop()
