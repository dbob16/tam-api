class ItemNotFound(Exception):
    def __init__(self, message:str):
        super().__init__()
        self.message = message
        print(self.message)