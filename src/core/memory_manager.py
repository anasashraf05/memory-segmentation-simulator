from models.hole import Hole
from typing import Tuple

class MemoryManager:
    def __init__(self, total_size: int):
        if total_size <= 0:
            raise ValueError("Total memory size must be positive.")
        self.total_size = total_size
        self.holes = []
        self.allocated = []  # List of (process_name, segment)

    def allocate_first_fit(self, process) -> Tuple[bool, str]:
        print(f"\n[First-Fit] Attempting to allocate {process.name}")
        if not process.segments:
            print(f" Process {process.name} has no segments. Nothing to allocate.")
            return True, "No segments to allocate"

        # Deep copy for safe rollback
        original_holes = [Hole(h.start, h.size) for h in self.holes]
        temp_allocated = []

        for segment in process.segments:
            if segment.size <= 0:
                print(f" Segment '{segment.name}' has invalid size ({segment.size}). Skipping.")
                continue

            allocated = False
            for i, hole in enumerate(self.holes):
                if hole.size >= segment.size:
                    segment.start = hole.start
                    temp_allocated.append((process.name, segment))
                    hole.start += segment.size
                    hole.size -= segment.size

                    if hole.size == 0:
                        self.holes.pop(i)  # Safe removal during iteration
                    allocated = True
                    break

            if not allocated:
                print(f" Process {process.name} cannot fit segment '{segment.name}' (needs {segment.size}).")
                self.holes = original_holes  # Rollback
                # Reset partially allocated segments
                for _, seg in temp_allocated:
                    seg.start = None
                return False, "Failed"

        self.allocated.extend(temp_allocated)
        return True, "Allocated successfully"

    def allocate_best_fit(self, process) -> Tuple[bool, str]:
        print(f"\n[Best-Fit] Attempting to allocate {process.name}")
        if not process.segments:
            print(f" Process {process.name} has no segments. Nothing to allocate.")
            return True, "No segments to allocate"

        original_holes = [Hole(h.start, h.size) for h in self.holes]
        temp_allocated = []

        for segment in process.segments:
            if segment.size <= 0:
                print(f" Segment '{segment.name}' has invalid size ({segment.size}). Skipping.")
                continue

            best_hole = None
            best_idx = -1

            for i, hole in enumerate(self.holes):
                if hole.size >= segment.size:
                    if best_hole is None or hole.size < best_hole.size:
                        best_hole = hole
                        best_idx = i

            if best_hole is None:
                print(f" Process {process.name} cannot fit segment '{segment.name}' (needs {segment.size}).")
                self.holes = original_holes
                for _, seg in temp_allocated:
                    seg.start = None
                return False, "Failed"

            segment.start = best_hole.start
            temp_allocated.append((process.name, segment))
            best_hole.start += segment.size
            best_hole.size -= segment.size

            if best_hole.size == 0:
                self.holes.pop(best_idx)

        self.allocated.extend(temp_allocated)
        return True, "Allocated successfully"

    def deallocate(self, process_name: str) -> Tuple[bool, str]:
        print(f"\n[Dealloc] Attempting to deallocate {process_name}")
        segments_to_free = []
        remaining_allocated = []

        for proc_name, segment in self.allocated:
            if proc_name == process_name:
                segments_to_free.append(segment)
            else:
                remaining_allocated.append((proc_name, segment))

        if not segments_to_free:
            print(f" Process {process_name} is not allocated. Nothing to deallocate.")
            return False, "Failed"

        self.allocated = remaining_allocated
        self.holes.extend(Hole(s.start, s.size) for s in segments_to_free)
        self.merge_holes()

        print(f" {process_name} deallocated successfully.")
        return True, "Deallocated successfully"

    def merge_holes(self):
        if not self.holes:
            return

        self.holes.sort(key=lambda h: h.start)
        merged = []

        for hole in self.holes:
            if not merged:
                merged.append(hole)
            else:
                last = merged[-1]
                if last.start + last.size == hole.start:
                    last.size += hole.size
                else:
                    merged.append(hole)

        self.holes = merged

    def print_status(self):
        alloc_size = sum(seg.size for _, seg in self.allocated)
        free_size = sum(h.size for h in self.holes)
        print(f" Status: Total={self.total_size} | Allocated={alloc_size} | Free={free_size} | Holes={self.holes}")