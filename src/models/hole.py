class Hole:
    def __init__(self, start, size):
        self.start = start
        self.size = size

    def __repr__(self):
        return f"Hole(start={self.start}, size={self.size})"