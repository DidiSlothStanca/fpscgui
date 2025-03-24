import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk, colorchooser, filedialog, simpledialog

CONFIG_DIR = os.path.expanduser('~/.config/MangoHud')
DEFAULT_CONFIG = os.path.expanduser('~/.fpscgui/mangohudgui/conf/MangoHud.conf')
BACKUP_FILE = os.path.expanduser('~/.fpscgui/mangohudgui/conf/MangoHud.conf_back')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'MangoHud.conf')
SHORTCUT_DIR = os.path.expanduser('~/.fpscgui/mangohudgui/shortcutmango')

DEFAULT_COLORS = {
    'text_color': 'FFFFFF',
    'gpu_color': '2E9762',
    'cpu_color': '2E97CB',
    'vram_color': 'AD64C1',
    'ram_color': 'C26693',
    'engine_color': 'EB5B5B',
    'io_color': 'A491D3',
    'frametime_color': '00FF00',
    'background_color': '020202',
    'media_player_color': 'FFFFFF',
    'wine_color': 'EB5B5B',
    'battery_color': 'FF9078',
}

# Pastikan direktori dan konfigurasi awal ada
def ensure_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(CONFIG_FILE):
        shutil.copy(DEFAULT_CONFIG, CONFIG_FILE)
    if not os.path.exists(BACKUP_FILE):
        shutil.copy(DEFAULT_CONFIG, BACKUP_FILE)
    if not os.path.exists(SHORTCUT_DIR):
        os.makedirs(SHORTCUT_DIR)

# Fungsi untuk membaca file konfigurasi
def load_config():
    ensure_config()
    config = {}
    with open(CONFIG_FILE, 'r') as f:
        for line in f:
            key_value = line.strip().split('=')
            if len(key_value) == 2:
                key, value = key_value
                config[key.strip()] = value.strip()
    return config

# Fungsi untuk menyimpan file konfigurasi
def save_config(lines):
    with open(CONFIG_FILE, 'w') as f:
        f.writelines(lines)

class MangoHudGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('MangoHud GUI Configurator')
        
        # Muat konfigurasi
        self.config = load_config()
        
        # Set ukuran window dari konfigurasi (jika ada)
        self.geometry(self.config.get('window_size', '420x600'))
        
        # Simpan ukuran window saat di-resize
        self.bind("<Configure>", self.on_window_resize)
        
        self.check_buttons = {}
        self.color_vars = {}
        
        self.font_size_var = tk.StringVar(value=self.config.get('font_size', '15'))
        self.bg_alpha_var = tk.DoubleVar(value=float(self.config.get('background_alpha', 0.5)))
        self.position_var = tk.StringVar(value=self.config.get('position', 'top-left'))
        
        self.create_widgets()

    def create_scrollable_frame(self, parent):
        frame = tk.Frame(parent)
        canvas = tk.Canvas(frame)
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-int(e.delta/120), "units"))

        return frame, scrollable_frame

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        
        # Buat frame untuk setiap tab
        play_frame, play_scrollable = self.create_scrollable_frame(notebook)
        main_frame, main_scrollable = self.create_scrollable_frame(notebook)
        color_frame, color_scrollable = self.create_scrollable_frame(notebook)
        
        # Tambahkan tab dengan urutan baru (Play di posisi pertama)
        notebook.add(play_frame, text='Play')
        notebook.add(main_frame, text='Main')
        notebook.add(color_frame, text='Color Font')
        
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab Play
        self.shortcut_list = tk.Listbox(play_scrollable)
        self.shortcut_list.pack(fill=tk.BOTH, expand=True, pady=10)
        self.update_shortcut_list()

        button_frame = tk.Frame(play_scrollable)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text='Create', command=self.create_shortcut).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text='Remove', command=self.remove_shortcut).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text='Play', command=self.play_shortcut).pack(side=tk.LEFT, padx=5)

        # Dropdown FPS Counter
        self.fps_var = tk.StringVar(value='Normal')
        fps_options = ['MangoVK', 'MangoGL', 'Normal']
        ttk.Combobox(button_frame, textvariable=self.fps_var, values=fps_options).pack(side=tk.LEFT, padx=5)
        
        # Tab Main
        elements = ['time', 'version', 'gpu_stats', 'gpu_temp', 'cpu_stats', 'cpu_temp', 'core_load', 'io_stats', 'vram', 'ram', 'swap', 'procmem', 'battery', 'fps', 'frametime', 'frame_timing', 'gamemode', 'vkbasalt', 'resolution']
        
        for element in elements:
            var = tk.BooleanVar(value=self.config.get(element, '0') == '1')
            chk = tk.Checkbutton(main_scrollable, text=element, variable=var)
            chk.pack(anchor='w')
            self.check_buttons[element] = var
        
        tk.Label(main_scrollable, text='Font Size:').pack(pady=5)
        font_sizes = [12, 14, 16, 18, 20, 24, 28, 32]
        ttk.Combobox(main_scrollable, textvariable=self.font_size_var, values=font_sizes).pack()
        
        tk.Label(main_scrollable, text='Background Alpha (0.0 - 1.0):').pack(pady=5)
        tk.Scale(main_scrollable, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, variable=self.bg_alpha_var).pack()
        
        tk.Label(main_scrollable, text='HUD Position:').pack(pady=5)
        positions = ['top-left', 'top-right', 'middle-left', 'middle-right', 'bottom-left', 'bottom-right', 'top-center', 'bottom-center']
        ttk.Combobox(main_scrollable, textvariable=self.position_var, values=positions).pack()
        
        # Tab Color Font
        for color_key, default_color in DEFAULT_COLORS.items():
            tk.Label(color_scrollable, text=f'{color_key.replace("_", " ").title()}:').pack(pady=5)
            color_value = self.config.get(color_key, default_color)
            self.color_vars[color_key] = tk.StringVar(value=color_value)
            color_entry_frame = tk.Frame(color_scrollable)
            color_entry_frame.pack()
            tk.Entry(color_entry_frame, textvariable=self.color_vars[color_key], width=10).pack(side=tk.LEFT)
            tk.Button(color_entry_frame, text='Pick Color', command=lambda key=color_key: self.pick_color(key)).pack(side=tk.LEFT)
        
        # Tombol Save dan Exit
        tk.Button(self, text='Save', command=self.save_and_apply).pack(side=tk.LEFT, padx=20, pady=10)
        tk.Button(self, text='Exit', command=self.quit).pack(side=tk.RIGHT, padx=20, pady=10)

    def pick_color(self, key):
        color_code = colorchooser.askcolor(title=f"Pick {key}")[1]
        if color_code:
            self.color_vars[key].set(color_code.strip('#').upper())

    def save_and_apply(self):
        lines = []
        for element, var in self.check_buttons.items():
            lines.append(f'{element}={1 if var.get() else 0}\n')
        lines.append(f'font_size={self.font_size_var.get()}\n')
        lines.append(f'background_alpha={self.bg_alpha_var.get()}\n')
        lines.append(f'position={self.position_var.get()}\n')
        for color_key, color_var in self.color_vars.items():
            lines.append(f'{color_key}={color_var.get()}\n')
        save_config(lines)
        messagebox.showinfo('Saved', 'Configuration saved to ~/.config/MangoHud/MangoHud.conf')

    def update_shortcut_list(self):
        self.shortcut_list.delete(0, tk.END)
        for file in os.listdir(SHORTCUT_DIR):
            if file.endswith('.sh'):
                self.shortcut_list.insert(tk.END, file[:-3])  # Remove .sh extension

    def create_shortcut(self):
        # Browse file executable (semua jenis file)
        file_path = filedialog.askopenfilename(
            title="Select Game Executable",
            filetypes=[("All Files", "*.*")]
        )
        if file_path:
            # Ambil nama file tanpa ekstensi
            default_name = os.path.splitext(os.path.basename(file_path))[0]

            # Dialog untuk rename file
            custom_name = simpledialog.askstring(
                "Rename Shortcut",
                "Enter shortcut name (or leave blank to use default):",
                initialvalue=default_name
            )
            shortcut_name = custom_name if custom_name else default_name

            # Tentukan apakah file adalah .exe (Wine)
            is_wine = file_path.endswith('.exe')

            # Buat konten script
            script_content = f"#!/bin/bash\ncd \"{os.path.dirname(file_path)}\"\n"
            script_content += f"{'wine ' if is_wine else ''}\"./{os.path.basename(file_path)}\"\n"

            # Simpan file .sh
            shortcut_path = os.path.join(SHORTCUT_DIR, f"{shortcut_name}.sh")
            with open(shortcut_path, 'w') as f:
                f.write(script_content)
            os.chmod(shortcut_path, 0o755)  # Set permission executable
            self.update_shortcut_list()

    def remove_shortcut(self):
        selected = self.shortcut_list.curselection()
        if selected:
            game_name = self.shortcut_list.get(selected)
            os.remove(os.path.join(SHORTCUT_DIR, f"{game_name}.sh"))
            self.update_shortcut_list()

    def play_shortcut(self):
        selected = self.shortcut_list.curselection()
        if selected:
            game_name = self.shortcut_list.get(selected)
            shortcut_path = os.path.join(SHORTCUT_DIR, f"{game_name}.sh")
            fps_mode = self.fps_var.get()

            # Debug: Tampilkan path dan mode yang dipilih
            print(f"Selected shortcut: {shortcut_path}")
            print(f"FPS mode: {fps_mode}")

            # Menyusun perintah yang sesuai dengan pilihan FPS Counter
            if fps_mode == 'MangoVK':
                command = ["mangohud", shortcut_path]
            elif fps_mode == 'MangoGL':
                command = ["mangohud", "--dlsym", shortcut_path]
            elif fps_mode == 'Normal':
                command = ["bash", shortcut_path]
            else:
                messagebox.showerror("Error", "Invalid FPS mode selected!")
                return

            # Debug: Tampilkan command yang akan dijalankan
            print(f"Running command: {' '.join(command)}")

            # Jalankan command
            try:
                subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch game: {e}")

    def on_window_resize(self, event):
        # Simpan ukuran window saat di-resize
        if event.widget == self:
            window_size = self.geometry()
            self.config['window_size'] = window_size
            lines = []
            for key, value in self.config.items():
                lines.append(f'{key}={value}\n')
            save_config(lines)

if __name__ == '__main__':
    app = MangoHudGUI()
    app.mainloop()
