class Segment:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.start = None

    def __repr__(self):
        return f"{self.name} (size={self.size}, start={self.start})"