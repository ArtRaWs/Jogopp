# ============================================================
#  ELDORIA GAME - ESTADO: SUBIU DE NÍVEL
# ============================================================

import pygame
import math
from utils.game_state_manager import BaseState
from utils.constants    import *
from utils.ui           import draw_text, draw_panel, Button, StarField


class LevelUpState(BaseState):

    def enter(self, data: dict = None):
        data             = data or {}
        self._t          = 0.0
        self._stars      = StarField(100)
        self._xp_ganho   = data.get("xp_ganho", 0)
        self._ouro_ganho = data.get("ouro_ganho", 0)
        self._inimigo    = data.get("inimigo_nome", "Inimigo")
        self._heroi      = self.manager.heroi
        self._alpha      = 0.0

        self.manager.heroi.ouro = getattr(self.manager.heroi, 'ouro', 0) + self._ouro_ganho

        self._btn_cont = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 100, 240, 55),
            "Continuar →", color=PRIMARY, font_size=FONT_MEDIUM
        )

        # Partículas de celebração
        import random
        self._particles = [
            {
                "x": float(random.randint(100, SCREEN_WIDTH - 100)),
                "y": float(random.randint(100, SCREEN_HEIGHT - 100)),
                "vx": random.uniform(-60, 60),
                "vy": random.uniform(-120, -30),
                "color": random.choice([GOLD, ACCENT, PRIMARY, PURPLE, GREEN]),
                "r": random.randint(3, 7),
                "life": 1.0,
            }
            for _ in range(60)
        ]

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        self._btn_cont.update((mx, my))
        for e in events:
            if self._btn_cont.is_clicked(e):
                self._continuar()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                self._continuar()

    def _continuar(self):
        progresso = self.manager.progresso
        if progresso == 1:
            self.manager.inimigo_atual = "general_bug"
            self.go_to(STATE_MAP)
        elif progresso == 2:
            self.manager.inimigo_atual = "rei_drakon"
            self.go_to(STATE_MAP)
        elif progresso >= 3:
            self.go_to(STATE_VICTORY)
        else:
            self.go_to(STATE_MAP)

    def update(self, dt: float):
        self._t += dt
        self._stars.update(dt)
        self._alpha = min(1.0, self._alpha + dt * 1.5)

        for p in self._particles:
            p["x"]    += p["vx"] * dt
            p["y"]    += p["vy"] * dt
            p["vy"]   += 120 * dt   # gravidade
            p["life"] -= dt * 0.4
        self._particles = [p for p in self._particles if p["life"] > 0]

    def draw(self, surface: pygame.Surface):
        surface.fill(DARK_BG)
        self._stars.draw(surface)

        # Partículas
        for p in self._particles:
            if p["life"] <= 0:
                continue
            alpha = int(p["life"] * 255)
            r     = max(1, p["r"])
            s     = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p["color"], alpha), (r, r), r)
            surface.blit(s, (int(p["x"] - r), int(p["y"] - r)))

        # Título pulsante
        pulse = abs(math.sin(self._t * 2)) * 30
        col   = (int(GOLD[0]), int(GOLD[1] - pulse), 0)
        draw_text(surface, "✦ SUBIU DE NÍVEL! ✦",
                  SCREEN_WIDTH // 2, 60,
                  size=FONT_HUGE, color=GOLD, bold=True, center=True)

        draw_text(surface, f"{self._inimigo} foi derrotado!",
                  SCREEN_WIDTH // 2, 130,
                  size=FONT_MEDIUM, color=ACCENT, center=True)

        h    = self._heroi
        rect = pygame.Rect(SCREEN_WIDTH // 2 - 260, 175, 520, 340)
        draw_panel(surface, rect, border_color=GOLD, border_width=2)

        draw_text(surface, h.nome,
                  rect.centerx, rect.y + 20,
                  size=FONT_LARGE, color=h.cor, bold=True, center=True)
        draw_text(surface, f"Nível {h.nivel}",
                  rect.centerx, rect.y + 55,
                  size=FONT_MEDIUM, color=GOLD, center=True)

        pygame.draw.line(surface, PANEL_BORDER,
                         (rect.x + 20, rect.y + 82), (rect.x + rect.width - 20, rect.y + 82), 1)

        recompensas = [
            (f"XP Ganho:   +{self._xp_ganho}",    ACCENT),
            (f"Ouro Ganho: +{self._ouro_ganho}",   GOLD),
            (f"Ouro Total: {h.ouro}",              GOLD),
            ("",                                    WHITE),
            (f"HP Máximo:  {h.hp_max}",            HP_GREEN),
            (f"MP Máximo:  {h.mp_max}",            MP_BLUE),
            (f"Ataque:     {h.ataque}",            ORANGE),
            (f"Defesa:     {h.defesa}",            CYAN),
        ]

        cy = rect.y + 100
        for txt, col in recompensas:
            if txt:
                draw_text(surface, txt,
                          rect.centerx, cy,
                          size=FONT_SMALL, color=col, center=True)
            cy += 28

        self._btn_cont.draw(surface)