# ============================================================
#  ELDORIA GAME - ESTADO: MAPA DE ATRINIUM (Hub)
# ============================================================

import pygame
import math
import os
import sys
from utils.game_state_manager import BaseState
from utils.constants    import *
from utils.ui           import draw_text, draw_panel, Button, StarField, get_font

# ── Resolve o diretório raiz do projeto ──────────────────────
# Funciona independente de onde o script é executado
_THIS_DIR    = os.path.dirname(os.path.abspath(__file__))       # .../states/
_PROJECT_DIR = os.path.dirname(_THIS_DIR)                       # .../eldoria_game/

# ── Resolução do mapa ────────────────────────────────────────
W = 1164
H = 818

# ── Posições dos locais (ajustadas ao pixel art) ─────────────
_LOCAIS = {
    1: {
        "nome":  "Oficina de Kael",
        "desc":  "Compre poções e equipamentos.",
        "cor":   GOLD,
        "pos":   (248, 412),
        "icon":  "⚗",
        "acao":  STATE_SHOP,
    },
    2: {
        "nome":      "Torre do Castelo",
        "desc":      "General Bug aguarda batalha.",
        "cor":       ORANGE,
        "pos":       (620, 258),
        "icon":      "⚔",
        "acao":      STATE_BATTLE,
        "inimigo":   "general_bug",
        "nivel_req": 1,
    },
    3: {
        "nome":      "Núcleo do Kernel",
        "desc":      "Rei Drakon — Batalha Final.",
        "cor":       RED,
        "pos":       (858, 502),
        "icon":      "☠",
        "acao":      STATE_BATTLE,
        "inimigo":   "rei_drakon",
        "nivel_req": 2,
    },
}

# ── Caminhos no mapa ─────────────────────────────────────────
_CAMINHOS = [
    {"pts": [(248, 528), (248, 412)],             "cor": (40, 160, 255), "tipo": "azul"},
    {"pts": [(248, 412), (400, 345), (620, 258)], "cor": (40, 160, 255), "tipo": "azul"},
    {"pts": [(620, 258), (720, 380), (858, 502)], "cor": (220, 50,  20), "tipo": "lava"},
]


class MapState(BaseState):

    _bg_cache = None

    @classmethod
    def _load_bg(cls):
        if cls._bg_cache is not None:
            return cls._bg_cache

        candidates = [
            os.path.join(_PROJECT_DIR, "assets", "mapa.png"),
            os.path.join(_PROJECT_DIR, "mapa.png"),
            os.path.join(os.getcwd(), "assets", "mapa.png"),
            os.path.join(os.getcwd(), "mapa.png"),
        ]

        for path in candidates:
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert()
                    cls._bg_cache = pygame.transform.scale(img, (W, H))
                    print(f"[MapState] Imagem carregada: {path}")
                    return cls._bg_cache
                except Exception as e:
                    print(f"[MapState] Erro ao carregar {path}: {e}")

        print("[MapState] AVISO: mapa.png nao encontrado. Candidatos testados:")
        for p in candidates:
            print(f"  {chr(10003) if os.path.exists(p) else chr(10007)} {p}")
        return None

    def enter(self, data=None):
        self._t           = 0.0
        self._heroi       = self.manager.heroi
        self._hover       = None
        self._progresso   = self.manager.progresso
        self._bg          = self._load_bg()
        self._show_status = False

        self._btns = {}
        for k, loc in _LOCAIS.items():
            bw, bh = 188, 48
            cx, cy = loc["pos"]
            rect   = pygame.Rect(cx - bw // 2, cy - bh // 2, bw, bh)
            avail  = self._local_disponivel(k)
            btn    = Button(
                rect,
                f"{loc['icon']}  {loc['nome']}",
                color       = loc["cor"] if avail else GRAY_DARK,
                hover_color = tuple(min(255, c + 60) for c in loc["cor"]),
                font_size   = FONT_SMALL,
            )
            btn.enabled   = avail
            self._btns[k] = btn

        self._btn_status = Button(
            pygame.Rect(W - 178, H - 60, 158, 44),
            "⊞  Status",
            color=(40, 30, 80),
            font_size=FONT_SMALL,
        )

    def _local_disponivel(self, k):
        loc = _LOCAIS[k]
        if "nivel_req" not in loc:
            return True
        if loc.get("inimigo") == "general_bug":
            return self._progresso >= 1
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

    def _ir_para(self, k):
        loc = _LOCAIS[k]
        if loc["acao"] == STATE_BATTLE:
            inimigo = loc.get("inimigo", "")
            self.manager.inimigo_atual = inimigo
            self.go_to(STATE_BATTLE, {"inimigo": inimigo})
        elif loc["acao"] == STATE_SHOP:
            self.go_to(STATE_SHOP)

    def update(self, dt):
        self._t += dt

    def draw(self, surface):
        # 1) Fundo
        if self._bg:
            surface.blit(self._bg, (0, 0))
        else:
            surface.fill(DARK_BG)
            self._draw_grid_fallback(surface)

        # 2) Overlay leve
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 20, 55))
        surface.blit(ov, (0, 0))

        # 3) Caminhos
        self._draw_caminhos(surface)

        # 4) Ponto de início
        self._draw_inicio(surface)

        # 5) Botões (pins)
        self._draw_pins(surface)

        # 6) HUD
        self._draw_hud(surface)

        # 7) Título
        self._draw_titulo(surface)

        # 8) Bússola
        self._draw_bussola(surface, W - 88, 88)

        # 9) Botão status
        self._btn_status.draw(surface)

        # 10) Painel status
        if self._show_status:
            self._draw_status(surface)

    # ── Título ───────────────────────────────────────────────

    def _draw_titulo(self, surface):
        for ox, oy in [(3, 3), (1, 1)]:
            draw_text(surface, "MAPA DE ATRINIUM",
                      W // 2 + ox, 36 + oy,
                      size=FONT_TITLE, color=(0, 0, 0),
                      bold=True, center=True, shadow=False)
        draw_text(surface, "MAPA DE ATRINIUM",
                  W // 2, 36,
                  size=FONT_TITLE, color=GOLD,
                  bold=True, center=True, shadow=False)
        draw_text(surface, "Escolha seu próximo destino",
                  W // 2, 80,
                  size=FONT_SMALL, color=(160, 170, 200),
                  center=True, shadow=False)

    # ── Caminhos com glow ────────────────────────────────────

    def _draw_caminhos(self, surface):
        t = self._t
        for caminho in _CAMINHOS:
            pts  = caminho["pts"]
            cor  = caminho["cor"]
            tipo = caminho["tipo"]

            if len(pts) < 2:
                continue

            # Desativa cor se caminho bloqueado
            if tipo == "lava" and self._progresso < 1:
                cor = (60, 60, 70)

            # Glow em 3 passes
            for larg, alpha in [(12, 35), (6, 75), (2, 210)]:
                gs = pygame.Surface((W, H), pygame.SRCALPHA)
                for i in range(len(pts) - 1):
                    pygame.draw.line(gs, (*cor, alpha),
                                     pts[i], pts[i + 1], larg)
                surface.blit(gs, (0, 0))

            # Partícula viajando
            desbloqueado = tipo == "azul" or (tipo == "lava" and self._progresso >= 1)
            if desbloqueado:
                total = len(pts) - 1
                prog  = (t * 0.4) % total
                seg   = int(prog)
                frac  = prog - seg
                if seg < total:
                    p0 = pts[seg]
                    p1 = pts[seg + 1]
                    px = int(p0[0] + (p1[0] - p0[0]) * frac)
                    py = int(p0[1] + (p1[1] - p0[1]) * frac)
                    brilho = int(abs(math.sin(t * 4)) * 80 + 175)
                    pcor = (brilho, brilho, 255) if tipo == "azul" else (255, brilho // 2, 0)
                    pygame.draw.circle(surface, pcor,        (px, py), 5)
                    pygame.draw.circle(surface, (255,255,255), (px, py), 2)

    # ── Ponto de início ──────────────────────────────────────

    def _draw_inicio(self, surface):
        cx, cy = 248, 528
        pulse  = abs(math.sin(self._t * 2)) * 10
        ring   = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(ring, (0, 220, 130, 55),
                           (40, 40), int(16 + pulse))
        surface.blit(ring, (cx - 40, cy - 40))
        pygame.draw.circle(surface, ACCENT, (cx, cy), 9)
        pygame.draw.circle(surface, WHITE,  (cx, cy), 9, 2)
        draw_text(surface, "Início",
                  cx + 16, cy - 9,
                  size=FONT_TINY, color=ACCENT,
                  bold=True, shadow=True)

    # ── Pins de localização ──────────────────────────────────

    def _draw_pins(self, surface):
        for k, loc in _LOCAIS.items():
            cx, cy = loc["pos"]
            avail  = self._local_disponivel(k)
            cor    = loc["cor"] if avail else GRAY_DARK
            btn    = self._btns[k]
            hover  = (self._hover == k)

            if hover:
                pulse = int(abs(math.sin(self._t * 3)) * 18)
                ring  = pygame.Surface((130, 130), pygame.SRCALPHA)
                pygame.draw.circle(ring, (*cor, 45), (65, 65), 44 + pulse)
                surface.blit(ring, (cx - 65, cy - 65))

            btn.draw(surface)

            label_y = btn.rect.bottom + 7
            draw_text(surface, loc["nome"],
                      cx, label_y,
                      size=FONT_TINY, color=cor,
                      center=True, shadow=True)
            if not avail:
                draw_text(surface, "[BLOQUEADO]",
                          cx, label_y + 16,
                          size=FONT_TINY, color=GRAY,
                          center=True, shadow=False)

    # ── HUD ──────────────────────────────────────────────────

    def _draw_hud(self, surface):
        h    = self._heroi
        rect = pygame.Rect(16, H - 84, 316, 70)
        hud  = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(hud, (5, 8, 25, 220), hud.get_rect(), border_radius=8)
        pygame.draw.rect(hud, (*h.cor, 180), hud.get_rect(), 2, border_radius=8)
        surface.blit(hud, rect.topleft)
        draw_text(surface, f"{h.nome}   Nv.{h.nivel}",
                  rect.x + 12, rect.y + 9,
                  size=FONT_SMALL, color=h.cor, bold=True)
        draw_text(surface,
                  f"HP {h.hp}/{h.hp_max}    MP {h.mp}/{h.mp_max}    Ouro {h.ouro}",
                  rect.x + 12, rect.y + 38,
                  size=FONT_TINY, color=(180, 190, 220))

    # ── Bússola ──────────────────────────────────────────────

    def _draw_bussola(self, surface, cx, cy):
        r  = 44
        bg = pygame.Surface((r * 2 + 12, r * 2 + 12), pygame.SRCALPHA)
        pygame.draw.circle(bg, (5, 8, 25, 210), (r + 6, r + 6), r)
        pygame.draw.circle(bg, (60, 80, 140, 255), (r + 6, r + 6), r, 2)
        surface.blit(bg, (cx - r - 6, cy - r - 6))

        for angulo, letra, col in [
            (0,   "N", (100, 190, 255)),
            (90,  "L", (120, 120, 140)),
            (180, "S", (120, 120, 140)),
            (270, "O", (120, 120, 140)),
        ]:
            rad = math.radians(angulo - 90)
            tx  = int(cx + math.cos(rad) * (r - 11))
            ty  = int(cy + math.sin(rad) * (r - 11))
            draw_text(surface, letra, tx, ty - 8,
                      size=FONT_TINY, color=col,
                      center=True, shadow=True)

        # Agulha Norte azul
        an = math.radians(-90)
        nx = int(cx + math.cos(an) * (r - 18))
        ny = int(cy + math.sin(an) * (r - 18))
        pygame.draw.polygon(surface, (100, 180, 255), [
            (nx, ny), (cx - 5, cy), (cx + 5, cy)
        ])
        # Agulha Sul cinza
        aso = math.radians(90)
        sx  = int(cx + math.cos(aso) * (r - 18))
        sy  = int(cy + math.sin(aso) * (r - 18))
        pygame.draw.polygon(surface, (80, 80, 105), [
            (sx, sy), (cx - 5, cy), (cx + 5, cy)
        ])
        pygame.draw.circle(surface, WHITE, (cx, cy), 4)

    # ── Painel de status ─────────────────────────────────────

    def _draw_status(self, surface):
        h    = self._heroi
        rect = pygame.Rect(W // 2 - 215, H // 2 - 235, 430, 470)

        blur = pygame.Surface((W, H), pygame.SRCALPHA)
        blur.fill((0, 0, 20, 140))
        surface.blit(blur, (0, 0))

        draw_panel(surface, rect, bg_color=(10, 8, 30),
                   border_color=h.cor, border_width=3, alpha=252)

        draw_text(surface, f"⚔  {h.nome}",
                  rect.centerx, rect.y + 20,
                  size=FONT_LARGE, color=h.cor, bold=True, center=True)
        draw_text(surface, f"Nível {h.nivel}  ·  {h.tipo.title()}",
                  rect.centerx, rect.y + 56,
                  size=FONT_SMALL, color=GOLD, center=True)

        pygame.draw.line(surface, h.cor,
                         (rect.x + 24, rect.y + 82),
                         (rect.x + rect.width - 24, rect.y + 82), 1)

        stats = [
            ("HP",     f"{h.hp} / {h.hp_max}",           HP_GREEN),
            ("MP",     f"{h.mp} / {h.mp_max}",           MP_BLUE),
            ("Ataque", str(h.ataque),                     ORANGE),
            ("Defesa", str(h.defesa),                     CYAN),
            ("Poções", str(h.pocoes),                     WHITE),
            ("Ouro",   str(h.ouro),                       GOLD),
            ("XP",     f"{h.xp} / {h.xp_proximo_nivel}", ACCENT),
        ]

        cy = rect.y + 98
        for label, val, col in stats:
            pygame.draw.line(surface, (40, 35, 70),
                             (rect.x + 20, cy - 2),
                             (rect.x + rect.width - 20, cy - 2), 1)
            draw_text(surface, label,
                      rect.x + 32, cy + 2,
                      size=FONT_SMALL, color=GRAY)
            draw_text(surface, val,
                      rect.x + rect.width - 32 - len(val) * 9, cy + 2,
                      size=FONT_SMALL, color=col)
            cy += 35

        if h.habilidades:
            pygame.draw.line(surface, PANEL_BORDER,
                             (rect.x + 20, cy + 4),
                             (rect.x + rect.width - 20, cy + 4), 1)
            cy += 20
            draw_text(surface, "Habilidades:",
                      rect.x + 32, cy,
                      size=FONT_TINY, color=PURPLE)
            cy += 18
            for hab in h.habilidades:
                draw_text(surface, f"  •  {hab}",
                          rect.x + 32, cy,
                          size=FONT_TINY, color=WHITE)
                cy += 16

        draw_text(surface, "[ ESC para fechar ]",
                  rect.centerx, rect.y + rect.height - 24,
                  size=FONT_TINY, color=GRAY, center=True)

    # ── Fallback sem imagem ──────────────────────────────────

    def _draw_grid_fallback(self, surface):
        for gx in range(0, W, 60):
            pygame.draw.line(surface, (20, 30, 55), (gx, 0), (gx, H), 1)
        for gy in range(0, H, 60):
            pygame.draw.line(surface, (20, 30, 55), (0, gy), (W, gy), 1)