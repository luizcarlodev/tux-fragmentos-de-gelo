import config
import pygame
from entidade import Entidade

class Plataforma(Entidade):

    def __init__(self, x, y, largura, altura):
        super().__init__(x, y, largura, altura, vida=0)

    def desenhar(self, tela):
        super().desenhar(tela, (100, 100, 100))

def criar_plataformas_fase1():
    return [
        Plataforma(0, config.CHAO_Y, config.LARGURA_TELA, config.ALTURA_TELA - config.CHAO_Y),
        Plataforma(300, 400, 150, 20),
        Plataforma(550, 300, 150, 20),
    ]