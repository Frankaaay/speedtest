import tkinter as tk
import importlib

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("飞猫智联网络稳定性测试")
        self.create_widgets()

    def create_widgets(self):
        # Frame for buttons
        self.button_frame = tk.Frame(self.root, width=1000, bg='lightgrey')
        self.button_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Frame for content
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Add buttons
        self.buttons = {
            'Live Recorder': 'gui_stability_recorder',
            'Speed Test': 'gui_speed_recorder',
            # Add other pages as needed
        }
        
        for text, module_name in self.buttons.items():
            button = tk.Button(self.button_frame, text=text, command=lambda m=module_name: self.show_page(m))
            button.pack(pady=10)

    def show_page(self, module_name):
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Import and display new page
        module = importlib.import_module(module_name)
        module.main(self.content_frame)

    def clear_current_page(self):
        if self.current_page is not None:
            if hasattr(self.current_page, 'stop'):  # Check if the page has a stop method to clean up
                self.current_page.stop()  # Stop any processes or threads in the current page
            for widget in self.content_frame.winfo_children():
                widget.destroy()
        self.current_page = None

if __name__ == "__main__":
    root = tk.Tk()
    root.state("zoomed")
    app = MainApp(root)
    root.mainloop()
