import tkinter as tk
from tkinter import messagebox
import importlib
import threading
import server_speed
import server_live
import server_contest
import tkinter.font as tkFont
from PIL import Image, ImageTk
import subprocess
import gui_iperf3
import gui_speed_recorder
import gui_stability_recorder

import os

class Lazy:
    def __init__(self, f, default):
        self.wait = True
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
        self.root.title("飞猫智联")
        self.current_module = None  # Track the current module
        self.create_widgets()

    def create_widgets(self):
        self.sidebar = tk.Frame(self.root, width=900, bg='dodgerblue')
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.sub_sidebar = tk.Frame(self.root, bg='lightyellow')
        self.sub_sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sub_sidebar_visible = True
        self.current_category = None

        self.load_image()
        self.image_label.pack(side=tk.TOP, pady=10)

        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.buttons = {
            '网络体验稳定性': 'gui_stability_recorder',
            '网络速率稳定性': 'gui_speed_recorder',
            'iperf3': 'gui_iperf3'
        }
        button_font = tkFont.Font(family="Helvetica", size=15, weight="bold")

        for text, module_name in self.buttons.items():
            button = tk.Button(self.sidebar, text=text, command=lambda m=module_name: self.check_and_show_page(m),
                               width=15, height=1, font=button_font)
            button.pack(pady=15, fill=tk.X)

        button7 = tk.Button(self.sidebar, text="数据整理", command=lambda c="数据整理": self.toggle_category(c),
                            width=15, height=2, font=button_font)
        button7.pack(pady=15, fill=tk.X)

        button7 = tk.Button(self.sidebar, text="网络工具", command=lambda c="网络工具": self.toggle_category(c),
                            width=15, height=2, font=button_font)
        button7.pack(pady=15, fill=tk.X)

        button7 = tk.Button(self.sidebar, text="辅助工具", command=lambda c="辅助工具": self.toggle_category(c),
                            width=15, height=2, font=button_font)
        button7.pack(pady=15, fill=tk.X)

    def toggle_category(self, category):
        if self.sub_sidebar_visible and self.current_category == category:
            self.hide_submenu()
        else:
            self.show_category(category)

    def show_category(self, category):
        self.current_category = category  # Set the current category
        server_live_obj = Lazy(lambda :threading.Thread(target=server_live.main).start(),
                               lambda :threading.Thread(target=server_live.open_browser).start())
        
        server_speed_obj = Lazy(lambda :threading.Thread(target=server_speed.main).start(),
                                lambda :threading.Thread(target=server_speed.open_browser).start())
        
        server_contest_obj = Lazy(lambda :threading.Thread(target=server_contest.main).start(),
                                lambda :threading.Thread(target=server_contest.open_browser).start())

        # Repack the sub_sidebar if it was hidden
        if not self.sub_sidebar_visible:
            self.sub_sidebar.pack(side=tk.LEFT, fill=tk.Y)
            self.sub_sidebar_visible = True

        for widget in self.sub_sidebar.winfo_children():
            widget.destroy()

        if category == "网络工具":
            buttons = [("一键遗忘", forget_networks),
                       ("启用以太网", enable_ethernet),
                       ("禁用以太网", disable_ethernet)]
        elif category == "辅助工具":
            buttons = [("BandwidthMeter", band_pro)]
        elif category == "数据整理":
            buttons = [("ping数据整理", server_live_obj.run),
                       ("测速数据整理", server_speed_obj.run),
                       ("ping数据对比", server_contest_obj.run)]

        for button_text, func in buttons:
            btn = tk.Button(self.sub_sidebar, text=button_text, width=15, height=2,
                            command=lambda f=func: self.run_and_hide(f))
            btn.pack(pady=15, fill=tk.X)

    def check_and_show_page(self, module_name):
        if self.current_module and self.current_module.IS_RUNNING:
            messagebox.showwarning("Warning", "A program is still running. Please stop it before switching.")
            return  # After showing the warning, return and do not switch the page
        self.show_page(module_name)

    def show_page(self, module_name):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # if module_name == "graph":
        #     module.main()

        module = importlib.import_module(module_name)
        self.current_module = module  # Track the currently running module
        module.main(self.content_frame)

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
        self.image_label = tk.Label(self.sidebar, image=self.image, bg='lightgrey')


def band_pro():
    os.system(r'start BandwidthMeterPro\BWMeterPro.exe"')


def forget_networks():
    os.system('netsh wlan delete profile name=FM* i=*')
    os.system('netsh wlan delete profile name=ZTE* i=*')


def disable_ethernet():
    command = 'Get-NetAdapter | Where-Object { $_.Name -like "Ethernet *" } | Disable-NetAdapter -Confirm:$false'
    subprocess.run(['powershell', '-Command', command], shell=True)


def enable_ethernet():
    command = 'Get-NetAdapter | Where-Object { $_.Name -like "Ethernet *" } | Enable-NetAdapter -Confirm:$false'
    subprocess.run(['powershell', '-Command', command], shell=True)


def stop_exe():
    os.system("taskkill /f /im toolkit.exe")


if __name__ == "__main__":
    root = tk.Tk()
    root.state("zoomed")
    app = MainApp(root)
    root.mainloop()
    root.protocol("WM_DELETE_WINDOW", stop_exe)

#3%的概率删除系统盘