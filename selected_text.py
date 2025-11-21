import time
import threading
import pyperclip
from win32api import keybd_event

def get_selected_text_by_clipboard():
    """
    通过剪贴板获取选中的文本
    
    当直接API方法失败时，这是一个后备方法。使用剪贴板，但会小心处理。
    
    参数:
        restore_clipboard: 是否恢复原始剪贴板内容(默认为True)
    
    返回:
        选中的文本，如果没有选中文本则返回None
    """
    try:
        
        old_clipboard = pyperclip.paste()

        
        # 清空剪贴板
        pyperclip.copy("")
        
        # 发送 Ctrl+C 复制选中的文本
        # 使用win32api代替keybd_event以提高可靠性
        keybd_event(0x11, 0, 0, 0)  # Ctrl 按下
        keybd_event(0x43, 0, 0, 0)  # C 按下
        keybd_event(0x43, 0, 2, 0)  # C 释放
        keybd_event(0x11, 0, 2, 0)  # Ctrl 释放
        
        # 等待剪贴板更新 (增加等待时间以防复杂应用响应慢)
        # 获取复制的文本
        text = ""
        for _ in range(10):
            time.sleep(0.02)
            text = pyperclip.paste()
            if text:
                break
            
        # 恢复原始剪贴板
        def restore(old_clipboard):
            time.sleep(0.2) # 等待应用读取完复制的内容
            pyperclip.copy(old_clipboard)
        threading.Thread(target=restore, args=(old_clipboard,), daemon=True).start()
           
        return text
        
    except Exception as e:
        print(f"剪贴板获取文本时出错: {e}")
        return None


def get_selected_text():
    """
    获取选中文本
    
    返回:
        选中的文本，如果所有方法都失败则返回空字符串
    """

    text = get_selected_text_by_clipboard()
        
    if text:
        print(f"成功获取到 {len(text)} 个字符")
    else:
        print("未能获取到任何文本")
        
    return text or ""

if __name__ == "__main__":
    # 直接测试模块
    print("请选择一些文本并按回车键...")
    input()
    text = get_selected_text()
    print(f"选中的文本: {text}")