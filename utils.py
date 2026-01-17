import json
import os
from plyer import notification
import winreg
import sys
import winsound
from PIL import Image, ImageTk


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

def notify(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name="Health Reminder",
        timeout=10
    )

def set_autostart(enabled=True):
    app_name = "HealthReminderApp"
    script_path = os.path.abspath(sys.argv[0])
    # For python scripts, we need to run it with pythonw.exe to avoid terminal window
    python_exe = sys.executable
    if python_exe.lower().endswith("python.exe"):
        python_path = python_exe.replace("python.exe", "pythonw.exe")
    else:
        python_path = python_exe
        
    cmd = f'"{python_path}" "{script_path}"'
    
    key = winreg.HKEY_CURRENT_USER
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        reg_key = winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE)
        if enabled:
            winreg.SetValueEx(reg_key, app_name, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(reg_key, app_name)
            except FileNotFoundError:
                pass
        winreg.CloseKey(reg_key)
        return True
    except Exception as e:
        print(f"Error setting autostart: {e}")
        return False

import tkinter as tk
from tkinter import font as tkfont

def show_fullscreen_message(root, title, message, icon_path=None, duration_seconds=10):
    def close_window(event=None):
        if window.winfo_exists():
            window.destroy()

    # Play a subtle notification sound
    try:
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
    except Exception:
        pass

    window = tk.Toplevel(root)
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Set geometry to cover the entire screen
    window.geometry(f"{screen_width}x{screen_height}+0+0")
    
    # Remove window decorations
    window.overrideredirect(True)
    window.attributes("-topmost", True)
    
    window.configure(bg='#121212') # Dark background
    
    # Ensure it's on top
    window.lift()
    window.focus_force()
    
    # Allow clicking to dismiss
    window.bind("<Button-1>", close_window)
    window.bind("<Escape>", close_window)

    frame = tk.Frame(window, bg='#121212')
    frame.place(relx=0.5, rely=0.5, anchor='center')

    # Display Icon if provided
    if icon_path:
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                # Scale icon to a reasonable size
                img = img.resize((250, 250), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                icon_label = tk.Label(frame, image=photo, bg='#121212')
                icon_label.image = photo # Keep a reference
                icon_label.pack(pady=20)
            except Exception as e:
                print(f"Error loading icon {icon_path}: {e}")
        else:
            print(f"Icon path DOES NOT EXIST: {icon_path}")


    title_font = tkfont.Font(family="Segoe UI", size=48, weight="bold")
    msg_font = tkfont.Font(family="Segoe UI", size=24)

    tk.Label(frame, text=title, font=title_font, fg='#4CAF50', bg='#121212').pack(pady=10)
    tk.Label(frame, text=message, font=msg_font, fg='white', bg='#121212', wraplength=screen_width-200).pack(pady=10)
    tk.Label(frame, text="(Click or Press ESC to dismiss)", font=("Segoe UI", 12), fg='#888888', bg='#121212').pack(pady=30)

    # Auto close after duration
    window.after(duration_seconds * 1000, close_window)

def is_autostart_enabled():
    app_name = "HealthReminderApp"
    key = winreg.HKEY_CURRENT_USER
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        reg_key = winreg.OpenKey(key, key_path, 0, winreg.KEY_READ)
        winreg.QueryValueEx(reg_key, app_name)
        winreg.CloseKey(reg_key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

class PomodoroOverlay:
    def __init__(self, root):
        self.root = root
        self.overlay = tk.Toplevel(self.root)
        self.overlay.title("Pomodoro Timer")
        
        # Remove window decorations
        self.overlay.overrideredirect(True)
        # Always on top
        self.overlay.attributes("-topmost", True)
        # Transparent-ish background or semi-opaque
        self.overlay.configure(bg='#212121')
        
        # Set size and position (top middle)
        width = 150
        height = 40
        screen_width = self.overlay.winfo_screenwidth()
        x = (screen_width // 2) - (width // 2)
        y = 10 # 10 pixels from top
        self.overlay.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make it draggable (optional but helpful)
        self.overlay.bind("<Button-1>", self.start_move)
        self.overlay.bind("<B1-Motion>", self.do_move)
        
        self.label = tk.Label(self.overlay, text="00:00", font=("Segoe UI", 16, "bold"), 
                             fg="#4CAF50", bg="#212121")
        self.label.pack(expand=True)
        
        self._x = 0
        self._y = 0

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.overlay.winfo_x() + (event.x - self._x)
        y = self.overlay.winfo_y() + (event.y - self._y)
        self.overlay.geometry(f"+{x}+{y}")

    def update_timer(self, text, is_work=True):
        color = "#4CAF50" if is_work else "#2196F3" # Green for work, Blue for rest
        self.label.config(text=text, fg=color)
        # Removing explicit update() as root.update() in main loop handles it better

    def show(self):
        self.overlay.deiconify()
        self.overlay.lift()

    def hide(self):
        self.overlay.withdraw()


class BreakConfirmationUI:
    def __init__(self, root, on_start_break, on_remind_later, icon_path=None):
        self.root = root
        self.on_start_break = on_start_break
        self.on_remind_later = on_remind_later
        
        self.window = tk.Toplevel(root)
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg='#121212')
        
        frame = tk.Frame(self.window, bg='#121212')
        frame.place(relx=0.5, rely=0.5, anchor='center')

        if icon_path and os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                icon_label = tk.Label(frame, image=photo, bg='#121212')
                icon_label.image = photo
                icon_label.pack(pady=10)
            except Exception: pass

        title_font = tkfont.Font(family="Segoe UI", size=36, weight="bold")
        tk.Label(frame, text="Work session finished!", font=title_font, fg='#4CAF50', bg='#121212').pack(pady=10)
        tk.Label(frame, text="Would you like to start your break now?", font=("Segoe UI", 18), fg='white', bg='#121212').pack(pady=20)

        btn_frame = tk.Frame(frame, bg='#121212')
        btn_frame.pack(pady=20)

        # Start Break Button
        start_btn = tk.Button(btn_frame, text="Start Break", command=self._start_break, 
                               font=("Segoe UI", 14, "bold"), fg="white", bg="#4CAF50", 
                               padx=20, pady=10, relief="flat", cursor="hand2")
        start_btn.pack(side="left", padx=10)
        
        # Remind Later Button
        later_btn = tk.Button(btn_frame, text="Remind Later (5 min)", command=self._remind_later,
                                font=("Segoe UI", 14), fg="white", bg="#555555",
                                padx=20, pady=10, relief="flat", cursor="hand2")
        later_btn.pack(side="left", padx=10)

        self.window.lift()
        self.window.focus_force()

    def _start_break(self):
        self.window.destroy()
        self.on_start_break()

    def _remind_later(self):
        self.window.destroy()
        self.on_remind_later()

class BreakFullscreenOverlay:
    def __init__(self, root, on_cancel):
        self.root = root
        self.on_cancel = on_cancel
        self.window = tk.Toplevel(root)
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg='black')
        
        self.label = tk.Label(self.window, text="00:00", font=("Segoe UI", 72, "bold"), 
                             fg="white", bg="black")
        self.label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Keep instruction label subtle
        self.info = tk.Label(self.window, text="Taking a break...", font=("Segoe UI", 18), 
                             fg="#555555", bg="black")
        self.info.place(relx=0.5, rely=0.6, anchor='center')

        # Cancel button at bottom right or center bottom
        self.cancel_btn = tk.Button(self.window, text="Cancel Break", command=self._cancel,
                                     font=("Segoe UI", 12), fg="#444444", bg="black",
                                     relief="flat", cursor="hand2", activebackground="black", activeforeground="#888888")
        self.cancel_btn.place(relx=0.5, rely=0.9, anchor='center')

        self.window.lift()
        self.window.focus_force()

    def _cancel(self):
        self.close()
        self.on_cancel()

    def update_timer(self, text):
        if self.window.winfo_exists():
            self.label.config(text=text)

    def close(self):
        if self.window.winfo_exists():
            self.window.destroy()

