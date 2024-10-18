import openai
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

class Translator(QThread):
    signal = pyqtSignal(str)
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
        assert self.api_key, "API Key is required."
        assert self.base_url, "API URL is required."
        assert self.default_headers, "API Headers is required."
        assert self.model, "Model is required."
        assert self.prompt, "Prompt is required."
        openai.api_key = self.api_key
        openai.base_url = self.base_url
        openai.default_headers = self.default_headers
        print(f"request")
        res = openai.chat.completions.create(
          model=self.model,
          messages=[{"role": "system", "content": self.prompt}, {"role": "user", "content": self.text}]
        )
        self.signal.emit(res.choices[0].message.content)
      except Exception as e:
        print(e)
        self.signal.emit(f'@An error occurred:{str(e)}')
