from PyQt5.QtCore import QThread, pyqtSignal
from cache import Cache

from api import openai_request

class Translator(QThread):
    signal = pyqtSignal(str)
    cache = Cache()
    def __init__(self, text:str, api_key=None, base_url=None, default_headers={"x-foo": "true"}, model="gpt-3.5-turbo", prompt="Translate the following text to Chinese:"):
      self.text = text
      self.api_key = api_key
      self.base_url = base_url
      self.default_headers = default_headers
      self.model = model
      self.prompt = prompt
      super().__init__()
      
    def run(self):
      try:
        # cache
        cache_text = self.__class__.cache.get(self.text, gap=3)
        if cache_text:
          self.signal.emit(cache_text)
          return

        completion_stream = openai_request(self.text, self.api_key, self.base_url, self.default_headers, self.model, self.prompt, Structured=False)
        response_content = ""
        n = 0
        for chunk in completion_stream:
          try:
            response_content += chunk.choices[0].delta.content or ""
            if n % 3 == 0:
              self.signal.emit(response_content)
            n += 1
          except Exception as e:
            print(e)
            print(chunk)
        print(f"Translated text\n----{response_content}\n----")
        self.signal.emit(response_content)
        self.__class__.cache.set(self.text, response_content)
      except Exception as e:
        print(e)
        self.signal.emit(f'@An error occurred:{str(e)}\n ')
        

