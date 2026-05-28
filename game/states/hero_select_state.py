# ============================================================
#  ELDORIA GAME - ESTADO: ESCOLHA DO HERÓI
# ============================================================

import pygame
import math
import os
from utils.game_state_manager import BaseState
from utils.constants          import *
from utils.ui                 import draw_text, draw_panel, Button, StarField, get_font
from classes.Heroi            import criar_arthur, criar_luna


class HeroSelectState(BaseState):

    def _asset_path(self, filename: str) -> str:
        game_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(game_dir, "assets", filename)

    def enter(self, data: dict = None):
        self._stars = StarField(100)
        self._t     = 0.0
        self._hover = None   # 'arthur' | 'luna' | None

        # Fundo (inicio.png)
        self._bg = None
        try:
            path = self._asset_path("inicio.png")
            self._bg = pygame.image.load(path).convert()
            self._bg = pygame.transform.smoothscale(self._bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception:
            self._bg = None

        # Sprites dos heróis (artraws.png e luna.png)
        self._spr_arthur = None
        self._spr_luna   = None
        try:
            self._spr_arthur = pygame.image.load(self._asset_path("artraws.png")).convert_alpha()
        except Exception:
            self._spr_arthur = None
        try:
            self._spr_luna = pygame.image.load(self._asset_path("luna.png")).convert_alpha()
        except Exception:
            self._spr_luna = None

        cw = 340
        ch = 460
        cy = (SCREEN_HEIGHT - ch) // 2 + 30

        self._rect_arthur = pygame.Rect(SCREEN_WIDTH // 2 - cw - 20, cy, cw, ch)
        self._rect_luna   = pygame.Rect(SCREEN_WIDTH // 2 + 20,       cy, cw, ch)

        self._btn_back = Button(
            pygame.Rect(20, 20, 110, 40),
            "← Voltar", color=GRAY_DARK, font_size=FONT_SMALL
        )

        self._arthur = criar_arthur()
        self._luna   = criar_luna()

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        self._hover = None
        if self._rect_arthur.collidepoint(mx, my):
            self._hover = "arthur"
        elif self._rect_luna.collidepoint(mx, my):
            self._hover = "luna"

        for e in events:
            if self._btn_back.is_clicked(e):
                self.go_to(STATE_INTRO)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self._rect_arthur.collidepoint(e.pos):
                    self._selecionar("arthur")
                elif self._rect_luna.collidepoint(e.pos):
                    self._selecionar("luna")

        self._btn_back.update((mx, my))

    def _selecionar(self, tipo: str):
        if tipo == "arthur":
            self.manager.heroi = criar_arthur()
        else:
            self.manager.heroi = criar_luna()
        self.go_to("video")   # ← VAI PARA O VÍDEO antes do prólogo

    def update(self, dt: float):
        self._t += dt
        self._stars.update(dt)

    def draw(self, surface: pygame.Surface):
        if self._bg:
            surface.blit(self._bg, (0, 0))
            # escurece um pouco pra UI ficar legível
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 120))
            surface.blit(ov, (0, 0))
        else:
            surface.fill(DARK_BG)
            self._stars.draw(surface)

        draw_text(surface, "ESCOLHA SEU HERÓI",
                  SCREEN_WIDTH // 2, 38,
                  size=FONT_TITLE, color=GOLD,
                  bold=True, center=True)
        draw_text(surface, "Quem irá restaurar o Grande Código?",
                  SCREEN_WIDTH // 2, 82,
                  size=FONT_SMALL, color=GRAY,
                  center=True)

        self._draw_hero_card(surface, self._arthur, self._rect_arthur, "arthur")
        self._draw_hero_card(surface, self._luna,   self._rect_luna,   "luna")
        self._btn_back.draw(surface)

    def _draw_hero_card(self, surface, heroi, rect, tipo: str):
        hover = (self._hover == tipo)
        pulse = abs(math.sin(self._t * 2.0)) * 20

        border = (heroi.cor[0], heroi.cor[1], heroi.cor[2]) if hover else PANEL_BORDER
        bg     = (35, 25, 65) if hover else (20, 15, 45)

        if hover:
            shadow = pygame.Rect(rect.x - 4, rect.y - 4, rect.width + 8, rect.height + 8)
            pygame.draw.rect(surface, (*heroi.cor, 80), shadow, border_radius=12)

        draw_panel(surface, rect, bg_color=bg, border_color=border, border_width=3, alpha=240)

        cx = rect.centerx
        cy = rect.y + 20

        sprite_y = cy + 10
        spr = self._spr_arthur if tipo == "arthur" else self._spr_luna
        if spr:
            # Escala e posiciona sprite no topo do card
            target_h = 140
            scale = target_h / spr.get_height()
            nw = max(1, int(spr.get_width() * scale))
            nh = max(1, int(spr.get_height() * scale))
            img = pygame.transform.smoothscale(spr, (nw, nh))
            bob = int(math.sin(self._t * 2) * 4) if hover else 0
            r = img.get_rect(center=(cx, sprite_y + 75 + bob))
            surface.blit(img, r)
        else:
            self._draw_hero_sprite(surface, heroi, cx, sprite_y + 60, hover, self._t)

        draw_text(surface, heroi.nome,
                  cx, rect.y + 170,
                  size=FONT_LARGE, color=heroi.cor,
                  bold=True, center=True)

        tipo_label = "Guerreiro" if tipo == "arthur" else "Maga"
        draw_text(surface, f"— {tipo_label} —",
                  cx, rect.y + 202,
                  size=FONT_TINY, color=GRAY,
                  center=True)

        sy = rect.y + 230
        stats = [
            ("❤  HP",     f"{heroi.hp_max}",  HP_GREEN),
            ("✦  ATK",    f"{heroi.ataque}",   ORANGE),
            ("⬡  DEF",    f"{heroi.defesa}",   CYAN),
            ("◈  MP",     f"{heroi.mp_max}",   MP_BLUE),
            ("⊕  Poções", f"{heroi.pocoes}",   WHITE),
        ]
        for label, val, col in stats:
            draw_text(surface, label, rect.x + 30, sy, size=FONT_SMALL, color=GRAY)
            draw_text(surface, val,  rect.x + rect.width - 60, sy, size=FONT_SMALL, color=col)
            sy += 28

        pygame.draw.line(surface, PANEL_BORDER,
                         (rect.x + 20, sy + 5), (rect.x + rect.width - 20, sy + 5), 1)
        sy += 15
        for line in heroi.descricao.split('\n'):
            draw_text(surface, line, cx, sy,
                      size=FONT_TINY, color=GRAY,
                      center=True, shadow=False)
            sy += 18

        if hover:
            alpha = int(abs(math.sin(self._t * 3)) * 200 + 55)
            draw_text(surface, "[ CLIQUE PARA ESCOLHER ]",
                      cx, rect.y + rect.height - 28,
                      size=FONT_TINY, color=(alpha, alpha, 80),
                      center=True)

    @staticmethod
    def _draw_hero_sprite(surface, heroi, cx, cy, hover, t):
        offset = int(math.sin(t * 2) * 4) if hover else 0
        cy    += offset
        col    = heroi.cor
        dark   = tuple(max(0, c - 60) for c in col)

        if heroi.tipo == "arthur":
            pygame.draw.rect(surface, col,  pygame.Rect(cx - 18, cy - 30, 36, 44))
            pygame.draw.rect(surface, dark, pygame.Rect(cx - 18, cy - 30, 36, 44), 2)
            pygame.draw.circle(surface, col, (cx, cy - 42), 20)
            pygame.draw.circle(surface, dark, (cx, cy - 42), 20, 2)
            pygame.draw.polygon(surface, GOLD, [
                (cx - 22, cy - 48), (cx, cy - 72), (cx + 22, cy - 48)
            ])
            pygame.draw.rect(surface, GOLD, pygame.Rect(cx + 20, cy - 50, 6, 60))
            pygame.draw.rect(surface, WHITE, pygame.Rect(cx + 15, cy - 24, 16, 6))
            pygame.draw.rect(surface, dark, pygame.Rect(cx - 16, cy + 14, 14, 24))
            pygame.draw.rect(surface, dark, pygame.Rect(cx + 2,  cy + 14, 14, 24))
        else:
            pygame.draw.polygon(surface, col, [
                (cx - 24, cy + 40), (cx, cy - 28), (cx + 24, cy + 40)
            ])
            pygame.draw.rect(surface, dark, pygame.Rect(cx - 12, cy - 28, 24, 36))
            pygame.draw.circle(surface, col, (cx, cy - 42), 18)
            pygame.draw.circle(surface, dark, (cx, cy - 42), 18, 2)
            pygame.draw.arc(surface, PURPLE,
                            pygame.Rect(cx - 22, cy - 62, 44, 30),
                            0, math.pi, 4)
            pygame.draw.line(surface, GOLD, (cx - 26, cy + 38), (cx - 22, cy - 54), 4)
            pygame.draw.circle(surface, ACCENT, (cx - 22, cy - 56), 8)
            pygame.draw.circle(surface, WHITE,  (cx - 22, cy - 56), 8, 1)
            if hover:
                for i in range(4):
                    a  = t * 2 + i * (math.pi / 2)
                    sx = int(cx + math.cos(a) * 30)
                    sy = int(cy - 30 + math.sin(a) * 20)
                    pygame.draw.circle(surface, ACCENT, (sx, sy), 3)