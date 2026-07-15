import pygame


class Entidade:
    def __init__(self, x, y, largura, altura, vida):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self._vida = vida
        self.velocidade = 5

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.largura,
            self.altura
        )

    @property
    def vida(self):
        return self._vida

    def mover(self, dx, dy):
        self.x += dx
        self.y += dy

        self.rect.x = self.x
        self.rect.y = self.y

    def receber_dano(self, dano):
        self._vida -= dano

    def desenhar(self, tela, cor, camera_x=0):
        rect_tela = pygame.Rect(self.rect.x - camera_x , self.rect.y, self.rect.width, self.rect.height)

        pygame.draw.rect(tela, cor, rect_tela)