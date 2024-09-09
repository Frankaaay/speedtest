# Importing the necessary libraries
import tkinter as tk
# Defining the function to create radio buttons in submenu
def on_radio_select(submenu_name):
   selected_option = submenu_var[submenu_name].get()
   print(f"{submenu_name}: Selected option - {selected_option}")
    
# Create the main window
root = tk.Tk()
# Give title to the main window
root.title("Cretaing Multiple Submenus with Radiobuttons")

# Set window dimensions
root.geometry("720x250")

# Create a menu bar
menubar = tk.Menu(root)
root.config(menu=menubar)

# Create a dictionary to store StringVars for each submenu
submenu_var = {}

# Create the first submenu
submenu1 = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Menu 1", menu=submenu1)

submenu_var["Menu 1"] = tk.StringVar()

submenu1.add_radiobutton(label="Option A", variable=submenu_var["Menu 1"], value="Option A", command=lambda: on_radio_select("Menu 1"))
submenu1.add_radiobutton(label="Option B", variable=submenu_var["Menu 1"], value="Option B", command=lambda: on_radio_select("Menu 1"))
submenu1.add_radiobutton(label="Option C", variable=submenu_var["Menu 1"], value="Option C", command=lambda: on_radio_select("Menu 1"))

# Create the second submenu
submenu2 = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Menu 2", menu=submenu2)

submenu_var["Menu 2"] = tk.StringVar()

submenu2.add_radiobutton(label="Option X", variable=submenu_var["Menu 2"], value="Option X", command=lambda: on_radio_select("Menu 2"))
submenu2.add_radiobutton(label="Option Y", variable=submenu_var["Menu 2"], value="Option Y", command=lambda: on_radio_select("Menu 2"))
submenu2.add_radiobutton(label="Option Z", variable=submenu_var["Menu 2"], value="Option Z", command=lambda: on_radio_select("Menu 2"))

# Run the Tkinter event loop
root.mainloop()