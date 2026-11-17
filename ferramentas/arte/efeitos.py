"""Gerador dos efeitos visuais (recursos/efeitos/*): cacos de gelo, brilho, explosão, congelamento...

    python ferramentas/arte/efeitos.py
"""
import math
import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ferramentas.arte.base import (  # noqa: E402
    AZUL, AZUL_GLACIAL, CIANO, CONTORNO, GELO, GELO_CLARO, NEVE, NEVE_SOMBRA, OURO,
    iniciar_pygame,
)
from ferramentas.arte.inimigos import contorno, elipse, linha, montar, novo, poli, px, pxs, retangulo  # noqa: E402

BRANCO = (255, 255, 255)


def caco():
    """Caco de gelo 8x8 (pedaço de bloco quebrando)."""
    s = novo(8, 8)
    poli(s, [(1, 6), (3, 0), (7, 3), (5, 7)], GELO_CLARO)
    poli(s, [(3, 1), (6, 3), (4, 5)], NEVE)
    pxs(s, [(5, 5), (4, 6), (6, 4)], GELO)
    px(s, 3, 2, BRANCO)
    return contorno(s, AZUL)


def brilho(f):
    """Estrela de coleta: cresce, brilha e se desfaz em faíscas."""
    s = novo(16, 16)
    r = (3, 6, 7, 4)[f]
    corpo = (CIANO, NEVE, NEVE, GELO_CLARO)[f]
    for d in range(-r, r + 1):
        k = abs(d)
        cor = BRANCO if k < 2 else corpo
        px(s, 8 + d, 8, cor)
        px(s, 8, 8 + d, cor)
        if k < r // 2 + 1:
            px(s, 8 + d, 7, corpo)
            px(s, 7, 8 + d, corpo)
    if f in (1, 2):
        d = r // 2
        pxs(s, [(8 - d, 8 - d), (8 + d, 8 - d), (8 - d, 8 + d), (8 + d, 8 + d)], BRANCO)
    if f >= 2:
        d = 2 + f * 2
        pxs(s, [(8 - d, 8 - d), (8 + d, 8 - d), (8 - d, 8 + d + 1), (8 + d, 8 + d + 1)], CIANO)
    return s


def explosao(f):
    """Estilhaços de gelo irradiando do centro."""
    s = novo(16, 16)
    rng = random.Random(11)
    raio = (2.5, 5.0, 7.0)[f]
    if f == 0:
        elipse(s, 8, 8, 3.2, 3.2, NEVE)
        elipse(s, 8, 8, 1.8, 1.8, BRANCO)
    for i in range(8):
        ang = i * math.pi / 4 + rng.random() * 0.3
        cx, cy = 8 + math.cos(ang) * raio, 8 + math.sin(ang) * raio
        tam = 2 if f < 2 else 1
        cor = (GELO_CLARO, CIANO, NEVE)[i % 3]
        if f == 2 and i % 2:
            continue
        poli(s, [(cx - tam, cy), (cx, cy - tam - 1), (cx + tam, cy), (cx, cy + tam)], cor)
        px(s, cx, cy, BRANCO)
    if f < 2:
        for i in range(8):
            ang = i * math.pi / 4 + 0.4
            px(s, 8 + math.cos(ang) * raio * 0.55, 8 + math.sin(ang) * raio * 0.55, GELO_CLARO)
    return s


def congelamento(f):
    """Flocão de gelo que cresce sobre o alvo."""
    s = novo(16, 16)
    r = (3, 5, 7, 6)[f]
    if f >= 1:
        for y in range(16):
            for x in range(16):
                d = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
                if d <= r - 1 and (x + y) % 2 == 0 and f in (1, 2):
                    s.set_at((x, y), (170, 226, 250, 140))
    for k in range(6):
        ang = k * math.pi / 3 + math.pi / 6
        ex, ey = 8 + math.cos(ang) * r, 8 + math.sin(ang) * r
        linha(s, (8, 8), (ex, ey), NEVE if f != 3 else GELO_CLARO)
        mx, my = 8 + math.cos(ang) * r * 0.6, 8 + math.sin(ang) * r * 0.6
        for da in (-0.9, 0.9):
            linha(s, (mx, my), (mx + math.cos(ang + da) * 2, my + math.sin(ang + da) * 2), CIANO)
    px(s, 8, 8, BRANCO)
    if f == 3:
        for i in range(6):
            ang = i * 1.05
            px(s, 8 + math.cos(ang) * 7.5, 8 + math.sin(ang) * 7.5, GELO_CLARO)
    return s


def poeira_dash(f):
    """Nuvem de neve que fica para trás do dash (Tux olha para a direita: nuvem à esquerda)."""
    s = novo(16, 16)
    rng = random.Random(5)
    n = 3
    for i in range(n):
        cx = 10 - f * 3 - i * 2.2
        cy = 12 - i * 1.5 - f * 0.8
        r = (2.2 + i * 0.6 + f * 0.5)
        cor = NEVE if f < 2 else NEVE_SOMBRA
        elipse(s, cx, cy, r, r * 0.8, cor)
    # riscos de velocidade
    for k in range(3 - f):
        y = 5 + k * 3
        linha(s, (14 - f * 2, y), (9 - f * 2, y), (255, 255, 255, 190))
    for y in range(16):
        for x in range(16):
            c = s.get_at((x, y))
            if c.a and f == 2 and (x + y) % 2:
                s.set_at((x, y), (c.r, c.g, c.b, 90))
    return s


def floco(tipo):
    """Partícula de neve (8x8): pequeno, médio e grande."""
    s = novo(8, 8)
    if tipo == "pequeno":
        retangulo(s, 3, 3, 2, 2, BRANCO)
    elif tipo == "medio":
        pxs(s, [(3, 2), (3, 4), (2, 3), (4, 3)], NEVE)
        px(s, 3, 3, BRANCO)
    else:
        pxs(s, [(3, 1), (3, 2), (3, 4), (3, 5), (1, 3), (2, 3), (4, 3), (5, 3)], NEVE)
        pxs(s, [(2, 2), (4, 2), (2, 4), (4, 4)], GELO_CLARO)
        px(s, 3, 3, BRANCO)
    return s


def gerar():
    montar("efeitos/fragmento", "efeito.png", 8, 8, [("parado", [caco()], 0.12, True)])
    montar("efeitos/brilho", "efeito.png", 16, 16, [("brilho", [brilho(i) for i in range(4)], 0.07, False)])
    montar("efeitos/explosao_gelo", "efeito.png", 16, 16,
           [("explosao", [explosao(i) for i in range(3)], 0.08, False)])
    montar("efeitos/congelamento", "efeito.png", 16, 16,
           [("congelar", [congelamento(i) for i in range(4)], 0.07, False)])
    montar("efeitos/poeira_dash", "efeito.png", 16, 16,
           [("dash", [poeira_dash(i) for i in range(3)], 0.06, False)])
    montar("efeitos/floco", "efeito.png", 8, 8,
           [("pequeno", [floco("pequeno")], 1.0, True), ("medio", [floco("medio")], 1.0, True),
            ("grande", [floco("grande")], 1.0, True)])
    print("Efeitos gerados.")


if __name__ == "__main__":
    iniciar_pygame()
    gerar()
