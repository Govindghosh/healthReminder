# 🧘‍♂️ Health Reminder App

A modern, unobtrusive health tracking and reminder application designed to keep you productive and healthy while working. Built with Python and Tkinter, it integrates seamlessly into your Windows workflow with system tray support and beautiful fullscreen overlays.

---

## ✨ Features

- **🍅 Pomodoro Timer**: Stay focused with customizable work and break cycles. Includes a floating timer overlay and fullscreen break reminders.
- **💧 Water Reminders**: Get periodic notifications to stay hydrated.
- **🍽️ Meal Reminders**: Schedule meal timings to never miss a beat (or a bite).
- **🖥️ Fullscreen Overlays**: Beautiful dark-themed overlays that gently nudge you to take breaks or drink water.
- **⚓ System Tray Integration**: Runs quietly in the background. Access settings or quit from the system tray icon.
- **🚀 Auto-start on Boot**: Optional feature to start the app automatically when you log into Windows.
- **⚙️ Dynamic Configuration**: Easily adjust intervals and timings via `config.json` with real-time reload.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- **Python 3.x**: Ensure you have Python installed. You can download it from [python.org](https://www.python.org/).
- **Windows OS**: Currently optimized for Windows (uses `winreg` for autostart and `winsound` for alerts).

### 2. Clone the Project
```bash
git clone https://github.com/your-username/health-reminder.git
cd "health reminder"
```

### 3. Setup Virtual Environment
It is recommended to use a virtual environment to manage dependencies:
```powershell
# Create the virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.\.venv\Scripts\activate

# Install the required Python packages:
pip install -r requirements.txt
```

---

## 🚀 How to Run

### Standard Run
To start the application with a terminal window:
```bash
python main.py
```

### Run in Background (Hidden)
To run the app without a terminal window (recommended for daily use):
- Double-click `run_hidden.vbs`
- Or run via command line:
  ```bash
  wscript run_hidden.vbs
  ```

---

## ⚙️ Configuration

You can customize the application by editing `config.json`. The app will automatically detect changes and reload settings.

```json
{
    "pomodoro": {
        "work_minutes": 25,
        "break_minutes": 5,
        "enabled": true
    },
    "water": {
        "interval_minutes": 45,
        "enabled": true
    },
    "meals": {
        "timings": [
            "10:25",
            "13:30",
            "17:10"
        ],
        "enabled": true
    },
    "auto_start": true
}
```

---

## 🧰 Technologies Used

- **Python**: Core logic.
- **Tkinter**: GUI and fullscreen overlays.
- **Pystray**: System tray implementation.
- **Plyer**: Native Windows notifications.
- **Pillow (PIL)**: Image and icon processing.
- **VBScript**: Utility for hidden background execution.

---

## 🎨 Assets
The app uses custom icons for various reminders:
- `work_icon.png`
- `break_icon.png`
- `water_icon.png`
- `meal_icon.png`

---

## 📝 License
This project is open-source. Feel free to modify and adapt it for your personal use!

---
*Made with ❤️ for a healthier workspace.*
