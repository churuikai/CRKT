"""
Windows API 获取选中文本的方法集合
这些函数提供了多种方式来获取当前活动窗口/应用程序中选中的文本，无需总是依赖剪贴板操作。
"""

import time
from win32api import keybd_event
from uiautomation import GetFocusedControl

def get_selected_text_by_clipboard(restore_clipboard=True):
    """
    通过剪贴板获取选中的文本
    
    当直接API方法失败时，这是一个后备方法。使用剪贴板，但会小心处理。
    
    参数:
        restore_clipboard: 是否恢复原始剪贴板内容(默认为True)
    
    返回:
        选中的文本，如果没有选中文本则返回None
    """
    # 使用 pyperclip 作为替代方案，它在处理剪贴板时更可靠
    try:
        import pyperclip
        old_clipboard = ""
        
        if restore_clipboard:
            try:
                old_clipboard = pyperclip.paste()
            except Exception as e:
                print(f"无法获取原有剪贴板内容: {e}")
        
        # 清空剪贴板
        pyperclip.copy("")
        
        # 发送 Ctrl+C 复制选中的文本
        # 使用win32api代替keybd_event以提高可靠性
        keybd_event(0x11, 0, 0, 0)  # Ctrl 按下
        keybd_event(0x43, 0, 0, 0)  # C 按下
        keybd_event(0x43, 0, 2, 0)  # C 释放
        keybd_event(0x11, 0, 2, 0)  # Ctrl 释放
        
        # 等待剪贴板更新 (增加等待时间以防复杂应用响应慢)
        time.sleep(0.1)
        
        # 获取复制的文本
        text = pyperclip.paste() or ""
        
        # 恢复原始剪贴板
        if restore_clipboard and old_clipboard:
            try:
                pyperclip.copy(old_clipboard)
            except Exception as e:
                print(f"无法恢复原有剪贴板内容: {e}")
                
        return text
        
    except ImportError:
        print("未安装pyperclip模块，无法使用剪贴板方法")
        return None
    except Exception as e:
        print(f"剪贴板获取文本时出错: {e}")
        return None

def try_ui_automation():
    """
    尝试使用UI自动化技术获取选中文本。
    需要安装uiautomation包。
    
    返回:
        成功时返回选中的文本，失败时返回None
    """
    try:
        # 获取焦点元素
        element = GetFocusedControl()
        if not element:
            return None
            
        # 尝试使用TextPattern获取选择
        if hasattr(element, 'GetTextPattern'):
            text_pattern = element.GetTextPattern()
            if text_pattern:
                selection = text_pattern.GetSelection()
                if selection:
                    text = ''.join(range.GetText(-1) for range in selection)
                    if text:
                        return text
        
        # 如果TextPattern不可用，尝试使用ValuePattern
        if hasattr(element, 'GetValuePattern'):
            value_pattern = element.GetValuePattern()
            if value_pattern and value_pattern.Value:
                return value_pattern.Value
                
    except ImportError:
        print("未安装uiautomation包，无法使用UI自动化方法")
    except Exception as e:
        print(f"UI自动化获取文本时出错: {e}")
        
    return None

def get_selected_text():
    """
    获取选中文本，使用多种方法依次尝试，直到成功获取
    
    返回:
        选中的文本，如果所有方法都失败则返回空字符串
    """
    # 首先尝试使用UI自动化（如果可用）
    text = try_ui_automation()
        
    # 如果上述方法都失败，使用改进的剪贴板方法
    if not text:
        print("使用剪贴板方法获取选中文本...")
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