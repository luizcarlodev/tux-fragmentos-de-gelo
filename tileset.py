import os
import pygame
import config
import sprites

_PASTA = "assets/tileset"
_ALTURA_TILE = {"chao": config.CHAO_ALTURA, "plataforma": config.TILE}


def desenhar_bloco(tela, tipo, x, y, largura, altura, camera_x, cor_fallback):
    """Preenche o bloco repetindo o tile '<tipo>_meio.png'. Sem o PNG, desenha um retângulo."""
    x_tela = x - camera_x
    if x_tela + largura < 0 or x_tela > config.LARGURA_TELA:
        return

    tile = sprites.carregar(os.path.join(_PASTA, f"{tipo}_meio.png"), _ALTURA_TILE[tipo])
    if tile is None:
        pygame.draw.rect(tela, cor_fallback, (x_tela, y, largura, altura))
        return

    largura_tile = tile.get_width()
    cursor = x_tela
    limite = x_tela + largura

    while cursor < limite:
        restante = limite - cursor
        if restante >= largura_tile:
            tela.blit(tile, (cursor, y))
        else:
            tela.blit(tile, (cursor, y), (0, 0, int(restante), altura))
        cursor += largura_tile
