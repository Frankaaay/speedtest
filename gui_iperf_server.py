import tkinter as tk
from tkinter import ttk
import subprocess
import iperf
import utils

IS_RUNNING : int = 0

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

class IperfServer:
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
        self.create_widgets()


    def create_widgets(self):
        frame1 = ttk.Frame(self.root)
        server_frame = tk.Frame(frame1)

        tk.Label(server_frame, text="-s 服务端 端口").pack()
        self.server_ports = tk.Listbox(server_frame, selectmode=tk.SINGLE, width=20, height=9)
        for item in ['5201','5202']:
            self.server_ports.insert(tk.END, item)
        self.server_ports.pack()

        no_name_frame_1 = ttk.Frame(server_frame)
        self.add_port_entry = tk.Entry(no_name_frame_1, width=8)
        self.add_port_entry.pack(side=tk.LEFT)
        add_button = tk.Button(no_name_frame_1, text="添加", command=self.add_port)
        add_button.pack(side=tk.LEFT)
        delete_button = tk.Button(no_name_frame_1, text="删除", command=self.delete_port)
        delete_button.pack(side=tk.LEFT)
        no_name_frame_1.pack()

        button_frame = ttk.Frame(server_frame)
        start_button = tk.Button(button_frame, text="开始", command=self.start_server_button_clicked)
        start_button.pack(side=tk.LEFT)
        stop_button = tk.Button(button_frame, text="停止", command=self.stop_server_button_clicked)
        stop_button.pack(side=tk.LEFT)
        button_frame.pack()
        server_frame.pack(side=tk.LEFT)
        frame1.pack()
        output_text = tk.Text(self.root, wrap="word", height=20, width=80)
        output_text.pack(expand=True, fill=tk.X)
        self.not_stdout = StdoutRedirector(output_text)

        pass
    
    def start_server_button_clicked(self,):
        if self.server_obj is not None:
            self.not_stdout.write("服务端已在运行!\n")
            return
        self.not_stdout.write("开启服务端\n")
        self.server_obj = iperf.Servers(self.server_ports.get(0, tk.END), self.not_stdout)
        self.server_obj.start()
        global IS_RUNNING
        IS_RUNNING += 1

    def stop_server_button_clicked(self,):
        if self.server_obj is not None:
            self.not_stdout.write("Stopping\n")
            self.server_obj.stop()
            self.server_obj = None
            global IS_RUNNING
            IS_RUNNING -= 1
        else:
            self.not_stdout.write("Not running!\n")

    def add_port(self,) -> None:
        item = self.add_port_entry.get()
        if item:
            self.server_ports.insert(tk.END, item)
            self.add_port_entry.delete(0, tk.END)
        else:
            self.not_stdout.write("输入要添加的网站\n")
            pass
            # messagebox.showwarning("警告", "请输入要添加的项！")


    def delete_port(self,):
        selected_index = self.server_ports.curselection()
        if selected_index:
            self.server_ports.delete(selected_index)
        else:
            self.not_stdout.write("选择要删除的网站\n")
            pass
            # messagebox.showwarning("警告", "请选择要删除的项！")

def main(root:tk.Tk):
    IperfServer(root)

if __name__ == "__main__":
    root = tk.Tk()
    app = IperfServer(root)
    root.mainloop()
