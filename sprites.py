import os
import pygame

_cache = {}


def carregar(caminho, altura_alvo):
    """Carrega um PNG, corta o espaço transparente e escala para a altura alvo.
    Retorna None se o arquivo não existir."""
    chave = (caminho, altura_alvo)
    if chave in _cache:
        return _cache[chave]

    if not os.path.isfile(caminho):
        _cache[chave] = None
        return None

    img = pygame.image.load(caminho).convert_alpha()
    img = img.subsurface(img.get_bounding_rect()).copy()

    fator = altura_alvo / img.get_height()
    nova_largura = max(1, round(img.get_width() * fator))

    _cache[chave] = pygame.transform.scale(img, (nova_largura, altura_alvo))
    return _cache[chave]
