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

class SpeedUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        try:
            root.title("测速捏~")
        except:
            pass
        
        self.root = root
        self.create_widgets()

    def create_widgets(self):
    
        self.headless = tk.BooleanVar(value=True)
        tk.Checkbutton(self.root, text="浏览器无头", variable=self.headless).pack()
        
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
        self.save_log = tk.BooleanVar(value=False)
        tk.Checkbutton(no_name_frame_1_2, text="保存结果到文件", variable=self.save_log).pack()
        tk.Label(no_name_frame_1_2, text="保存至：时间戳+[...]").pack()
        self.folder_name_addon = tk.Entry(no_name_frame_1_2)
        self.folder_name_addon.insert(0, 'FM电信')
        self.folder_name_addon.pack()
        no_name_frame_1_2.pack(side=tk.RIGHT)

        no_name_frame_1.pack()

        # 创建默认项列表
        tk.Label(self.root, text="测速网站").pack()
        self.url_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, width=50, height=8)
        for item in speedspider.URLS:
            self.url_listbox.insert(tk.END, item)
        self.url_listbox.pack()

        # 输入框和按钮
        no_name_frame_2 = ttk.Frame(self.root)
        self.add_url = tk.Entry(no_name_frame_2, width=38)
        self.add_url.pack(side=tk.LEFT)
        add_button = tk.Button(no_name_frame_2, text="添加", command=self.add_item)
        add_button.pack(side=tk.LEFT)
        delete_button = tk.Button(no_name_frame_2, text="删除", command=self.delete_item)
        delete_button.pack(side=tk.LEFT)
        no_name_frame_2.pack()

        custom_frame = ttk.Frame(self.root)
        tk.Label(custom_frame, text="每隔").pack(side=tk.LEFT)
        self.delta_custom = tk.Entry(custom_frame, width=3)
        self.delta_custom.insert(0, "5")
        self.delta_custom.pack(side=tk.LEFT)
        tk.Label(custom_frame, text="分钟").pack(side=tk.LEFT)
        custom_frame.pack()

        no_name_frame_3 = ttk.Frame(self.root)
        start_button = tk.Button(no_name_frame_3, text="开始", command=self.start_button_clicked)
        start_button.pack(side=tk.LEFT)
        stop_button = tk.Button(no_name_frame_3, text="停止", command=self.stop_button_clicked)
        stop_button.pack(side=tk.LEFT)
        copy_button = tk.Button(no_name_frame_3, text="复制选中到剪贴板", command=self.copy_selected_to_clipboard)
        copy_button.pack(side=tk.LEFT)
        clear_button = tk.Button(no_name_frame_3, text="清空历史", command=self.clear_tree)
        clear_button.pack(side=tk.LEFT)
        no_name_frame_3.pack()   

        output_text = tk.Text(self.root, wrap="word", height=15)
        output_text.pack(expand=True, fill=tk.X)

        self.not_stdout = StdoutRedirector(output_text)

        columns = ("延迟", "抖动", "下载", "上传")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
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
            self.not_stdout.write("输入要添加的网站\n")
            pass
            # messagebox.showwarning("警告", "请输入要添加的项！")


    def delete_item(self,):
        selected_index = self.url_listbox.curselection()
        if selected_index:
            self.url_listbox.delete(selected_index)
        else:
            self.not_stdout.write("选择要删除的网站\n")
            pass
            # messagebox.showwarning("警告", "请选择要删除的项！")


    def start_button_clicked(self,):
        if self.obj is not None:
            self.not_stdout.write("Already running! Flushing\n")
            self.obj.flush()
            return
        else:
            self.not_stdout.write("Starting\n")
        
        delta = timedelta(minutes=float(self.delta_custom.get()), microseconds=1)
        self.obj = speed_recorder.Main(
            self.url_listbox.get(0, tk.END),
            self.record_device.get(), self.device_ip.get(),
            self.save_log.get(), self.headless.get(),
            self.not_stdout,
            self.folder_name_addon.get()
            )
        

        self.obj.add_recorder(Result2Display(self.tree))
        self.obj = common.AutoFlush(self.obj, timedelta(minutes=20))
        self.obj = common.Sequence(self.obj, delta)
        self.obj.start()


    def stop_button_clicked(self,):
        if self.obj is not None:
            self.not_stdout.write("Stopping\n")
            self.obj.flush()
            self.obj.stop()
            self.obj = None
        else:
            self.not_stdout.write("Not running!\n")


    def copy_selected_to_clipboard(self,):
        selected_items: tuple[str, ...] = self.tree.selection()
        if selected_items:
            selected_data = []
            for item in selected_items:
                row = self.tree.item(item)['values']
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
    
    def clear_tree(self,):
        for item in self.tree.get_children():
            self.tree.delete(item)

def main(root:tk.Tk):
    SpeedUI(root)

if __name__ == "__main__":
    root = tk.Tk()
    SpeedUI(root)
    root.mainloop()