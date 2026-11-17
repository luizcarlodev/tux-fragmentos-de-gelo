"""Tela de créditos com texto rolando (fundo glacial com neve)."""
import pygame

from cenas.cena import Cena
from configuracoes import ALTURA_BASE, CORES, LARGURA_BASE
from interface.efeitos_de_tela import gradiente_vertical
from interface.textos import desenhar_texto
from sistemas.neve import SistemaDeNeve

LINHAS = [
    ("TUX", 76, "titulo"), ("A ERA DOS FRAGMENTOS DE GELO", 40, "destaque"), ("", 30, "texto"),
    ("HISTÓRIA E DESIGN", 38, "destaque"), ("Uma aventura original na Era Glacial", 28, "texto"), ("", 30, "texto"),
    ("PROGRAMAÇÃO", 38, "destaque"), ("Python + Pygame", 28, "texto"), ("", 30, "texto"),
    ("ARTE, MÚSICA E EFEITOS SONOROS", 38, "destaque"),
    ("Gerados por código (ferramentas/gerar_recursos.py)", 26, "texto"),
    ("Recursos provisórios, prontos para serem substituídos", 24, "texto_suave"), ("", 30, "texto"),
    ("PERSONAGENS", 38, "destaque"), ("Tux  ·  Princesa do Gelo", 28, "texto"),
    ("Criatura de Neve  ·  Pinguim Selvagem", 28, "texto"),
    ("Morcego Glacial  ·  Golem de Gelo", 28, "texto"), ("", 30, "texto"),
    ("INSPIRAÇÃO", 38, "destaque"), ("Os clássicos jogos de plataforma 2D", 28, "texto"), ("", 30, "texto"),
    ("OBRIGADO POR JOGAR!", 52, "titulo"),
]


class Creditos(Cena):
    """Rolagem automática; qualquer tecla acelera/volta."""

    def __init__(self, aplicacao):
        super().__init__(aplicacao)
        self.fundo = gradiente_vertical((16, 30, 88), (4, 6, 28))
        self.neve = SistemaDeNeve(aplicacao.recursos, {"densidade": 110, "vento": -30}, semente=9)
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
        self.neve.atualizar(dt)
        rapido = pygame.key.get_pressed()[pygame.K_DOWN]
        self.deslocamento += dt * (260 if rapido else 70)
        if self.deslocamento > self.altura_total + ALTURA_BASE:
            self.voltar()

    def desenhar(self, tela):
        tela.blit(self.fundo, (0, 0))
        self.neve.desenhar(tela)
        y = ALTURA_BASE - self.deslocamento
        for texto, tamanho, cor in LINHAS:
            if texto:
                desenhar_texto(tela, texto, tamanho, CORES[cor], (LARGURA_BASE // 2, int(y)))
            y += int(tamanho * 1.5)
        desenhar_texto(tela, "ESC para voltar", 24, CORES["texto_suave"], (LARGURA_BASE // 2, ALTURA_BASE - 24))
