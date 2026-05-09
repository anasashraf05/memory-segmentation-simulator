class Process:
    def __init__(self, name):
        self.name = name
        self.segments = []

    def add_segment(self, segment):
        self.segments.append(segment)

    def __repr__(self):
        return f"{self.name}: {self.segments}"