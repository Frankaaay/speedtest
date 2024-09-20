import tkinter as tk
from tkinter import ttk
import common
import iperf
import utils

IS_RUNNING : int = 0

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
        if self.target_cnt > 0 and self.cnt >= self.target_cnt:
            self.callback_final()

class Result2Display(common.Recorder):
    def __init__(self, table: ttk.Treeview):
        super().__init__(None)
        self.table = table
        # self.len = 0

    def record(self, res:tuple[str,float]):
        txt, speed = res
        # if self.len > 8:
        #     self.table.delete(self.table.get_children()[0])
        # else:
        #     self.len += 1
        self.table.insert("", tk.END,
                        values=(common.datetime.now().strftime("%H:%M:%S"),txt,speed))
        self.table.yview_moveto(1)

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

class IperfClient:
    def __init__(self, root):
        try:
            root.title("Iperf 测试")
        except:
            pass

        self.root = root
        self.server_ports: tk.Listbox = None
        self.server_obj = None
        self.client_obj = None
        self.add_port_entry = None
        self.display_only= None

        self.widgets = []
        self.create_widgets()

    def create_widgets(self):
    
        def f(x):
            self.widgets.append(x)
            return self.widgets[-1]
        
        frame1 = tk.Frame(self.root)

        client_frame = tk.Frame(frame1)
        client_frame_common = tk.Frame(client_frame)
        # server_ip, server_port, duration, num_streams, reverse
        tk.Label(client_frame_common, text="-c 客户端").pack()

        no_name_frame_2 = tk.Frame(client_frame_common)
        tk.Label(no_name_frame_2, text="IP").pack(side=tk.LEFT)
        self.client_ip = tk.StringVar(value="192.168.0.100")
        f(tk.Entry(no_name_frame_2, textvariable=self.client_ip,width=13)).pack(side=tk.LEFT)
        tk.Label(no_name_frame_2, text="端口").pack(side=tk.LEFT)
        self.client_port = tk.StringVar(value="5201")
        f(tk.Entry(no_name_frame_2, textvariable=self.client_port,width=6)).pack(side=tk.LEFT)
        no_name_frame_2.pack()

        no_name_frame_3 = tk.Frame(client_frame_common)
        tk.Label(no_name_frame_3, text="时长").pack(side=tk.LEFT)
        self.client_duration = tk.StringVar(value="5")
        f(tk.Entry(no_name_frame_3, textvariable=self.client_duration,width=5)).pack(side=tk.LEFT)
        tk.Label(no_name_frame_3, text="秒").pack(side=tk.LEFT)
        tk.Label(no_name_frame_3, text="线程").pack(side=tk.LEFT)
        self.client_num = tk.StringVar(value="12")
        f(tk.Entry(no_name_frame_3, textvariable=self.client_num,width=5)).pack(side=tk.LEFT)
        no_name_frame_3.pack()

        no_name_frame_4 = tk.Frame(client_frame_common)
        self.use_udp = tk.BooleanVar(value=False)
        f(tk.Checkbutton(no_name_frame_4, text="UDP", variable=self.use_udp)).pack(side=tk.LEFT)
        tk.Label(no_name_frame_4, text="带宽").pack(side=tk.LEFT)
        self.client_bandwidth = tk.StringVar(value="")
        f(tk.Entry(no_name_frame_4, textvariable=self.client_bandwidth,width=8)).pack(side=tk.LEFT)
        no_name_frame_4.pack()

        options = ["上行", "下行"]
        self.dir_option = tk.StringVar()
        self.dir_option.set(options[0])
        dir_frame = tk.Frame(client_frame_common)
        for option in options:
            radio_button = f(tk.Radiobutton(dir_frame, text=option, value=option, variable=self.dir_option))
            radio_button.pack(side=tk.LEFT)
        dir_frame.pack()

        no_name_frame_1 = tk.Frame(client_frame_common)
        self.repeat_count = tk.StringVar(value="1")
        tk.Label(no_name_frame_1, text="重复次数").pack(side=tk.LEFT)
        f(tk.Entry(no_name_frame_1, textvariable=self.repeat_count,width=5)).pack(side=tk.LEFT)
        self.display_only = tk.BooleanVar(value=False)
        f(tk.Checkbutton(no_name_frame_1, text="预热", variable=self.display_only)).pack(side=tk.LEFT)
        no_name_frame_1.pack()
        
        button_frame = tk.Frame(client_frame_common)
        start_button = tk.Button(button_frame, text="开始", command=self.start_client_button_clicked)
        start_button.pack(side=tk.LEFT)
        stop_button = tk.Button(button_frame, text="停止", command=self.stop_client_button_clicked)
        stop_button.pack(side=tk.LEFT)
        self.count_label = tk.Label(button_frame, text="第0次")
        self.count_label.pack(side=tk.LEFT)
        copy_button = tk.Button(button_frame, text="复制选中", command=self.copy_selected_to_clipboard)
        copy_button.pack(side=tk.LEFT)
        clear_button = tk.Button(button_frame, text="清空历史", command=self.clear_tree)
        clear_button.pack(side=tk.LEFT)
        button_frame.pack()

        client_frame_common.pack()
        client_frame.pack(side=tk.LEFT)

        frame1.pack()
        output_text = tk.Text(self.root, wrap="word", height=12, width=50)
        output_text.pack(expand=True, fill=tk.X)
        self.not_stdout = StdoutRedirector(output_text)

        columns = ("时间","方向","Mb/秒",)
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill=tk.X)


        pass

    def start_client_button_clicked(self,):
        if self.client_obj is not None:
            self.not_stdout.write("Already running!\n")
            return
        self.not_stdout.write("正在开始\n")
        if self.use_udp.get():
            self.client_obj = iperf.ClientUdp(
                server_ip=self.client_ip.get(),
                server_port=self.client_port.get(),
                duration=self.client_duration.get(),
                num_streams=self.client_num.get(),
                reverse=self.dir_option.get() == '下行',
                bandwidth=self.client_bandwidth.get(),
                output=self.not_stdout,
                capture_output=not self.display_only.get(),
            )
        else:
            self.client_obj = iperf.ClientTcp(
                server_ip=self.client_ip.get(),
                server_port=self.client_port.get(),
                duration=self.client_duration.get(),
                num_streams=self.client_num.get(),
                reverse=self.dir_option.get() == '下行',
                bandwidth=self.client_bandwidth.get(),
                output=self.not_stdout,
                capture_output=not self.display_only.get(),
            )
        repeat_cnt = self.repeat_count.get()
        try:
            repeat_cnt = int(repeat_cnt)
        except ValueError:
            repeat_cnt = -1
        self.client_obj.add_recorder(Result2Display(self.tree))
        self.client_obj.add_recorder(StopCounter(
            callback_each=lambda cnt:self.count_label.config(text=f"第{cnt}次"),
            callback_final=self.stop_client_button_clicked,
            target_cnt=repeat_cnt
            ))
        self.client_obj = common.Sequence(self.client_obj, common.timedelta(seconds=0.5))
        self.client_obj.start()
        global IS_RUNNING
        IS_RUNNING = True
        self.disable_when_running()

    def stop_client_button_clicked(self,):
        if self.client_obj is not None:
            self.not_stdout.write("正在停止\n")
            self.client_obj.stop()
            self.client_obj = None
            global IS_RUNNING
            IS_RUNNING = False
            self.enable_when_stopped()
        else:
            self.not_stdout.write("已停止!\n")
        
    def disable_when_running(self, ):
        for i in self.widgets:
            i.configure(state=tk.DISABLED)

    def enable_when_stopped(self, ):
        for i in self.widgets:
            i.configure(state=tk.NORMAL)

    def copy_selected_to_clipboard(self,):
        selected_items: tuple[str, ...] = self.tree.selection()
        if selected_items:
            selected_data = []
            for item in selected_items:
                row = self.tree.item(item)['values'][-1:]
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
    IperfClient(root)

if __name__ == "__main__":
    root = tk.Tk()
    app = IperfClient(root)
    root.mainloop()
