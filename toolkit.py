import tkinter as tk
from tkinter import messagebox
import threading
import server_speed
import server_live
import server_contest
import tkinter.font as tkFont
from PIL import Image, ImageTk
import subprocess
import os

# import modules and not use it
# Since we use exec 🥰🥰
import gui_speed_recorder  # noqa: F401
import gui_live_recorder  # noqa: F401
import gui_pings  # noqa: F401
import gui_iperf_server  # noqa: F401
import gui_iperf_client  # noqa: F401
import gui_reset_device  # noqa: F401
# from ctypes import windll
# import importlib


# clicking many times, only one program(same function) is running
class Lazy:
    def __init__(self, f, default):
        self.wait = True  # status if last one is finished
        self.f = f
        self.default = default

    def run(self):
        if self.wait:
            self.wait = False
            self.f()
        self.default()


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("飞猫品控集成测试工具平台")
        self.current_module = None  # Track the current module
        self.create_widgets()  # create pages

    def create_widgets(self):
        # sidebar
        self.sidebar = tk.Frame(self.root, bg="white")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # sub sidebar(第二级菜单栏)
        self.sub_sidebar = tk.Frame(self.root, bg="lightyellow")
        self.sub_sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sub_sidebar_visible = True
        self.current_category = None

        self.load_image()
        self.image_label.pack(side=tk.TOP, pady=10)

        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.buttons = {
            "网络体验稳定性": "gui_live_recorder",
            "网络速率稳定性": "gui_speed_recorder",
        }
        button_font = tkFont.Font(family="Comic Sans MS", size=13, weight="bold")

        for text, module_name in self.buttons.items():
            button = tk.Button(
                self.sidebar,
                text=text,
                command=lambda m=module_name: self.check_and_show_page(m),
                width=15,
                height=0,
                font=button_font,
                bg="#3389ff",
                fg="white",
            )
            button.pack(pady=15, fill=tk.X)

        button7 = tk.Button(
            self.sidebar,
            text="体验&网速数据统计",
            command=lambda c="体验&网速数据统计": self.toggle_category(c),
            width=15,
            height=0,
            font=button_font,
            bg="#3389ff",
            fg="white",
        )
        button7.pack(pady=15, fill=tk.X)

        button1 = tk.Button(
            self.sidebar,
            text="iperf灌包",
            command=lambda c="iperf": self.toggle_category(c),
            width=15,
            height=0,
            font=button_font,
            bg="#3389ff",
            fg="white",
        )
        button1.pack(pady=15, fill=tk.X)

        button7 = tk.Button(
            self.sidebar,
            text="网络禁用/开启",
            command=lambda c="网络工具": self.toggle_category(c),
            width=15,
            height=0,
            font=button_font,
            bg="#3389ff",
            fg="white",
        )
        button7.pack(pady=15, fill=tk.X)

        button7 = tk.Button(
            self.sidebar,
            text="辅助工具",
            command=lambda c="辅助工具": self.toggle_category(c),
            width=15,
            height=0,
            font=button_font,
            bg="#3389ff",
            fg="white",
        )
        button7.pack(pady=15, fill=tk.X)

    # let the sub meau hide after click twice
    def toggle_category(self, category):
        if self.sub_sidebar_visible and self.current_category == category:
            self.hide_submenu()
        else:
            self.show_category(category)

    # show the sub_meau when select a button on the sidebar
    def show_category(self, category):
        if self.current_module and self.current_module.IS_RUNNING:
            messagebox.showwarning("任在运行", "请先结束当前任务")
            return  # After showing the warning, return and do not switch the page
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.content_frame.destroy()
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        def thread_with_daemon(target):
            h = threading.Thread(target=target)
            h.setDaemon(True)  # 守护线程，确保主线程退出时所有子线程也推出
            return h

        self.current_category = category  # Set the current category

        # 三个网站的实例化，带上lazy类即可实现非常牛逼的功能
        server_live_obj = Lazy(
            lambda: thread_with_daemon(target=server_live.main).start(),
            lambda: threading.Thread(target=server_live.open_browser).start(),
        )

        server_speed_obj = Lazy(
            lambda: thread_with_daemon(target=server_speed.main).start(),
            lambda: threading.Thread(target=server_speed.open_browser).start(),
        )

        server_contest_obj = Lazy(
            lambda: thread_with_daemon(target=server_contest.main).start(),
            lambda: threading.Thread(target=server_contest.open_browser).start(),
        )

        # Repack the sub_sidebar if it was hidden
        if not self.sub_sidebar_visible:
            self.sub_sidebar.pack(side=tk.LEFT, fill=tk.Y)
            self.sub_sidebar_visible = True

        for widget in self.sub_sidebar.winfo_children():
            widget.destroy()

        if category == "网络工具":
            buttons = [
                ("Wi-Fi一键遗忘", self.ask_to_forget),
                ("启用以太网", enable_ethernet),
                ("禁用以太网", disable_ethernet),
            ]
        elif category == "辅助工具":
            buttons = [
                ("BandwidthMeter", band_pro),
                ("Ping包", ping_exe),
                ("Ping三网", self.multi_pings),
                ("设备重启", self.restart_device),
            ]
        elif category == "体验&网速数据统计":
            buttons = [
                ("直播数据统计", server_live_obj.run),
                ("测速数据统计", server_speed_obj.run),
                ("多设备\n直播数据对比", server_contest_obj.run),
            ]
        elif category == "iperf":
            buttons = [
                ("服务端", self.iperf_server),
                ("客户端", self.iperf_client),
            ]

        for button_text, func in buttons:
            # 子菜单按钮
            btn = tk.Button(
                self.sub_sidebar,
                text=button_text,
                width=20,
                height=2,
                command=lambda f=func: self.run_and_hide(f),
            )
            btn.pack(pady=10, fill=tk.X)

    # pop out warning page if the current page is still running.
    def check_and_show_page(self, module_name):
        if self.current_module and self.current_module.IS_RUNNING:
            messagebox.showwarning("任在运行", "请先结束当前任务")
            return  # After showing the warning, return and do not switch the page
        self.show_page(module_name)
        self.hide_submenu()

    # show GUI on the right side when select function
    def show_page(self, module_name):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # module = importlib.import_module(module_name)
        # self.current_module = module  # Track the currently running module
        exec(f"{module_name}.main(self.content_frame)")

    def run_and_hide(self, func):
        func()
        self.hide_submenu()

    def hide_submenu(self):
        self.sub_sidebar.pack_forget()
        self.sub_sidebar_visible = False

    def load_image(self):
        image = Image.open("flymodem.png")
        image = image.resize((100, 100), Image.LANCZOS)
        self.image = ImageTk.PhotoImage(image)
        self.image_label = tk.Label(self.sidebar, image=self.image, bg="white")

    def iperf_server(self):
        self.check_and_show_page("gui_iperf_server")

    def iperf_client(self):
        self.check_and_show_page("gui_iperf_client")

    def multi_pings(self):
        self.check_and_show_page("gui_pings")

    def restart_device(self):
        self.check_and_show_page("gui_reset_device")

    def ask_to_forget(self):
        response = messagebox.askquestion(
            "遗忘网络", "您保存的Wi-Fi网络将被删除\n请确认"
        )
        if response == "yes":
            forget_networks()


def band_pro():
    os.system(r'start BandwidthMeterPro\BWMeterPro.exe"')


def ping_exe():
    os.system(r"start ping_exe.exe")


# 让你的网络一去不复返
def forget_networks():
    os.system("netsh wlan delete profile name=* i=*")


def disable_ethernet():
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "./Operate-Ethernet.ps1",
            "-Action",
            "Disable",
        ]
    )
    # command = 'Get-NetAdapter | Where-Object { $_.Name -like "Ethernet *" } | Disable-NetAdapter -Confirm:$false'
    # subprocess.run(['powershell', '-Command', command])
    # command = 'Get-NetAdapter | Where-Object { $_.Name -like "以太网 *" } | Disable-NetAdapter -Confirm:$false'
    # subprocess.run(['powershell', '-Command', command])


def enable_ethernet():
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "./Operate-Ethernet.ps1",
            "-Action",
            "Enable",
        ]
    )
    # command = 'Get-NetAdapter | Where-Object { $_.Name -like "Ethernet *" } | Enable-NetAdapter -Confirm:$false'
    # subprocess.run(['powershell', '-Command', command])
    # command = 'Get-NetAdapter | Where-Object { $_.Name -like "以太网 *" } | Enable-NetAdapter -Confirm:$false'
    # subprocess.run(['powershell', '-Command', command])


# 没用的玩意儿
def stop_exe():
    os.system("taskkill /f /im toolkit.exe")


if __name__ == "__main__":
    # improve for high DPI displays but with bugs
    # windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    root.iconbitmap("flymodem.ico")
    root.state("zoomed")
    app = MainApp(root)
    root.mainloop()


# 3%的概率删除系统盘
