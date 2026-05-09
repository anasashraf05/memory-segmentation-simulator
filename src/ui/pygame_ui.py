import pygame
from utils.visualization import build_memory_map

WIDTH = 400
HEIGHT = 700


def draw_memory(screen, memory_manager):
    blocks = build_memory_map(memory_manager)

    total = memory_manager.total_size
    y = 0

    for block in blocks:
        block_size = block["end"] - block["start"]
        height = int((block_size / total) * HEIGHT)

        rect = pygame.Rect(50, y, 300, height)

        # Colors
        if block["label"] == "HOLE":
            color = (200, 200, 200)
        else:
            color = (100, 150, 255)

        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)

        # Text
        font = pygame.font.SysFont(None, 20)
        text = font.render(block["label"], True, (0, 0, 0))
        screen.blit(text, (60, y + 5))

        y += height


def run_pygame(memory_manager):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Memory Visualization")

    running = True
    while running:
        screen.fill((255, 255, 255))

        draw_memory(screen, memory_manager)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()

    pygame.quit()