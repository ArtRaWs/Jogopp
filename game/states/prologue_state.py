# ============================================================
#  ELDORIA GAME - ESTADO: PRÓLOGO (Tutorial com Mestre Kael)
# ============================================================

import pygame
import math
import os
from utils.game_state_manager import BaseState
from utils.constants    import *
from utils.ui           import draw_text, draw_panel, Button, StarField


_DIALOGOS = [
    {
        "speaker": "Mestre Kael",
        "text": (
            "Ah, você veio! Eu sabia que chegaria alguém capaz.\n"
            "Sou Kael, Arquimestre dos Compiladores.\n"
            "Eldoria precisa de você, jovem herói."
        ),
        "cor": GOLD,
    },
    {
        "speaker": "Mestre Kael",
        "text": (
            "Drakon corrompeu o Grande Código com seus bugs.\n"
            "Mas há uma arte antiga que pode restaurá-lo:\n"
            "a linguagem PYTHON — o Compilar de Energia."
        ),
        "cor": GOLD,
    },
    {
        "speaker": "Mestre Kael",
        "text": (
            "Em batalha, você terá três opções:\n\n"
            "⚔  ATAQUE BÁSICO — dano físico direto ao inimigo.\n"
            "⊕  USAR POÇÃO    — restaura seus pontos de vida.\n"
            "✦  HABILIDADE    — abre o Painel de Python!"
        ),
        "cor": GOLD,
    },
    {
        "speaker": "Mestre Kael",
        "text": (
            "No Painel de Python, uma pergunta surgirá.\n"
            "Responda corretamente e seu golpe especial\n"
            "causará dano massivo ao inimigo!"
        ),
        "cor": GOLD,
    },
    {
        "speaker": "Mestre Kael",
        "text": (
            "Se errar... a habilidade falhará e você ficará\n"
            "vulnerável por um turno. Estude bem Python!\n"
            "O conhecimento é sua maior arma."
        ),
        "cor": ORANGE,
    },
    {
        "speaker": "Mestre Kael",
        "text": (
            "Os chefes que você enfrentará são:\n\n"
            "• Sentinela de Sucata (Dicionários Python)\n"
            "• General Bug        (Listas de Listas)\n"
            "• Rei Drakon         (Arquivos e Estruturas)"
        ),
        "cor": RED,
    },
    {
        "speaker": "Mestre Kael",
        "text": (
            "Minha Oficina sempre estará disponível no mapa.\n"
            "Compre poções e equipamentos para se preparar.\n\n"
            "Que o código seja com você, herói!"
        ),
        "cor": GOLD,
    },
    {
        "speaker": "Sistema",
        "text": (
            "TUTORIAL CONCLUÍDO!\n\n"
            "Primeiro destino: MINAS NECRON.\n"
            "Enfrente a Sentinela de Sucata!\n\n"
            "[ Pressione ENTER ou clique para iniciar ]"
        ),
        "cor": ACCENT,
    },
]


class PrologueState(BaseState):

    def _asset_path(self, filename: str) -> str:
        game_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(game_dir, "assets", filename)

    def enter(self, data: dict = None):
        self._stars    = StarField(80)
        self._t        = 0.0
        self._idx      = 0
        self._alpha    = 0.0
        self._char_idx = 0.0   # índice de caracteres para efeito typewriter
        self._speed    = 40.0  # chars por segundo

        # Fundo (inicio.png)
        self._bg = None
        try:
            path = self._asset_path("inicio.png")
            self._bg = pygame.image.load(path).convert()
            self._bg = pygame.transform.smoothscale(self._bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception:
            self._bg = None

        self._btn_next = Button(
            pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 70, 180, 48),
            "Próximo →", color=PRIMARY, font_size=FONT_MEDIUM
        )
        self._btn_skip = Button(
            pygame.Rect(20, SCREEN_HEIGHT - 60, 110, 40),
            "Pular »", color=GRAY_DARK, font_size=FONT_SMALL
        )

    def _dialogo_atual(self):
        return _DIALOGOS[self._idx]

    def _texto_visivel(self) -> str:
        full = self._dialogo_atual()["text"]
        n    = int(self._char_idx)
        return full[:n]

    def _texto_completo(self) -> bool:
        full = self._dialogo_atual()["text"]
        return int(self._char_idx) >= len(full)

    def _avancar(self):
        if not self._texto_completo():
            # Completa o texto primeiro
            self._char_idx = float(len(self._dialogo_atual()["text"]))
            return
        self._idx += 1
        if self._idx >= len(_DIALOGOS):
            self._iniciar_batalha()
            return
        self._char_idx = 0.0
        self._alpha    = 0.0

    def _iniciar_batalha(self):
        self.manager.inimigo_atual = ENEMY_SENTINELA
        self.go_to(STATE_BATTLE, {"inimigo": ENEMY_SENTINELA, "primeiro": True})

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        self._btn_next.update((mx, my))
        self._btn_skip.update((mx, my))

        for e in events:
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._avancar()
            if self._btn_next.is_clicked(e):
                self._avancar()
            if self._btn_skip.is_clicked(e):
                self._iniciar_batalha()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self._avancar()

    def update(self, dt: float):
        self._t += dt
        self._stars.update(dt)
        if self._alpha < 1.0:
            self._alpha = min(1.0, self._alpha + dt * 1.5)
        if not self._texto_completo():
            self._char_idx += self._speed * dt

    def draw(self, surface: pygame.Surface):
        if self._bg:
            surface.blit(self._bg, (0, 0))
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 140))
            surface.blit(ov, (0, 0))
        else:
            surface.fill(DARK_BG)
            self._stars.draw(surface)

        dialogo = self._dialogo_atual()

        # ── Título ────────────────────────────────────────────
        draw_text(surface, "PRÓLOGO — O TUTORIAL DO MESTRE",
                  SCREEN_WIDTH // 2, 30,
                  size=FONT_MEDIUM, color=PURPLE,
                  bold=True, center=True)

        # ── Sprite do Kael ────────────────────────────────────
        self._draw_kael(surface, 160, SCREEN_HEIGHT // 2 - 20)

        # ── Painel de diálogo ─────────────────────────────────
        dlg_rect = pygame.Rect(280, 120, SCREEN_WIDTH - 310, SCREEN_HEIGHT - 220)
        draw_panel(surface, dlg_rect, alpha=220)

        # Speaker
        draw_text(surface, dialogo["speaker"],
                  dlg_rect.x + 20, dlg_rect.y + 15,
                  size=FONT_MEDIUM, color=dialogo["cor"],
                  bold=True)
        pygame.draw.line(surface, dialogo["cor"],
                         (dlg_rect.x + 20, dlg_rect.y + 42),
                         (dlg_rect.x + 260, dlg_rect.y + 42), 1)

        # Texto com typewriter
        ty  = dlg_rect.y + 55
        visible = self._texto_visivel()
        for line in visible.split('\n'):
            draw_text(surface, line, dlg_rect.x + 20, ty,
                      size=FONT_SMALL, color=WHITE, shadow=True)
            ty += FONT_SMALL + 8

        # Cursor piscando
        if not self._texto_completo():
            if int(self._t * 4) % 2 == 0:
                pygame.draw.rect(surface, WHITE,
                                 pygame.Rect(dlg_rect.x + 22, ty, 10, 16))

        # Indicador de progresso
        prog = f"{self._idx + 1} / {len(_DIALOGOS)}"
        draw_text(surface, prog,
                  dlg_rect.x + 20, dlg_rect.y + dlg_rect.height - 28,
                  size=FONT_TINY, color=GRAY)

        self._btn_next.draw(surface)
        self._btn_skip.draw(surface)

    def _draw_kael(self, surface, cx, cy):
        """Desenha o Mestre Kael com formas geométricas."""
        t = self._t
        bob = int(math.sin(t * 1.5) * 5)
        cy += bob

        # Manto longo
        pygame.draw.polygon(surface, (60, 40, 100), [
            (cx - 30, cy + 70), (cx, cy - 10), (cx + 30, cy + 70)
        ])
        # Corpo
        pygame.draw.rect(surface, (80, 55, 130), pygame.Rect(cx - 18, cy - 10, 36, 50))
        # Cabeça
        pygame.draw.circle(surface, (200, 170, 130), (cx, cy - 26), 22)
        # Barba
        pygame.draw.polygon(surface, (220, 210, 200), [
            (cx - 14, cy - 10), (cx + 14, cy - 10), (cx + 8, cy + 20), (cx - 8, cy + 20)
        ])
        # Chapéu
        pygame.draw.polygon(surface, (40, 20, 80), [
            (cx - 26, cy - 44), (cx, cy - 88), (cx + 26, cy - 44)
        ])
        pygame.draw.ellipse(surface, (40, 20, 80),
                            pygame.Rect(cx - 32, cy - 52, 64, 16))
        # Estrela no chapéu
        pygame.draw.circle(surface, GOLD, (cx, cy - 70), 5)
        # Cajado
        pygame.draw.line(surface, (140, 100, 60),
                         (cx + 26, cy + 68), (cx + 28, cy - 60), 5)
        orb_col = (
            int(abs(math.sin(t)) * 200 + 55),
            int(abs(math.cos(t * 0.7)) * 100 + 50),
            255
        )
        pygame.draw.circle(surface, orb_col, (cx + 28, cy - 64), 10)
        pygame.draw.circle(surface, WHITE,   (cx + 28, cy - 64), 10, 1)

        # Aura mágica
        for i in range(3):
            a  = t * 1.5 + i * (math.pi * 2 / 3)
            ax = int(cx + math.cos(a) * 35)
            ay = int(cy - 20 + math.sin(a) * 20)
            pygame.draw.circle(surface, PURPLE, (ax, ay), 3)