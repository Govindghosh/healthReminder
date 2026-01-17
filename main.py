import time
import threading
from datetime import datetime
import pystray
from PIL import Image, ImageDraw
import os
import sys
from utils import load_config, save_config, notify, set_autostart, is_autostart_enabled, show_fullscreen_message, PomodoroOverlay, BreakConfirmationUI, BreakFullscreenOverlay

# Ensure we are in the script's directory (important for autostart)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class HealthReminderApp:
    def __init__(self):
        self.config = load_config()
        self.running = True
        self.icon = None
        self.pomodoro_start_time = time.time()
        self.water_start_time = time.time()
        self.last_meal_check = ""
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        self.last_config_mtime = os.path.getmtime(self.config_path) if os.path.exists(self.config_path) else 0
        self.assets_dir = os.path.dirname(__file__)
        import tkinter as tk
        self.root = tk.Tk()
        self.root.withdraw() # Main root is hidden
        self.pomodoro_overlay = PomodoroOverlay(self.root) if self.config["pomodoro"]["enabled"] else None
        
        # New Pomodoro State Management
        self.pomodoro_state = "WORK"
        self.pomodoro_duration = self.config["pomodoro"]["work_minutes"] * 60
        self.pomodoro_start_time = time.time()
        self.break_ui = None
        self.break_overlay = None
        
        # Track when reminders were last shown to avoid duplicates if loop runs fast
        self.last_reminders = {
            "pomodoro_work": 0,
            "pomodoro_break": 0,
            "water": 0
        }
        
        # Check if autostart matches config
        current_autostart = is_autostart_enabled()
        if self.config.get("auto_start", False) != current_autostart:
            set_autostart(self.config.get("auto_start", False))

    def create_image(self):
        # Generate a simple icon: a green circle
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), (255, 255, 255))
        dc = ImageDraw.Draw(image)
        dc.ellipse([10, 10, 54, 54], fill=(0, 200, 0))
        return image

    def on_quit(self, icon, item):
        self.running = False
        icon.stop()
        try:
            self.root.after(0, self.root.destroy)
        except:
            pass

    def toggle_autostart(self, icon, item):
        new_state = not is_autostart_enabled()
        if set_autostart(new_state):
            self.config["auto_start"] = new_state
            save_config(self.config)
            notify("Auto-start", f"Auto-start {'enabled' if new_state else 'disabled'}")

    def run_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("Health Reminder Running", lambda: None, enabled=False),
            pystray.MenuItem("Settings", self.open_settings),
            pystray.MenuItem("Auto-start", self.toggle_autostart, checked=lambda item: is_autostart_enabled()),
            pystray.MenuItem("Quit", self.on_quit)
        )
        self.icon = pystray.Icon("HealthReminder", self.create_image(), "Health Reminder", menu)
        self.icon.run()

    def open_settings(self, icon, item):
        # In a real app, this might open a GUI. For now, we'll just notify where the config is.
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.json'))
        notify("Settings", f"Edit settings in: {config_path}")

    def reminder_loop(self):
        while self.running:
            try:
                now = time.time()
                # --- Efficient Config Reload (only if file changed) ---
                if os.path.exists(self.config_path):
                    current_mtime = os.path.getmtime(self.config_path)
                    if current_mtime > self.last_config_mtime:
                        print(f"Config change detected! Reloading... ({datetime.now().strftime('%H:%M:%S')})")
                        self.config = load_config()
                        self.last_config_mtime = current_mtime

                current_time_str = datetime.now().strftime("%H:%M")
                # print(f"Checking reminders... Time: {current_time_str}") # Debugging

                
                # --- Pomodoro Check (State Machine) ---
                if self.config["pomodoro"]["enabled"]:
                    elapsed = now - self.pomodoro_start_time
                    remaining = max(0, self.pomodoro_duration - elapsed)
                    mins, secs = divmod(int(remaining), 60)
                    timer_text = f"{mins:02d}:{secs:02d}"

                    if self.pomodoro_state == "WORK":
                        if self.pomodoro_overlay:
                            self.pomodoro_overlay.update_timer(timer_text, is_work=True)
                            self.pomodoro_overlay.show()
                        
                        if elapsed >= self.pomodoro_duration:
                            self.pomodoro_state = "BREAK_PENDING"
                            if self.pomodoro_overlay: self.pomodoro_overlay.hide()
                            self.break_ui = BreakConfirmationUI(
                                self.root, 
                                on_start_break=self.start_break, 
                                on_remind_later=self.remind_later,
                                icon_path=os.path.join(self.assets_dir, "break_icon.png")
                            )

                    elif self.pomodoro_state == "BREAK":
                        if self.break_overlay:
                            self.break_overlay.update_timer(timer_text)
                        
                        if elapsed >= self.pomodoro_duration:
                            self.pomodoro_state = "WORK"
                            self.pomodoro_duration = self.config["pomodoro"]["work_minutes"] * 60
                            self.pomodoro_start_time = now
                            if self.break_overlay:
                                self.break_overlay.close()
                                self.break_overlay = None
                            
                            show_fullscreen_message(self.root, "Work Time", f"Time to work for {self.config['pomodoro']['work_minutes']} mins!", 
                                                     icon_path=os.path.join(self.assets_dir, "work_icon.png"))

                    elif self.pomodoro_state == "REMIND_LATER":
                        if self.pomodoro_overlay:
                            self.pomodoro_overlay.update_timer(timer_text, is_work=False)
                            self.pomodoro_overlay.show()
                        
                        if elapsed >= self.pomodoro_duration:
                            self.pomodoro_state = "BREAK_PENDING"
                            if self.pomodoro_overlay: self.pomodoro_overlay.hide()
                            self.break_ui = BreakConfirmationUI(
                                self.root,
                                on_start_break=self.start_break,
                                on_remind_later=self.remind_later,
                                icon_path=os.path.join(self.assets_dir, "break_icon.png")
                            )

                    elif self.pomodoro_state == "BREAK_PENDING":
                        # Just waiting for UI interaction
                        pass
                else:
                    if self.pomodoro_overlay:
                        self.pomodoro_overlay.hide()

                # --- Water Check ---
                if self.config["water"]["enabled"]:
                    water_sec = self.config["water"]["interval_minutes"] * 60
                    if now - self.water_start_time >= water_sec:
                        show_fullscreen_message(self.root, "Water Reminder", "Time to drink some water!",
                                                icon_path=os.path.join(self.assets_dir, "water_icon.png"))
                        self.water_start_time = time.time() # Reset based on current time
                        self.last_reminders["water"] = now

                # --- Meal Check ---
                if self.config["meals"]["enabled"]:
                    if current_time_str in self.config["meals"]["timings"] and current_time_str != self.last_meal_check:
                        print(f"Triggering meal reminder for {current_time_str}")
                        show_fullscreen_message(self.root, "Meal Time", f"It's {current_time_str}! Time for your scheduled meal.",
                                                icon_path=os.path.join(self.assets_dir, "meal_icon.png"))
                        self.last_meal_check = current_time_str
            except Exception as e:
                print(f"CRITICAL ERROR in reminder loop: {e}")
                import traceback
                traceback.print_exc()
            
            try:
                self.root.update()
            except:
                pass
            time.sleep(0.1)

    def start_break(self):
        self.pomodoro_state = "BREAK"
        self.pomodoro_duration = self.config["pomodoro"]["break_minutes"] * 60
        self.pomodoro_start_time = time.time()
        self.break_overlay = BreakFullscreenOverlay(self.root, on_cancel=self.cancel_break)

    def cancel_break(self):
        self.pomodoro_state = "WORK"
        self.pomodoro_duration = self.config["pomodoro"]["work_minutes"] * 60
        self.pomodoro_start_time = time.time()
        if self.break_overlay:
            self.break_overlay.close()
            self.break_overlay = None

    def remind_later(self):
        self.pomodoro_state = "REMIND_LATER"
        self.pomodoro_duration = 5 * 60
        self.pomodoro_start_time = time.time()

    def start(self):
        # Start the tray icon in a background thread
        threading.Thread(target=self.run_tray, daemon=True).start()
        # Run the reminder loop in the main thread (needed for Tkinter)
        self.reminder_loop()

if __name__ == "__main__":
    app = HealthReminderApp()
    app.start()
