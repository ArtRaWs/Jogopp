# ============================================================
#  ELDORIA GAME - ESTADO: LOJA (Oficina de Kael)
# ============================================================

import pygame
import math
from utils.game_state_manager import BaseState
from utils.constants    import *
from utils.ui           import draw_text, draw_panel, Button, StarField


_ITENS = [
    {
        "id":    "pocao_pequena",
        "nome":  "Poção Pequena",
        "desc":  "Restaura 50 HP.",
        "preco": 15,
        "icon":  "⊕",
        "cor":   GREEN,
        "acao":  "pocao",
        "quantidade": 1,
    },
    {
        "id":    "pocao_grande",
        "nome":  "Poção Grande",
        "desc":  "Restaura 120 HP.",
        "preco": 35,
        "icon":  "⊕",
        "cor":   ACCENT,
        "acao":  "pocao_grande",
        "quantidade": 1,
    },
    {
        "id":    "elixir_mp",
        "nome":  "Elixir de Mana",
        "desc":  "Restaura 40 MP.",
        "preco": 20,
        "icon":  "◈",
        "cor":   MP_BLUE,
        "acao":  "mp",
        "quantidade": 40,
    },
    {
        "id":    "amuleto",
        "nome":  "Amuleto de Kael",
        "desc":  "+10 Ataque por batalha.",
        "preco": 50,
        "icon":  "✦",
        "cor":   GOLD,
        "acao":  "bonus_atk",
        "quantidade": 10,
    },
    {
        "id":    "escudo",
        "nome":  "Escudo Arcano",
        "desc":  "+5 Defesa permanente.",
        "preco": 40,
        "icon":  "⬡",
        "cor":   CYAN,
        "acao":  "bonus_def",
        "quantidade": 5,
    },
]


class ShopState(BaseState):

    def enter(self, data: dict = None):
        self._t      = 0.0
        self._stars  = StarField(70)
        self._heroi  = self.manager.heroi
        self._msg    = ""
        self._msg_t  = 0.0
        self._msg_col = WHITE

        # Botões de compra
        bw, bh = 160, 44
        self._item_btns = []
        for i, item in enumerate(_ITENS):
            row  = i // 2
            col  = i  % 2
            bx   = 200 + col * 400
            by   = 200 + row * 100
            btn  = Button(
                pygame.Rect(bx + 280, by + 4, bw, bh),
                f"Comprar ({item['preco']}g)",
                color=(50, 40, 90), hover_color=item["cor"],
                font_size=FONT_TINY
            )
            self._item_btns.append((item, btn))

        self._btn_voltar = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 90, 200, 52),
            "← Voltar ao Mapa", color=PRIMARY, font_size=FONT_MEDIUM
        )

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        self._btn_voltar.update((mx, my))
        for _, btn in self._item_btns:
            btn.update((mx, my))

        for e in events:
            if self._btn_voltar.is_clicked(e):
                self.go_to(STATE_MAP)
            for item, btn in self._item_btns:
                if btn.is_clicked(e):
                    self._comprar(item)

    def _comprar(self, item: dict):
        h = self._heroi
        if h.ouro < item["preco"]:
            self._msg     = "Ouro insuficiente!"
            self._msg_col = RED
            self._msg_t   = 0.0
            return

        h.ouro -= item["preco"]
        acao    = item["acao"]

        if acao == "pocao":
            h.pocoes += item["quantidade"]
            h.pocao_cura = 50
            self._msg = f"Comprou {item['nome']}! Poções: {h.pocoes}"

        elif acao == "pocao_grande":
            h.pocoes    += 1
            h.pocao_cura = 120
            self._msg    = f"Comprou Poção Grande! Cura 120 HP por uso."

        elif acao == "mp":
            restaurado = h.restaurar_mp(item["quantidade"])
            self._msg  = f"Mana restaurada: +{restaurado} MP"

        elif acao == "bonus_atk":
            h.ataque += item["quantidade"]
            self._msg = f"Ataque aumentado para {h.ataque}!"

        elif acao == "bonus_def":
            h.defesa += item["quantidade"]
            self._msg = f"Defesa aumentada para {h.defesa}!"

        self._msg_col = ACCENT
        self._msg_t   = 0.0

    def update(self, dt: float):
        self._t     += dt
        self._msg_t += dt
        self._stars.update(dt)

    def draw(self, surface: pygame.Surface):
        surface.fill(DARK_BG)
        self._stars.draw(surface)

        # Kael decorativo
        self._draw_kael_small(surface, 110, 300)

        draw_text(surface, "⚗ OFICINA DO MESTRE KAEL",
                  SCREEN_WIDTH // 2, 30,
                  size=FONT_TITLE, color=GOLD, bold=True, center=True)
        draw_text(surface, "Bem-vindo, herói! O que posso fazer por você?",
                  SCREEN_WIDTH // 2, 75,
                  size=FONT_SMALL, color=GRAY, center=True)

        # Ouro do herói
        h = self._heroi
        draw_text(surface, f"Seu Ouro: {h.ouro}",
                  SCREEN_WIDTH - 200, 35,
                  size=FONT_MEDIUM, color=GOLD, bold=True)

        # Itens
        panel = pygame.Rect(160, 115, SCREEN_WIDTH - 200, 500)
        draw_panel(surface, panel, alpha=180)

        for i, (item, btn) in enumerate(self._item_btns):
            row = i // 2
            col = i  % 2
            bx  = 200 + col * 400
            by  = 200 + row * 100

            # Card do item
            card = pygame.Rect(bx - 20, by - 8, 470, 70)
            draw_panel(surface, card, bg_color=(28, 20, 55),
                       border_color=item["cor"], alpha=200)

            draw_text(surface, f"{item['icon']} {item['nome']}",
                      bx, by + 5,
                      size=FONT_SMALL, color=item["cor"], bold=True)
            draw_text(surface, item["desc"],
                      bx, by + 28,
                      size=FONT_TINY, color=GRAY)
            draw_text(surface, f"{item['preco']} 🪙",
                      bx + 205, by + 15,
                      size=FONT_SMALL, color=GOLD)

            btn.enabled = h.ouro >= item["preco"]
            btn.draw(surface)

        # Mensagem de feedback
        if self._msg and self._msg_t < 3.0:
            alpha = min(255, int((3.0 - self._msg_t) * 120))
            s     = pygame.font.SysFont("consolas", FONT_MEDIUM).render(self._msg, True, self._msg_col)
            s.set_alpha(alpha)
            surface.blit(s, (SCREEN_WIDTH // 2 - s.get_width() // 2, SCREEN_HEIGHT - 150))

        self._btn_voltar.draw(surface)

    def _draw_kael_small(self, surface, cx, cy):
        t   = self._t
        bob = int(math.sin(t * 1.5) * 3)
        cy += bob
        pygame.draw.polygon(surface, (60, 40, 100), [(cx-22, cy+55), (cx, cy-8), (cx+22, cy+55)])
        pygame.draw.rect(surface, (80, 55, 130), pygame.Rect(cx - 14, cy - 8, 28, 38))
        pygame.draw.circle(surface, (200, 170, 130), (cx, cy - 20), 17)
        pygame.draw.polygon(surface, (40, 20, 80), [(cx-20, cy-34), (cx, cy-66), (cx+20, cy-34)])
        pygame.draw.ellipse(surface, (40, 20, 80), pygame.Rect(cx - 25, cy - 41, 50, 13))
        pygame.draw.circle(surface, GOLD, (cx, cy - 53), 4)
        pygame.draw.line(surface, (140, 100, 60), (cx + 20, cy + 52), (cx + 22, cy - 46), 4)
        orb = (int(abs(math.sin(t)) * 200 + 55), 80, 255)
        pygame.draw.circle(surface, orb, (cx + 22, cy - 49), 7)