# ============================================================
#  ELDORIA GAME - MAIN
# ============================================================

import pygame
import sys
from utils.constants      import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from utils.game_state_manager import GameManager


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock  = pygame.time.Clock()

    manager = GameManager(screen)
    manager.register_all()
    manager.change_state("intro")

    while True:
        dt     = clock.tick(FPS) / 1000.0
        events = pygame.event.get()

        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        manager.handle_events(events)
        manager.update(dt)
        manager.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()