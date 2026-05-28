# ============================================================
#  ELDORIA GAME - HERÓI (CORRIGIDO)
# ============================================================

from classes.Personagem import Personagem


class Heroi(Personagem):
    """
    Classe Herói — estende Personagem com MP, poções,
    XP, habilidades especiais desbloqueáveis e inventário.
    """

    def __init__(self, nome: str, tipo: str,
                 hp_max: int, ataque: int, defesa: int,
                 mp_max: int = 60):
        super().__init__(nome, hp_max, hp_max, ataque, defesa, nivel=1)

        # ── Tipo ─────────────────────────────────────────────
        self.tipo = tipo           # 'arthur' | 'luna'

        # ── Mana / Energia ───────────────────────────────────
        self.mp     = mp_max
        self.mp_max = mp_max

        # ── Inventário ───────────────────────────────────────
        self.pocoes      = 3
        self.pocao_cura  = 50    # quanto cura cada poção
        self.ouro        = 0

        # ── Progressão ───────────────────────────────────────
        self.xp                = 0
        self.xp_proximo_nivel  = 100
        self.habilidades       = []
        self.habilidades_desc  = {}

        # ── Bônus temporários de batalha ─────────────────────
        self.bonus_ataque_temp = 0
        self.turnos_bonus      = 0

    # ── Poções ───────────────────────────────────────────────

    def usar_pocao(self) -> tuple[bool, int]:
        """Usa uma poção de cura. Retorna (sucesso, hp_recuperado).
        
        CORREÇÃO: typo 'pocoa_cura' removido — usa self.pocao_cura diretamente.
        """
        if self.pocoes <= 0:
            return False, 0
        recuperado = self.curar(self.pocao_cura)  # BUGFIX: era 'pocoa_cura'
        self.pocoes -= 1
        return True, recuperado

    # ── Mana ─────────────────────────────────────────────────

    def gastar_mp(self, custo: int) -> bool:
        if self.mp >= custo:
            self.mp -= custo
            return True
        return False

    def restaurar_mp(self, quantidade: int) -> int:
        antes   = self.mp
        self.mp = min(self.mp_max, self.mp + quantidade)
        return self.mp - antes

    # ── Progressão ───────────────────────────────────────────

    def ganhar_xp(self, quantidade: int) -> bool:
        """Adiciona XP. Retorna True se subiu de nível."""
        self.xp += quantidade
        if self.xp >= self.xp_proximo_nivel:
            self._subir_nivel()
            return True
        return False

    def _subir_nivel(self):
        self.nivel           += 1
        self.xp              -= self.xp_proximo_nivel
        self.xp_proximo_nivel = int(self.xp_proximo_nivel * 1.6)

        self.hp_max += 25
        self.hp      = self.hp_max
        self.ataque += 8
        self.defesa += 3
        self.mp_max += 15
        self.mp      = self.mp_max

    def desbloquear_habilidade(self, nome: str, descricao: str = ""):
        if nome not in self.habilidades:
            self.habilidades.append(nome)
            self.habilidades_desc[nome] = descricao

    # ── Bônus temporários ────────────────────────────────────

    def aplicar_bonus_ataque(self, bonus: int, turnos: int = 2):
        self.bonus_ataque_temp = bonus
        self.turnos_bonus      = turnos

    def processar_turno(self):
        if self.turnos_bonus > 0:
            self.turnos_bonus -= 1
            if self.turnos_bonus == 0:
                self.bonus_ataque_temp = 0

    @property
    def ataque_total(self) -> int:
        return self.ataque + self.bonus_ataque_temp

    @property
    def percentual_mp(self) -> float:
        return self.mp / self.mp_max if self.mp_max > 0 else 0.0

    def __repr__(self) -> str:
        return (f"Herói({self.nome!r}, tipo={self.tipo!r}, "
                f"HP={self.hp}/{self.hp_max}, MP={self.mp}/{self.mp_max}, "
                f"Nível={self.nivel}, XP={self.xp}/{self.xp_proximo_nivel})")


# ── Fábricas de heróis ────────────────────────────────────────

def criar_arthur() -> Heroi:
    """Arthur — Guerreiro Compilador. Alto ATK e DEF, MP menor."""
    h            = Heroi("Arthur", "arthur", hp_max=140, ataque=28, defesa=12, mp_max=45)
    h.descricao  = ("Guerreiro da Ordem dos Compiladores.\n"
                    "Usa força bruta e foco absoluto para\n"
                    "destruir bugs com código preciso.")
    h.cor        = (80, 140, 255)
    h.pocao_cura = 55
    h.desbloquear_habilidade("Golpe Compilado", "Ataque poderoso que ignora metade da defesa inimiga.")
    return h


def criar_luna() -> Heroi:
    """Luna — Maga das Estruturas. Alto MP, ataques mágicos especiais."""
    h            = Heroi("Luna", "luna", hp_max=110, ataque=20, defesa=7, mp_max=90)
    h.descricao  = ("Arquiteta de dados e feiticeira dos\n"
                    "algoritmos. Converte erros em energia\n"
                    "pura para destruir o caos.")
    h.cor        = (200, 80, 255)
    h.pocao_cura = 45
    h.desbloquear_habilidade("Fluxo de Dados", "Ataque mágico que dobra o dano com resposta correta.")
    return h