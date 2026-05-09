def build_memory_map(memory_manager):
    blocks = []

    # Add allocated segments
    for proc_name, seg in memory_manager.allocated:
        blocks.append({
            "start": seg.start,
            "end": seg.start + seg.size,
            "label": f"{proc_name}:{seg.name}"
        })

    # Add holes
    for hole in memory_manager.holes:
        blocks.append({
            "start": hole.start,
            "end": hole.start + hole.size,
            "label": "HOLE"
        })

    # Sort by memory address
    blocks.sort(key=lambda b: b["start"])

    return blocks

def print_memory_map(memory_manager):
    print("\n=== Memory Layout ===")

    blocks = build_memory_map(memory_manager)

    for block in blocks:
        print(f"[{block['start']} - {block['end']}]  {block['label']}")

def print_segment_table(memory_manager):
    print("\n=== Segment Table ===")

    processes = {}

    for proc_name, seg in memory_manager.allocated:
        if proc_name not in processes:
            processes[proc_name] = []
        processes[proc_name].append(seg)

    for proc, segs in processes.items():
        print(f"\nProcess {proc}:")
        for s in segs:
            print(f"  {s.name} -> Start: {s.start}, Size: {s.size}")