import threading
import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from pynput import keyboard
from get_selected_text import get_selected_text

class Listener(QThread):
    signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.ctrl_time = time.time()

    def run(self):
        with keyboard.GlobalHotKeys({
            '<ctrl>': self.on_hotkey_press
        }) as listener:
            listener.join()

    def on_hotkey_press(self):
        try:
            time_now = time.time()
            if time_now - self.ctrl_time < 0.3:
                text = get_selected_text()
                self.signal.emit(text)
                print(f"Selected text: {text}")
            self.ctrl_time = time_now
        except Exception as e:
            print(e)
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")       

            

