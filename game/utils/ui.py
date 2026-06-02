
import pygame
from utils.constants import *


# ── Cache de fontes ──────────────────────────────────────────
_font_cache: dict = {}


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _font_cache:
        try:
            path = "assets/font.ttf"
            _font_cache[key] = pygame.font.Font(path, size)
        except Exception:
            _font_cache[key] = pygame.font.SysFont("consolas" if not bold else "consolas", size, bold=bold)
    return _font_cache[key]


# ── Texto ────────────────────────────────────────────────────

def draw_text(surface, text: str, x: int, y: int,
              size: int = FONT_MEDIUM, color=WHITE,
              bold: bool = False, center: bool = False,
              shadow: bool = True):
    font = get_font(size, bold)
    if shadow:
        srf = font.render(text, True, (0, 0, 0))
        if center:
            r = srf.get_rect(center=(x, y))
            surface.blit(srf, (r.x + 2, r.y + 2))
        else:
            surface.blit(srf, (x + 2, y + 2))
    srf = font.render(text, True, color)
    if center:
        r = srf.get_rect(center=(x, y))
        surface.blit(srf, r)
    else:
        surface.blit(srf, (x, y))
    return srf.get_rect()


def draw_text_wrapped(surface, text: str, x: int, y: int, max_width: int,
                      size: int = FONT_SMALL, color=WHITE, line_spacing: int = 6) -> int:
    """Renderiza texto com quebra automática. Retorna Y final."""
    font  = get_font(size)
    words = text.split(' ')
    lines = []
    cur   = ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    cy = y
    for line in lines:
        draw_text(surface, line, x, cy, size=size, color=color)
        cy += font.get_height() + line_spacing
    return cy


# ── Painéis ──────────────────────────────────────────────────

def draw_panel(surface, rect: pygame.Rect,
               bg_color=DARK_PANEL, border_color=PANEL_BORDER,
               border_width: int = 2, alpha: int = 230,
               corner_radius: int = 8):
    """Desenha um painel com fundo semitransparente e borda."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    r     = pygame.Rect(0, 0, rect.width, rect.height)
    pygame.draw.rect(panel, (*bg_color, alpha), r, border_radius=corner_radius)
    pygame.draw.rect(panel, (*border_color, 255), r, border_width, border_radius=corner_radius)
    surface.blit(panel, rect.topleft)


def draw_panel_gradient(surface, rect: pygame.Rect,
                        color_top=(30, 20, 60), color_bottom=(10, 8, 30),
                        border_color=PANEL_BORDER, border_width: int = 2):
    """Painel com gradiente vertical."""
    for i in range(rect.height):
        t   = i / rect.height
        r   = int(color_top[0] * (1-t) + color_bottom[0] * t)
        g   = int(color_top[1] * (1-t) + color_bottom[1] * t)
        b   = int(color_top[2] * (1-t) + color_bottom[2] * t)
        pygame.draw.line(surface, (r, g, b),
                         (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))
    pygame.draw.rect(surface, border_color, rect, border_width, border_radius=6)


# ── Barras ───────────────────────────────────────────────────

def draw_bar(surface, x: int, y: int, width: int, height: int,
             value: float, max_value: float, label: str = "",
             fg_color=HP_GREEN, bg_color=GRAY_DARK):
    """Barra de progresso genérica (HP, MP, XP)."""
    ratio = max(0.0, min(1.0, value / max_value)) if max_value > 0 else 0.0

    # Fundo
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, bg_color, bg_rect, border_radius=4)

    # Preenchimento
    if ratio > 0:
        fill_w = int(width * ratio)
        # Cor dinâmica para HP
        if fg_color == HP_GREEN:
            if ratio < 0.25:
                fg_color = HP_RED
            elif ratio < 0.50:
                fg_color = HP_YELLOW
        fill_rect = pygame.Rect(x, y, fill_w, height)
        pygame.draw.rect(surface, fg_color, fill_rect, border_radius=4)

    # Borda
    pygame.draw.rect(surface, PANEL_BORDER, bg_rect, 1, border_radius=4)

    # Label
    if label:
        draw_text(surface, label, x + 4, y + height // 2 - 7,
                  size=FONT_TINY, color=WHITE, shadow=True)

    # Valor
    val_text = f"{int(value)}/{int(max_value)}"
    draw_text(surface, val_text, x + width - 80, y + height // 2 - 7,
              size=FONT_TINY, color=WHITE, shadow=True)


# ── Botões ───────────────────────────────────────────────────

class Button:
    """Botão interativo com hover e estado desabilitado."""

    NORMAL   = 0
    HOVER    = 1
    DISABLED = 2

    def __init__(self, rect: pygame.Rect, text: str,
                 color=PRIMARY, hover_color=ACCENT,
                 text_color=WHITE, disabled_color=GRAY_DARK,
                 font_size: int = FONT_MEDIUM):
        self.rect           = rect
        self.text           = text
        self.color          = color
        self.hover_color    = hover_color
        self.text_color     = text_color
        self.disabled_color = disabled_color
        self.font_size      = font_size
        self.enabled        = True
        self._state         = self.NORMAL

    def update(self, mouse_pos):
        if not self.enabled:
            self._state = self.DISABLED
        elif self.rect.collidepoint(mouse_pos):
            self._state = self.HOVER
        else:
            self._state = self.NORMAL

    def is_clicked(self, event) -> bool:
        return (self.enabled and
                event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))

    def draw(self, surface):
        if self._state == self.DISABLED:
            bg = self.disabled_color
        elif self._state == self.HOVER:
            bg = self.hover_color
        else:
            bg = self.color

        pygame.draw.rect(surface, bg, self.rect, border_radius=6)
        pygame.draw.rect(surface, PANEL_BORDER, self.rect, 2, border_radius=6)
        draw_text(surface, self.text,
                  self.rect.centerx, self.rect.centery,
                  size=self.font_size, color=self.text_color,
                  center=True, shadow=True)


# ── Fundo animado ────────────────────────────────────────────

class StarField:
    """Fundo de estrelas animadas."""

    def __init__(self, count: int = 80):
        import random
        self._stars = [
            (random.randint(0, SCREEN_WIDTH),
             random.randint(0, SCREEN_HEIGHT),
             random.uniform(0.2, 1.0),
             random.uniform(0.3, 1.5))
            for _ in range(count)
        ]
        self._t = 0.0

    def update(self, dt: float):
        self._t += dt

    def draw(self, surface):
        import math
        for sx, sy, brightness, speed in self._stars:
            alpha = int(abs(math.sin(self._t * speed + sx)) * 200 + 55)
            v     = int(brightness * 200)
            color = (v, v, min(255, v + 55))
            r     = 1 if brightness < 0.5 else 2
            pygame.draw.circle(surface, color, (sx, sy), r)


# ── Log de combate ───────────────────────────────────────────

class CombatLog:
    """Exibe as últimas mensagens do combate."""

    MAX_LINES = 6

    def __init__(self, rect: pygame.Rect):
        self.rect  = rect
        self._msgs: list[tuple[str, tuple]] = []

    def add(self, msg: str, color=WHITE):
        self._msgs.append((msg, color))
        if len(self._msgs) > self.MAX_LINES:
            self._msgs.pop(0)

    def clear(self):
        self._msgs.clear()

    def draw(self, surface):
        draw_panel(surface, self.rect, alpha=200)
        y = self.rect.y + 8
        for msg, color in self._msgs:
            draw_text(surface, msg, self.rect.x + 10, y,
                      size=FONT_TINY, color=color, shadow=True)
            y += FONT_TINY + 6


# ── Animação de dano flutuante ───────────────────────────────

class DamagePopup:
    """Número de dano que flutua e desaparece."""

    def __init__(self, text: str, x: int, y: int, color=RED):
        self.text    = text
        self.x       = float(x)
        self.y       = float(y)
        self.color   = color
        self.alpha   = 255
        self.alive   = True
        self._vy     = -80.0   # velocidade de subida (px/s)

    def update(self, dt: float):
        self.y     += self._vy * dt
        self.alpha -= 280 * dt
        if self.alpha <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        font = get_font(FONT_LARGE, bold=True)
        srf  = font.render(self.text, True, self.color)
        srf.set_alpha(int(max(0, self.alpha)))
        r    = srf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(srf, r)