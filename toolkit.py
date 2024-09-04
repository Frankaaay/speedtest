import tkinter as tk
import importlib
import threading
import server_speed
import server_live
import tkinter.font as tkFont
from PIL import Image, ImageTk
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
        self.button_frame = tk.Frame(self.root, width=900, bg='dodgerblue')  # Adjust width as needed
        self.button_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Load and display image
        self.load_image()
        self.image_label.pack(side=tk.TOP, pady=10)  # Add image above the buttons
        
        # Frame for content
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Add buttons
        self.buttons = {
            '直播稳定性': 'gui_stability_recorder',
            '间隔测速': 'gui_speed_recorder',
       
        }
        button_font = tkFont.Font(family="Helvetica", size=15, weight="bold")

        for text, module_name in self.buttons.items():
            button = tk.Button(self.button_frame, text=text, command=lambda m=module_name: self.show_page(m),
                               width=15, height=2, font = button_font)
            
            button.pack(pady=15, fill=tk.X)  # `fill=tk.X` ensures buttons stretch across the width
        

        server_live_obj = Lazy(lambda :threading.Thread(target=server_live.main).start(),
                               lambda :threading.Thread(target=server_live.open_browser).start())
        button3 = tk.Button(self.button_frame, text="直播数据整理", command = server_live_obj.run,
                            width=15, height=2, font = button_font)
        button3.pack(pady=15, fill=tk.X)

        server_speed_obj = Lazy(lambda :threading.Thread(target=server_speed.main).start(),
                                lambda :threading.Thread(target=server_speed.open_browser).start())
        button4 = tk.Button(self.button_frame, text="测速数据整理", command=server_speed_obj.run, 
                            width=15, height=2, font = button_font)
        button4.pack(pady=15, fill=tk.X)

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
        self.image_label = tk.Label(self.button_frame, image=self.image, bg='lightgrey')


# if __name__ == "__main__":
#     style = Style(theme = "darkly")
#     root = style.master
#     # root = tk.Tk()
#     root.state("zoomed")
#     app = MainApp(root)
#     root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    root.state("zoomed")
    app = MainApp(root)
    root.mainloop()
