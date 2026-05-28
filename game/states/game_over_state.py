# ============================================================
#  ELDORIA GAME - ESTADO: GAME OVER
# ============================================================

import pygame
import math
import random
from utils.game_state_manager import BaseState
from utils.constants    import *
from utils.ui           import draw_text, draw_panel, Button, StarField


class GameOverState(BaseState):

    def enter(self, data: dict = None):
        data           = data or {}
        self._t        = 0.0
        self._stars    = StarField(80)
        self._alpha    = 0.0
        self._dica     = data.get("dica", "")
        self._inimigo  = data.get("inimigo", "Inimigo")

        # Partículas de derrota (cinza/vermelho caindo)
        self._particles = [
            {
                "x":    float(random.randint(0, SCREEN_WIDTH)),
                "y":    float(random.randint(-50, SCREEN_HEIGHT)),
                "vy":   random.uniform(30, 90),
                "vx":   random.uniform(-15, 15),
                "color": random.choice([(180, 30, 30), (100, 100, 100), (220, 60, 60)]),
                "r":    random.randint(2, 5),
                "alpha": random.uniform(0.5, 1.0),
            }
            for _ in range(50)
        ]

        self._btn_tentar = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 260, SCREEN_HEIGHT - 100, 240, 55),
            "↺ Tentar Novamente", color=(120, 30, 30), hover_color=RED,
            font_size=FONT_MEDIUM
        )
        self._btn_inicio = Button(
            pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 100, 240, 55),
            "⌂ Tela Inicial", color=(40, 30, 80), hover_color=PRIMARY,
            font_size=FONT_MEDIUM
        )

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        self._btn_tentar.update((mx, my))
        self._btn_inicio.update((mx, my))

        for e in events:
            if self._btn_tentar.is_clicked(e):
                self._reiniciar()
            if self._btn_inicio.is_clicked(e):
                self._ir_inicio()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    self._reiniciar()
                elif e.key == pygame.K_ESCAPE:
                    self._ir_inicio()

    def _reiniciar(self):
        # Reseta progresso e volta à seleção de herói
        self.manager.progresso     = 0
        self.manager.heroi         = None
        self.manager.inimigo_atual = ""
        self.go_to(STATE_HERO_SELECT)

    def _ir_inicio(self):
        self.manager.progresso     = 0
        self.manager.heroi         = None
        self.manager.inimigo_atual = ""
        self.go_to(STATE_INTRO)

    def update(self, dt: float):
        self._t     += dt
        self._alpha  = min(1.0, self._alpha + dt * 0.8)
        self._stars.update(dt)

        for p in self._particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            if p["y"] > SCREEN_HEIGHT + 20:
                p["y"] = float(random.randint(-40, -5))
                p["x"] = float(random.randint(0, SCREEN_WIDTH))

    def draw(self, surface: pygame.Surface):
        surface.fill((8, 0, 0))
        self._stars.draw(surface)

        # Partículas de derrota
        for p in self._particles:
            r = max(1, p["r"])
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p["color"], int(p["alpha"] * 180)),
                               (r, r), r)
            surface.blit(s, (int(p["x"] - r), int(p["y"] - r)))

        # Overlay de fade
        if self._alpha < 1.0:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            ov.fill((8, 0, 0))
            ov.set_alpha(int((1.0 - self._alpha) * 255))
            surface.blit(ov, (0, 0))

        # Título pulsante
        pulse = int(abs(math.sin(self._t * 1.5)) * 20)
        draw_text(surface, "GAME OVER",
                  SCREEN_WIDTH // 2, 70,
                  size=FONT_HUGE, color=(200 + pulse, 30, 30),
                  bold=True, center=True)

        draw_text(surface, f"Você foi derrotado por {self._inimigo}.",
                  SCREEN_WIDTH // 2, 145,
                  size=FONT_MEDIUM, color=ORANGE, center=True)

        # Painel de dica Python
        if self._dica:
            panel = pygame.Rect(80, 185, SCREEN_WIDTH - 160, 320)
            draw_panel(surface, panel, bg_color=(20, 5, 30),
                       border_color=(120, 40, 40), border_width=2, alpha=230)

            draw_text(surface, "— O QUE ESTUDAR PARA A PRÓXIMA VEZ —",
                      SCREEN_WIDTH // 2, panel.y + 18,
                      size=FONT_SMALL, color=(180, 100, 100),
                      bold=True, center=True)

            pygame.draw.line(surface, (100, 40, 40),
                             (panel.x + 20, panel.y + 42),
                             (panel.x + panel.width - 20, panel.y + 42), 1)

            y = panel.y + 55
            for line in self._dica.split('\n'):
                # Linhas de código têm destaque diferente
                col = CYAN if line.strip().startswith(('d ', 'print', 'with', 'matriz', '#')) else WHITE
                if '💡' in line:
                    col = GOLD
                draw_text(surface, line,
                          panel.x + 30, y,
                          size=FONT_SMALL, color=col, shadow=True)
                y += FONT_SMALL + 7

        draw_text(surface, "[ R ] Tentar Novamente   [ ESC ] Menu Inicial",
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT - 135,
                  size=FONT_TINY, color=GRAY, center=True)

        self._btn_tentar.draw(surface)
        self._btn_inicio.draw(surface)