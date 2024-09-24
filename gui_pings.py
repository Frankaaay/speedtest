import tkinter as tk
from tkinter import ttk
import common
from datetime import timedelta
import utils
import stable

IS_RUNNING: bool = False
PATH = './log/pings'

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


class StopCounter(common.Recorder):
    '''
    记录运行次数，当达到目标次数时停止运行
    '''
    def __init__(self, callback_each, callback_final, target_cnt):
        super().__init__(None)
        self.cnt = 0
        self.callback_each = callback_each
        self.callback_final = callback_final
        self.target_cnt = target_cnt
        self.callback_each(0)
    
    def record(self, any):
        super().record(any)
        self.cnt += 1
        self.callback_each(self.cnt)
        if self.target_cnt >= 0 and self.cnt >= self.target_cnt:
            self.callback_final()

class Result2Display(common.Recorder):
    def __init__(self, table: ttk.Treeview):
        super().__init__(None)
        self.table = table

    def record(self, res: dict[str,float]):
        res: list = list(res.items())
        res.sort(key=lambda x: x[0])
        self.table.insert("", tk.END,values=[i[1] for i in res])
        self.table.yview_moveto(1)
        
class Result2File(common.Recorder):
    def __init__(self, file):
        super().__init__(file)
        self.record = self.record_first_time

    def record_first_time(self, res: dict[str,float]):
        self.keys = list(res.keys())
        self.keys.sort()
        self.file.write(f"{','.join(self.keys)}\n")
        self.record = self._record
        self.record(res)

    def _record(self, res: dict[str,float]):
        self.file.write(f"{','.join(str(res[i]) for i in self.keys)}\n")
        

class SpeedUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        try:
            root.title("Ping~")
        except:
            pass
        
        self.root = root
        self.widgets = []
        self.create_widgets()

    def create_widgets(self):

        def f(x):
            self.widgets.append(x)
            return self.widgets[-1]
        
        no_name_frame_1 = ttk.Frame(self.root)

        no_name_frame_1_2 = ttk.Frame(no_name_frame_1)
        self.save_log = tk.BooleanVar(value=True)
        f(tk.Checkbutton(no_name_frame_1_2, text="保存结果到文件", variable=self.save_log)).pack()
        tk.Label(no_name_frame_1_2, text="保存至：时间戳+[...]").pack()
        self.folder_name_addon = f(tk.Entry(no_name_frame_1_2))
        self.folder_name_addon.insert(0, '为你的设备命名')
        self.folder_name_addon.pack()
        no_name_frame_1_2.pack(side=tk.RIGHT)

        no_name_frame_1.pack()

        # 创建默认项列表
        tk.Label(self.root, text="目标").pack()
        self.url_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, width=50, height=8)
        for item in ['www.baidu.com','www.qq.com',utils.which_is_device_ip()]:
            self.url_listbox.insert(tk.END, item)
        self.url_listbox.pack()

        # 输入框和按钮
        no_name_frame_2 = ttk.Frame(self.root)
        self.add_url = f(tk.Entry(no_name_frame_2, width=38))
        self.add_url.pack(side=tk.LEFT)
        add_button = f(tk.Button(no_name_frame_2, text="添加", command=self.add_item))
        add_button.pack(side=tk.LEFT)
        delete_button = f(tk.Button(no_name_frame_2, text="删除", command=self.delete_item))
        delete_button.pack(side=tk.LEFT)
        no_name_frame_2.pack()

        # 单选列表

        custom_frame = ttk.Frame(self.root)
        tk.Label(custom_frame, text="每隔").pack(side=tk.LEFT)
        self.delta_custom = f(tk.Entry(custom_frame, width=6))
        self.delta_custom.insert(0, "1000")
        self.delta_custom.pack(side=tk.LEFT)
        tk.Label(custom_frame, text="毫秒").pack(side=tk.LEFT)
        tk.Label(custom_frame, text="总共").pack(side=tk.LEFT)
        self.count_custom = f(tk.Entry(custom_frame, width=3))
        self.count_custom.insert(0, "∞")
        self.count_custom.pack(side=tk.LEFT)
        tk.Label(custom_frame, text="次").pack(side=tk.LEFT)
        custom_frame.pack()

        no_name_frame_3 = ttk.Frame(self.root)
        start_button = tk.Button(no_name_frame_3, text="开始", command=self.start_button_clicked)
        start_button.pack(side=tk.LEFT)
        stop_button = tk.Button(no_name_frame_3, text="停止", command=self.stop_button_clicked)
        stop_button.pack(side=tk.LEFT)
        self.count_label = tk.Label(no_name_frame_3, text="第0次")
        self.count_label.pack(side=tk.LEFT)
        clear_button = tk.Button(no_name_frame_3, text="清空历史", command=self.clear_tree)
        clear_button.pack(side=tk.LEFT)
        no_name_frame_3.pack()   

        output_text = tk.Text(self.root, wrap="word", height=3)
        output_text.pack(expand=True, fill=tk.X)

        self.not_stdout = StdoutRedirector(output_text)

        columns = ("地址", "平均", "超时")
        self.statistics = ttk.Treeview(self.root, columns=columns, show="headings", height=6)
        for col in columns:
            self.statistics.heading(col, text=col)
        self.statistics.pack(expand=True, fill=tk.X)

        columns = ("地址1", "地址2", "...")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=4)
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill=tk.X)

        self.obj:common.Sequence|None = None
    

    def add_item(self,):
        item = self.add_url.get()
        if item:
            self.url_listbox.insert(tk.END, item)
            self.add_url.delete(0, tk.END)
        else:
            self.not_stdout.write("输入要添加的地址\n")
            pass
            # messagebox.showwarning("警告", "请输入要添加的项！")


    def delete_item(self,):
        selected_index = self.url_listbox.curselection()
        if selected_index:
            self.url_listbox.delete(selected_index)
        else:
            self.not_stdout.write("选择要删除的地址\n")
            pass
            # messagebox.showwarning("警告", "请选择要删除的项！")


    def start_button_clicked(self,):
        if self.obj is not None:
            self.not_stdout.write("已在运行! 刷新文件缓存\n")
            self.obj.flush()
            return
        
        else:
            self.not_stdout.write("正在开始…\n")

        try:
            interval = float(self.delta_custom.get())
        except ValueError:
            interval = 0
        delta = timedelta(milliseconds=max(0,interval))

        try:
            count = int(self.count_custom.get())
        except ValueError:
            count = -1

        self.clear_tree()
        urls:list = list(self.url_listbox.get(0, tk.END))
        urls.sort()
        print(urls)

        
        self.summary = stable.Summary()
        
        self.tree.config(columns=urls, show="headings")
        for col in urls:
            self.tree.heading(col, text=col)
        

        self.obj = stable.Pings(urls, delta*4)
        if self.save_log.get():
            import os
            now = common.datetime.now().strftime(f'%Y-%m-%d_%H-%M-%S')
            folder_name = self.folder_name_addon.get()
            os.makedirs(f"{PATH}/{now}#{folder_name}/", exist_ok=True)
            self.obj.add_recorder(Result2File(open(f"{PATH}/{now}#{folder_name}/ping.csv",'w')))
        self.obj.add_recorder(Result2Display(self.tree))
        self.obj.add_recorder(self.summary)
        self.obj.add_recorder(StopCounter(
            callback_each=lambda cnt:self.update_each_time(cnt),
            callback_final=self.stop_button_clicked,
            target_cnt=count))
        self.obj = common.AutoFlush(self.obj, timedelta(minutes=2))
        self.obj = common.Sequence(self.obj, delta)
        self.obj.start()

        global IS_RUNNING
        IS_RUNNING = True
        self.disable_when_running()

    def update_each_time(self,cnt:int):
        self.count_label.config(text=f"第{cnt}次")
        
        for address in self.summary.res:
            if address not in self.statistics.get_children():
                self.statistics.insert("", "end", iid=address, values=(address, 0, 0))
            self.statistics.item(address, values=(address, self.summary.res[address].avg, self.summary.res[address].timeout))

    def stop_button_clicked(self,):
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

    def disable_when_running(self, ):
        for i in self.widgets:
            i.configure(state=tk.DISABLED)

    def enable_when_stopped(self, ):
        for i in self.widgets:
            i.configure(state=tk.NORMAL)
    def clear_tree(self,):
        for item in self.tree.get_children():
            self.tree.delete(item)


def main(root:tk.Tk):
    return SpeedUI(root)

if __name__ == "__main__":
    root = tk.Tk()
    SpeedUI(root)
    root.mainloop()