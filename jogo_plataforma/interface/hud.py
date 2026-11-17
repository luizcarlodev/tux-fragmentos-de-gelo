"""HUD: informações fixas na tela durante a partida (não acompanham a câmera)."""
import pygame

from configuracoes import CORES, LARGURA_BASE
from interface.textos import desenhar_texto


def formatar_tempo(segundos):
    """Formata segundos como ``M:SS``."""
    segundos = max(0, int(segundos))
    return f"{segundos // 60}:{segundos % 60:02d}"


class Hud:
    """Desenha pontuação, moedas, vidas, tempo e progresso da fase."""

    def __init__(self, recursos):
        self.icone_moeda = recursos.imagem("interface/icone_moeda.png", 2)
        self.icone_vida = recursos.imagem("interface/icone_vida.png", 2)
        self.icone_relogio = recursos.imagem("interface/icone_relogio.png", 2)
        self.painel = pygame.Surface((LARGURA_BASE, 72), pygame.SRCALPHA)
        self.painel.fill((8, 12, 36, 170))
        pygame.draw.line(self.painel, (255, 255, 255, 90), (0, 71), (LARGURA_BASE, 71), 2)
        self.relogio = 0.0

    def atualizar(self, dt):
        self.relogio += dt

    def desenhar(self, tela, pontuacao, fase, melhor_pontuacao=0):
        tela.blit(self.painel, (0, 0))
        # pontuação
        desenhar_texto(tela, "PONTOS", 20, CORES["texto_suave"], (24, 6), "topo_esquerda")
        desenhar_texto(tela, f"{pontuacao.pontos:06d}", 38, CORES["texto"], (24, 26), "topo_esquerda")
        # moedas
        tela.blit(self.icone_moeda, (230, 20))
        desenhar_texto(tela, f"x {pontuacao.moedas:02d}", 34, CORES["destaque"], (270, 36), "esquerda")
        # vidas
        desenhar_texto(tela, "VIDAS", 20, CORES["texto_suave"], (380, 6), "topo_esquerda")
        if pontuacao.vidas <= 5:
            for i in range(pontuacao.vidas):
                tela.blit(self.icone_vida, (380 + i * 36, 30))
        else:
            tela.blit(self.icone_vida, (380, 30))
            desenhar_texto(tela, f"x {pontuacao.vidas}", 32, CORES["texto"], (420, 46), "esquerda")
        # progresso
        self._desenhar_progresso(tela, fase)
        # tempo
        baixo = pontuacao.tempo_restante <= 60
        cor = CORES["erro"] if baixo and int(self.relogio * 3) % 2 == 0 else CORES["texto"]
        tela.blit(self.icone_relogio, (1086, 20))
        desenhar_texto(tela, formatar_tempo(pontuacao.tempo_restante), 38, cor, (1130, 36), "esquerda")
        # estrela
        if fase.jogador.com_estrela:
            desenhar_texto(tela, f"ESTRELA {fase.jogador.tempo_estrela:0.0f}s", 28, CORES["destaque"],
                           (LARGURA_BASE // 2, 90), "topo_centro", contorno=True)

    def _desenhar_progresso(self, tela, fase):
        x, y, largura = 600, 38, 420
        desenhar_texto(tela, "PROGRESSO", 20, CORES["texto_suave"], (x, 6), "topo_esquerda")
        pygame.draw.rect(tela, (20, 24, 60), (x, y, largura, 16), border_radius=8)
        preenchido = int(largura * fase.progresso)
        if preenchido > 0:
            pygame.draw.rect(tela, CORES["destaque"], (x, y, max(10, preenchido), 16), border_radius=8)
        pygame.draw.rect(tela, CORES["branco"], (x, y, largura, 16), width=2, border_radius=8)
        for ponto in fase.checkpoints:                       # marcadores dos checkpoints
            mx = x + int(largura * ponto.centro_x / fase.mapa.largura_pixels)
            cor = CORES["sucesso"] if ponto.ativado else CORES["texto_suave"]
            pygame.draw.rect(tela, cor, (mx - 2, y - 5, 4, 26))
