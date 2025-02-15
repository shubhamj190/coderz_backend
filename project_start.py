import pyautogui
import time

def open_terminal(commands):
    """Open a new terminal in VS Code and run a command."""
    pyautogui.hotkey("ctrl", "shift", "`")  # Open a new terminal
    time.sleep(1)  # Wait for the terminal to open
    pyautogui.typewrite(commands + "\n")  # Execute the command
    time.sleep(2)  # Wait before opening the next terminal

if __name__ == "__main__":
    commands = [
        "source venv/scripts/activate && python manage.py shell",
        "source venv/scripts/activate && python manage.py runserver",
        "celery -A config worker --loglevel=info -P eventlet",
        "celery -A config flower",
        ""
    ]

    time.sleep(2)  # Allow time to switch to VS Code before execution starts

    for command in commands:
        open_terminal(command)
