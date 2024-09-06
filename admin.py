import ctypes
import sys
from winreg import *

def add_runas():
    """Add the RUNASADMIN flag to make the Python executable always run as administrator."""
    exe_path = sys.executable
    # Check if the script is running with admin privileges, if not request them
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe_path, __file__, None, 1)
        return  # After relaunch, the script will continue from here

    reg_path = r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"
    reg_key = OpenKey(HKEY_CURRENT_USER, reg_path, access=KEY_SET_VALUE | KEY_READ)
    runas_value = "~ RUNASADMIN"
    try:
        value = QueryValueEx(reg_key, exe_path)
    except FileNotFoundError:
        # If the value is not set, add it
        SetValueEx(reg_key, exe_path, 0, REG_SZ, runas_value)
    else:
        if runas_value[2:] not in value[0]:
            # Append RUNASADMIN if it's not already set
            SetValueEx(reg_key, exe_path, 0, REG_SZ, value[0] + ' ' + runas_value[2:])
    CloseKey(reg_key)

def remove_runas():
    """Remove the RUNASADMIN flag to make the Python executable run without admin privileges."""
    exe_path = sys.executable
    reg_path = r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"
    reg_key = OpenKey(HKEY_CURRENT_USER, reg_path, access=KEY_SET_VALUE | KEY_READ)
    try:
        value, value_type = QueryValueEx(reg_key, exe_path)
        if "~ RUNASADMIN" in value:
            # Remove the RUNASADMIN flag from the registry value
            new_value = value.replace("~ RUNASADMIN", "").strip()
            if new_value:
                SetValueEx(reg_key, exe_path, 0, REG_SZ, new_value)  # Update with the modified value
            else:
                DeleteValue(reg_key, exe_path)  # Delete the value if it's empty
    except FileNotFoundError:
        print("No RUNASADMIN entry found for this executable.")
    finally:
        CloseKey(reg_key)

if __name__ == "__main__":
    # Uncomment the one you need

    # add_runas()  # To make Python run as admin every time
    remove_runas()  # To revert Python to run without admin privileges