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
                text = self.__get_selected_text()
                self.signal.emit(text)
                print(f"Selected text: {text}")
            self.ctrl_time = time_now
        except Exception as e:
            print(e)
    
    def __get_selected_text(self):
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
        # 处理失焦问题
        if not text or text == "":
            text = self.text_before
            print(f"Get text before: {text}")
        else:
            self.text_before = text
        # 格式化      
        text = self.__format_text(text)
        return text
    
    def __format_text(self, text):
        # 去除首尾空格
        while text and text[0] in " \n\t\r.": text = text[1:]
        while text and text[-1] in " \n\t\r.": text = text[:-1]
        return text

            

