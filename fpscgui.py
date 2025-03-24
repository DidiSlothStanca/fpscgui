import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import json

# Path ke file .sh
GALLIUM_SCRIPT = os.path.expanduser("~/.fpscgui/galliumhudgui/gallium.sh")
MANGOHUD_SCRIPT = os.path.expanduser("~/.fpscgui/mangohudgui/mango.sh")

# Path ke file konfigurasi ukuran jendela
WINDOW_CONFIG_PATH = os.path.expanduser("~/.fpscgui/window_config.json")

# Fungsi untuk memuat konfigurasi ukuran jendela
def load_window_config():
    if os.path.exists(WINDOW_CONFIG_PATH):
        with open(WINDOW_CONFIG_PATH, "r") as f:
            return json.load(f)
    return {"width": 300, "height": 200}  # Ukuran default

# Fungsi untuk menyimpan konfigurasi ukuran jendela
def save_window_config():
    config = {
        "width": root.winfo_width(),
        "height": root.winfo_height()
    }
    os.makedirs(os.path.dirname(WINDOW_CONFIG_PATH), exist_ok=True)
    with open(WINDOW_CONFIG_PATH, "w") as f:
        json.dump(config, f)

# Fungsi untuk mengatur jendela di tengah layar
def center_window(window, width, height):
    # Dapatkan lebar dan tinggi layar
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Hitung posisi x dan y untuk menempatkan jendela di tengah
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Atur posisi jendela
    window.geometry(f"{width}x{height}+{x}+{y}")

# Fungsi untuk menjalankan skrip Gallium FPS
def run_gallium():
    if not os.path.exists(GALLIUM_SCRIPT):
        messagebox.showerror("Error", f"File '{GALLIUM_SCRIPT}' tidak ditemukan!")
        return
    
    # Nonaktifkan tombol lainnya
    gallium_button.config(state=tk.DISABLED)
    mangohud_button.config(state=tk.DISABLED)
    winecfg_button.config(state=tk.DISABLED)
    
    try:
        # Jalankan skrip Gallium
        subprocess.Popen(["/bin/bash", GALLIUM_SCRIPT])
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menjalankan Gallium FPS: {e}")
    finally:
        # Setelah proses selesai, aktifkan kembali tombol
        gallium_button.config(state=tk.NORMAL)
        mangohud_button.config(state=tk.NORMAL)
        winecfg_button.config(state=tk.NORMAL)

# Fungsi untuk menjalankan skrip MangoHud FPS
def run_mangohud():
    if not os.path.exists(MANGOHUD_SCRIPT):
        messagebox.showerror("Error", f"File '{MANGOHUD_SCRIPT}' tidak ditemukan!")
        return
    
    # Nonaktifkan tombol lainnya
    gallium_button.config(state=tk.DISABLED)
    mangohud_button.config(state=tk.DISABLED)
    winecfg_button.config(state=tk.DISABLED)
    
    try:
        # Jalankan skrip MangoHud
        subprocess.Popen(["/bin/bash", MANGOHUD_SCRIPT])
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menjalankan MangoHud FPS: {e}")
    finally:
        # Setelah proses selesai, aktifkan kembali tombol
        gallium_button.config(state=tk.NORMAL)
        mangohud_button.config(state=tk.NORMAL)
        winecfg_button.config(state=tk.NORMAL)

# Fungsi untuk menjalankan Wine Config (winecfg)
def run_winecfg():
    try:
        # Jalankan winecfg
        subprocess.Popen(["winecfg"])
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menjalankan Wine Config: {e}")

# Fungsi untuk keluar aplikasi
def exit_app():
    save_window_config()  # Simpan ukuran jendela sebelum keluar
    root.quit()

# Inisialisasi GUI
root = tk.Tk()
root.title("FPS Overlay Launcher")

# Muat konfigurasi ukuran jendela
window_config = load_window_config()
width = window_config['width']
height = window_config['height']

# Atur ukuran dan posisi jendela
root.geometry(f"{width}x{height}")
center_window(root, width, height)

# Tombol Gallium FPS
gallium_button = tk.Button(root, text="Gallium FPS", command=run_gallium, width=20, height=2)
gallium_button.pack(pady=10)

# Tombol MangoHud FPS
mangohud_button = tk.Button(root, text="MangoHud FPS", command=run_mangohud, width=20, height=2)
mangohud_button.pack(pady=10)

# Tombol Wine Config
winecfg_button = tk.Button(root, text="Wine Config", command=run_winecfg, width=20, height=2)
winecfg_button.pack(pady=10)

# Tombol Exit
exit_button = tk.Button(root, text="Exit", command=exit_app, width=20, height=2)
exit_button.pack(pady=10)

# Binding event untuk menyimpan ukuran jendela saat di-resize
root.bind("<Configure>", lambda event: save_window_config())

# Jalankan aplikasi
root.mainloop()
