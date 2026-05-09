from core.memory_manager import MemoryManager
from models.hole import Hole
from models.process import Process
from models.segment import Segment
from utils.visualization import print_memory_map, print_segment_table
from ui.pygame_ui import run_pygame

def safe_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print(" Invalid number. Try again.")

# Define function AT MODULE LEVEL (before run_cli)
def allocate_process(mm):
    name = input("Process name: ")
    p = Process(name)


    n = safe_int("Number of segments: ")
    for _ in range(n):
        seg_name = input("Segment name: ")
        seg_size = safe_int("Segment size: ")
        p.add_segment(Segment(seg_name, seg_size))

    method = input("Method (first/best): ").lower()

    if method == "first":
        result = mm.allocate_first_fit(p)
    elif method == "best":
        result = mm.allocate_best_fit(p)
    else:
        print(" Invalid method. Use 'first' or 'best'.")
        return

    # Handle tuple returns
    success, message = result
    if success:
        print(f" {message}")
    else:
        print(f" {message}")
    

def is_valid_hole(new_hole, holes, total_size):
    # Check bounds
    if new_hole.start < 0 or new_hole.size <= 0:
        return False

    if new_hole.start + new_hole.size > total_size:
        return False

    # Check overlap
    for h in holes:
        if not (new_hole.start + new_hole.size <= h.start or
                new_hole.start >= h.start + h.size):
            return False

    return True

def run_cli():
    print("=== Memory Segmentation Simulator ===")
    
    total = safe_int("Enter total memory size: ")
    mm = MemoryManager(total)

    n = safe_int("Enter number of holes: ")
    added = 0
    while added < n:
        print(f"\n Hole {added + 1}:")
        start = safe_int("  Start address: ")
        size = safe_int("  Size: ")
        hole = Hole(start, size)

        if is_valid_hole(hole, mm.holes, mm.total_size):
            mm.holes.append(hole)
            added += 1
            print(" Hole added.")
        else:
            print(" Invalid hole (out of bounds or overlaps). Try again.")
            
    # Ensure holes are sorted for consistent merging
    mm.holes.sort(key=lambda h: h.start)
    
    while True:
        print("\n1. Allocate Process")
        print("2. Deallocate Process")
        print("3. Show Memory")
        print("4. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            allocate_process(mm)  #  Now safely callable
        elif choice == "2":
            name = input("Process name to deallocate: ")
            success, message = mm.deallocate(name)
            print(f" {message}")
        elif choice == "3":
            mm.print_status()
            print_memory_map(mm)
            print_segment_table(mm)
            run_pygame(mm)
        elif choice == "4":
            print(" Exiting simulator.")
            break
        else:
            print(" Invalid choice. Enter 1-4.")
