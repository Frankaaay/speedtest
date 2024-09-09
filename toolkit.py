import tkinter as tk
import importlib
import threading
import server_speed
import server_live
import server_contest
import tkinter.font as tkFont
from PIL import Image, ImageTk
import subprocess
import sys
import ctypes
import gui_iperf3
import gui_speed_recorder
import gui_stability_recorder

import os
# from ttkbootstrap import Style

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
        self.root.title("飞猫智联网络稳定性测试")
        self.create_widgets()

    def create_widgets(self):
        # Frame for buttons with increased width
        self.sidebar = tk.Frame(self.root, width=900, bg='dodgerblue')  # Adjust width as needed
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Frame for the secondary sidebar (to show more buttons)
        self.sub_sidebar = tk.Frame(self.root, bg='red')
        self.sub_sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sub_sidebar_visible = True  # Track visibility
        self.current_category = None  # Track which category is selected

        # Load and display image
        self.load_image()
        self.image_label.pack(side=tk.TOP, pady=10)  # Add image above the buttons
        
        # Frame for content
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Add buttons
        self.buttons = {
            '网络体验稳定性': 'gui_stability_recorder',
            '网络速率稳定性': 'gui_speed_recorder',
            'iperf3': 'gui_iperf3'
        }
        button_font = tkFont.Font(family="Helvetica", size=15, weight="bold")

        for text, module_name in self.buttons.items():
            button = tk.Button(self.sidebar, text=text, command=lambda m=module_name: self.show_page(m),
                               width=15, height=1, font = button_font)
            
            button.pack(pady=15, fill=tk.X)  # `fill=tk.X` ensures buttons stretch across the width
    
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
        # If the same category is clicked, toggle visibility
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

        # Clear the sub-sidebar content before showing new buttons
        for widget in self.sub_sidebar.winfo_children():
            widget.destroy()

        # Add buttons with unique functions to the sub-sidebar based on the selected category
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

        # Create and pack new buttons with bound functions
        for button_text, func in buttons:
            btn = tk.Button(self.sub_sidebar, text=button_text, width=15, height=2, 
                            command=lambda f=func: self.run_and_hide(f))  # Bind the function and hide submenu
            btn.pack(pady=15, fill=tk.X)

    def run_and_hide(self, func):
        # Execute the specific function and hide the submenu
        func()
        self.hide_submenu()

    def hide_submenu(self):
        # Hide the sub_sidebar by forgetting it and toggle visibility flag
        self.sub_sidebar.pack_forget()
        self.sub_sidebar_visible = False

    def show_page(self, module_name):
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        if module_name == "graph":
            module.main()
        # Import and display new page
        module = importlib.import_module(module_name)
        module.main(self.content_frame)

    def load_image(self):
        # Load the image
        image = Image.open("flymodem.png")  # Update with your image path
        image = image.resize((100, 100), Image.LANCZOS)  # Use LANCZOS for high-quality downsampling
        self.image = ImageTk.PhotoImage(image)
        
        # Create a label to hold the image
        self.image_label = tk.Label(self.sidebar, image=self.image, bg='lightgrey')

def band_pro():
    os.system(r'start BandwidthMeterPro\BWMeterPro.exe"')

def forget_networks():
    os.system('netsh wlan delete profile name=FM* i=*')
    os.system('netsh wlan delete profile name=ZTE* i=*')
    print("Holy shit! networks are removed successfully!")

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-launch the script as admin if it is not already elevated."""
    if not is_admin():
        # Relaunch the script with admin privileges
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def disable_ethernet():

    """Disable Ethernet adapters using PowerShell commands with admin privileges."""
    command = 'Get-NetAdapter | Where-Object { $_.Name -like "Ethernet *" } | Disable-NetAdapter -Confirm:$false'
    subprocess.run(['powershell', '-Command', command], shell=True)

    command_cn = 'Get-NetAdapter | Where-Object { $_.Name -like "以太网 *" } | Disable-NetAdapter -Confirm:$false'
    subprocess.run(['powershell', '-Command', command_cn], shell=True)

def enable_ethernet():
    """Enable Ethernet adapters using PowerShell commands with admin privileges."""
    command = 'Get-NetAdapter | Where-Object { $_.Name -like "Ethernet *" } | Enable-NetAdapter -Confirm:$false'
    subprocess.run(['powershell', '-Command', command], shell=True)

    command_cn = 'Get-NetAdapter | Where-Object { $_.Name -like "以太网 *" } | Enable-NetAdapter -Confirm:$false'
    subprocess.run(['powershell', '-Command', command_cn], shell=True)


if __name__ == "__main__":
    # run_as_admin()
    root = tk.Tk()
    root.state("zoomed")
    app = MainApp(root)
    root.mainloop()