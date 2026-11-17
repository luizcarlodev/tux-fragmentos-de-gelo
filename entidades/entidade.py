"""Classe base de todas as entidades com posição, tamanho e sprite."""
import pygame


class Entidade:
    """Objeto do mundo com caixa de colisão (x, y, largura, altura) e sprite animado.

    O sprite é desenhado com a base centralizada na base da caixa de colisão,
    então a imagem pode ser maior que a caixa (cabelos, espinhos, sombras...).
    """

    def __init__(self, x, y, largura, altura):
        self.x = float(x)
        self.y = float(y)
        self.largura = int(largura)
        self.altura = int(altura)
        self.vx = 0.0
        self.vy = 0.0
        self.ativo = True
        self.animador = None
        self.espelhado = False

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.largura, self.altura)

    @property
    def centro_x(self):
        return self.x + self.largura / 2

    @property
    def centro_y(self):
        return self.y + self.altura / 2

    @property
    def base(self):
        return self.y + self.altura

    def desenhar(self, tela, camera, imagem=None):
        """Desenha o sprite na tela convertendo a posição do mundo."""
        if imagem is None:
            if self.animador is None:
                return
            imagem = self.animador.imagem(self.espelhado)
        px = self.x + self.largura / 2 - imagem.get_width() / 2
        py = self.y + self.altura - imagem.get_height()
        sx, sy = camera.mundo_para_tela(px, py)
        tela.blit(imagem, (round(sx), round(sy)))
