"""Tela de créditos com texto rolando."""
import pygame

from cenas.cena import Cena
from configuracoes import ALTURA_BASE, CORES, LARGURA_BASE
from interface.efeitos_de_tela import gradiente_vertical
from interface.textos import desenhar_texto

LINHAS = [
    ("SUPER AVENTURA", 64, "destaque"), ("Base de jogo de plataforma 2D", 30, "texto_suave"), ("", 30, "texto"),
    ("PROGRAMAÇÃO", 40, "destaque"), ("Python + Pygame", 30, "texto"), ("", 30, "texto"),
    ("ARTE E SONS PROVISÓRIOS", 40, "destaque"),
    ("Gerados por código (ferramentas/gerar_recursos.py)", 28, "texto"),
    ("Substitua os PNGs e WAVs para criar a sua identidade visual", 26, "texto_suave"), ("", 30, "texto"),
    ("INSPIRAÇÃO", 40, "destaque"), ("Os clássicos jogos de plataforma 2D", 30, "texto"), ("", 30, "texto"),
    ("OBRIGADO POR JOGAR!", 52, "titulo"),
]


class Creditos(Cena):
    """Rolagem automática; qualquer tecla acelera/volta."""

    def __init__(self, aplicacao):
        super().__init__(aplicacao)
        self.fundo = gradiente_vertical((20, 24, 70), (4, 4, 20))
        self.deslocamento = 0.0
        self.altura_total = sum(int(t * 1.5) for _, t, _ in LINHAS) + 40

    def voltar(self):
        self.app.audio.tocar_efeito("selecao")
        self.app.cenas.desempilhar("fade")

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_RETURN):
            self.voltar()
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self.voltar()

    def atualizar(self, dt):
        rapido = pygame.key.get_pressed()[pygame.K_DOWN]
        self.deslocamento += dt * (260 if rapido else 70)
        if self.deslocamento > self.altura_total + ALTURA_BASE:
            self.voltar()

    def desenhar(self, tela):
        tela.blit(self.fundo, (0, 0))
        y = ALTURA_BASE - self.deslocamento
        for texto, tamanho, cor in LINHAS:
            if texto:
                desenhar_texto(tela, texto, tamanho, CORES[cor], (LARGURA_BASE // 2, int(y)))
            y += int(tamanho * 1.5)
        desenhar_texto(tela, "ESC para voltar", 24, CORES["texto_suave"], (LARGURA_BASE // 2, ALTURA_BASE - 24))
