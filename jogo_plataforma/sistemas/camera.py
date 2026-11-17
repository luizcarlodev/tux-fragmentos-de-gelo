"""Câmera lateral com seguimento suave, limites e conversão de coordenadas."""
import math
import random

import pygame


class Camera:
    """Câmera que acompanha o jogador horizontalmente.

    ``x``/``y`` são a posição do canto superior esquerdo da tela no mundo.
    """

    def __init__(self, largura_tela, altura_tela, largura_mundo, altura_mundo):
        self.largura_tela = largura_tela
        self.altura_tela = altura_tela
        self.largura_mundo = largura_mundo
        self.altura_mundo = altura_mundo
        self.x = 0.0
        self.y = 0.0
        self.posicao_do_jogador = 0.40      # jogador fica a 40% da largura da tela
        self.suavizacao = 7.0
        self._tremor_tempo = 0.0
        self._tremor_forca = 0.0
        self.deslocamento_tremor = (0, 0)

    # ------------------------------------------------------------ limites
    def _limitar(self, x):
        return max(0.0, min(x, self.largura_mundo - self.largura_tela))

    def centralizar_em(self, alvo_x):
        """Posiciona a câmera imediatamente (sem suavização)."""
        self.x = self._limitar(alvo_x - self.largura_tela * self.posicao_do_jogador)
        self.y = max(0.0, min(0.0, self.altura_mundo - self.altura_tela))

    def seguir(self, retangulo_alvo, dt):
        """Aproxima suavemente a câmera do alvo (movimento independente do FPS)."""
        desejado = self._limitar(retangulo_alvo.centerx - self.largura_tela * self.posicao_do_jogador)
        fator = 1.0 - math.exp(-self.suavizacao * dt)
        self.x += (desejado - self.x) * fator
        self.x = self._limitar(self.x)
        if self._tremor_tempo > 0:
            self._tremor_tempo -= dt
            f = self._tremor_forca * max(0.0, self._tremor_tempo) / 0.3
            self.deslocamento_tremor = (random.uniform(-f, f), random.uniform(-f, f))
        else:
            self.deslocamento_tremor = (0, 0)

    def tremer(self, forca=6.0, duracao=0.3):
        self._tremor_forca = forca
        self._tremor_tempo = duracao

    # ------------------------------------------------------------ conversões
    @property
    def esquerda(self):
        return self.x

    @property
    def direita(self):
        return self.x + self.largura_tela

    @property
    def centro_x(self):
        return self.x + self.largura_tela / 2

    def mundo_para_tela(self, x, y):
        """Converte coordenadas do mundo para coordenadas da tela."""
        return x - self.x + self.deslocamento_tremor[0], y - self.y + self.deslocamento_tremor[1]

    def tela_para_mundo(self, x, y):
        return x + self.x, y + self.y

    def retangulo_para_tela(self, retangulo):
        px, py = self.mundo_para_tela(retangulo.x, retangulo.y)
        return pygame.Rect(round(px), round(py), retangulo.width, retangulo.height)

    def visivel(self, retangulo, margem=64):
        """``True`` se o retângulo (em coordenadas do mundo) aparece na tela."""
        return (retangulo.right >= self.x - margem and retangulo.left <= self.x + self.largura_tela + margem)
