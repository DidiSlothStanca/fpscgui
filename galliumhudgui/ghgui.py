import tkinter as tk
from tkinter import filedialog, simpledialog
import subprocess
import os
import math
import json

CONFIG_PATH = os.path.expanduser("~/.fpscgui/galliumhudgui/config.json")
SHORTCUT_DIR = os.path.expanduser("~/.fpscgui/galliumhudgui/shortcut/")

# Load configuration
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {"executables": [], "scale": 1, "show_all": False, "show_fps": False}

# Save configuration
def save_config():
    config = {
        "executables": list(app_listbox.get(0, tk.END)),
        "scale": scale_var.get(),
        "show_all": show_all_var.get(),
        "show_fps": show_fps_var.get()
    }
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

def run_galliumhud():
    selected = app_listbox.curselection()
    if not selected:
        return
    
    executable = app_listbox.get(selected[0])
    script_path = os.path.join(SHORTCUT_DIR, executable)
    
    if not os.path.exists(script_path):
        print(f"Error: Script '{script_path}' not found.")
        return
    
    if show_all_var.get():
        hud_string = ".h80.w105cpufreq-cur-cpu0+cpufreq-cur-cpu1+cpufreq-cur-cpu2+cpufreq-cur-cpu3+cpufreq-cur-cpu4+cpufreq-cur-cpu5+cpufreq-cur-cpu6+cpufreq-cur-cpu7;.h80.x185.w230.c100cpu0+cpu1+cpu2+cpu3+cpu4+cpu5+cpu6+cpu7;.x445.h80.w75.dGPU-load+cpu+fps;.x565.h80.w875.dfps;.x1470.h80.w190.c100sensors_temp_cu-amdgpu-pci-0100.temp1+GPU-load:100;.x1690.h80.w170requested-VRAM+VRAM-usage"
    elif show_fps_var.get():
        hud_string = "GPU-load+cpu+fps"
    else:
        return
    
    scale_value = max(1, int(math.floor(scale_var.get())))
    
    command = f'GALLIUM_HUD_PERIOD=0.07 GALLIUM_HUD="{hud_string}" GALLIUM_HUD_SCALE={scale_value} "{script_path}"'
    
    try:
        subprocess.Popen(command, shell=True, executable="/bin/bash")
    except Exception as e:
        print(f"Error running command: {e}")
    
    save_config()

def remove_executable():
    selected = app_listbox.curselection()
    if selected:
        executable = app_listbox.get(selected[0])
        script_path = os.path.join(SHORTCUT_DIR, executable)
        
        # Hapus file dari direktori shortcut
        if os.path.exists(script_path):
            try:
                os.remove(script_path)
                print(f"File '{script_path}' deleted.")
            except Exception as e:
                print(f"Error deleting file: {e}")
        
        # Hapus dari listbox
        app_listbox.delete(selected[0])
        save_config()

def create_file():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    
    default_name = os.path.splitext(os.path.basename(file_path))[0]
    custom_name = simpledialog.askstring(
        "Rename Shortcut",
        "Enter shortcut name (or leave blank to use default):",
        initialvalue=default_name
    )
    shortcut_name = custom_name if custom_name else default_name

    os.makedirs(SHORTCUT_DIR, exist_ok=True)
    script_name = f"{shortcut_name}.sh"
    script_path = os.path.join(SHORTCUT_DIR, script_name)
    
    with open(script_path, "w") as f:
        f.write("#!/bin/bash\n")
        exe_dir = os.path.dirname(file_path)
        if file_path.lower().endswith(".exe"):
            f.write(f'cd "{exe_dir}"\n')
            f.write(f'wine "./{os.path.basename(file_path)}"\n')
        else:
            f.write(f'cd "{exe_dir}"\n')
            f.write(f'"./{os.path.basename(file_path)}"\n')
    
    os.chmod(script_path, 0o755)
    print(f"Script created at: {script_path}")

    app_listbox.insert(tk.END, script_name)
    save_config()

def toggle_checkboxes(selected_var):
    if selected_var.get():
        if selected_var == show_all_var:
            show_fps_var.set(False)
        elif selected_var == show_fps_var:
            show_all_var.set(False)
    save_config()

def exit_app():
    save_config()
    root.quit()

# Initialize UI
root = tk.Tk()
root.title("Gallium HUD Manager")

# Menghitung ukuran layar
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Membuat jendela dan memastikan ukuran jendela dihitung
root.update_idletasks()  # Memastikan ukuran jendela dihitung
window_width = root.winfo_width()
window_height = root.winfo_height()

# Menghitung posisi tengah layar
x_position = (screen_width // 2) - (window_width // 2)
y_position = (screen_height // 2) - (window_height // 2)

# Mengatur posisi jendela aplikasi
root.geometry(f"+{x_position}+{y_position}")

tk.Label(root, text="Executable List:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
app_listbox = tk.Listbox(root, width=50, height=5)
app_listbox.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

btn_frame = tk.Frame(root)
btn_frame.grid(row=2, column=0, columnspan=3, pady=5)

# Tombol Remove dan Create File
tk.Button(btn_frame, text="Create File", command=create_file).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Remove", command=remove_executable).pack(side=tk.LEFT, padx=5)

show_all_var = tk.BooleanVar()
show_fps_var = tk.BooleanVar()

tk.Checkbutton(root, text="Show All Resource", variable=show_all_var, command=lambda: toggle_checkboxes(show_all_var)).grid(row=3, column=0, padx=5, pady=2, sticky="w")
tk.Checkbutton(root, text="Show FPS, CPU, GPU", variable=show_fps_var, command=lambda: toggle_checkboxes(show_fps_var)).grid(row=4, column=0, padx=5, pady=2, sticky="w")

tk.Label(root, text="Scale:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
scale_var = tk.DoubleVar(value=1.0)
tk.Entry(root, textvariable=scale_var, width=5).grid(row=5, column=1, padx=5, pady=5)

tk.Button(root, text="Play", command=run_galliumhud).grid(row=6, column=0, padx=5, pady=10)
tk.Button(root, text="Exit", command=exit_app).grid(row=6, column=1, padx=5, pady=10)

# Load configuration
data = load_config()
for exe in data.get("executables", []):
    app_listbox.insert(tk.END, exe)
scale_var.set(data.get("scale", 1))
show_all_var.set(data.get("show_all", False))
show_fps_var.set(data.get("show_fps", False))

root.mainloop()
