"""Partículas de neve (nevasca) desenhadas em tela, com intensidade e vento configuráveis por tema."""
import math
import random

import pygame

from configuracoes import ALTURA_BASE, LARGURA_BASE

TAMANHOS = {"pequeno": 7, "medio": 11, "grande": 16}


class SistemaDeNeve:
    """Flocos caindo continuamente. ``configurar`` aceita ``{"densidade": 80, "vento": -40}``.

    A densidade muda suavemente (ex.: ao entrar na zona da tempestade).
    """

    MAXIMO = 260

    def __init__(self, recursos, configuracao=None, semente=7):
        self.rng = random.Random(semente)
        folha = recursos.folha("efeitos/floco")
        self.imagens = []
        for nome, lado in TAMANHOS.items():
            quadro = folha.obter(nome).quadros[0]
            self.imagens.append(pygame.transform.scale(quadro, (lado, lado)))
        self.flocos = [self._novo(aleatorio=True) for _ in range(self.MAXIMO)]
        self.densidade = 0.0
        self.densidade_alvo = 0.0
        self.vento = 0.0
        self.vento_alvo = 0.0
        self.tempo = 0.0
        self._camera_x = None
        self.configurar(configuracao, instantaneo=True)

    def _novo(self, aleatorio=False):
        tamanho = self.rng.choice((0, 0, 1, 1, 2))
        return [self.rng.uniform(-60, LARGURA_BASE + 60),
                self.rng.uniform(0, ALTURA_BASE) if aleatorio else -20.0,
                40.0 + tamanho * 40.0 + self.rng.uniform(0, 40),      # velocidade de queda
                self.rng.uniform(0, 6.28),                            # fase do balanço
                tamanho]

    def configurar(self, configuracao, instantaneo=False):
        configuracao = configuracao or {}
        self.densidade_alvo = float(min(self.MAXIMO, configuracao.get("densidade", 0)))
        self.vento_alvo = float(configuracao.get("vento", -20.0))
        if instantaneo:
            self.densidade, self.vento = self.densidade_alvo, self.vento_alvo

    def atualizar(self, dt, camera_x=None):
        self.tempo += dt
        self.densidade += (self.densidade_alvo - self.densidade) * min(1.0, dt * 0.8)
        self.vento += (self.vento_alvo - self.vento) * min(1.0, dt * 0.8)
        deslocamento_camera = 0.0
        if camera_x is not None:
            if self._camera_x is not None:
                deslocamento_camera = (camera_x - self._camera_x) * 0.35      # leve paralaxe
            self._camera_x = camera_x
        ativos = int(self.densidade)
        for i, floco in enumerate(self.flocos):
            if i >= ativos:
                continue
            floco[1] += floco[2] * dt
            floco[0] += (self.vento + math.sin(self.tempo * 1.3 + floco[3]) * 22.0) * dt - deslocamento_camera
            if floco[1] > ALTURA_BASE + 10 or floco[0] < -80 or floco[0] > LARGURA_BASE + 80:
                self.flocos[i] = self._novo()
                if floco[0] < -80 or floco[0] > LARGURA_BASE + 80:
                    self.flocos[i][1] = self.rng.uniform(0, ALTURA_BASE)

    def desenhar(self, tela):
        ativos = int(self.densidade)
        for i in range(min(ativos, len(self.flocos))):
            x, y, _, _, tamanho = self.flocos[i]
            tela.blit(self.imagens[tamanho], (round(x), round(y)))
