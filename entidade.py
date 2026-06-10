import pygame


class Entidade:
    def __init__(self, x, y, largura, altura, vida):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.vida = vida
        self.velocidade = 5

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.largura,
            self.altura
        )

    def mover(self, dx, dy):
        self.x += dx
        self.y += dy

        self.rect.x = self.x
        self.rect.y = self.y

    def receber_dano(self, dano):
        self.vida -= dano

    def desenhar(self, tela, cor):
        pygame.draw.rect(
            tela,
            cor,
            self.rect
        )