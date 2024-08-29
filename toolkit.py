import tkinter as tk
import subprocess

def run_script_1():
    subprocess.run(["python", "server.py"])

def run_script_2():
    subprocess.run(["python", "script2.py"])

def run_script_3():
    subprocess.run(["python", "server.py"])

# Create the main window
root = tk.Tk()
root.title("Fancy Script Runner")

# Set a larger window size
root.geometry("600x400")
root.configure(bg="#282c34")  # Dark background

# Create a title label with fancy font and color
title_label = tk.Label(root, text="Select a Script to Run", font=("Helvetica", 24, "bold"), fg="#61dafb", bg="#282c34")
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

# Create and place buttons with fancy styles
button1 = tk.Button(button_frame, text="耐测王", command=run_script_1, **button_style)
button1.grid(row=0, column=0, padx=20, pady=10)

button2 = tk.Button(button_frame, text="Run Script 2", command=run_script_2, **button_style)
button2.grid(row=0, column=1, padx=20, pady=10)

button3 = tk.Button(button_frame, text="Run Script 3", command=run_script_3, **button_style)
button3.grid(row=1, column=0, columnspan=2, pady=10)

# Create a footer label
footer_label = tk.Label(root, text="© 2024 My Script Runner", font=("Helvetica", 12), fg="#888", bg="#282c34")
footer_label.pack(side="bottom", pady=20)

# Start the GUI event loop
root.mainloop()
