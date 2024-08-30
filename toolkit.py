import tkinter as tk
import threading
import server
import gui_speed_recorder
import gui_stability_recorder

# Function to run a script's main function in a new thread
def run_script(func):
    thread = threading.Thread(target=func)
    thread.start()

# Create the main window
root = tk.Tk()
root.title("大力王")
root.geometry("1000x800")
root.configure(bg="#282c34")

# Create a title label with fancy font and color
title_label = tk.Label(root, text="请选择你的王", font=("Helvetica", 24, "bold"), fg="#61dafb", bg="#282c34")
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

# Create and place buttons with fancy styles
button1 = tk.Button(button_frame, text="耐测王", command=lambda :threading.Thread(target=open_new_window,args=(gui_speed_recorder.main,)).start(), **button_style)
button1.grid(row=0, column=0, padx=20, pady=10)

button2 = tk.Button(button_frame, text="耐看王", command=lambda :threading.Thread(target=open_new_window,args=(gui_stability_recorder.main,)).start(), **button_style)
button2.grid(row=0, column=1, padx=20, pady=10)

button3 = tk.Button(button_frame, text="金山画王", command=lambda :threading.Thread(target=server.main).start(), **button_style)
button3.grid(row=1, column=0, columnspan=2, pady=10)

# Create a footer label
footer_label = tk.Label(root, text="© 2024 Flymodem", font=("Helvetica", 12), fg="#888", bg="#282c34")
footer_label.pack(side="bottom", pady=20)

# Start the GUI event loop
root.mainloop()
