# ============================================================
#  ELDORIA GAME - ESTADO: MAPA DE ELDORIA (Hub)
# ============================================================

import pygame
import math
from utils.game_state_manager import BaseState
from utils.constants    import *
from utils.ui           import draw_text, draw_panel, Button, StarField


_LOCAIS = {
    1: {
        "nome": "Oficina de Kael",
        "desc": "Compre poções e equipamentos.",
        "cor":  GOLD,
        "pos":  (200, 300),
        "icon": "⚗",
        "acao": STATE_SHOP,
    },
    2: {
        "nome": "Torre do Castelo",
        "desc": "General Bug aguarda batalha.",
        "cor":  ORANGE,
        "pos":  (600, 220),
        "icon": "⚔",
        "acao": STATE_BATTLE,
        "inimigo": "general_bug",
        "nivel_req": 1,
    },
    3: {
        "nome": "Núcleo do Kernel",
        "desc": "Rei Drakon — Batalha Final.",
        "cor":  RED,
        "pos":  (720, 420),
        "icon": "☠",
        "acao": STATE_BATTLE,
        "inimigo": "rei_drakon",
        "nivel_req": 2,
    },
}


class MapState(BaseState):

    def enter(self, data: dict = None):
        self._t        = 0.0
        self._stars    = StarField(90)
        self._heroi    = self.manager.heroi
        self._hover    = None
        self._progresso = self.manager.progresso

        # Botões de localização
        self._btns = {}
        for k, loc in _LOCAIS.items():
            bw, bh = 180, 55
            cx, cy = loc["pos"]
            rect   = pygame.Rect(cx - bw // 2, cy - bh // 2, bw, bh)
            avail  = self._local_disponivel(k)
            btn    = Button(rect, f"{loc['icon']}  {loc['nome']}",
                            color=loc["cor"] if avail else GRAY_DARK,
                            hover_color=loc["cor"],
                            font_size=FONT_TINY)
            btn.enabled = avail
            self._btns[k] = btn

        # Botão de status
        self._btn_status = Button(
            pygame.Rect(SCREEN_WIDTH - 190, SCREEN_HEIGHT - 65, 170, 48),
            "📊 Status", color=(40, 30, 80), font_size=FONT_SMALL
        )
        self._show_status = False

    def _local_disponivel(self, k: int) -> bool:
        loc = _LOCAIS[k]
        req = loc.get("nivel_req", 0)
        if req == 0:
            return True
        # Batalha 2 disponível após progresso >= 1
        if loc.get("inimigo") == "general_bug":
            return self._progresso >= 1
        # Batalha 3 disponível após progresso >= 2
        if loc.get("inimigo") == "rei_drakon":
            return self._progresso >= 2
        return True

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        self._hover = None
        for k, btn in self._btns.items():
            btn.update((mx, my))
            if btn.rect.collidepoint(mx, my) and btn.enabled:
                self._hover = k

        self._btn_status.update((mx, my))

        for e in events:
            if self._btn_status.is_clicked(e):
                self._show_status = not self._show_status

            for k, btn in self._btns.items():
                if btn.is_clicked(e):
                    self._ir_para(k)

            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self._show_status = False

    def _ir_para(self, k: int):
        loc = _LOCAIS[k]
        if loc["acao"] == STATE_BATTLE:
            inimigo = loc.get("inimigo", "")
            self.manager.inimigo_atual = inimigo
            self.go_to(STATE_BATTLE, {"inimigo": inimigo})
        elif loc["acao"] == STATE_SHOP:
            self.go_to(STATE_SHOP)

    def update(self, dt: float):
        self._t += dt
        self._stars.update(dt)

    def draw(self, surface: pygame.Surface):
        surface.fill(DARK_BG)
        self._stars.draw(surface)
        self._draw_mapa(surface)
        self._draw_hud(surface)
        self._draw_botoes(surface)
        if self._show_status:
            self._draw_status(surface)

    def _draw_mapa(self, surface):
        # Título
        draw_text(surface, "MAPA DE Atrinium",
                  SCREEN_WIDTH // 2, 30,
                  size=FONT_TITLE, color=GOLD, bold=True, center=True)
        draw_text(surface, "Escolha seu próximo destino",
                  SCREEN_WIDTH // 2, 72,
                  size=FONT_SMALL, color=GRAY, center=True)

        # Fundo do mapa
        mapa_rect = pygame.Rect(80, 100, SCREEN_WIDTH - 160, SCREEN_HEIGHT - 220)
        draw_panel(surface, mapa_rect, bg_color=(8, 15, 30), border_color=(60, 80, 120),
                   border_width=2, alpha=200)

        # Grade decorativa
        for gx in range(80, SCREEN_WIDTH - 80, 60):
            pygame.draw.line(surface, (20, 30, 55), (gx, 100), (gx, SCREEN_HEIGHT - 120), 1)
        for gy in range(100, SCREEN_HEIGHT - 120, 60):
            pygame.draw.line(surface, (20, 30, 55), (80, gy), (SCREEN_WIDTH - 80, gy), 1)

        # Ponto inicial
        pygame.draw.circle(surface, ACCENT, (200, 450), 10)
        draw_text(surface, "Início", 215, 440, size=FONT_TINY, color=ACCENT)

        # Conexões entre locais
        conexoes = [(200, 450, 200, 300), (200, 300, 600, 220), (600, 220, 720, 420)]
        for x1, y1, x2, y2 in conexoes:
            pygame.draw.line(surface, (50, 60, 100), (x1, y1), (x2, y2), 2)

        # Locais no mapa (círculos decorativos)
        for k, loc in _LOCAIS.items():
            cx, cy = loc["pos"]
            avail  = self._local_disponivel(k)
            col    = loc["cor"] if avail else GRAY_DARK
            r      = 30

            # Pulso se hover
            if self._hover == k:
                p = int(abs(math.sin(self._t * 3)) * 15)
                pygame.draw.circle(surface, (*col, 60), (cx, cy), r + p + 5)

            pygame.draw.circle(surface, DARK_BG, (cx, cy), r)
            pygame.draw.circle(surface, col, (cx, cy), r, 3)
            draw_text(surface, loc["icon"], cx, cy,
                      size=FONT_LARGE, color=col, center=True, shadow=False)
            draw_text(surface, loc["nome"],
                      cx, cy + r + 8,
                      size=FONT_TINY, color=col, center=True)
            if not avail:
                draw_text(surface, "[BLOQUEADO]",
                          cx, cy + r + 22,
                          size=FONT_TINY, color=GRAY, center=True)

    def _draw_hud(self, surface):
        h    = self._heroi
        rect = pygame.Rect(20, SCREEN_HEIGHT - 90, 320, 75)
        draw_panel(surface, rect, border_color=h.cor)
        draw_text(surface, f"{h.nome}  Nv.{h.nivel}",
                  rect.x + 10, rect.y + 8,
                  size=FONT_SMALL, color=h.cor, bold=True)
        draw_text(surface, f"HP {h.hp}/{h.hp_max}   MP {h.mp}/{h.mp_max}   Ouro {h.ouro}",
                  rect.x + 10, rect.y + 38,
                  size=FONT_TINY, color=WHITE)
        self._btn_status.draw(surface)

    def _draw_botoes(self, surface):
        for btn in self._btns.values():
            btn.draw(surface)

    def _draw_status(self, surface):
        h    = self._heroi
        rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 220, 400, 440)
        draw_panel(surface, rect, bg_color=(15, 10, 35),
                   border_color=h.cor, border_width=3, alpha=250)

        draw_text(surface, f"⚔ {h.nome}",
                  rect.centerx, rect.y + 18,
                  size=FONT_LARGE, color=h.cor, bold=True, center=True)
        draw_text(surface, f"Nível {h.nivel}  |  {h.tipo.title()}",
                  rect.centerx, rect.y + 52,
                  size=FONT_SMALL, color=GOLD, center=True)

        pygame.draw.line(surface, h.cor,
                         (rect.x + 20, rect.y + 75), (rect.x + rect.width - 20, rect.y + 75), 1)

        stats = [
            ("HP",      f"{h.hp} / {h.hp_max}",    HP_GREEN),
            ("MP",      f"{h.mp} / {h.mp_max}",    MP_BLUE),
            ("Ataque",  str(h.ataque),              ORANGE),
            ("Defesa",  str(h.defesa),              CYAN),
            ("Poções",  str(h.pocoes),              WHITE),
            ("Ouro",    str(h.ouro),                GOLD),
            ("XP",      f"{h.xp}/{h.xp_proximo_nivel}", ACCENT),
        ]

        cy = rect.y + 92
        for label, val, col in stats:
            draw_text(surface, label, rect.x + 30, cy,
                      size=FONT_SMALL, color=GRAY)
            draw_text(surface, val,
                      rect.x + rect.width - 30 - len(val) * 9, cy,
                      size=FONT_SMALL, color=col)
            cy += 32

        if h.habilidades:
            pygame.draw.line(surface, PANEL_BORDER,
                             (rect.x + 20, cy + 5), (rect.x + rect.width - 20, cy + 5), 1)
            cy += 18
            draw_text(surface, "Habilidades:", rect.x + 30, cy,
                      size=FONT_TINY, color=PURPLE)
            cy += 20
            for hab in h.habilidades:
                draw_text(surface, f"  • {hab}", rect.x + 30, cy,
                          size=FONT_TINY, color=WHITE)
                cy += 16

        draw_text(surface, "[ ESC para fechar ]",
                  rect.centerx, rect.y + rect.height - 25,
                  size=FONT_TINY, color=GRAY, center=True)