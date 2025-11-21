from PyQt5.QtCore import QThread, pyqtSignal
from cache import Cache
import openai

class Translator(QThread):
    signal = pyqtSignal(str)

    def __init__(self, text:str, api_key=None, base_url=None, model="gpt-4.1-nano", prompt="Translate the following text to Chinese:", cache:Cache=None):
        super().__init__()

        self.text = text
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.prompt = prompt
        self.cache = cache
      
    def run(self):
        try:
            # 检查是否被请求中断
            if self.isInterruptionRequested():
                return
                
            # 检查缓存
            cache_text = self.cache.get(self.text, gap=3)
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
                
            # 创建 OpenAI 客户端并请求API
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            completion_stream = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": self.prompt}],
                stream=True,
            )
            
            response_content = ""
            n = 0
            for chunk in completion_stream:
                # 检查是否被请求中断
                if self.isInterruptionRequested():
                    print("翻译线程收到中断请求，正在停止...")
                    return
                    
                try:
                    content = chunk.choices[0].delta.content or ""
                    response_content += content
                    if n < 3 or n % 3 == 0:
                        self.signal.emit(response_content)
                    n += 1
                except Exception as e:
                    print(f"Error processing chunk: {e}")
                    print(f"Chunk content: {chunk}")
                    
            print(f"Translated text\n----{response_content}\n----")
            self.signal.emit(response_content)
            # 保存到缓存
            self.cache.set(self.text, response_content)
            
        except Exception as e:
            # 只有在非主动中断的情况下才报错
            if not self.isInterruptionRequested():
                print(f"Translation error: {e}")
                self.signal.emit(f'@An error occurred:{str(e)}\n ')