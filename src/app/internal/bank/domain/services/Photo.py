class Photo:
    def __init__(self, unique_name: str, content: bytes, size: int):
        self.unique_name = unique_name
        self.content = content
        self.size = size
