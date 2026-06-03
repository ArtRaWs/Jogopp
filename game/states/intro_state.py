# ============================================================
#  ELDORIA GAME - ESTADO: INTRODUÇÃO
# ============================================================

import pygame
import os
from utils.game_state_manager import BaseState
from utils.constants    import *
from utils.ui           import draw_text, draw_panel, StarField, get_font


class IntroState(BaseState):

    def _asset_path(self, filename: str) -> str:
        game_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(game_dir, "assets", filename)

    def enter(self, data: dict = None):
        self._stars    = StarField(120)
        self._t        = 0.0
        self._line_idx = 0
        self._lines    = LORE_LINES
        self._alpha    = 0.0            # fade-in da tela
        self._flash    = 0.0            # blink no "ENTER"
        self._overlay  = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Fundo (inicio.png)
        self._bg = None
        try:
            path = self._asset_path("inicio.png")
            self._bg = pygame.image.load(path).convert()
            self._bg = pygame.transform.smoothscale(self._bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception:
            self._bg = None

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                self.go_to(STATE_HERO_SELECT)
            if e.type == pygame.MOUSEBUTTONDOWN:
                self.go_to(STATE_HERO_SELECT)

    def update(self, dt: float):
        self._t     += dt
        self._flash += dt
        self._stars.update(dt)
        if self._alpha < 1.0:
            self._alpha = min(1.0, self._alpha + dt * 0.6)

    def draw(self, surface: pygame.Surface):
        if self._bg:
            surface.blit(self._bg, (0, 0))
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 130))
            surface.blit(ov, (0, 0))
        else:
            surface.fill(DARK_BG)
            self._stars.draw(surface)

        # ── Título do jogo ────────────────────────────────────
        import math
        pulse = int(abs(math.sin(self._t * 0.8)) * 30)
        title_col = (80 + pulse, 100 + pulse, 255)
        draw_text(surface, "Atrinium",
                  SCREEN_WIDTH // 2, 60,
                  size=FONT_TITLE, color=title_col,
                  bold=True, center=True)

        # ── Separador ─────────────────────────────────────────
        pygame.draw.line(surface, PANEL_BORDER,
                         (80, 135), (SCREEN_WIDTH - 80, 135), 1)

        # ── Texto de lore ─────────────────────────────────────
        panel = pygame.Rect(80, 150, SCREEN_WIDTH - 160, 520)
        draw_panel(surface, panel, alpha=160)

        font  = get_font(FONT_MEDIUM)
        y     = 175
        alpha = int(self._alpha * 255)

        for i, line in enumerate(self._lines):
            if not line:
                y += 12
                continue

            if "[ Pressione" in line:
                blink = int(abs(math.sin(self._flash * 2.5)) * 255)
                col   = (blink, blink, 80)
                draw_text(surface, line,
                          SCREEN_WIDTH // 2, y,
                          size=FONT_MEDIUM, color=col,
                          center=True, shadow=True)
            else:
                # Renderiza com fade
                srf = font.render(line, True, WHITE)
                srf.set_alpha(alpha)
                rx  = SCREEN_WIDTH // 2 - srf.get_width() // 2
                surface.blit(srf, (rx, y))

            y += font.get_height() + 4

        # ── Fade overlay ──────────────────────────────────────
        if self._alpha < 1.0:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            ov.fill(DARK_BG)
            ov.set_alpha(int((1.0 - self._alpha) * 255))
            surface.blit(ov, (0, 0))