# ============================================================
#  ELDORIA GAME - CONSTANTS
# ============================================================

SCREEN_WIDTH  = 1024
SCREEN_HEIGHT = 768
FPS           = 60
TITLE         = "Atrinium"

# ── Cores ────────────────────────────────────────────────────
BLACK        = (0,   0,   0)
WHITE        = (255, 255, 255)
DARK_BG      = (12,  10,  30)
DARK_PANEL   = (25,  20,  55)
PANEL_BORDER = (80,  60, 160)
PRIMARY      = (90, 120, 255)
ACCENT       = (0,  220, 150)
GOLD         = (255, 210,  50)
RED          = (220,  50,  50)
RED_DARK     = (140,  20,  20)
GREEN        = (50,  200,  80)
PURPLE       = (160,  60, 220)
CYAN         = (0,   200, 230)
ORANGE       = (255, 140,  20)
GRAY         = (120, 120, 130)
GRAY_DARK    = (50,   50,  65)
HP_GREEN     = (60,  200,  80)
HP_YELLOW    = (230, 200,  30)
HP_RED       = (210,  40,  40)
MP_BLUE      = (50,  130, 255)

# ── Tamanhos de fonte ─────────────────────────────────────────
FONT_HUGE   = 52
FONT_TITLE  = 38
FONT_LARGE  = 28
FONT_MEDIUM = 22
FONT_SMALL  = 17
FONT_TINY   = 13

# ── Estados do jogo ───────────────────────────────────────────
STATE_INTRO       = "intro"
STATE_HERO_SELECT = "hero_select"
STATE_PROLOGUE    = "prologue"
STATE_BATTLE      = "battle"
STATE_MAP         = "map"
STATE_SHOP        = "shop"
STATE_LEVELUP     = "levelup"
STATE_GAME_OVER   = "game_over"
STATE_VICTORY     = "victory"

# ── Inimigos disponíveis ──────────────────────────────────────
ENEMY_SENTINELA  = "sentinela"
ENEMY_GENERAL    = "general_bug"
ENEMY_DRAKON     = "rei_drakon"

# ── Textos de lore ────────────────────────────────────────────
LORE_LINES = [
    "Em um reino antigo chamado Atrinium...",
    "",
    "Todo o conhecimento do mundo era guardado no Grande Código,",
    "um cristal vivo que mantinha a ordem entre os reinos.",
    "",
    "Mas nas profundezas do Núcleo do Kernel,",
    "o terrível Rei Drakon corrompeu os fios do saber,",
    "espalhando erros, exceções e bugs pelo mundo.",
    "",
    "As Minas Necron foram tomadas por sentinelas de sucata.",
    "A Torre do Castelo caiu sob o comando do General Bug.",
    "O próprio sistema corre risco de colapso total.",
    "",
    "Apenas um herói capaz de dominar a arte de",
    "COMPILAR ENERGIA — a antiga linguagem Python —",
    "poderá restaurar o Grande Código.",
    "",
    "Você é esse herói.",
    "",
    "[ Pressione ENTER para iniciar sua jornada ]",
]