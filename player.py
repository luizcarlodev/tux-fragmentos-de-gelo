import pygame
from entidade import Entidade


class Player(Entidade):

    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            50,
            50,
            3
        )

        self.pontuacao = 0
        self.velocidade = 4

        self.velocidade_y = 0
        self.gravidade = 0.8
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

    def pular(self, teclas):

        if teclas[pygame.K_SPACE] and not self.pulando:

            self.velocidade_y = -15
            self.pulando = True

        self.velocidade_y += self.gravidade

        self.y += self.velocidade_y

        #chao temporario
        if self.y >= 500:
            self.y = 500
            self.velocidade_y = 0
            self.pulando = False

        self.rect.y = self.y

    def desenhar(self, tela):
        super().desenhar(
            tela,
            (0, 150, 255)
        )