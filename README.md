# Memory Segmentation Simulator

A Python-based simulation of memory allocation using **Segmentation** with support for:

- First-Fit Allocation
- Best-Fit Allocation
- Dynamic allocation & deallocation
- Hole merging
- Real-time memory visualization (Pygame UI)

---

##  Features

- Interactive GUI 
- Add memory holes dynamically
- Create processes with multiple segments
- Allocate using First-Fit or Best-Fit
- Deallocate processes with automatic hole merging
- Live memory layout visualization
- Segment table display per process

---

##  Concepts Implemented

- Memory Segmentation
- Dynamic Storage Allocation
- External Fragmentation Handling
- Allocation Algorithms (First-Fit, Best-Fit)

---

## 📁 Project Structure
src/
├── core/ # Memory management logic
├── models/ # Data structures (Hole, Segment, Process)
├── ui/ # Pygame GUI
├── utils/ # Visualization helpers
└── main.py

## ▶️ How to Run
-First option
exe file link: https://drive.google.com/drive/folders/1G60ZGInXsYCz4oNjQWLZ6fYBWZntMSXT?usp=sharing

-second from VS
```bash
pip install pygame
python src/ui/pygame_ui.py
