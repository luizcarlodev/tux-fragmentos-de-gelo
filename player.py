from projetil import Projetil
import utils
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

        self.direcao = 1
        self.dash_timer = 0
        self.dash_cooldown = 0

        self.atacando = False
        self.ataque_timer = 0
        self.ataque_cooldown = 0

    def mover_player(self, teclas):

        if teclas[pygame.K_a]:
            self.direcao = -1
            self.mover(-self.velocidade, 0)

        if teclas[pygame.K_d]:
            self.direcao = 1
            self.mover(self.velocidade, 0)

        # colisão(esquerda)
        if self.x < config.LIMITE_ESQUERDA:
            self.x = config.LIMITE_ESQUERDA

        # colisão(direita)
        if self.x > config.LIMITE_DIREITA:
            self.x = config.LIMITE_DIREITA

    def pular(self, teclas, plataformas):

        if teclas[pygame.K_SPACE] and not self.pulando:

            self.velocidade_y = config.PLAYER_FORCA_PULO
            self.pulando = True

        self.velocidade_y += self.gravidade
        self.y += self.velocidade_y
        self.rect.y = self.y

        self.pulando = True

        #colisão com plataformas(só quando caindo)
        if self.velocidade_y >= 0:
            for plataforma in plataformas:
                if utils.checar_colisao(self.rect, plataforma.rect):
                    self.y = plataforma.y - self.altura
                    self.rect.y = self.y
                    self.velocidade_y = 0
                    self.pulando = False

    def dash(self, teclas):
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        if teclas[config.TECLA_DASH] and self.dash_timer <= 0 and self.dash_cooldown <= 0:
            self.dash_timer = config.DASH_DURACAO
            self.dash_cooldown = config.DASH_COOLDOWN

        if self.dash_timer > 0:
            self.mover(self.direcao * self.velocidade * config.DASH_MULTIPLICADOR, 0)
            self.dash_timer -= 1

    def atacar(self, teclas):
        if self.ataque_cooldown > 0:
            self.ataque_cooldown -= 1

        if teclas[config.TECLA_ATAQUE] and self.ataque_cooldown <= 0:
            self.ataque_cooldown = config.ATAQUE_COOLDOWN
            return Projetil(self.x + self.largura / 2, self.y + self.altura / 2, self.direcao)

        return None

    def desenhar(self, tela, camera_x=0):
        super().desenhar(tela, config.COR_TUX, camera_x)