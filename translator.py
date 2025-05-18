from PyQt5.QtCore import QThread, pyqtSignal
from cache import Cache
from api import openai_request

class Translator(QThread):
    signal = pyqtSignal(str)
    cache:Cache = None
    
    def __init__(self, text:str, api_key=None, base_url=None, model="gpt-4.1-nano", prompt="Translate the following text to Chinese:"):
        super().__init__()
        assert self.cache is not None, "Cache not initialized. Please set Translator.cache first."
        self.text = text
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.prompt = prompt
        self.is_terminated = False
      
    def run(self):
        try:
            # 检查是否被终止
            if self.is_terminated:
                return
                
            # 检查缓存
            cache_text = self.__class__.cache.get(self.text, gap=3)
            if cache_text:
                self.signal.emit(cache_text)
                return
                
            # 如果没有API密钥，提示错误
            if not self.api_key:
                self.signal.emit('@An error occurred:API密钥未设置，请在设置中配置API。\n ')
                return
                
            # 如果没有基础URL，提示错误
            if not self.base_url:
                self.signal.emit('@An error occurred:API基础URL未设置，请在设置中配置。\n ')
                return
                
            # 确保base_url以斜杠结尾
            if not self.base_url.endswith('/'):
                self.base_url += '/'
                
            # 请求API
            completion_stream = openai_request(
                self.text, 
                self.api_key, 
                self.base_url, 
                self.model, 
                self.prompt, 
                Structured=False
            )
            
            response_content = ""
            n = 0
            for chunk in completion_stream:
                # 检查是否被终止
                if self.is_terminated:
                    return
                    
                try:
                    content = chunk.choices[0].delta.content or ""
                    response_content += content
                    if n % 3 == 0:
                        self.signal.emit(response_content)
                    n += 1
                except Exception as e:
                    print(f"Error processing chunk: {e}")
                    print(f"Chunk content: {chunk}")
                    
            print(f"Translated text\n----{response_content}\n----")
            self.signal.emit(response_content)
            # 保存到缓存
            self.__class__.cache.set(self.text, response_content)
            
        except Exception as e:
            if not self.is_terminated:  # 只有在非主动终止的情况下才报错
                print(f"Translation error: {e}")
                self.signal.emit(f'@An error occurred:{str(e)}\n ')
    
    def terminate(self):
        """重写terminate方法，添加标志位"""
        self.is_terminated = True
        super().terminate()