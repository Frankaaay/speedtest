import tkinter as tk
from tkinter import ttk
import subprocess
import threading

class Iperf3TestApp:
    def __init__(self, root):
        try:
            root.title("Iperf Test App")
        except:
            pass

        self.root = root

        # Initialize variables
        self.ip_base = "192.168."
        self.ip_suffix1 = ""
        self.ip_suffix2 = ""
        self.working_directory = r"D:\fly\iperf-3.1.3-win64"  # Default directory
        self.num_runs = 5  # Default number of runs
        self.duration = 30  # Default duration in seconds
        self.process = None
        self.stop_event = threading.Event()

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # IP address input
        ttk.Label(self.root, text="192.168.").grid(column=0, row=0, padx=10, pady=5)
        self.ip_suffix1_var = tk.StringVar(value=self.ip_suffix1)
        ttk.Entry(self.root, textvariable=self.ip_suffix1_var).grid(column=1, row=0, padx=10, pady=5)

        # Number of runs input
        ttk.Label(self.root, text="Number of Runs:").grid(column=0, row=2, padx=10, pady=5)
        self.num_runs_var = tk.IntVar(value=self.num_runs)
        ttk.Entry(self.root, textvariable=self.num_runs_var).grid(column=1, row=2, padx=10, pady=5)

        # Duration input
        ttk.Label(self.root, text="Duration (seconds):").grid(column=0, row=3, padx=10, pady=5)
        self.duration_var = tk.IntVar(value=self.duration)
        ttk.Entry(self.root, textvariable=self.duration_var).grid(column=1, row=3, padx=10, pady=5)

        self.download = tk.BooleanVar(value=False)
        tk.Checkbutton(self.root, text="Download", variable=self.download).grid(column=1, row=4, padx=10, pady=5)

        # Start and Stop buttons
        ttk.Button(self.root, text="Start", command=self.start_test).grid(column=0, row=5, padx=10, pady=10)
        ttk.Button(self.root, text="Stop", command=self.stop_test).grid(column=1, row=5, padx=10, pady=10)

        # Output display
        ttk.Label(self.root, text="Output:").grid(column=0, row=6, padx=10, pady=5)
        self.output_text = tk.Text(self.root, height=10, width=80, wrap=tk.WORD)
        self.output_text.grid(column=1, row=6, padx=10, pady=5)
        self.output_text.config(state=tk.DISABLED)  # Make it read-only initially

    def start_test(self):
        self.stop_event.clear()
        self.test_thread = threading.Thread(target=self.run_iperf_tests, daemon=True)
        self.test_thread.start()

    def stop_test(self):
        self.stop_event.set()
        if self.process:
            self.process.terminate()
            self.process = None

    def run_iperf_tests(self):
        num_runs = self.num_runs_var.get()
        duration = self.duration_var.get()  # Get the duration from user input
        for run_num in range(num_runs):
            if self.stop_event.is_set():
                break
            ip_address = f"{self.ip_base}{self.ip_suffix1_var.get()}"
            
            if self.download.get():
                self.process = subprocess.Popen(
                    f'Iperf3 -c {ip_address} -t {duration} -P 12 -R',  # Use the user-defined duration
                    shell=True,
                    cwd=self.working_directory,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                self.process = subprocess.Popen(
                    f'Iperf3 -c {ip_address} -t {duration} -P 12',  # Use the user-defined duration
                    shell=True,
                    cwd=self.working_directory,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )          
            
            output_lines = []
            while True:
                output = self.process.stdout.readline()
                if output == "" and self.process.poll() is not None:
                    break
                if output:
                    output_lines.append(output.strip())

            # Get the third line from the last
            if len(output_lines) >= 3:
                third_line_from_last = output_lines[-3]
                self.update_output_text(f"Run {run_num + 1}: {third_line_from_last}")

            self.process.wait()
            self.process = None

    def update_output_text(self, text):
        # Update the Text widget in the main thread
        self.root.after(0, self._update_text_widget, text)

    def _update_text_widget(self, text):
        self.output_text.config(state=tk.NORMAL)  # Enable editing
        self.output_text.insert(tk.END, text + "\n")  # Insert new text at the end
        self.output_text.config(state=tk.DISABLED)  # Make it read-only

def main(root:tk.Tk):
    Iperf3TestApp(root)

if __name__ == "__main__":
    root = tk.Tk()
    app = Iperf3TestApp(root)
    root.mainloop()
