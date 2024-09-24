import tkinter as tk
from tkinter import ttk
from gui_common import StdoutRedirector
import iperf

x: bool = False


class IperfServer:
    def __init__(self, root):
        try:
            root.title("Iperf 测试")
        except:  # noqa: E722
            pass

        self.root = root
        self.server_ports: tk.Listbox = None
        self.server_obj = None
        self.client_obj = None
        self.add_port_entry = None

        self.widgets = []
        self.create_widgets()

    def create_widgets(self):
        def f(x):
            self.widgets.append(x)
            return x

        frame1 = ttk.Frame(self.root)
        server_frame = tk.Frame(frame1)

        tk.Label(server_frame, text="-s 服务端 端口").pack()
        self.server_ports = tk.Listbox(
            server_frame, selectmode=tk.SINGLE, width=20, height=9
        )
        for item in ["5201", "5202"]:
            self.server_ports.insert(tk.END, item)
        self.server_ports.pack()

        no_name_frame_1 = ttk.Frame(server_frame)
        self.add_port_entry = f(tk.Entry(no_name_frame_1, width=8))
        self.add_port_entry.pack(side=tk.LEFT)
        add_button = f(tk.Button(no_name_frame_1, text="添加", command=self.add_port))
        add_button.pack(side=tk.LEFT)
        delete_button = f(
            tk.Button(no_name_frame_1, text="删除", command=self.delete_port)
        )
        delete_button.pack(side=tk.LEFT)
        no_name_frame_1.pack()

        button_frame = ttk.Frame(server_frame)
        start_button = tk.Button(
            button_frame, text="开始", command=self.start_server_button_clicked
        )
        start_button.pack(side=tk.LEFT)
        stop_button = tk.Button(
            button_frame, text="停止", command=self.stop_server_button_clicked
        )
        stop_button.pack(side=tk.LEFT)
        button_frame.pack()
        server_frame.pack(side=tk.LEFT)
        frame1.pack()
        output_text = tk.Text(self.root, wrap="word", height=20, width=80)
        output_text.pack(expand=True, fill=tk.X)
        self.not_stdout = StdoutRedirector(output_text)

        pass

    def start_server_button_clicked(
        self,
    ):
        if self.server_obj is not None:
            self.not_stdout.write("服务端已在运行!\n")
            return
        self.not_stdout.write("开启服务端\n")
        self.server_obj = iperf.Servers(
            self.server_ports.get(0, tk.END), self.not_stdout
        )
        self.server_obj.start()
        global x
        x = True
        self.disable_when_running()

    def stop_server_button_clicked(
        self,
    ):
        if self.server_obj is not None:
            self.not_stdout.write("正在停止…\n")
            self.server_obj.stop()
            self.server_obj = None
            global x
            x = False
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

    def add_port(
        self,
    ) -> None:
        item = self.add_port_entry.get()
        if item:
            self.server_ports.insert(tk.END, item)
            self.add_port_entry.delete(0, tk.END)
        else:
            self.not_stdout.write("输入要添加的网站\n")
            pass
            # messagebox.showwarning("警告", "请输入要添加的项！")

    def delete_port(
        self,
    ):
        selected_index = self.server_ports.curselection()
        if selected_index:
            self.server_ports.delete(selected_index)
        else:
            self.not_stdout.write("选择要删除的网站\n")
            pass
            # messagebox.showwarning("警告", "请选择要删除的项！")


def main(root: tk.Tk):
    IperfServer(root)


if __name__ == "__main__":
    root = tk.Tk()
    app = IperfServer(root)
    root.mainloop()
