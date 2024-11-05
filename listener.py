import time
from PyQt5.QtCore import QThread, pyqtSignal
from pynput import keyboard
import pyperclip
import time

class Listener(QThread):
    signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.ctrl_time = 0
        self.shift_time = 0
        self.text_before = ""
        self.text_append = ""

    def run(self):
        # with keyboard.GlobalHotKeys({
        #     '<ctrl>': self.on_ctrl_press,
        #     '<shift>': self.on_shift_press
        # }) as listener:
        #     listener.join()
        keyboard.Listener(on_release=self.on_release).start()

    def on_release(self, key):
        try:
            if key == keyboard.Key.shift or key == keyboard.Key.shift_r or key == keyboard.Key.shift_l:
                time_now = time.time()
                if time_now - self.shift_time < 0.3:
                    self.shift_time -= 0.3
                    self.on_double_shift()
                else:
                    self.shift_time = time_now
            elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r or key == keyboard.Key.ctrl:
                time_now = time.time()
                if time_now - self.ctrl_time < 0.3:
                    self.ctrl_time -= 0.3
                    self.on_double_ctrl()
                else:
                    self.ctrl_time = time_now
        except Exception as e:
            print(e)
    
    def on_double_ctrl(self):
        try:
            text = self.__get_selected_text()
            if self.text_append == "":
                if text != "":
                    self.text_before = text
            else:
                if text == self.text_before:
                    self.text_before = self.text_append
                else:
                    self.text_before = self.text_append + text
            self.text_append = ""
            self.signal.emit(self.text_before)
            print(f"selected text----\n{self.text_before}\n----")
        except Exception as e:
            print(e)
            
    def on_double_shift(self):
        try:
            keyboard.Controller().press(keyboard.Key.ctrl)
            time.sleep(0.1)
            self.ctrl_time = 0
            text = self.__get_selected_text()
            if text != "" and text != self.text_before:
                self.text_before = text
                self.text_append = self.text_append + text
            elif self.text_append == "" and text == self.text_before:
                self.text_append = text
            # self.signal.emit(self.text_before)
            print(f"Append text----\n{self.text_append}\n----")
        except Exception as e:
            print(e)
    
    def __get_selected_text(self):
        print("get selected text")
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
        self.ctrl_time = 0
        # 获取剪切板内容
        text = pyperclip.paste() or ""
        # 恢复剪切板内容
        pyperclip.copy(old_clipboard)
        # 格式化      
        text = self.__format_text(text)
        print(text)
        return text
    
    def __format_text(self, text):
        # 去除首尾空格
        while text and text[0] in " \n\t\r.": text = text[1:]
        while text and text[-1] in " \n\t\r.": text = text[:-1]
        return text

            

