import os
import functools
import pygame
import config

_PASTA = "assets/background"

# (arquivo, fator de parallax) - da mais distante para a mais próxima
_CAMADAS = [("camada_parede", 0.5)]

_Y_INICIO_VOID = 400   # onde o escurecimento do abismo começa


@functools.lru_cache(maxsize=None)
def _carregar(nome):
    caminho = os.path.join(_PASTA, f"{nome}.png")
    if not os.path.isfile(caminho):
        return None

    img = pygame.image.load(caminho).convert_alpha()
    fator = config.ALTURA_TELA / img.get_height()
    nova_largura = max(1, round(img.get_width() * fator))
    return pygame.transform.scale(img, (nova_largura, config.ALTURA_TELA))


@functools.lru_cache(maxsize=None)
def _gradiente_void():
    altura = config.ALTURA_TELA - _Y_INICIO_VOID
    grad = pygame.Surface((config.LARGURA_TELA, altura), pygame.SRCALPHA)
    for y in range(altura):
        alpha = int(255 * (y / max(1, altura - 1)) ** 1.6)
        pygame.draw.line(grad, (0, 0, 0, alpha), (0, y), (config.LARGURA_TELA, y))
    return grad


def desenhar(tela, camera_x):
    tela.fill(config.COR_FUNDO)

    for nome, fator_parallax in _CAMADAS:
        img = _carregar(nome)
        if img is None:
            continue

        largura_img = img.get_width()
        x = -((camera_x * fator_parallax) % largura_img)
        while x < config.LARGURA_TELA:
            tela.blit(img, (x, 0))
            x += largura_img

    tela.blit(_gradiente_void(), (0, _Y_INICIO_VOID))
