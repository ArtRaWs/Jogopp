# ============================================================
#  ELDORIA GAME - VILÃO
# ============================================================

import random
from classes.Personagem import Personagem


class Vilao(Personagem):
    """
    Classe Vilão — estende Personagem com recompensas,
    dicas de Python e ataques especiais.
    """

    def __init__(self, nome: str, hp_max: int,
                 ataque: int, defesa: int,
                 xp_recompensa: int, ouro_recompensa: int = 0):
        super().__init__(nome, hp_max, hp_max, ataque, defesa)

        self.xp_recompensa   = xp_recompensa
        self.ouro_recompensa = ouro_recompensa
        self.dica_python     = ""          # exibida no game over
        self.topico_python   = ""          # tema das perguntas

        # ── Comportamento ────────────────────────────────────
        self.frases_ataque      = ["atacou!", "golpeou!", "investiu contra você!"]
        self.frases_especial    = ["usou um ataque especial!"]
        self.frase_derrotado    = "foi derrotado!"
        self.frase_apresentacao = ""

        # ── Fase Enraivecida (<30% HP) ───────────────────────
        self.enraivecido      = False
        self._bonus_rage      = 0          # bônus de ATK em rage

        # ── IA ───────────────────────────────────────────────
        self._turno = 0

    # ── IA do inimigo ────────────────────────────────────────

    def decidir_acao(self) -> str:
        """Retorna 'ataque', 'especial' ou 'defesa'."""
        self._turno += 1
        if self.percentual_hp < 0.30 and not self.enraivecido:
            self.enraivecido  = True
            self.ataque      += self._bonus_rage
        if self.enraivecido and random.random() < 0.50:
            return "especial"
        if self._turno % 3 == 0:
            return "especial"
        return "ataque"

    def executar_acao(self, heroi) -> tuple[str, int]:
        """
        Executa ação contra o herói.
        Retorna (tipo_acao, dano_causado).
        """
        acao = self.decidir_acao()
        if acao == "especial":
            dano  = self._ataque_especial(heroi)
            frase = random.choice(self.frases_especial)
        else:
            dano  = self.atacar(heroi)
            frase = random.choice(self.frases_ataque)
        return frase, dano

    def _ataque_especial(self, heroi) -> int:
        """Ataque especial padrão — 1.5× o ataque normal (sem defesa)."""
        dano = int(self.ataque * 1.5)
        return heroi.receber_dano_fixo(dano)

    def __repr__(self) -> str:
        return (f"Vilão({self.nome!r}, HP={self.hp}/{self.hp_max}, "
                f"ATK={self.ataque}, DEF={self.defesa})")


# ════════════════════════════════════════════════════════════
#  INIMIGOS ESPECÍFICOS
# ════════════════════════════════════════════════════════════

class SentinelaSuccata(Vilao):
    """Chefe 1 — Minas Necron. Tema: Dicionários Python."""

    def __init__(self):
        super().__init__(
            nome            = "Sentinela de Sucata",
            hp_max          = 80,
            ataque          = 18,
            defesa          = 4,
            xp_recompensa   = 100,
            ouro_recompensa = 30,
        )
        self._bonus_rage         = 6
        self.cor                 = (100, 180, 100)
        self.topico_python       = "dicionarios"
        self.descricao           = "Guardião de ferro das Minas Necron.\nConstruído com peças de código corrompido."
        self.frase_apresentacao  = "ALERTA! INTRUSO DETECTADO. PROTOCOLO DE ELIMINAÇÃO ATIVADO."
        self.frases_ataque       = [
            "disparou rajadas de parafusos!",
            "usou Soco de Ferrugem!",
            "lançou Sobrecarga de Sistema!",
        ]
        self.frases_especial     = [
            "ativou MODO TURBO — Ataque Crítico de Dados!",
            "usou Explosão de Cache!",
        ]
        self.frase_derrotado     = "SISTEMA FALHO... DESLIGANDO..."
        self.dica_python         = (
            "💡 Dica sobre Dicionários Python:\n\n"
            "Dicionários são coleções de pares chave→valor.\n"
            "  d = {'nome': 'Arthur', 'nivel': 5}\n"
            "  print(d['nome'])        # Arthur\n"
            "  print(d.get('hp', 0))  # 0 (padrão se não existir)\n"
            "  d['hp'] = 100          # adiciona ou atualiza"
        )

    def _ataque_especial(self, heroi) -> int:
        dano = int(self.ataque * 1.8)
        return heroi.receber_dano_fixo(dano)


class GeneralBug(Vilao):
    """Chefe 2 — Torre do Castelo. Tema: Listas de Listas."""

    def __init__(self):
        super().__init__(
            nome            = "General Bug",
            hp_max          = 140,
            ataque          = 26,
            defesa          = 8,
            xp_recompensa   = 200,
            ouro_recompensa = 60,
        )
        self._bonus_rage         = 10
        self.cor                 = (220, 100, 50)
        self.topico_python       = "listas"
        self.descricao           = "Comandante das forças de Drakon.\nDomina erros de índice e loops infinitos."
        self.frase_apresentacao  = "Você ousa invadir minha torre?! Prepare-se para um STACK OVERFLOW!"
        self.frases_ataque       = [
            "usou Erro de Índice!",
            "lançou Loop Infinito!",
            "invocou Exceção Fatal!",
        ]
        self.frases_especial     = [
            "ativou KERNEL PANIC — dano massivo!",
            "usou Pilha de Erros — ataque em cadeia!",
        ]
        self.frase_derrotado     = "Impossível... meu código era perfeito..."
        self.dica_python         = (
            "💡 Dica sobre Listas de Listas:\n\n"
            "Matrizes em Python são listas dentro de listas.\n"
            "  matriz = [[1,2,3], [4,5,6], [7,8,9]]\n"
            "  print(matriz[0][1])  # 2 (linha 0, coluna 1)\n"
            "  print(matriz[2][0])  # 7 (linha 2, coluna 0)\n"
            "Lembre: índices começam em 0!"
        )

    def _ataque_especial(self, heroi) -> int:
        # Ataque em dois golpes
        dano1 = heroi.receber_dano(int(self.ataque * 0.9))
        dano2 = heroi.receber_dano(int(self.ataque * 0.7))
        return dano1 + dano2


class ReiDrakon(Vilao):
    """Chefe Final — Núcleo do Kernel. Tema: Arquivos e Estruturas Avançadas."""

    def __init__(self):
        super().__init__(
            nome            = "Rei Drakon",
            hp_max          = 220,
            ataque          = 34,
            defesa          = 12,
            xp_recompensa   = 400,
            ouro_recompensa = 150,
        )
        self._bonus_rage         = 15
        self.cor                 = (180, 30, 220)
        self.topico_python       = "arquivos"
        self.descricao           = "O Corruptor Supremo. Rei das Exceções.\nSeu código infecta tudo que toca."
        self.frase_apresentacao  = "Eu SOU o Grande Código agora! Você não pode me parar!"
        self.frases_ataque       = [
            "usou Corrupção de Dados!",
            "lançou Fragmento do Kernel!",
            "invocou Vírus Ancestral!",
        ]
        self.frases_especial     = [
            "ativou KERNEL OF CHAOS — ataque devastador!",
            "usou REWRITE REALITY — ignora sua defesa!",
            "invocou as Sombras do Kernel!",
        ]
        self.frase_derrotado     = "NÃO... O CÓDIGO... ESTÁ... SE RESTAURANDO..."
        self.dica_python         = (
            "💡 Dica sobre Arquivos em Python:\n\n"
            "Para ler um arquivo com segurança, use 'with':\n"
            "  with open('dados.txt', 'r') as f:\n"
            "      conteudo = f.read()\n\n"
            "Modos: 'r'=leitura, 'w'=escrita, 'a'=append\n"
            "O 'with' fecha o arquivo automaticamente!"
        )
        self._fase_caos = False

    def decidir_acao(self) -> str:
        self._turno += 1
        if self.percentual_hp < 0.50 and not self._fase_caos:
            self._fase_caos   = True
            self.enraivecido  = True
            self.ataque      += self._bonus_rage
        if self.percentual_hp < 0.25:
            return "especial"
        if self._turno % 2 == 0:
            return "especial"
        return "ataque"

    def _ataque_especial(self, heroi) -> int:
        dano = int(self.ataque * 2.0)
        return heroi.receber_dano_fixo(dano)


# ── Fábrica ──────────────────────────────────────────────────

def criar_inimigo(tipo: str) -> Vilao:
    mapa = {
        "sentinela":  SentinelaSuccata,
        "general_bug": GeneralBug,
        "rei_drakon":  ReiDrakon,
    }
    cls = mapa.get(tipo)
    if cls is None:
        raise ValueError(f"Inimigo desconhecido: {tipo!r}")
    return cls()