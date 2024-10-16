# 获取选中文本，清楚剪切板的影响
import pyperclip
from pynput import keyboard
import time

def get_selected_text():
    # 保存剪切板内容
    old_clipboard = pyperclip.paste()
    # 清空剪切板
    pyperclip.copy("")
    # 模拟按下 Ctrl+C
    time.sleep(0.05)
    with keyboard.Controller().pressed(keyboard.Key.ctrl):
        keyboard.Controller().press('c')
        keyboard.Controller().release('c')
    time.sleep(0.05)
    # 获取剪切板内容
    text = pyperclip.paste()
    # 恢复剪切板内容
    pyperclip.copy(old_clipboard)
    return text

if __name__ == "__main__":
    print(get_selected_text())
    