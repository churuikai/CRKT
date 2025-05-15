import time
from PyQt5.QtCore import QThread, pyqtSignal
from pynput import keyboard

TIME_LIMIT = 0.2
COOLDOWN_TIME = 1  # 冷却时间，防止重复触发

class Listener(QThread):
    signal = pyqtSignal(str)
    double_shift = pyqtSignal(str)
    double_ctrl = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.ctrl_time = 0
        self.shift_time = 0
        self.text_before = ""
        self.is_append = False
        self.last_ctrl_action_time = 0  # 上次执行双击Ctrl动作的时间
        self.ctrl_cooldown = False  # 是否处于冷却状态
        
    def run(self):
        keyboard.Listener(on_release=self.__on_release).start()
        
    def __on_release(self, key):
        try:
            current_time = time.time()
            
            # 处理Shift键
            if key == keyboard.Key.shift or key == keyboard.Key.shift_r or key == keyboard.Key.shift_l:
                if current_time - self.shift_time < TIME_LIMIT:
                    self.shift_time -= TIME_LIMIT  # 防止连续触发
                    self.__on_double_shift()
                else:
                    self.shift_time = current_time
                    
            # 处理Ctrl键，增加冷却期检查
            elif (key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r or key == keyboard.Key.ctrl) and not self.ctrl_cooldown:
                if current_time - self.ctrl_time < TIME_LIMIT:
                    self.ctrl_time -= TIME_LIMIT  # 防止连续触发
                    
                    # 设置冷却标志
                    self.ctrl_cooldown = True
                    self.last_ctrl_action_time = current_time
                    
                    # 执行双击Ctrl动作
                    self.__on_double_ctrl()
                    
                    # 启动一个定时任务，在冷却时间后重置冷却标志
                    QThread.msleep(int(COOLDOWN_TIME * 1000))
                    self.ctrl_cooldown = False
                else:
                    self.ctrl_time = current_time
                    
        except Exception as e:
            print(f"键盘事件处理错误: {e}")
    
    def __on_double_ctrl(self):
        try:
            text = self.__get_selected_text()
            if self.is_append:
                self.is_append = False
                if text == self.text_before:
                    self.double_ctrl.emit("")
                else:
                    self.double_ctrl.emit(text)
            else:
                if text == "":
                    text = self.text_before
                    
                self.double_ctrl.emit(text)
            self.text_before = text if text != "" else self.text_before
                    
        except Exception as e:
            print(f"双击Ctrl处理错误: {e}")
            
    def __on_double_shift(self):
        try:
            keyboard.Controller().press(keyboard.Key.ctrl)
            # 重置ctrl_time避免这个模拟的Ctrl触发自己的监听器
            self.ctrl_time = 0
            text = self.__get_selected_text()
            self.text_before = text
            self.double_shift.emit(text)
            self.is_append = True
        except Exception as e:
            print(f"双击Shift处理错误: {e}")
            
    def __get_selected_text(self):
        print("正在获取选中文本...")
        try:
            # 使用改进的方法获取选中文本
            from selected_text import get_selected_text
            text = get_selected_text()
        except Exception as e:
            print(f"获取选中文本时出错: {e}")
            text = ""
            
        # 格式化文本并返回     
        text = self.__format_text(text)
        if text:
            print(f"获取到 {len(text)} 个字符")
        else:
            print("未获取到文本")
            
        return text
    
    def __format_text(self, text):
        # 去除首尾空格
        # while text and text[0] in " \n\t\r.": text = text[1:]
        # while text and text[-1] in " \n\t\r.": text = text[:-1]
        return text or ""