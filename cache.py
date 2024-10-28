import time
import pickle

class Cache():
    def __init__(self, path='cache.pkl', max_size=1000, frequency=20):
        print("Cache loaded")
        # 缓存文件路径
        self.path = path
        # 最大容量
        self.max_size = max_size
        # 数据持久化频率
        self.frequency = frequency
        try:
            self.load()
        except:
            self.cache = {}
        self.count = 0
     
    def set(self, key, value):

        if len(self.cache) > self.max_size:
            while len(self.cache) > self.max_size*4/5:
                self.cache.pop(next(iter(self.cache)))
        self.cache[key] = (time.time(), value)
        self.count += 1
        if self.count > self.frequency:
            self.save()
            self.count = 0

    def get(self, key, gap=3):
        # 两次请求时间间隔小于3秒，返回None
        if key not in self.cache:
            return None
        elif time.time() - self.cache[key][0] < gap:
            self.cache[key] = (time.time(), self.cache[key][1])
            return None
        else:
            self.cache[key] = (time.time(), self.cache[key][1])
            return self.cache[key][1]
    
    def save(self):
        start_time = time.time()
        with open(self.path, "wb") as f:
            pickle.dump(self.cache, f)
            print(f"Cache saved in {time.time()-start_time:.2f} seconds")
    def load(self):
        with open(self.path, "rb") as f:
            self.cache = pickle.load(f)

