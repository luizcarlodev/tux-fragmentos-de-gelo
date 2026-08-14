import config
import pygame
from entidade import Entidade
from enemy import ChefeCriaturaCongelada, ChefeMacaco

class Plataforma(Entidade):

    def __init__(self, x, y, largura, altura, cor=None):
        super().__init__(x, y, largura, altura, vida=0)
        self.cor = cor if cor else config.COR_PLATAFORMA

    def desenhar(self, tela, camera_x=0):
        super().desenhar(tela, self.cor, camera_x)

def criar_plataformas_fase1():
    return [
        Plataforma(0, config.CHAO_Y, config.LARGURA_MUNDO, config.ALTURA_TELA - config.CHAO_Y, cor=config.COR_CHAO),
        Plataforma(300, 360, 150, 20),
        Plataforma(550, 260, 150, 20),
        Plataforma(850, 380, 150, 20),
        Plataforma(1150, 300, 150, 20),
        Plataforma(1450, 360, 150, 20),
        Plataforma(1750, 260, 150, 20),
        Plataforma(2050, 380, 150, 20),
    ]

def criar_chefe1():
    return ChefeCriaturaCongelada(600, config.CHAO_Y - 80, config.CHEFE1_ARENA_INICIO, config.CHEFE1_ARENA_FIM)

def criar_chefe2():
    return ChefeMacaco(
        1400,
        config.CHAO_Y - 80,
        config.CHEFE2_ARENA_INICIO,
        config.CHEFE2_ARENA_FIM
    )