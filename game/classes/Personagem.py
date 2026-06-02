

class Personagem:
    """Classe base para todos os personagens do jogo."""

    def __init__(self, nome: str, hp: int, hp_max: int,
                 ataque: int, defesa: int, nivel: int = 1):
        self.nome      = nome
        self.hp        = hp
        self.hp_max    = hp_max
        self.ataque    = ataque
        self.defesa    = defesa
        self.nivel     = nivel
        self.descricao = ""
        self.cor       = (200, 200, 200)   # cor visual padrão

    # ── Combate ──────────────────────────────────────────────

    def receber_dano(self, dano: int) -> int:
        """Aplica dano considerando defesa. Retorna dano real."""
        dano_real = max(1, dano - self.defesa)
        self.hp   = max(0, self.hp - dano_real)
        return dano_real

    def receber_dano_fixo(self, dano: int) -> int:
        """Aplica dano ignorando defesa (dano mágico)."""
        self.hp = max(0, self.hp - dano)
        return dano

    def atacar(self, alvo: "Personagem") -> int:
        """Ataca um alvo. Retorna dano causado."""
        return alvo.receber_dano(self.ataque)

    def curar(self, quantidade: int) -> int:
        """Cura o personagem. Retorna HP restaurado."""
        hp_antes = self.hp
        self.hp  = min(self.hp_max, self.hp + quantidade)
        return self.hp - hp_antes

    # ── Status ───────────────────────────────────────────────

    def esta_vivo(self) -> bool:
        return self.hp > 0

    @property
    def percentual_hp(self) -> float:
        return self.hp / self.hp_max if self.hp_max > 0 else 0.0

    # ── Representação ────────────────────────────────────────

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}({self.nome!r}, "
                f"HP={self.hp}/{self.hp_max}, "
                f"ATK={self.ataque}, DEF={self.defesa}, "
                f"Nível={self.nivel})")