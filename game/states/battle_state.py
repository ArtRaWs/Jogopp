# ============================================================
#  ELDORIA GAME - ESTADO: BATALHA
# ============================================================

import pygame
import math
import random
import os
from utils.game_state_manager import BaseState
from utils.constants    import *
from utils.ui           import (draw_text, draw_panel, draw_bar,
                                Button, CombatLog, DamagePopup, StarField)
from classes.vilao      import criar_inimigo
from data.perguntas     import get_perguntas


# ── Fases da batalha ─────────────────────────────────────────
FASE_PLAYER_TURNO  = "player"
FASE_QUIZ          = "quiz"
FASE_INIMIGO_TURNO = "inimigo"
FASE_ANIMACAO      = "animacao"
FASE_VITORIA       = "vitoria"
FASE_DERROTA       = "derrota"
FASE_APRESENTACAO  = "apresentacao"


class BattleState(BaseState):

    def _asset_path(self, filename: str) -> str:
        game_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(game_dir, "assets", filename)

    def enter(self, data: dict = None):
        data = data or {}
        self._t         = 0.0
        self._stars     = StarField(60)
        self._fase      = FASE_APRESENTACAO
        self._fase_t    = 0.0
        self._popups: list[DamagePopup] = []
        self._shake     = 0.0
        self._shake_x   = 0
        self._shake_y   = 0

        # ── Personagens ──────────────────────────────────────
        self._heroi   = self.manager.heroi
        self._inimigo = criar_inimigo(data.get("inimigo", ENEMY_SENTINELA))

        # ── Artes (fundo e sprites) ───────────────────────────
        self._bg_img = None
        self._hero_img = None
        self._enemy_img = None

        try:
            p = self._asset_path("fundo1.png")
            self._bg_img = pygame.image.load(p).convert()
            self._bg_img = pygame.transform.smoothscale(self._bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception:
            self._bg_img = None

        # Herói
        try:
            tipo_heroi = getattr(self._heroi, "tipo", "")
            if tipo_heroi == "arthur":
                self._hero_img = pygame.image.load(self._asset_path("artraws.png")).convert_alpha()
            elif tipo_heroi == "luna":
                self._hero_img = pygame.image.load(self._asset_path("luna.png")).convert_alpha()
        except Exception:
            self._hero_img = None

        # Inimigo
        try:
            inimigo_nome = type(self._inimigo).__name__
            if inimigo_nome == "SentinelaSuccata":
                self._enemy_img = pygame.image.load(self._asset_path("sentinela.png")).convert_alpha()
            elif inimigo_nome == "ReiDrakon":
                self._enemy_img = pygame.image.load(self._asset_path("drakon.png")).convert_alpha()
        except Exception:
            self._enemy_img = None

        # ── Log de combate ───────────────────────────────────
        log_rect    = pygame.Rect(30, SCREEN_HEIGHT - 185, SCREEN_WIDTH - 60, 115)
        self._log   = CombatLog(log_rect)
        self._log.add(f"Batalha iniciada: {self._heroi.nome} vs {self._inimigo.nome}!", GOLD)

           # ── Quiz ─────────────────────────────────────────────
        self._perguntas    = get_perguntas(self._inimigo.topico_python)
        self._pergunta     = None
        self._resp_btns    = []
        self._quiz_result  = None
        self._quiz_t       = 0.0
        self._pergunta_idx = 0

        # ── Botões de ação ───────────────────────────────────
        bw, bh = 220, 52
        bx      = SCREEN_WIDTH // 2 - bw // 2
        self._btns = {
            "ataque": Button(pygame.Rect(bx - bw - 10, SCREEN_HEIGHT - 295, bw, bh),
                             "⚔  Ataque Básico", color=(100, 30, 30), hover_color=RED),
            "pocao":  Button(pygame.Rect(bx,           SCREEN_HEIGHT - 295, bw, bh),
                             "⊕  Usar Poção",    color=(30, 100, 40), hover_color=GREEN),
            "habil":  Button(pygame.Rect(bx + bw + 10, SCREEN_HEIGHT - 295, bw, bh),
                             "✦  Habilidade Especial", color=(60, 20, 120), hover_color=PURPLE),
        }
        self._atualizar_btns()

        # ── Animação de apresentação do inimigo ───────────────
        self._apres_t = 0.0
        self._log.add(self._inimigo.frase_apresentacao, RED)

    # ── Helpers ──────────────────────────────────────────────

    def _atualizar_btns(self):
        h = self._heroi
        self._btns["pocao"].enabled  = h.pocoes > 0
        self._btns["habil"].enabled  = bool(self._perguntas)
        self._btns["ataque"].enabled = True

    def _add_popup(self, text: str, x: int, y: int, color=RED):
        self._popups.append(DamagePopup(text, x, y, color))

    def _shake_screen(self, intensity: float = 8.0):
        self._shake = intensity

    def _proxima_pergunta(self):
        if not self._perguntas:
            return None
        q = self._perguntas[self._pergunta_idx % len(self._perguntas)]
        self._pergunta_idx += 1
        return q

    def _criar_botoes_quiz(self, pergunta: dict):
        self._resp_btns = []
        bw, bh = SCREEN_WIDTH - 160, 44
        bx     = 80
        by0    = 360
        for i, opcao in enumerate(pergunta["opcoes"]):
            btn = Button(
                pygame.Rect(bx, by0 + i * (bh + 10), bw, bh),
                opcao, color=(40, 35, 80), hover_color=(80, 60, 140),
                font_size=FONT_SMALL
            )
            self._resp_btns.append(btn)

    # ── Ações do jogador ─────────────────────────────────────

    def _acao_ataque(self):
        dano = self._heroi.atacar(self._inimigo)
        self._log.add(f"{self._heroi.nome} atacou! Dano: {dano}", ORANGE)
        self._add_popup(f"-{dano}", 620, 280)
        self._shake_screen(5)
        self._heroi.processar_turno()
        self._iniciar_turno_inimigo()

    def _acao_pocao(self):
        ok, cura = self._heroi.usar_pocao()
        if ok:
            self._log.add(f"{self._heroi.nome} usou uma Poção! +{cura} HP", GREEN)
            self._add_popup(f"+{cura} HP", 200, 280, GREEN)
        else:
            self._log.add("Sem poções!", RED)
        self._heroi.processar_turno()
        self._iniciar_turno_inimigo()

    def _acao_habilidade(self):
        self._pergunta = self._proxima_pergunta()
        if not self._pergunta:
            self._log.add("Nenhuma habilidade disponível!", GRAY)
            return
        self._criar_botoes_quiz(self._pergunta)
        self._quiz_result = None
        self._quiz_t      = 0.0
        self._fase        = FASE_QUIZ

    def _processar_resposta(self, idx: int):
        correto = (idx == self._pergunta["correta"])
        if correto:
            # Habilidade especial com acerto
            dano_base  = self._heroi.ataque_total * 2 + 15
            dano_total = self._inimigo.receber_dano_fixo(dano_base)
            self._log.add(f"✓ Correto! {self._heroi.nome} usou golpe especial! Dano: {dano_total}", ACCENT)
            self._add_popup(f"CRÍTICO! -{dano_total}", 600, 260, GOLD)
            self._shake_screen(10)
            self._quiz_result = "certo"
        else:
            # Falha — recebe contra-ataque
            self._log.add(f"✗ Errado! Habilidade falhou! {self._pergunta['explicacao']}", RED)
            contra  = int(self._inimigo.ataque * 0.8)
            recebido = self._heroi.receber_dano_fixo(contra)
            self._log.add(f"{self._inimigo.nome} aproveitou a abertura! Dano: {recebido}", RED)
            self._add_popup(f"-{recebido}", 180, 260, RED)
            self._quiz_result = "errado"

        self._quiz_t = 0.0
        self._heroi.processar_turno()

    def _iniciar_turno_inimigo(self):
        self._fase   = FASE_INIMIGO_TURNO
        self._fase_t = 0.0

    def _executar_turno_inimigo(self):
        if not self._inimigo.esta_vivo():
            return
        frase, dano = self._inimigo.executar_acao(self._heroi)
        self._log.add(f"{self._inimigo.nome} {frase} Dano: {dano}", (255, 140, 140))
        self._add_popup(f"-{dano}", 200, 300, RED)
        self._shake_screen(6)

        if not self._heroi.esta_vivo():
            self._fase   = FASE_DERROTA
            self._fase_t = 0.0
        elif not self._inimigo.esta_vivo():
            self._fase   = FASE_VITORIA
            self._fase_t = 0.0
        else:
            self._fase = FASE_PLAYER_TURNO
            self._atualizar_btns()

    # ── Verificações de fim de combate ────────────────────────

    def _checar_vitoria(self):
        if not self._inimigo.esta_vivo():
            self._fase   = FASE_VITORIA
            self._fase_t = 0.0

    def _checar_derrota(self):
        if not self._heroi.esta_vivo():
            self._fase   = FASE_DERROTA
            self._fase_t = 0.0

    # ── Handle events ────────────────────────────────────────

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()

        if self._fase == FASE_PLAYER_TURNO:
            for k, btn in self._btns.items():
                btn.update((mx, my))
            for e in events:
                if self._btns["ataque"].is_clicked(e):
                    self._acao_ataque()
                    self._checar_vitoria()
                elif self._btns["pocao"].is_clicked(e):
                    self._acao_pocao()
                elif self._btns["habil"].is_clicked(e):
                    self._acao_habilidade()

        elif self._fase == FASE_QUIZ:
            if self._quiz_result is None:
                for i, btn in enumerate(self._resp_btns):
                    btn.update((mx, my))
                for e in events:
                    for i, btn in enumerate(self._resp_btns):
                        if btn.is_clicked(e):
                            self._processar_resposta(i)

            else:
                # Aguarda 2s após resultado
                for e in events:
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                        self._fechar_quiz()
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        self._fechar_quiz()

        elif self._fase == FASE_VITORIA and self._fase_t > 2.0:
            for e in events:
                if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    self._ir_para_levelup()

        elif self._fase == FASE_DERROTA and self._fase_t > 2.0:
            for e in events:
                if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    self._ir_para_game_over()

        elif self._fase == FASE_APRESENTACAO and self._fase_t > 3.0:
            for e in events:
                if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    self._fase = FASE_PLAYER_TURNO

    def _fechar_quiz(self):
        self._checar_vitoria()
        self._checar_derrota()
        if self._fase not in (FASE_VITORIA, FASE_DERROTA):
            self._iniciar_turno_inimigo()

    def _ir_para_levelup(self):
        gained_xp = self._inimigo.xp_recompensa
        self._heroi.ganhar_xp(gained_xp)
        self.manager.heroi            = self._heroi
        self.manager.ultima_batalha   = self.manager.inimigo_atual
        self.manager.progresso       += 1
        self.go_to("levelup", {
            "xp_ganho":    gained_xp,
            "ouro_ganho":  self._inimigo.ouro_recompensa,
            "inimigo_nome": self._inimigo.nome,
        })

    def _ir_para_game_over(self):
        self.go_to(STATE_GAME_OVER, {
            "dica":     self._inimigo.dica_python,
            "inimigo":  self._inimigo.nome,
        })

    # ── Update ───────────────────────────────────────────────

    def update(self, dt: float):
        self._t      += dt
        self._fase_t += dt
        self._stars.update(dt)

        # Shake
        if self._shake > 0:
            self._shake  -= dt * 30
            self._shake_x = random.randint(-int(self._shake), int(self._shake) + 1)
            self._shake_y = random.randint(-int(self._shake), int(self._shake) + 1)
        else:
            self._shake   = 0
            self._shake_x = 0
            self._shake_y = 0

        # Popups
        for p in self._popups:
            p.update(dt)
        self._popups = [p for p in self._popups if p.alive]

        # Turno inimigo automático após delay
        if self._fase == FASE_INIMIGO_TURNO and self._fase_t > 1.2:
            self._executar_turno_inimigo()

        # Apresentação → player turno
        if self._fase == FASE_APRESENTACAO and self._fase_t > 3.5:
            self._fase = FASE_PLAYER_TURNO

    # ── Draw ─────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        if self._bg_img:
            surface.blit(self._bg_img, (0, 0))
        else:
            surface.fill(DARK_BG)
            self._stars.draw(surface)

        ox, oy = self._shake_x, self._shake_y

        # ── HUD Herói (esquerda) ──────────────────────────────
        self._draw_hud_heroi(surface, ox, oy)

        # ── HUD Inimigo (direita) ─────────────────────────────
        self._draw_hud_inimigo(surface, ox, oy)

        # ── Sprites ───────────────────────────────────────────
        self._draw_heroi_sprite(surface, 160 + ox, 310 + oy)
        self._draw_inimigo_sprite(surface, 680 + ox, 300 + oy)

        # ── Log ───────────────────────────────────────────────
        self._log.draw(surface)

        # ── Botões de ação ────────────────────────────────────
        if self._fase == FASE_PLAYER_TURNO:
            self._draw_action_buttons(surface)

        # ── Quiz ──────────────────────────────────────────────
        elif self._fase == FASE_QUIZ:
            self._draw_quiz(surface)

        # ── Aguardando turno inimigo ──────────────────────────
        elif self._fase == FASE_INIMIGO_TURNO:
            draw_text(surface, f"Turno de {self._inimigo.nome}...",
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT - 260,
                      size=FONT_MEDIUM, color=RED, center=True)

        # ── Apresentação ──────────────────────────────────────
        elif self._fase == FASE_APRESENTACAO:
            self._draw_apresentacao(surface)

        # ── Vitória ───────────────────────────────────────────
        elif self._fase == FASE_VITORIA:
            self._draw_overlay_vitoria(surface)

        # ── Derrota ───────────────────────────────────────────
        elif self._fase == FASE_DERROTA:
            self._draw_overlay_derrota(surface)

        # ── Popups de dano ────────────────────────────────────
        for p in self._popups:
            p.draw(surface)

    def _draw_hud_heroi(self, surface, ox, oy):
        h     = self._heroi
        rect  = pygame.Rect(20 + ox, 20 + oy, 320, 130)
        draw_panel(surface, rect, border_color=h.cor)
        draw_text(surface, h.nome, rect.x + 10, rect.y + 8,
                  size=FONT_MEDIUM, color=h.cor, bold=True)
        draw_text(surface, f"Nível {h.nivel}", rect.x + 230, rect.y + 8,
                  size=FONT_TINY, color=GOLD)
        draw_bar(surface, rect.x + 10, rect.y + 38, 295, 20,
                 h.hp, h.hp_max, "HP", fg_color=HP_GREEN)
        draw_bar(surface, rect.x + 10, rect.y + 66, 295, 20,
                 h.mp, h.mp_max, "MP", fg_color=MP_BLUE)
        draw_text(surface, f"Poções: {h.pocoes}  Ouro: {h.ouro}",
                  rect.x + 10, rect.y + 95,
                  size=FONT_TINY, color=GOLD)

    def _draw_hud_inimigo(self, surface, ox, oy):
        e    = self._inimigo
        rect = pygame.Rect(SCREEN_WIDTH - 340 + ox, 20 + oy, 320, 100)
        draw_panel(surface, rect, border_color=e.cor)
        draw_text(surface, e.nome, rect.x + 10, rect.y + 8,
                  size=FONT_MEDIUM, color=e.cor, bold=True)
        draw_bar(surface, rect.x + 10, rect.y + 38, 295, 22,
                 e.hp, e.hp_max, "HP", fg_color=HP_RED)
        if e.enraivecido:
            draw_text(surface, "⚡ ENRAIVECIDO!", rect.x + 10, rect.y + 68,
                      size=FONT_TINY, color=RED)

    def _draw_heroi_sprite(self, surface, cx, cy):
        # Se tiver sprite PNG, usa ele.
        if self._hero_img:
            bob = int(math.sin(self._t * 2) * 4)
            cy += bob
            img = self._hero_img
            target_h = 300
            scale = target_h / img.get_height()
            nw = max(1, int(img.get_width() * scale))
            nh = max(1, int(img.get_height() * scale))
            spr = pygame.transform.smoothscale(img, (nw, nh))
            r = spr.get_rect(midbottom=(cx, cy + 120))
            surface.blit(spr, r)
            return

        h   = self._heroi
        bob = int(math.sin(self._t * 2) * 4)
        cy += bob
        col = h.cor
        dark = tuple(max(0, c - 60) for c in col)

        if h.tipo == "arthur":
            pygame.draw.rect(surface, col,  pygame.Rect(cx - 22, cy - 35, 44, 55))
            pygame.draw.rect(surface, dark, pygame.Rect(cx - 22, cy - 35, 44, 55), 2)
            pygame.draw.circle(surface, col, (cx, cy - 52), 24)
            pygame.draw.circle(surface, dark, (cx, cy - 52), 24, 2)
            pygame.draw.polygon(surface, GOLD, [(cx-26, cy-58), (cx, cy-88), (cx+26, cy-58)])
            pygame.draw.rect(surface, GOLD, pygame.Rect(cx + 26, cy - 60, 7, 72))
            pygame.draw.rect(surface, WHITE, pygame.Rect(cx + 19, cy - 28, 20, 7))
            pygame.draw.rect(surface, dark, pygame.Rect(cx - 20, cy + 20, 17, 28))
            pygame.draw.rect(surface, dark, pygame.Rect(cx + 3,  cy + 20, 17, 28))
        else:
            pygame.draw.polygon(surface, col, [(cx-28, cy+50), (cx, cy-32), (cx+28, cy+50)])
            pygame.draw.rect(surface, dark, pygame.Rect(cx - 14, cy - 32, 28, 44))
            pygame.draw.circle(surface, col, (cx, cy - 50), 22)
            pygame.draw.circle(surface, dark, (cx, cy - 50), 22, 2)
            pygame.draw.arc(surface, PURPLE, pygame.Rect(cx-26, cy-74, 52, 34), 0, math.pi, 4)
            pygame.draw.line(surface, GOLD, (cx - 30, cy + 46), (cx - 28, cy - 64), 5)
            a   = self._t * 2
            orb_col = (int(abs(math.sin(a))*200+55), int(abs(math.cos(a))*150+55), 255)
            pygame.draw.circle(surface, orb_col, (cx - 28, cy - 68), 10)
            pygame.draw.circle(surface, WHITE, (cx - 28, cy - 68), 10, 1)

    def _draw_inimigo_sprite(self, surface, cx, cy):
        # Se tiver sprite PNG, usa ele.
        if self._enemy_img:
            bob = int(math.sin(self._t * 1.8) * 5)
            cy += bob
            img = self._enemy_img
            target_h = 280
            scale = target_h / img.get_height()
            nw = max(1, int(img.get_width() * scale))
            nh = max(1, int(img.get_height() * scale))
            spr = pygame.transform.smoothscale(img, (nw, nh))
            r = spr.get_rect(midbottom=(cx, cy + 130))
            surface.blit(spr, r)
            return

        e   = self._inimigo
        t   = self._t
        bob = int(math.sin(t * 1.8) * 5)
        cy += bob
        col = e.cor
        dark = tuple(max(0, c - 50) for c in col)

        nome = type(e).__name__

        if nome == "SentinelaSuccata":
            # Robô de sucata
            pygame.draw.rect(surface, col, pygame.Rect(cx - 30, cy - 50, 60, 70))
            pygame.draw.rect(surface, dark, pygame.Rect(cx - 30, cy - 50, 60, 70), 3)
            pygame.draw.rect(surface, GRAY_DARK, pygame.Rect(cx - 22, cy - 44, 44, 30))
            pygame.draw.circle(surface, RED, (cx - 10, cy - 34), 6)
            pygame.draw.circle(surface, RED, (cx + 10, cy - 34), 6)
            pygame.draw.rect(surface, GRAY, pygame.Rect(cx - 16, cy - 20, 32, 6))
            pygame.draw.rect(surface, dark, pygame.Rect(cx - 38, cy - 45, 12, 55))
            pygame.draw.rect(surface, dark, pygame.Rect(cx + 26, cy - 45, 12, 55))
            pygame.draw.rect(surface, dark, pygame.Rect(cx - 18, cy + 20, 14, 30))
            pygame.draw.rect(surface, dark, pygame.Rect(cx + 4,  cy + 20, 14, 30))
            # Parafusos
            for px, py in [(cx-26, cy-46), (cx+18, cy-46), (cx-26, cy+14), (cx+18, cy+14)]:
                pygame.draw.circle(surface, GOLD, (px, py), 4)

        elif nome == "GeneralBug":
            # General militarista
            pygame.draw.rect(surface, col, pygame.Rect(cx - 26, cy - 40, 52, 65))
            pygame.draw.rect(surface, dark, pygame.Rect(cx - 26, cy - 40, 52, 65), 2)
            pygame.draw.circle(surface, col, (cx, cy - 55), 22)
            pygame.draw.circle(surface, dark, (cx, cy - 55), 22, 2)
            pygame.draw.polygon(surface, RED, [(cx - 28, cy - 68), (cx, cy - 95), (cx + 28, cy - 68)])
            # Insígnias
            pygame.draw.circle(surface, GOLD, (cx - 16, cy - 32), 5)
            pygame.draw.circle(surface, GOLD, (cx,      cy - 32), 5)
            pygame.draw.circle(surface, GOLD, (cx + 16, cy - 32), 5)
            # Espada larga
            pygame.draw.rect(surface, (180, 180, 200), pygame.Rect(cx + 28, cy - 60, 10, 80))
            pygame.draw.rect(surface, GOLD, pygame.Rect(cx + 22, cy - 22, 22, 8))
            pygame.draw.rect(surface, dark, pygame.Rect(cx - 22, cy + 25, 18, 30))
            pygame.draw.rect(surface, dark, pygame.Rect(cx + 4,  cy + 25, 18, 30))

        else:  # ReiDrakon
            # Rei draconico épico
            pulse = int(abs(math.sin(t * 2)) * 40)
            body_col = (col[0], max(0, col[1] - 20), min(255, col[2] + pulse))
            pygame.draw.polygon(surface, body_col, [
                (cx - 40, cy + 80), (cx - 20, cy - 40),
                (cx, cy - 60), (cx + 20, cy - 40), (cx + 40, cy + 80)
            ])
            pygame.draw.circle(surface, body_col, (cx, cy - 68), 28)
            pygame.draw.circle(surface, dark, (cx, cy - 68), 28, 2)
            # Coroa
            pygame.draw.polygon(surface, GOLD, [
                (cx - 30, cy - 90), (cx - 20, cy - 112), (cx - 8, cy - 94),
                (cx, cy - 118), (cx + 8, cy - 94), (cx + 20, cy - 112), (cx + 30, cy - 90)
            ])
            # Olhos brilhantes
            pygame.draw.circle(surface, (255, 50, 50), (cx - 12, cy - 72), 7)
            pygame.draw.circle(surface, (255, 50, 50), (cx + 12, cy - 72), 7)
            pygame.draw.circle(surface, WHITE, (cx - 12, cy - 72), 3)
            pygame.draw.circle(surface, WHITE, (cx + 12, cy - 72), 3)
            # Asas
            pygame.draw.polygon(surface, dark, [
                (cx - 20, cy - 30), (cx - 80, cy - 60), (cx - 70, cy + 10)
            ])
            pygame.draw.polygon(surface, dark, [
                (cx + 20, cy - 30), (cx + 80, cy - 60), (cx + 70, cy + 10)
            ])
            # Aura caótica
            for i in range(5):
                a  = t * 3 + i * (math.pi * 2 / 5)
                ax = int(cx + math.cos(a) * 50)
                ay = int(cy - 20 + math.sin(a) * 35)
                r  = 3 + int(abs(math.sin(t * 2 + i)) * 3)
                pygame.draw.circle(surface, (200, 0, 255), (ax, ay), r)

    def _draw_action_buttons(self, surface):
        rect = pygame.Rect(0, SCREEN_HEIGHT - 320, SCREEN_WIDTH, 120)
        draw_panel(surface, rect, alpha=160)
        draw_text(surface, "— SEU TURNO —",
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT - 310,
                  size=FONT_SMALL, color=GOLD, center=True)
        for btn in self._btns.values():
            btn.draw(surface)

    def _draw_quiz(self, surface):
        # Overlay
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        surface.blit(ov, (0, 0))

        # Painel principal
        panel = pygame.Rect(60, 60, SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120)
        draw_panel(surface, panel, bg_color=(20, 12, 50), border_color=PURPLE,
                   border_width=3, alpha=250)

        draw_text(surface, "✦ HABILIDADE ESPECIAL — PAINEL PYTHON ✦",
                  SCREEN_WIDTH // 2, 80,
                  size=FONT_MEDIUM, color=PURPLE, bold=True, center=True)

        topico = self._inimigo.topico_python.replace("_", " ").title()
        draw_text(surface, f"Tema: {topico}",
                  SCREEN_WIDTH // 2, 112,
                  size=FONT_SMALL, color=GOLD, center=True)

        pygame.draw.line(surface, PURPLE, (80, 135), (SCREEN_WIDTH - 80, 135), 1)

        if self._quiz_result is None:
            # Pergunta
            pergunta = self._pergunta["pergunta"]
            y = 150
            for line in pergunta.split('\n'):
                draw_text(surface, line,
                          SCREEN_WIDTH // 2, y,
                          size=FONT_MEDIUM, color=WHITE, center=True)
                y += FONT_MEDIUM + 6

            # Opções
            for btn in self._resp_btns:
                btn.draw(surface)

        else:
            # Resultado
            if self._quiz_result == "certo":
                draw_text(surface, "✓ RESPOSTA CORRETA!",
                          SCREEN_WIDTH // 2, 220,
                          size=FONT_TITLE, color=ACCENT, bold=True, center=True)
                draw_text(surface, "Golpe Especial executado com sucesso!",
                          SCREEN_WIDTH // 2, 280,
                          size=FONT_MEDIUM, color=GREEN, center=True)
            else:
                draw_text(surface, "✗ RESPOSTA INCORRETA!",
                          SCREEN_WIDTH // 2, 220,
                          size=FONT_TITLE, color=RED, bold=True, center=True)
                draw_text(surface, "A habilidade falhou! Você levou contra-ataque!",
                          SCREEN_WIDTH // 2, 275,
                          size=FONT_MEDIUM, color=ORANGE, center=True)

            expl = self._pergunta.get("explicacao", "")
            draw_text(surface, f"💡 {expl}",
                      SCREEN_WIDTH // 2, 335,
                      size=FONT_SMALL, color=CYAN, center=True)

            draw_text(surface, "[ Clique ou ENTER para continuar ]",
                      SCREEN_WIDTH // 2, 420,
                      size=FONT_SMALL, color=GRAY, center=True)

    def _draw_apresentacao(self, surface):
        if self._fase_t < 3.5:
            alpha = min(255, int(self._fase_t * 100))
            ov    = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(ov, (0, 0, 0, max(0, 180 - alpha * 2)),
                             ov.get_rect())
            surface.blit(ov, (0, 0))

            draw_text(surface, "NOVO INIMIGO!",
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40,
                      size=FONT_TITLE, color=RED, bold=True, center=True)
            draw_text(surface, self._inimigo.nome,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10,
                      size=FONT_LARGE, color=self._inimigo.cor,
                      bold=True, center=True)
            draw_text(surface, "[ Clique para iniciar ]",
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60,
                      size=FONT_SMALL, color=GRAY, center=True)

    def _draw_overlay_vitoria(self, surface):
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140))
        surface.blit(ov, (0, 0))

        draw_text(surface, "⚔ VITÓRIA! ⚔",
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                  size=FONT_HUGE, color=GOLD, bold=True, center=True)
        draw_text(surface, f"{self._inimigo.nome} foi derrotado!",
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20,
                  size=FONT_LARGE, color=ACCENT, center=True)
        if self._fase_t > 2.0:
            draw_text(surface, "[ Clique para continuar ]",
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70,
                      size=FONT_SMALL, color=GRAY, center=True)

    def _draw_overlay_derrota(self, surface):
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((80, 0, 0, 160))
        surface.blit(ov, (0, 0))

        draw_text(surface, "DERROTA...",
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                  size=FONT_HUGE, color=RED, bold=True, center=True)
        draw_text(surface, "Você caiu em batalha.",
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20,
                  size=FONT_LARGE, color=ORANGE, center=True)
        if self._fase_t > 2.0:
            draw_text(surface, "[ Clique para continuar ]",
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70,
                      size=FONT_SMALL, color=GRAY, center=True)