import tkinter as tk
import threading
from PIL import Image, ImageTk
import server_live
import server_speed
import gui_speed_recorder
import gui_stability_recorder
import random

# Function to run a script's main function in a new thread
def run_script(func):
    thread = threading.Thread(target=func)
    thread.start()



#5% chance to open mysterious page
if  random.randint(0, 99) <= 5:
    # Create the main window
    root = tk.Tk()
    root.title("Flymodem No.1")
    root.geometry("1000x800")

    # Load the background image
    background_image = Image.open("splash.png")
    background_image = background_image.resize((1000, 800), Image.LANCZOS)  # Resize image to fit the window
    background_photo = ImageTk.PhotoImage(background_image)

    # Create a Canvas to hold the background image
    canvas = tk.Canvas(root, width=1000, height=800)
    canvas.pack(fill="both", expand=True)

    # Add the background image to the canvas
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    # Create a title label with fancy font and color
    title_label = tk.Label(root, text="飞猫智联，启动！", font=("Helvetica", 24, "bold"), fg="#61dafb", bg="#282c34")
    title_label_window = canvas.create_window(500, 50, window=title_label)  # Place title in the center

    # Create a frame to hold buttons in the center with padding and background
    button_frame = tk.Frame(root, bg="#1c1f26", bd=5, relief="ridge")
    button_frame_window = canvas.create_window(500, 350, window=button_frame)  # Adjust this y-coordinate to move the buttons up

    # Define button styles
    button_style = {
        "font": ("Helvetica", 16),
        "bg": "#61dafb",
        "fg": "white",
        "activebackground": "#1f7aaf",
        "activeforeground": "white",
        "width": 20,
        "height": 2,
        "relief": "raised",
        "borderwidth": 4,
    }

    def open_new_window(f):
        new_window = tk.Toplevel(root)
        f(new_window)
        new_window.mainloop()

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

    # Create and place buttons with fancy styles
    button1 = tk.Button(button_frame, text="间隔测速", command=lambda :threading.Thread(target=open_new_window,args=(gui_speed_recorder.main,)).start(), **button_style)
    button1.grid(row=0, column=0, padx=20, pady=10)

    button2 = tk.Button(button_frame, text="直播数据生成", command=lambda :threading.Thread(target=open_new_window,args=(gui_stability_recorder.main,)).start(), **button_style)
    button2.grid(row=0, column=1, padx=20, pady=10)

    server_live_obj = Lazy(lambda :threading.Thread(target=server_live.main).start(),lambda :threading.Thread(target=server_live.open_browser).start())
    button3 = tk.Button(button_frame, text="直播数据整理", command = server_live_obj.run, **button_style)
    button3.grid(row=1, column=0, padx=20, pady=10)

    server_speed_obj = Lazy(lambda :threading.Thread(target=server_speed.main).start(),lambda :threading.Thread(target=server_speed.open_browser).start())
    button4 = tk.Button(button_frame, text="测速数据整理", command = server_speed_obj.run, **button_style)
    button4.grid(row=1, column=1, padx=20, pady=10)

    # Create a footer label
    footer_label = tk.Label(root, text="© 2024 Flymodem", font=("Helvetica", 12), fg="#888", bg="#282c34")
    footer_label_window = canvas.create_window(500, 750, window=footer_label)  # Place footer at the bottom center
else:
    # Create the main window
    root = tk.Tk()
    root.title("Flymodem No.1")
    root.geometry("1000x800")
    root.configure(bg="#282c34")

    # Create a title label with fancy font and color
    title_label = tk.Label(root, text="飞猫智联，启动！", font=("Helvetica", 24, "bold"), fg="#61dafb", bg="#282c34")
    title_label.pack(pady=20)

    # Create a frame to hold buttons with padding and background
    button_frame = tk.Frame(root, bg="#282c34")
    button_frame.pack(pady=20)

    # Define button styles
    button_style = {
        "font": ("Helvetica", 16),
        "bg": "#61dafb",
        "fg": "white",
        "activebackground": "#1f7aaf",
        "activeforeground": "white",
        "width": 20,
        "height": 2,
        "relief": "raised",
        "borderwidth": 4,
    }

    def open_new_window(f):
        new_window = tk.Toplevel(root)
        f(new_window)
        new_window.mainloop()

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

    # Create and place buttons with fancy styles
    button1 = tk.Button(button_frame, text="间隔测速", command=lambda :threading.Thread(target=open_new_window,args=(gui_speed_recorder.main,)).start(), **button_style)
    button1.grid(row=0, column=0, padx=20, pady=10)

    button2 = tk.Button(button_frame, text="直播数据生成", command=lambda :threading.Thread(target=open_new_window,args=(gui_stability_recorder.main,)).start(), **button_style)
    button2.grid(row=0, column=1, padx=20, pady=10)

    server_live_obj = Lazy(lambda :threading.Thread(target=server_live.main).start(),lambda :threading.Thread(target=server_live.open_browser).start())
    button3 = tk.Button(button_frame, text="直播数据整理", command = server_live_obj.run, **button_style)
    button3.grid(row=1, column=0, padx=20, pady=10)

    server_speed_obj = Lazy(lambda :threading.Thread(target=server_speed.main).start(),lambda :threading.Thread(target=server_speed.open_browser).start())
    button4 = tk.Button(button_frame, text="测速数据整理", command = server_speed_obj.run, **button_style)
    button4.grid(row=1, column=1, padx=20, pady=10)

    # Create a footer label
    footer_label = tk.Label(root, text="© 2024 Flymodem", font=("Helvetica", 12), fg="#888", bg="#282c34")
    footer_label.pack(side="bottom", pady=20)



# Start the GUI event loop
root.mainloop()
