# ============================================================
#  ELDORIA GAME - BASE STATE + GAME MANAGER
# ============================================================

import pygame
from utils.constants import *


# ── Estado base ──────────────────────────────────────────────

class BaseState:
    """Interface comum para todos os estados do jogo."""

    def __init__(self, manager: "GameManager"):
        self.manager = manager

    def enter(self, data: dict = None):
        """Chamado ao entrar no estado."""

    def exit(self):
        """Chamado ao sair do estado."""

    def handle_events(self, events: list):
        """Processa eventos do pygame."""

    def update(self, dt: float):
        """Atualiza lógica do estado."""

    def draw(self, surface: pygame.Surface):
        """Renderiza o estado."""

    def go_to(self, state_name: str, data: dict = None):
        self.manager.change_state(state_name, data)


# ── Game Manager ─────────────────────────────────────────────

class GameManager:
    """
    Máquina de estados central do jogo.
    Gerencia transições e dados compartilhados entre estados.
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._states: dict[str, BaseState] = {}
        self._current: BaseState | None     = None
        self._current_name: str             = ""

        # ── Dados globais da sessão ───────────────────────────
        self.heroi          = None
        self.inimigo_atual  = ""
        self.progresso      = 0
        self.ouro           = 0
        self.ultima_batalha = ""

    # ── Registro de estados ──────────────────────────────────

    def register(self, name: str, state: BaseState):
        self._states[name] = state

    def register_all(self):
        """Importa e registra todos os estados do jogo."""
        from states.intro_state       import IntroState
        from states.hero_select_state import HeroSelectState
        from states.prologue_state    import PrologueState
        from states.battle_state      import BattleState
        from states.map_state         import MapState
        from states.shop_state        import ShopState
        from states.levelup_state     import LevelUpState
        from states.game_over_state   import GameOverState
        from states.victory_state     import VictoryState
        from states.video_state       import VideoState       # ← NOVO

        self.register(STATE_INTRO,       IntroState(self))
        self.register(STATE_HERO_SELECT, HeroSelectState(self))
        self.register("video",           VideoState(self))    # ← NOVO
        self.register(STATE_PROLOGUE,    PrologueState(self))
        self.register(STATE_BATTLE,      BattleState(self))
        self.register(STATE_MAP,         MapState(self))
        self.register(STATE_SHOP,        ShopState(self))
        self.register(STATE_LEVELUP,     LevelUpState(self))
        self.register(STATE_GAME_OVER,   GameOverState(self))
        self.register(STATE_VICTORY,     VictoryState(self))

    # ── Transições ───────────────────────────────────────────

    def change_state(self, name: str, data: dict = None):
        if self._current:
            self._current.exit()
        self._current_name = name
        self._current      = self._states[name]
        self._current.enter(data or {})

    # ── Loop principal ───────────────────────────────────────

    def handle_events(self, events: list):
        if self._current:
            self._current.handle_events(events)

    def update(self, dt: float):
        if self._current:
            self._current.update(dt)

    def draw(self):
        if self._current:
            self._current.draw(self.screen)