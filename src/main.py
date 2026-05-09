from models.hole import Hole
from models.process import Process
from models.segment import Segment

def main():
    holes = [Hole(0, 1000)]

    p1 = Process("P1")
    p1.add_segment(Segment("Code", 100))
    p1.add_segment(Segment("Data", 200))

    print("Holes:", holes)
    print("Process:", p1)

if __name__ == "__main__":
    main()