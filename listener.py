import time
from PyQt5.QtCore import QThread, pyqtSignal
from pynput import keyboard
import pyperclip
from pynput import keyboard
import time

class Listener(QThread):
    signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.ctrl_time = time.time()
        self.text_before = ""

    def run(self):
        with keyboard.GlobalHotKeys({
            '<ctrl>': self.on_hotkey_press
        }) as listener:
            listener.join()

    def on_hotkey_press(self):
        try:
            time_now = time.time()
            if time_now - self.ctrl_time < 0.3:
                text = self.get_selected_text()
                if not text or text == "":
                    text = self.text_before
                    print(f"Before text: {text}")
                else:
                    self.text_before = text
                self.signal.emit(text)
                print(f"Selected text: {text}")
            self.ctrl_time = time_now
        except Exception as e:
            print(e)
    
    def get_selected_text(self):
        # 保存剪切板内容
        old_clipboard = pyperclip.paste()
        # 清空剪切板
        pyperclip.copy("")
        # 模拟按下 Ctrl+C
        time.sleep(0.05)
        with keyboard.Controller().pressed(keyboard.Key.ctrl):
            keyboard.Controller().press('c')
            keyboard.Controller().release('c')
        time.sleep(0.1)
        # 获取剪切板内容
        text = pyperclip.paste()
        # 恢复剪切板内容
        pyperclip.copy(old_clipboard)
        return text

            

