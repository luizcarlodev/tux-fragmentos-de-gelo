import config
import pygame
from entidade import Entidade


class Player(Entidade):

    def __init__(self, x, y):
        super().__init__(x, y, config.PLAYER_LARGURA, config.PLAYER_ALTURA, config.PLAYER_VIDA_INICIAL)

        self.pontuacao = 0
        self.velocidade = config.PLAYER_VELOCIDADE

        self.velocidade_y = 0
        self.gravidade = config.PLAYER_GRAVIDADE
        self.pulando = False

    def mover_player(self, teclas):

        if teclas[pygame.K_a]:
            self.mover(
                -self.velocidade,
                0
            )

        if teclas[pygame.K_d]:
            self.mover(
                self.velocidade,
                0
            )

        # colisão(esquerda)
        if self.x < config.LIMITE_ESQUERDA:
            self.x = config.LIMITE_ESQUERDA

        # colisão(direita)
        if self.x > config.LIMITE_DIREITA:
            self.x = config.LIMITE_DIREITA

    def pular(self, teclas):

        if teclas[pygame.K_SPACE] and not self.pulando:

            self.velocidade_y = config.PLAYER_FORCA_PULO
            self.pulando = True

        self.velocidade_y += self.gravidade

        self.y += self.velocidade_y

        # chao temporario
        if self.y >= config.CHAO_Y:
            self.y = config.CHAO_Y
            self.velocidade_y = 0
            self.pulando = False
        
        self.rect.y = self.y

    def desenhar(self, tela):
        super().desenhar(tela, config.COR_TUX)