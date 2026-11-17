"""Efeitos visuais temporários: estilhaços de gelo, textos, brilhos, fagulhas e corações."""
import math
import random

import pygame

from interface.textos import renderizar_texto
from sistemas.animacoes import Animador


class Efeito:
    """Base de efeitos: ``ativo`` vira ``False`` quando terminam."""

    def __init__(self):
        self.ativo = True

    def atualizar(self, dt):
        pass

    def desenhar(self, tela, camera):
        pass


class Fragmento(Efeito):
    """Pedaço de bloco que voa e cai (ao quebrar tijolos)."""

    def __init__(self, x, y, vx, vy, imagem, altura_mundo):
        super().__init__()
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.imagem = imagem
        self.altura_mundo = altura_mundo
        self.angulo = random.uniform(0, 360)
        self.giro = random.uniform(-500, 500)

    def atualizar(self, dt):
        self.vy += 1800.0 * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angulo += self.giro * dt
        if self.y > self.altura_mundo + 100:
            self.ativo = False

    def desenhar(self, tela, camera):
        img = pygame.transform.rotate(self.imagem, self.angulo)
        sx, sy = camera.mundo_para_tela(self.x, self.y)
        tela.blit(img, img.get_rect(center=(round(sx), round(sy))))


class TextoFlutuante(Efeito):
    """Texto (pontos) que sobe e desaparece."""

    def __init__(self, x, y, texto, cor=(255, 255, 255), tamanho=24, duracao=0.9):
        super().__init__()
        self.x, self.y = x, y
        self.texto = texto
        self.cor = cor
        self.tamanho = tamanho
        self.tempo = 0.0
        self.duracao = duracao

    def atualizar(self, dt):
        self.tempo += dt
        self.y -= 55.0 * dt
        if self.tempo >= self.duracao:
            self.ativo = False

    def desenhar(self, tela, camera):
        img = renderizar_texto(self.texto, self.tamanho, self.cor)
        alfa = int(255 * max(0.0, min(1.0, (self.duracao - self.tempo) / (self.duracao * 0.5))))
        img = img.copy()
        img.set_alpha(alfa)
        sx, sy = camera.mundo_para_tela(self.x, self.y)
        tela.blit(img, img.get_rect(center=(round(sx), round(sy))))


class EfeitoAnimado(Efeito):
    """Toca uma animação uma única vez numa posição (poeira, brilho...)."""

    def __init__(self, folha, animacao, centro_x, centro_y):
        super().__init__()
        self.animador = Animador(folha, animacao)
        self.centro = (centro_x, centro_y)

    def atualizar(self, dt):
        self.animador.atualizar(dt)
        if self.animador.finalizada:
            self.ativo = False

    def desenhar(self, tela, camera):
        img = self.animador.imagem()
        sx, sy = camera.mundo_para_tela(*self.centro)
        tela.blit(img, img.get_rect(center=(round(sx), round(sy))))


class MoedaDeBloco(Efeito):
    """Moeda que salta para fora de um bloco ? e some."""

    def __init__(self, folha, x_centro, y_topo_bloco):
        super().__init__()
        self.animador = Animador(folha, "girando")
        self.animador.velocidade = 2.5
        self.x = x_centro
        self.y = y_topo_bloco - 20
        self.vy = -820.0

    def atualizar(self, dt):
        self.animador.atualizar(dt)
        self.vy += 2600.0 * dt
        self.y += self.vy * dt
        if self.vy > 500:
            self.ativo = False

    def desenhar(self, tela, camera):
        img = self.animador.imagem()
        sx, sy = camera.mundo_para_tela(self.x, self.y)
        tela.blit(img, img.get_rect(center=(round(sx), round(sy))))


class Fagulha(Efeito):
    """Partícula colorida usada nos fogos de artifício."""

    def __init__(self, x, y, vx, vy, cor, vida=1.1):
        super().__init__()
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.cor = cor
        self.vida = vida
        self.tempo = 0.0

    def atualizar(self, dt):
        self.tempo += dt
        self.vy += 260.0 * dt
        self.vx *= 1.0 - 1.2 * dt
        self.vy *= 1.0 - 0.6 * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.tempo >= self.vida:
            self.ativo = False

    def desenhar(self, tela, camera):
        restante = 1.0 - self.tempo / self.vida
        raio = max(1, int(4 * restante) + 1)
        cor = tuple(int(c * (0.4 + 0.6 * restante)) for c in self.cor)
        sx, sy = camera.mundo_para_tela(self.x, self.y)
        pygame.draw.circle(tela, cor, (round(sx), round(sy)), raio)


def criar_fogos(x, y, cor=None, quantidade=34):
    """Retorna uma lista de fagulhas formando uma explosão radial."""
    cor = cor or random.choice([(110, 226, 255), (255, 255, 255), (176, 150, 246), (255, 214, 96), (96, 236, 214)])
    fagulhas = []
    for i in range(quantidade):
        ang = 2 * math.pi * i / quantidade + random.uniform(-0.1, 0.1)
        vel = random.uniform(120, 300)
        fagulhas.append(Fagulha(x, y, math.cos(ang) * vel, math.sin(ang) * vel, cor, random.uniform(0.8, 1.3)))
    return fagulhas


def criar_explosao_gelo(x, y, quantidade=14, cores=None):
    """Pequena explosão de estilhaços gelados (golpes, quebra de blocos, coleta de fragmentos)."""
    cores = cores or [(210, 246, 255), (120, 220, 255), (255, 255, 255), (150, 190, 255)]
    fagulhas = []
    for _ in range(quantidade):
        ang = random.uniform(0, 2 * math.pi)
        vel = random.uniform(80, 260)
        fagulhas.append(Fagulha(x, y, math.cos(ang) * vel, math.sin(ang) * vel - 60, random.choice(cores),
                                random.uniform(0.3, 0.7)))
    return fagulhas


class CoracaoFlutuante(Efeito):
    """Coração que sobe balançando (cena final)."""

    def __init__(self, folha, x, y):
        super().__init__()
        self.animador = Animador(folha, "flutuando")
        self.x0, self.y = x, y
        self.tempo = random.uniform(0, 6)
        self.vida = 2.2
        self.idade = 0.0

    def atualizar(self, dt):
        self.animador.atualizar(dt)
        self.tempo += dt
        self.idade += dt
        self.y -= 60.0 * dt
        if self.idade >= self.vida:
            self.ativo = False

    def desenhar(self, tela, camera):
        img = self.animador.imagem().copy()
        img.set_alpha(int(255 * max(0.0, min(1.0, (self.vida - self.idade) / 0.6))))
        sx, sy = camera.mundo_para_tela(self.x0 + math.sin(self.tempo * 3) * 12, self.y)
        tela.blit(img, img.get_rect(center=(round(sx), round(sy))))
