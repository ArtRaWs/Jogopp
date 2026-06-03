# ============================================================
#  ELDORIA GAME - ANIMAÇÃO DE ATAQUE (Arthur e Luna)
#
#  Spritesheet: assets/atack.png  —  grid 4 colunas x 2 linhas
#
#  Arthur / Luna compartilham o mesmo layout de frames:
#  [0:Idle ] [1:Prep ] [2:Dash  ] [3:Impact]
#  [4:Windup] [5:Blast] [6:Slash ] [7:Return]
# ============================================================

import pygame
import math
import random
from dataclasses import dataclass, field
from typing import Callable


# ── Constantes ───────────────────────────────────────────────

SHEET_COLS = 4
SHEET_ROWS = 2
FRAME_W    = 354
FRAME_H    = 554

# Índices dos frames (linha * 4 + coluna)
F_IDLE    = 0
F_PREP    = 1
F_DASH    = 2
F_IMPACT  = 3
F_WINDUP  = 4
F_BLAST   = 5
F_SLASH   = 6
F_RETURN  = 7

# Duração de cada fase em segundos
PHASE_DURATION = {
    "prep":      0.10,
    "dash":      0.13,
    "impact":    0.06,
    "freeze":    0.08,   # 80 ms — freeze frame estilo japonês
    "knockback": 0.18,
    "return":    0.15,
}

# Cores de efeito por personagem
EFFECT_COLORS = {
    "arthur": [(80, 160, 255), (120, 200, 255), (200, 230, 255)],
    "luna":   [(100, 60, 255), (160, 80, 255),  (200, 150, 255)],
}


# ── Partícula simples ────────────────────────────────────────

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: tuple
    radius: int
    life: float = 1.0

    def update(self, dt: float):
        self.x    += self.vx * dt
        self.y    += self.vy * dt
        self.vy   += 200 * dt   # gravidade
        self.life -= dt * 1.2

    @property
    def alive(self) -> bool:
        return self.life > 0

    def draw(self, surface: pygame.Surface):
        r   = max(1, int(self.radius * self.life))
        srf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        a   = min(255, int(self.life * 220))
        pygame.draw.circle(srf, (*self.color, a), (r, r), r)
        surface.blit(srf, (int(self.x) - r, int(self.y) - r))


# ── Animação de ataque ───────────────────────────────────────

class AttackAnimation:
    """
    Reproduz a animação de ataque de Arthur ou Luna
    usando o spritesheet assets/atack.png.

    Parâmetros
    ----------
    sheet      : spritesheet já carregado (pygame.Surface)
    hero_type  : "arthur" | "luna"
    heroi_x/y  : posição base do herói
    inimigo_x/y: posição base do inimigo
    scale      : fator de escala dos frames (padrão 0.55)
    """

    def __init__(self, sheet: pygame.Surface, hero_type: str,
                 heroi_x: int, heroi_y: int,
                 inimigo_x: int, inimigo_y: int,
                 scale: float = 0.55):

        self._sheet      = sheet
        self._hero_type  = hero_type
        self._colors     = EFFECT_COLORS.get(hero_type, EFFECT_COLORS["arthur"])
        self._scale      = scale
        self._frame_size = (int(FRAME_W * scale), int(FRAME_H * scale))

        # Posições
        self._base    = pygame.Vector2(heroi_x, heroi_y)
        self._target  = pygame.Vector2(inimigo_x - 130, heroi_y)
        self._enemy   = pygame.Vector2(inimigo_x, inimigo_y)
        self._pos     = pygame.Vector2(self._base)

        # Estado
        self._phase        = "prep"
        self._phase_t      = 0.0
        self._frame_idx    = F_PREP
        self._particles: list[Particle] = []
        self._blur_trail: list[tuple]   = []   # (x, y, alpha)
        self._flash_alpha  = 0
        self._enemy_offset = 0.0

        # Sinal público: True no frame do impacto
        self.deve_aplicar_dano = False

    # ── Cache de frames escalados ────────────────────────────

    def _get_frame(self, idx: int) -> pygame.Surface:
        col = idx % SHEET_COLS
        row = idx // SHEET_COLS
        region = self._sheet.subsurface(
            pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
        )
        srf = pygame.transform.smoothscale(region, self._frame_size)
        srf.set_colorkey((0, 0, 0), pygame.RLEACCEL)
        return srf

    def _blit_frame(self, surface: pygame.Surface, idx: int,
                    x: float, y: float, alpha: int = 255):
        spr = self._get_frame(idx)
        if alpha < 255:
            spr = spr.copy()
            spr.set_alpha(alpha)
        r = spr.get_rect(midbottom=(int(x), int(y) + self._frame_size[1] // 2))
        surface.blit(spr, r)

    # ── Spawn de partículas ──────────────────────────────────

    def _spawn_impact(self):
        ix, iy = self._target.x, self._target.y - 60
        # Partículas pequenas
        for _ in range(35):
            a   = random.uniform(0, math.tau)
            spd = random.uniform(80, 280)
            self._particles.append(Particle(
                x=ix, y=iy,
                vx=math.cos(a) * spd, vy=math.sin(a) * spd - 80,
                color=random.choice(self._colors),
                radius=random.randint(2, 5),
                life=1.0,
            ))
        # Partículas de runa maiores
        for _ in range(6):
            a   = random.uniform(0, math.tau)
            spd = random.uniform(40, 100)
            self._particles.append(Particle(
                x=ix + random.uniform(-40, 40),
                y=iy + random.uniform(-30, 30),
                vx=math.cos(a) * spd, vy=math.sin(a) * spd,
                color=self._colors[0],
                radius=random.randint(6, 11),
                life=1.1,
            ))

    # ── Update ───────────────────────────────────────────────

    def update(self, dt: float) -> bool:
        """Avança a animação. Retorna True quando concluída."""
        self._phase_t += dt

        for p in self._particles:
            p.update(dt)
        self._particles = [p for p in self._particles if p.alive]

        if self._flash_alpha > 0:
            self._flash_alpha = max(0, self._flash_alpha - int(dt * 1200))

        return getattr(self, f"_phase_{self._phase}")(dt)

    def _next(self, phase: str):
        self._phase   = phase
        self._phase_t = 0.0

    # ── Fases ────────────────────────────────────────────────

    def _phase_prep(self, dt) -> bool:
        self._frame_idx = F_PREP
        prog = self._phase_t / PHASE_DURATION["prep"]
        # Leve recuo
        self._pos.x = self._base.x - math.sin(prog * math.pi) * 20
        if self._phase_t >= PHASE_DURATION["prep"]:
            self._blur_trail.clear()
            self._next("dash")
        return False

    def _phase_dash(self, dt) -> bool:
        self._frame_idx = F_DASH
        prog      = min(1.0, self._phase_t / PHASE_DURATION["dash"])
        ease      = prog ** 2                          # aceleração quadrática
        self._pos = self._base.lerp(self._target, ease)

        # Registra trilha de motion blur
        self._blur_trail.append((self._pos.x, self._pos.y, 1.0))
        self._blur_trail = [
            (x, y, a - dt * 9)
            for x, y, a in self._blur_trail if a - dt * 9 > 0
        ]

        if prog >= 0.88 and not self.deve_aplicar_dano:
            self.deve_aplicar_dano = True   # sinal de dano

        if self._phase_t >= PHASE_DURATION["dash"]:
            self._pos = pygame.Vector2(self._target)
            self._spawn_impact()
            self._flash_alpha = 255
            self._next("impact")
        return False

    def _phase_impact(self, dt) -> bool:
        self._frame_idx = F_IMPACT
        # Tremor horizontal
        self._pos.x = self._target.x + math.sin(self._phase_t * 80) * 5
        if self._phase_t >= PHASE_DURATION["impact"]:
            self._pos.x = self._target.x
            self._next("freeze")
        return False

    def _phase_freeze(self, dt) -> bool:
        # Frame diferente para Arthur e Luna no freeze
        self._frame_idx = F_BLAST if self._hero_type == "arthur" else F_WINDUP
        if self._phase_t >= PHASE_DURATION["freeze"]:
            self._next("knockback")
        return False

    def _phase_knockback(self, dt) -> bool:
        self._frame_idx = F_SLASH
        prog = self._phase_t / PHASE_DURATION["knockback"]
        # Inimigo: vai +30px e volta
        self._enemy_offset = math.sin(prog * math.pi) * 30
        if self._phase_t >= PHASE_DURATION["knockback"]:
            self._enemy_offset = 0.0
            self._next("return")
        return False

    def _phase_return(self, dt) -> bool:
        self._frame_idx = F_RETURN
        prog      = min(1.0, self._phase_t / PHASE_DURATION["return"])
        ease      = 1 - (1 - prog) ** 2               # desaceleração
        self._pos = self._target.lerp(self._base, ease)
        if self._phase_t >= PHASE_DURATION["return"]:
            self._pos = pygame.Vector2(self._base)
            return True   # animação concluída
        return False

    # ── Propriedade para offset do inimigo ───────────────────

    @property
    def inimigo_offset_x(self) -> int:
        return int(self._enemy_offset)

    # ── Draw ─────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        # 1. Motion blur
        if self._phase == "dash":
            for x, y, a in self._blur_trail[:-1]:
                self._blit_frame(surface, F_DASH, x, y, alpha=int(a * 110))

        # 2. Partículas
        for p in self._particles:
            p.draw(surface)

        # 3. Linhas de corte no impacto / freeze
        if self._phase in ("impact", "freeze"):
            self._draw_slash_lines(surface)

        # 4. Flash de tela
        if self._flash_alpha > 0:
            flash = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            flash.fill((*self._colors[0], min(160, self._flash_alpha)))
            surface.blit(flash, (0, 0))

        # 5. Sprite do herói
        self._blit_frame(surface, self._frame_idx, self._pos.x, self._pos.y)

    def _draw_slash_lines(self, surface: pygame.Surface):
        ix = int(self._target.x)
        iy = int(self._target.y) - 60
        t  = self._phase_t
        a  = max(0, 255 - int(t * 1800))
        col = (*self._colors[0], a)
        for i in range(5):
            angle = math.pi * i / 5 + t * 3
            ex = ix + int(math.cos(angle) * 85)
            ey = iy + int(math.sin(angle) * 55)
            if a > 0:
                pygame.draw.line(surface, self._colors[0], (ix, iy), (ex, ey), 2)
        # Linha horizontal principal
        if a > 0:
            pygame.draw.line(surface, self._colors[1],
                             (ix - 80, iy), (ix + 80, iy), 3)