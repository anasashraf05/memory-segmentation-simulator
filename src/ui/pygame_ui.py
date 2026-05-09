import pygame
from models.hole import Hole
from models.process import Process
from models.segment import Segment
from core.memory_manager import MemoryManager
from utils.visualization import build_memory_map

# ====== THEME COLORS ======
COLOR_BG = (240, 244, 248)      
COLOR_PANEL = (44, 62, 80)      
COLOR_ACCENT = (52, 152, 219)   
COLOR_SUCCESS = (46, 204, 113)  
COLOR_DANGER = (231, 76, 60)    
COLOR_WHITE = (255, 255, 255)
COLOR_TEXT_DARK = (33, 37, 41)
COLOR_HOLE = (189, 195, 199)    

pygame.init()

WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Segmentation Simulator")

# Fonts
font_main = pygame.font.SysFont("Segoe UI", 22, bold=True)
font_label = pygame.font.SysFont("Segoe UI", 18)
font_small = pygame.font.SysFont("Segoe UI", 16)

# ====== UI COMPONENTS ======
class InputBox:
    def __init__(self, x, y, w, h, numeric=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.numeric = numeric

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                self.active = False
            elif not self.numeric or event.unicode.isdigit() or (event.unicode == '-' and not self.text):
                self.text += event.unicode

    def draw(self, screen, label=""):
        if label:
            lbl = font_label.render(label, True, COLOR_WHITE if self.rect.y < 110 else COLOR_TEXT_DARK)
            screen.blit(lbl, (self.rect.x, self.rect.y - 22))
        color = COLOR_ACCENT if self.active else (180, 180, 180)
        pygame.draw.rect(screen, COLOR_WHITE, self.rect, border_radius=5)
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=5)
        txt = font_label.render(self.text, True, COLOR_TEXT_DARK)
        screen.blit(txt, (self.rect.x + 8, self.rect.y + (self.rect.h - txt.get_height())//2))

class Button:
    def __init__(self, x, y, w, h, text, color=COLOR_ACCENT):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.base_color = color
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

    def draw(self, screen):
        color = tuple(min(255, c + 30) for c in self.base_color) if self.hovered else self.base_color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 1, border_radius=8)
        txt = font_small.render(self.text, True, COLOR_WHITE)
        screen.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))

# ====== STATE CONSTANTS ======
S_MEM_INPUT, S_HOLE_INPUT, S_PROC_NAME, S_ACTION_CHOICE, S_SEG_COUNT, S_SEG_DETAILS, S_ALLOC_METHOD, S_MESSAGE = range(8)

def run_pygame():
    global mm
    mm = None
    state = S_MEM_INPUT
    message = ""
    current_proc_name = ""
    temp_segments, seg_idx, seg_count_needed = [], 0, 0

    # UI Elements Initialization
    mem_box = InputBox(30, 55, 150, 35, numeric=True)
    btn_init = Button(190, 55, 130, 35, "Initialize", (39, 174, 96))
    
    hole_start = InputBox(400, 55, 100, 35, numeric=True)
    hole_size = InputBox(510, 55, 100, 35, numeric=True)
    btn_add_hole = Button(620, 55, 110, 35, "Add Hole", (230, 126, 34))
    btn_start_runtime = Button(840, 55, 130, 35, "Start Runtime", COLOR_ACCENT)

    # Reset Button (The "Finish" Button)
    btn_reset = Button(WIDTH - 150, 10, 130, 30, "Finish/Restart", COLOR_DANGER)

    proc_box = InputBox(30, HEIGHT - 70, 200, 35)
    btn_next = Button(250, HEIGHT - 70, 100, 35, "Confirm")
    
    btn_allocate = Button(30, HEIGHT - 70, 180, 40, "Allocate Process", COLOR_SUCCESS)
    btn_dealloc = Button(220, HEIGHT - 70, 180, 40, "Deallocate", COLOR_DANGER)
    
    btn_alloc_first = Button(30, HEIGHT - 70, 180, 40, "First-Fit", COLOR_ACCENT)
    btn_alloc_best = Button(220, HEIGHT - 70, 180, 40, "Best-Fit", COLOR_ACCENT)
    
    seg_count_box = InputBox(30, HEIGHT - 70, 150, 35, numeric=True)
    seg_name_box = InputBox(30, HEIGHT - 70, 150, 35)
    seg_size_box = InputBox(190, HEIGHT - 70, 100, 35, numeric=True)
    btn_add_seg = Button(310, HEIGHT - 70, 120, 35, "Add Segment")
    
    btn_ok = Button(450, HEIGHT - 80, 100, 40, "OK", COLOR_PANEL)

    clock = pygame.time.Clock()
    running = True

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: running = False

            # Reset Logic
            if btn_reset.handle_event(event):
                mm = None
                state = S_MEM_INPUT
                message = "System Reset."
                current_proc_name = ""
                temp_segments, seg_idx, seg_count_needed = [], 0, 0
                mem_box.text = ""; hole_start.text = ""; hole_size.text = ""
                proc_box.text = ""; seg_count_box.text = ""

            if state == S_MEM_INPUT: mem_box.handle_event(event)
            elif state == S_HOLE_INPUT: hole_start.handle_event(event); hole_size.handle_event(event)
            elif state == S_PROC_NAME: proc_box.handle_event(event)
            elif state == S_SEG_COUNT: seg_count_box.handle_event(event)
            elif state == S_SEG_DETAILS: seg_name_box.handle_event(event); seg_size_box.handle_event(event)

            # State Transitions
            if state == S_MEM_INPUT and btn_init.handle_event(event):
                if mem_box.text.isdigit() and int(mem_box.text) > 0:
                    mm = MemoryManager(int(mem_box.text))
                    state = S_HOLE_INPUT
                    message = "Memory Ready. Add Holes."
                else: message = "Invalid Memory Size"

            elif state == S_HOLE_INPUT:
                if btn_add_hole.handle_event(event):
                    if hole_start.text.isdigit() and hole_size.text.isdigit():
                        h = Hole(int(hole_start.text), int(hole_size.text))
                        if 0 <= h.start and h.start + h.size <= mm.total_size:
                            overlap = any(not (h.start + h.size <= ex.start or h.start >= ex.start + ex.size) for ex in mm.holes)
                            if not overlap:
                                mm.holes.append(h)
                                mm.holes.sort(key=lambda x: x.start)
                                hole_start.text = ""; hole_size.text = ""
                                message = "Hole added successfully."
                            else: message = "Overlap Error."
                        else: message = "Bounds Error."
                elif btn_start_runtime.handle_event(event):
                    state, message = S_PROC_NAME, "Runtime Started."

            elif state == S_PROC_NAME and btn_next.handle_event(event):
                if proc_box.text.strip():
                    current_proc_name = proc_box.text.strip()
                    state = S_ACTION_CHOICE
                else: message = "Name required."

            elif state == S_ACTION_CHOICE:
                if btn_dealloc.handle_event(event):
                    success, msg = mm.deallocate(current_proc_name)
                    message, state = msg, S_MESSAGE
                elif btn_allocate.handle_event(event):
                    state, message = S_SEG_COUNT, f"Configuring {current_proc_name}"

            elif state == S_SEG_COUNT and btn_next.handle_event(event):
                if seg_count_box.text.isdigit() and int(seg_count_box.text) > 0:
                    seg_count_needed = int(seg_count_box.text)
                    seg_idx, temp_segments, state = 0, [], S_SEG_DETAILS
                else: message = "Invalid Count."

            elif state == S_SEG_DETAILS and btn_add_seg.handle_event(event):
                if seg_name_box.text.strip() and seg_size_box.text.isdigit():
                    temp_segments.append(Segment(seg_name_box.text.strip(), int(seg_size_box.text)))
                    seg_idx += 1
                    seg_name_box.text = ""; seg_size_box.text = ""
                    if seg_idx >= seg_count_needed: state = S_ALLOC_METHOD
                else: message = "Invalid input."

            elif state == S_ALLOC_METHOD:
                p = Process(current_proc_name)
                p.segments = temp_segments[:]
                if btn_alloc_first.handle_event(event):
                    success, msg = mm.allocate_first_fit(p)
                    message, state = msg, S_MESSAGE
                elif btn_alloc_best.handle_event(event):
                    success, msg = mm.allocate_best_fit(p)
                    message, state = msg, S_MESSAGE

            elif state == S_MESSAGE and btn_ok.handle_event(event):
                current_proc_name = ""; proc_box.text = ""; state = S_PROC_NAME; message = ""

        # ====== DRAWING ======
        screen.fill(COLOR_BG)
        pygame.draw.rect(screen, COLOR_PANEL, (0, 0, WIDTH, 110))
        btn_reset.draw(screen) # Always available
        
        if state <= S_HOLE_INPUT:
            mem_box.draw(screen, "Total Memory")
            btn_init.draw(screen)
            hole_start.draw(screen, "Hole Start")
            hole_size.draw(screen, "Hole Size")
            btn_add_hole.draw(screen)
            btn_start_runtime.draw(screen)

        if mm:
            # Memory Map
            map_rect = pygame.Rect(20, 130, 380, HEIGHT - 280)
            pygame.draw.rect(screen, COLOR_WHITE, map_rect, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 200), map_rect, 2, border_radius=10)
            
            blocks = build_memory_map(mm)
            draw_y, draw_h_max = 180, map_rect.height - 70
            for block in blocks:
                size = block["end"] - block["start"]
                h = max(6, int((size / mm.total_size) * draw_h_max))
                b_rect = pygame.Rect(40, draw_y, 340, h)
                color = COLOR_HOLE if block["label"] == "HOLE" else COLOR_ACCENT
                pygame.draw.rect(screen, color, b_rect, border_radius=3)
                pygame.draw.rect(screen, COLOR_PANEL, b_rect, 1, border_radius=3)
                if h > 20:
                    lbl = font_small.render(f"{block['label']} ({block['start']}-{block['end']})", True, COLOR_TEXT_DARK)
                    screen.blit(lbl, (50, draw_y + (h - lbl.get_height())//2))
                draw_y += h

            # Segment Table
            tab_rect = pygame.Rect(420, 130, 560, HEIGHT - 280)
            pygame.draw.rect(screen, COLOR_WHITE, tab_rect, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 200), tab_rect, 2, border_radius=10)
            
            tx, ty = 440, 185
            procs = {}
            for p_n, s in mm.allocated: procs.setdefault(p_n, []).append(s)
            for p_n, ss in procs.items():
                p_lbl = font_main.render(f"Process: {p_n}", True, COLOR_ACCENT)
                screen.blit(p_lbl, (tx, ty)); ty += 30
                for s in ss:
                    stxt = font_small.render(f"• {s.name:12} | Base: {s.start:5} | Size: {s.size:5}", True, COLOR_TEXT_DARK)
                    screen.blit(stxt, (tx + 20, ty)); ty += 22
                ty += 10
                if ty > HEIGHT - 200: break

        # Footer Panel
        pygame.draw.rect(screen, (225, 230, 235), (0, HEIGHT - 130, WIDTH, 130))
        if message:
            m_color = COLOR_SUCCESS if "success" in message.lower() or "allocated" in message.lower() else COLOR_DANGER
            m_txt = font_label.render(message, True, m_color)
            screen.blit(m_txt, (WIDTH - m_txt.get_width() - 30, HEIGHT - 115))

        if state == S_PROC_NAME:
            proc_box.draw(screen, "Process Name")
            btn_next.draw(screen)
        elif state == S_ACTION_CHOICE:
            btn_allocate.draw(screen); btn_dealloc.draw(screen)
        elif state == S_SEG_COUNT:
            seg_count_box.draw(screen, "Number of Segments")
            btn_next.draw(screen)
        elif state == S_SEG_DETAILS:
            seg_name_box.draw(screen, "Segment Name"); seg_size_box.draw(screen, "Size")
            btn_add_seg.draw(screen)
        elif state == S_ALLOC_METHOD:
            btn_alloc_first.draw(screen); btn_alloc_best.draw(screen)
        elif state == S_MESSAGE:
            btn_ok.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()