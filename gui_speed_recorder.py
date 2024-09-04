import tkinter as tk
from tkinter import ttk
import speedspider
import common
from datetime import timedelta
import utils
import panel
import speed_recorder

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

def main(root: tk.Tk):
    try:
        root.title("直播稳定性检测")
    except:
        pass

    def add_item():
        nonlocal not_stdout
        item = add_url.get()
        if item:
            url_listbox.insert(tk.END, item)
            add_url.delete(0, tk.END)
        else:
            not_stdout.write("请输入要添加的网站！\n")
            pass
            # messagebox.showwarning("警告", "请输入要添加的项！")


    def delete_item():
        nonlocal not_stdout
        selected_index = url_listbox.curselection()
        if selected_index:
            url_listbox.delete(selected_index)
        else:
            not_stdout.write("请输入要删除的网站！\n")
            pass
            # messagebox.showwarning("警告", "请选择要删除的项！")


    class Result2Display(common.Recorder):
        def __init__(self, table: ttk.Treeview):
            super().__init__(None)
            self.table = table
            # self.len = 0

        def record(self, res: tuple[speedspider.SpeedTestResult,panel.PanelState]):
            res_speed,res_device = res
            # if self.len > 8:
            #     self.table.delete(self.table.get_children()[0])
            # else:
            #     self.len += 1
            self.table.insert("", tk.END,
                            values=(res_speed.lag, res_speed.jit, res_speed.dl, res_speed.ul))


    def start_button_clicked():
        nonlocal obj, not_stdout
        if obj is not None:
            not_stdout.write("Already running! Flushing\n")
            obj.flush()
            return
        nonlocal url_listbox, delta_custom, save_log, tree, headless, record_device, device_ip
        delta = timedelta(minutes=float(delta_custom.get()), microseconds=1)
        obj = speed_recorder.Main(
            url_listbox.get(0, tk.END),
            record_device.get(), device_ip.get(),
            save_log.get(), headless.get(),
            not_stdout)
        

        obj.add_recorder(Result2Display(tree))
        obj = common.AutoFlush(obj, timedelta(minutes=20))
        obj = common.Sequence(obj, delta)
        obj.start()


    def stop_button_clicked():
        nonlocal obj, not_stdout
        if obj is not None:
            not_stdout.write("Stopping\n")
            obj.stop()
            obj = None
        else:
            not_stdout.write("Not running!\n")


    def copy_selected_to_clipboard():
        nonlocal tree
        selected_items: tuple[str, ...] = tree.selection()
        if selected_items:
            selected_data = []
            for item in selected_items:
                row = tree.item(item)['values']
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


    # root.title("定时测速")

    record_device = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="记录设备状态", variable=record_device).pack()

    # 输入框
    tk.Label(root, text="设备IP地址").pack()
    device_ip = tk.Entry(root)
    device_ip.insert(0, utils.which_is_device_ip())
    device_ip.pack()

    # 创建默认项列表
    tk.Label(root, text="测速网站").pack()
    url_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50, height=8)
    for item in speedspider.URLS:
        url_listbox.insert(tk.END, item)
    url_listbox.pack()

    # 输入框和按钮
    edit_frame = ttk.Frame(root)
    add_url = tk.Entry(edit_frame, width=38)
    add_url.pack(side=tk.LEFT)
    add_button = tk.Button(edit_frame, text="添加", command=add_item)
    add_button.pack(side=tk.LEFT)
    delete_button = tk.Button(edit_frame, text="删除", command=delete_item)
    delete_button.pack(side=tk.LEFT)
    edit_frame.pack()

    no_name_frame_0 = ttk.Frame(root)
    save_log = tk.BooleanVar(value=True)
    tk.Checkbutton(no_name_frame_0, text="保存结果到文件", variable=save_log).pack(side=tk.LEFT)
    headless = tk.BooleanVar(value=True)
    tk.Checkbutton(no_name_frame_0, text="浏览器无头", variable=headless).pack(side=tk.LEFT)
    no_name_frame_0.pack()

    custom_frame = ttk.Frame(root)
    tk.Label(custom_frame, text="每隔").pack(side=tk.LEFT)
    delta_custom = tk.Entry(custom_frame, width=3)
    delta_custom.insert(0, "5")
    delta_custom.pack(side=tk.LEFT)
    tk.Label(custom_frame, text="分钟").pack(side=tk.LEFT)
    custom_frame.pack()

    edit_frame = ttk.Frame(root)
    start_button = tk.Button(edit_frame, text="开始", command=start_button_clicked)
    start_button.pack(side=tk.LEFT)
    stop_button = tk.Button(edit_frame, text="停止", command=stop_button_clicked)
    stop_button.pack(side=tk.RIGHT)
    edit_frame.pack()

    output_text = tk.Text(root, wrap="word", height=5, width=100)
    output_text.pack()

    not_stdout = StdoutRedirector(output_text)

    columns = ("延迟", "抖动", "下载", "上传")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill=tk.X)

    copy_button = tk.Button(root, text="复制选中到剪贴板", command=copy_selected_to_clipboard)
    copy_button.pack()

    obj:common.Sequence|None = None

if __name__ == "__main__":
    root = tk.Tk()
    main(root)
    root.mainloop()