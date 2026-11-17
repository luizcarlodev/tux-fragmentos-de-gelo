"""HUD: informações fixas na tela durante a partida (não acompanham a câmera).

Visual glacial: painel azul-noite com borda de gelo, corações congelados (vidas), cristais
(coletáveis) e os três Fragmentos de Gelo da campanha.
"""
import math

import pygame

from configuracoes import CORES, LARGURA_BASE, TOTAL_DE_FASES
from interface.textos import desenhar_texto

ALTURA_PAINEL = 72


def formatar_tempo(segundos):
    """Formata segundos como ``M:SS``."""
    segundos = max(0, int(segundos))
    return f"{segundos // 60}:{segundos % 60:02d}"


def _criar_painel():
    """Painel translúcido com degradê, brilho e uma borda inferior cintilante."""
    painel = pygame.Surface((LARGURA_BASE, ALTURA_PAINEL), pygame.SRCALPHA)
    for y in range(ALTURA_PAINEL):
        mistura = y / ALTURA_PAINEL
        cor = (int(10 + 14 * mistura), int(24 + 30 * mistura), int(64 + 36 * mistura), 205)
        pygame.draw.line(painel, cor, (0, y), (LARGURA_BASE, y))
    pygame.draw.line(painel, (150, 225, 255, 230), (0, ALTURA_PAINEL - 2), (LARGURA_BASE, ALTURA_PAINEL - 2), 2)
    pygame.draw.line(painel, (255, 255, 255, 90), (0, 1), (LARGURA_BASE, 1), 1)
    # pequenos "cristais" decorativos na borda inferior
    for x in range(8, LARGURA_BASE, 56):
        pygame.draw.polygon(painel, (190, 240, 255, 150), [(x, ALTURA_PAINEL - 2), (x + 5, ALTURA_PAINEL - 9),
                                                           (x + 10, ALTURA_PAINEL - 2)])
    return painel


class Hud:
    """Desenha pontuação, cristais, vidas, fragmentos, tempo e progresso da fase."""

    def __init__(self, recursos):
        self.icone_moeda = recursos.imagem("interface/icone_moeda.png", 2)
        self.icone_vida = recursos.imagem("interface/icone_vida.png", 2)
        self.icone_relogio = recursos.imagem("interface/icone_relogio.png", 2)
        self.icones_fragmento = [recursos.imagem(f"interface/icone_fragmento_{n}.png", 2)
                                 for n in range(1, TOTAL_DE_FASES + 1)]
        self.icone_fragmento_vazio = recursos.imagem("interface/icone_fragmento_vazio.png", 2)
        self.painel = _criar_painel()
        self.relogio = 0.0

    def atualizar(self, dt):
        self.relogio += dt

    def desenhar(self, tela, pontuacao, fase, melhor_pontuacao=0, fragmentos=()):
        tela.blit(self.painel, (0, 0))
        # pontuação
        desenhar_texto(tela, "PONTOS", 20, CORES["texto_suave"], (24, 6), "topo_esquerda")
        desenhar_texto(tela, f"{pontuacao.pontos:06d}", 38, CORES["texto"], (24, 26), "topo_esquerda")
        # cristais coletados
        tela.blit(self.icone_moeda, (222, 20))
        desenhar_texto(tela, f"x {pontuacao.moedas:02d}", 34, CORES["destaque"], (262, 36), "esquerda")
        # vidas (corações congelados)
        desenhar_texto(tela, "VIDAS", 20, CORES["texto_suave"], (356, 6), "topo_esquerda")
        if pontuacao.vidas <= 5:
            for i in range(pontuacao.vidas):
                flutuar = round(math.sin(self.relogio * 3 + i) * 1.5)
                tela.blit(self.icone_vida, (356 + i * 36, 30 + flutuar))
        else:
            tela.blit(self.icone_vida, (356, 30))
            desenhar_texto(tela, f"x {pontuacao.vidas}", 32, CORES["texto"], (396, 46), "esquerda")
        # fragmentos de gelo da campanha
        desenhar_texto(tela, "FRAGMENTOS", 20, CORES["texto_suave"], (560, 6), "topo_esquerda")
        for n in range(1, TOTAL_DE_FASES + 1):
            tem = n in fragmentos or (fase.altar is not None and fase.altar.numero == n and fase.altar.coletado)
            icone = self.icones_fragmento[n - 1] if tem else self.icone_fragmento_vazio
            tela.blit(icone, (560 + (n - 1) * 36, 30))
        # progresso
        self._desenhar_progresso(tela, fase)
        # tempo
        baixo = pontuacao.tempo_restante <= 60
        cor = CORES["erro"] if baixo and int(self.relogio * 3) % 2 == 0 else CORES["texto"]
        tela.blit(self.icone_relogio, (1100, 20))
        desenhar_texto(tela, formatar_tempo(pontuacao.tempo_restante), 38, cor, (1142, 36), "esquerda")
        # poder do Cristal Mágico (invencibilidade)
        if fase.jogador.com_cristal:
            desenhar_texto(tela, f"CRISTAL MÁGICO {fase.jogador.tempo_cristal:0.0f}s", 28, CORES["destaque"],
                           (LARGURA_BASE // 2, 90), "topo_centro", contorno=True)

    def _desenhar_progresso(self, tela, fase):
        x, y, largura = 740, 38, 320
        desenhar_texto(tela, "PROGRESSO", 20, CORES["texto_suave"], (x, 6), "topo_esquerda")
        pygame.draw.rect(tela, (12, 22, 58), (x, y, largura, 16), border_radius=8)
        preenchido = int(largura * fase.progresso)
        if preenchido > 0:
            pygame.draw.rect(tela, CORES["destaque"], (x, y, max(10, preenchido), 16), border_radius=8)
        pygame.draw.rect(tela, CORES["branco"], (x, y, largura, 16), width=2, border_radius=8)
        for ponto in fase.checkpoints:                       # marcadores dos totens (checkpoints)
            mx = x + int(largura * ponto.centro_x / fase.mapa.largura_pixels)
            cor = CORES["sucesso"] if ponto.ativado else CORES["texto_suave"]
            pygame.draw.rect(tela, cor, (mx - 2, y - 5, 4, 26))
