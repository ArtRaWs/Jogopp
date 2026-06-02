# ============================================================
#  ELDORIA GAME - ESTADO: VITÓRIA FINAL
# ============================================================

import pygame
import math
import random
from utils.game_state_manager import BaseState
from utils.constants    import *
from utils.ui           import draw_text, draw_panel, Button, StarField


class VictoryState(BaseState):

    def enter(self, data: dict = None):
        self._t      = 0.0
        self._stars  = StarField(150)
        self._alpha  = 0.0
        self._heroi  = self.manager.heroi

        # Fogos de artifício
        self._fogos: list[dict] = []
        self._proximo_fogo = 0.0

        # Partículas douradas contínuas
        self._particles: list[dict] = []

        self._btn_menu = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT - 90, 280, 58),
            "✦ Menu Principal", color=(60, 50, 10), hover_color=GOLD,
            font_size=FONT_MEDIUM
        )

    def _spawn_fogo(self):
        cx = random.randint(150, SCREEN_WIDTH - 150)
        cy = random.randint(100, SCREEN_HEIGHT // 2)
        col = random.choice([GOLD, ACCENT, PRIMARY, PURPLE, (255, 80, 80), CYAN])
        self._fogos.append({
            "cx": cx, "cy": cy,
            "particles": [
                {
                    "x": float(cx), "y": float(cy),
                    "vx": math.cos(a) * random.uniform(60, 180),
                    "vy": math.sin(a) * random.uniform(60, 180),
                    "color": col,
                    "life": 1.0,
                    "r": random.randint(2, 5),
                }
                for a in [i * (math.pi * 2 / 16) for i in range(16)]
            ],
            "life": 1.0,
        })

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        self._btn_menu.update((mx, my))

        for e in events:
            if self._btn_menu.is_clicked(e):
                self._ir_menu()
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self._ir_menu()

    def _ir_menu(self):
        self.manager.progresso     = 0
        self.manager.heroi         = None
        self.manager.inimigo_atual = ""
        self.go_to(STATE_INTRO)

    def update(self, dt: float):
        self._t     += dt
        self._alpha  = min(1.0, self._alpha + dt * 0.7)
        self._stars.update(dt)

        # Dispara fogos periodicamente
        self._proximo_fogo -= dt
        if self._proximo_fogo <= 0:
            self._spawn_fogo()
            self._proximo_fogo = random.uniform(0.4, 1.2)

        # Atualiza fogos
        for fogo in self._fogos:
            fogo["life"] -= dt * 0.8
            for p in fogo["particles"]:
                p["x"]  += p["vx"] * dt
                p["y"]  += p["vy"] * dt
                p["vy"] += 120 * dt   # gravidade
                p["life"] -= dt * 0.9
        self._fogos = [f for f in self._fogos if f["life"] > 0]

        # Partículas douradas
        if random.random() < 0.3:
            self._particles.append({
                "x": float(random.randint(0, SCREEN_WIDTH)),
                "y": float(SCREEN_HEIGHT + 10),
                "vy": -random.uniform(40, 100),
                "vx": random.uniform(-20, 20),
                "life": 1.0,
                "r": random.randint(2, 4),
                "color": random.choice([GOLD, (255, 240, 100), ACCENT]),
            })
        for p in self._particles:
            p["x"]  += p["vx"] * dt
            p["y"]  += p["vy"] * dt
            p["life"] -= dt * 0.5
        self._particles = [p for p in self._particles if p["life"] > 0]

    def draw(self, surface: pygame.Surface):
        surface.fill(DARK_BG)
        self._stars.draw(surface)

        # Partículas douradas
        for p in self._particles:
            r = max(1, p["r"])
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p["color"], int(p["life"] * 200)), (r, r), r)
            surface.blit(s, (int(p["x"] - r), int(p["y"] - r)))

        # Fogos de artifício
        for fogo in self._fogos:
            for p in fogo["particles"]:
                if p["life"] <= 0:
                    continue
                r = max(1, p["r"])
                s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*p["color"], int(p["life"] * 255)), (r, r), r)
                surface.blit(s, (int(p["x"] - r), int(p["y"] - r)))

        # Overlay de fade
        if self._alpha < 1.0:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            ov.fill(DARK_BG)
            ov.set_alpha(int((1.0 - self._alpha) * 255))
            surface.blit(ov, (0, 0))

        # ── Título ────────────────────────────────────────────
        pulse = abs(math.sin(self._t * 1.2)) * 25
        gold_pulse = (int(GOLD[0]), int(max(0, GOLD[1] - pulse)), 0)
        draw_text(surface, "✦ VITÓRIA! ✦",
                  SCREEN_WIDTH // 2, 60,
                  size=FONT_HUGE, color=GOLD, bold=True, center=True)

        draw_text(surface, "O Grande Código foi restaurado!",
                  SCREEN_WIDTH // 2, 128,
                  size=FONT_MEDIUM, color=ACCENT, center=True)

        # ── Painel central ────────────────────────────────────
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 300, 170, 600, 400)
        draw_panel(surface, panel, bg_color=(15, 20, 10),
                   border_color=GOLD, border_width=3, alpha=230)

        if self._heroi:
            h = self._heroi
            draw_text(surface, h.nome,
                      panel.centerx, panel.y + 22,
                      size=FONT_LARGE, color=h.cor, bold=True, center=True)
            draw_text(surface, f"Nível Final: {h.nivel}",
                      panel.centerx, panel.y + 58,
                      size=FONT_MEDIUM, color=GOLD, center=True)

            pygame.draw.line(surface, GOLD,
                             (panel.x + 30, panel.y + 85),
                             (panel.x + panel.width - 30, panel.y + 85), 1)

            stats = [
                ("HP Final",    f"{h.hp} / {h.hp_max}",  HP_GREEN),
                ("MP Final",    f"{h.mp} / {h.mp_max}",  MP_BLUE),
                ("Ataque",      str(h.ataque),            ORANGE),
                ("Defesa",      str(h.defesa),            CYAN),
                ("Ouro Total",  str(h.ouro),              GOLD),
                ("XP Total",    str(h.xp),                ACCENT),
            ]
            cy = panel.y + 105
            for label, val, col in stats:
                draw_text(surface, label, panel.x + 50, cy,
                          size=FONT_SMALL, color=GRAY)
                draw_text(surface, val,
                          panel.x + panel.width - 60 - len(val) * 9, cy,
                          size=FONT_SMALL, color=col)
                cy += 34

            if h.habilidades:
                pygame.draw.line(surface, PANEL_BORDER,
                                 (panel.x + 30, cy + 5),
                                 (panel.x + panel.width - 30, cy + 5), 1)
                cy += 20
                draw_text(surface, "Habilidades desbloqueadas:",
                          panel.x + 50, cy,
                          size=FONT_TINY, color=PURPLE)
                cy += 18
                for hab in h.habilidades:
                    draw_text(surface, f"  {hab}",
                              panel.x + 50, cy,
                              size=FONT_TINY, color=WHITE)
                    cy += 16

        # Texto épico de encerramento
        draw_text(surface, "Atrinium está salva. O código está limpo.",
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT - 130,
                  size=FONT_SMALL, color=GRAY, center=True)

        self._btn_menu.draw(surface)