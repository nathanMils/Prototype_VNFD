class Stream:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def read(self, n=-1):
        if n == -1:
            result = self.data[self.index:]
            self.index = len(self.data)
        else:
            result = self.data[self.index:self.index + n]
            self.index += n
        return result

    def write(self, data):
        self.data = self.data[:self.index] + data + self.data[self.index + len(data):]
        self.index += len(data)

    def seek(self, index):
        self.index = index

    def tell(self):
        return self.index

    def reset(self):
        self.index = 0