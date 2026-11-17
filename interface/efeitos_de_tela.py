"""Efeitos visuais reutilizáveis pelas telas: gradientes, confetes e escurecimento."""
import random

import pygame

from configuracoes import ALTURA_BASE, LARGURA_BASE


def gradiente_vertical(cor_topo, cor_base, largura=LARGURA_BASE, altura=ALTURA_BASE):
    """Superfície com degradê vertical."""
    superficie = pygame.Surface((largura, altura))
    for y in range(altura):
        f = y / max(1, altura - 1)
        cor = tuple(int(cor_topo[i] + (cor_base[i] - cor_topo[i]) * f) for i in range(3))
        pygame.draw.line(superficie, cor, (0, y), (largura, y))
    return superficie


def escurecer(tela, alfa=150):
    """Escurece toda a tela (usado atrás de menus transparentes)."""
    cobertura = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
    cobertura.fill((0, 0, 20, alfa))
    tela.blit(cobertura, (0, 0))


class Confetes:
    """Chuva de pequenos retângulos coloridos."""

    CORES = [(255, 90, 90), (255, 220, 80), (110, 220, 255), (170, 255, 140), (255, 140, 255)]

    def __init__(self, quantidade=90):
        self.pecas = [self._nova(True) for _ in range(quantidade)]

    def _nova(self, aleatoria_y=False):
        return [random.uniform(0, LARGURA_BASE), random.uniform(-ALTURA_BASE, 0) if not aleatoria_y
                else random.uniform(0, ALTURA_BASE), random.uniform(60, 200), random.uniform(-40, 40),
                random.choice(self.CORES), random.uniform(0, 6.28)]

    def atualizar(self, dt):
        for p in self.pecas:
            p[1] += p[2] * dt
            p[0] += p[3] * dt
            p[5] += dt * 5
            if p[1] > ALTURA_BASE + 10:
                p[:] = self._nova()

    def desenhar(self, tela):
        for x, y, _, _, cor, fase in self.pecas:
            largura = max(2, int(abs(__import__("math").sin(fase)) * 10))
            pygame.draw.rect(tela, cor, (int(x), int(y), largura, 8))
