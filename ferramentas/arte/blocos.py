"""Gerador do tileset glacial (recursos/blocos/tileset).

Cada tile tem 16x16 pixels e é desenhado por pequenos procedimentos
(texturas com ruído determinístico + detalhes). Execute:

    python -m ferramentas.arte.blocos
"""
import math
import random

try:
    from .base import *  # noqa: F401,F403
    from .base import (pygame, nova_folha, anim, salvar_folha, iniciar_pygame, CONTORNO, NEVE,
                       NEVE_SOMBRA, GELO_CLARO, CIANO, TURQUESA, GELO, AZUL_GLACIAL, AZUL,
                       AZUL_ESCURO, NOITE, ROXO_GELO, ROXO, ROXO_ESCURO, PEDRA, PEDRA_CLARA,
                       PEDRA_ESCURA, OURO, OURO_ESCURO, MADEIRA, MADEIRA_ESCURA)
except ImportError:  # execução direta: python blocos.py
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from ferramentas.arte.base import (pygame, nova_folha, anim, salvar_folha, iniciar_pygame,
                                       CONTORNO, NEVE, NEVE_SOMBRA, GELO_CLARO, CIANO, TURQUESA,
                                       GELO, AZUL_GLACIAL, AZUL, AZUL_ESCURO, NOITE, ROXO_GELO,
                                       ROXO, ROXO_ESCURO, PEDRA, PEDRA_CLARA, PEDRA_ESCURA, OURO,
                                       OURO_ESCURO, MADEIRA, MADEIRA_ESCURA)

T = 16


# ---------------------------------------------------------------- utilitários
def _novo(w=T, h=T):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def _px(s, x, y, c):
    if 0 <= x < s.get_width() and 0 <= y < s.get_height():
        s.set_at((x, y), c)


def _ret(s, x, y, w, h, c):
    s.fill(c, (x, y, w, h))


def _ruido(s, base_a, base_b, rng, claro=None, escuro=None, p_claro=0.12, p_escuro=0.12,
           rect=None, vertical=True):
    """Preenche ``rect`` com degradê base_a→base_b mais pontos claros/escuros aleatórios."""
    x0, y0, w, h = rect or (0, 0, s.get_width(), s.get_height())
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            t = (y - y0) / max(1, h - 1) if vertical else 0
            c = _mix(base_a, base_b, t)
            r = rng.random()
            if claro and r < p_claro:
                c = _mix(c, claro, 0.55)
            elif escuro and r < p_claro + p_escuro:
                c = _mix(c, escuro, 0.5)
            s.set_at((x, y), c)


def _neve_topo(s, perfil, x0=0, cor_borda=GELO_CLARO, gotejar=True):
    """Cobertura de neve fofa; ``perfil[x]`` = espessura (em px) na coluna."""
    for i, d in enumerate(perfil):
        x = x0 + i
        for y in range(d):
            c = NEVE
            if y == d - 1:
                c = NEVE_SOMBRA
            if y == d - 2 and d >= 4 and i % 3 == 1:
                c = _mix(NEVE, NEVE_SOMBRA, 0.5)
            _px(s, x, y, c)
        _px(s, x, d, cor_borda if gotejar else s.get_at((x, d)))
    # brilhos
    for i in range(0, len(perfil), 5):
        _px(s, x0 + i, 0, (255, 255, 255, 255))


PERFIL_NEVE = [4, 5, 4, 3, 4, 5, 6, 5, 4, 4, 5, 4, 3, 4, 5, 4]
PERFIL_NEVE_B = [3, 4, 4, 3, 3, 4, 5, 4, 3, 3, 4, 4, 3, 3, 4, 3]


def _bisel(s, x, y, w, h, claro, escuro, topo=True, esq=True, dir=True, baixo=True):
    if topo:
        _ret(s, x, y, w, 1, claro)
    if esq:
        _ret(s, x, y, 1, h, claro)
    if baixo:
        _ret(s, x, y + h - 1, w, 1, escuro)
    if dir:
        _ret(s, x + w - 1, y, 1, h, escuro)


# ---------------------------------------------------------------- tiles básicos
def t_neve():
    s = _novo()
    rng = random.Random(11)
    _ruido(s, GELO, AZUL_GLACIAL, rng, claro=GELO_CLARO, escuro=AZUL, p_claro=0.13, p_escuro=0.14)
    for (x, y, n) in ((2, 9, 3), (9, 8, 2), (5, 12, 4), (11, 13, 3)):
        _ret(s, x, y, n, 1, CIANO)
        _px(s, x + n, y + 1, GELO_CLARO)
    for (x, y) in ((1, 14), (13, 10), (7, 10)):
        _px(s, x, y, NEVE)
    _neve_topo(s, PERFIL_NEVE, cor_borda=AZUL_GLACIAL)
    # base mais escura (ancora o bloco)
    _ret(s, 0, 15, 16, 1, AZUL)
    return s


def t_solo_congelado():
    s = _novo()
    rng = random.Random(23)
    base_a, base_b = (66, 84, 138), (52, 66, 118)
    _ruido(s, base_a, base_b, rng, claro=(100, 124, 176), escuro=(38, 48, 96), p_claro=0.15, p_escuro=0.15)
    # veios de gelo
    for (x, y) in ((1, 3), (2, 4), (3, 4), (4, 5), (5, 6)):
        _px(s, x, y, GELO_CLARO)
        _px(s, x, y + 1, GELO)
    for (x, y) in ((10, 9), (11, 10), (12, 10), (13, 11), (14, 12), (15, 12)):
        _px(s, x, y, CIANO)
        _px(s, x, y + 1, GELO)
    _px(s, 0, 3, GELO_CLARO)
    # pedrinhas
    for (x, y, c) in ((8, 2, PEDRA), (3, 11, PEDRA), (12, 5, PEDRA_CLARA), (7, 13, PEDRA)):
        _ret(s, x, y, 2, 2, c)
        _px(s, x, y, PEDRA_CLARA)
        _px(s, x + 1, y + 1, PEDRA_ESCURA)
    _px(s, 14, 14, NEVE_SOMBRA)
    _px(s, 5, 8, NEVE_SOMBRA)
    return s


def t_bloco_gelo():
    s = _novo()
    for y in range(16):
        for x in range(16):
            t = (x + y) / 30
            s.set_at((x, y), _mix(GELO_CLARO, GELO, t * 0.9))
    # miolo translúcido-claro
    _ret(s, 2, 2, 12, 12, (150, 214, 246))
    for y in range(2, 14):
        for x in range(2, 14):
            s.set_at((x, y), _mix((184, 234, 252), (120, 192, 240), (x + y - 4) / 22))
    # borda chanfrada
    _ret(s, 0, 0, 16, 1, NEVE_SOMBRA)
    _ret(s, 0, 0, 1, 16, NEVE_SOMBRA)
    _ret(s, 0, 15, 16, 1, AZUL_GLACIAL)
    _ret(s, 15, 0, 1, 16, AZUL_GLACIAL)
    _ret(s, 1, 1, 14, 1, NEVE)
    _ret(s, 1, 1, 1, 14, NEVE)
    _ret(s, 1, 14, 14, 1, GELO)
    _ret(s, 14, 1, 1, 14, GELO)
    for (x, y) in ((0, 0), (15, 0), (0, 15), (15, 15)):
        s.set_at((x, y), AZUL_GLACIAL)
    # brilho diagonal
    for i in range(5):
        _px(s, 3 + i, 9 - i, NEVE)
    for i in range(3):
        _px(s, 6 + i, 12 - i, (230, 248, 255, 255))
    _px(s, 4, 4, (255, 255, 255, 255))
    _px(s, 5, 4, NEVE)
    _px(s, 4, 5, NEVE)
    # fissuras internas
    for (x, y) in ((10, 5), (11, 6), (11, 7), (12, 8)):
        _px(s, x, y, CIANO)
    _px(s, 9, 4, CIANO)
    return s


def _moldura_gelo(s, escuro=False):
    """Moldura de gelo 2px para blocos de recompensa."""
    if escuro:
        c_cl, c_md, c_es = PEDRA_CLARA, PEDRA, PEDRA_ESCURA
    else:
        c_cl, c_md, c_es = NEVE, GELO_CLARO, GELO
    _ret(s, 0, 0, 16, 16, c_md)
    _ret(s, 0, 0, 16, 1, c_cl)
    _ret(s, 0, 0, 1, 16, c_cl)
    _ret(s, 0, 15, 16, 1, _mix(c_es, CONTORNO, 0.25))
    _ret(s, 15, 0, 1, 16, _mix(c_es, CONTORNO, 0.25))
    _ret(s, 1, 14, 14, 1, c_es)
    _ret(s, 14, 1, 1, 14, c_es)
    s.set_at((0, 0), c_md)
    s.set_at((15, 15), c_es)
    s.set_at((0, 15), c_es)
    s.set_at((15, 0), c_md)


def t_cristal(intens):
    s = _novo()
    _moldura_gelo(s)
    # campo interno escuro
    for y in range(2, 14):
        for x in range(2, 14):
            s.set_at((x, y), _mix(AZUL_ESCURO, NOITE, (y - 2) / 11))
    _ret(s, 2, 2, 12, 1, AZUL)       # sombra interna
    _ret(s, 2, 2, 1, 12, AZUL)
    # halo
    halo = [0.18, 0.34, 0.55][intens]
    for y in range(2, 14):
        for x in range(2, 14):
            d = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
            if d < 6.5:
                c = s.get_at((x, y))
                s.set_at((x, y), _mix(c[:3], CIANO, halo * (1 - d / 6.5) ** 1.2))
    # gema
    claro = _mix((255, 236, 150), (255, 255, 235), intens / 2)
    medio = _mix(OURO, (255, 232, 130), intens / 2)
    escuro = _mix(OURO_ESCURO, OURO, intens / 3)
    nucleo = _mix(CIANO, (230, 255, 255), intens / 2)
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - 8, y + 0.5 - 8.2
            if abs(dx) / 4.1 + abs(dy) / 5.2 <= 1.0:
                if dy < -1.5 and abs(dx) < 2.2:
                    c = claro
                elif dx < -0.3 and dy < 1.0:
                    c = claro if (x + y) % 3 else medio
                elif dx < 0.3:
                    c = medio
                elif dy < 0.8:
                    c = medio
                else:
                    c = escuro
                if abs(dx) < 1.0 and abs(dy) < 2.0:
                    c = nucleo
                _px(s, x, y, c)
    # contorno dourado-escuro da gema
    copia = s.copy()
    for y in range(2, 14):
        for x in range(2, 14):
            if copia.get_at((x, y)) in (_mix(AZUL_ESCURO, NOITE, 0),):
                continue
    # brilho (cruz de luz)
    if intens >= 1:
        _px(s, 6, 5, (255, 255, 255, 255))
    if intens == 2:
        for (x, y) in ((5, 4), (7, 4), (6, 3), (6, 6)):
            _px(s, x, y, (255, 255, 255, 255))
        _px(s, 11, 11, NEVE)
        _px(s, 10, 12, CIANO)
    elif intens == 1:
        _px(s, 11, 11, GELO_CLARO)
    # rebites dourados nos cantos
    for (x, y) in ((1, 1), (14, 1), (1, 14), (14, 14)):
        _px(s, x, y, OURO if intens else OURO_ESCURO)
    return s


def t_cristal_usado():
    s = _novo()
    _moldura_gelo(s, escuro=True)
    # recolore a moldura para cinza-azulado frio
    for y in range(16):
        for x in range(16):
            c = s.get_at((x, y))
            s.set_at((x, y), _mix(c[:3], (110, 124, 160), 0.35))
    for y in range(2, 14):
        for x in range(2, 14):
            s.set_at((x, y), _mix((52, 60, 90), (40, 46, 74), (y - 2) / 11))
    _ret(s, 2, 2, 12, 1, (34, 40, 66))
    _ret(s, 2, 2, 1, 12, (34, 40, 66))
    # gema apagada
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - 8, y + 0.5 - 8.2
            if abs(dx) / 4.1 + abs(dy) / 5.2 <= 1.0:
                c = (86, 98, 130) if dx < 0.3 else (66, 76, 106)
                if dy < -1.5 and abs(dx) < 2.2:
                    c = (104, 116, 148)
                _px(s, x, y, c)
    for (x, y) in ((1, 1), (14, 1), (1, 14), (14, 14)):
        _px(s, x, y, (96, 104, 128))
    return s


def t_bloco_pedra():
    s = _novo()
    rng = random.Random(5)
    _ruido(s, PEDRA, PEDRA_ESCURA, rng, claro=PEDRA_CLARA, escuro=PEDRA_ESCURA,
           p_claro=0.1, p_escuro=0.1, rect=(0, 0, 16, 16))
    # juntas (duas fileiras de pedras)
    _ret(s, 0, 9, 16, 1, PEDRA_ESCURA)
    _ret(s, 5, 4, 1, 5, PEDRA_ESCURA)
    _ret(s, 12, 4, 1, 5, PEDRA_ESCURA)
    _ret(s, 2, 10, 1, 6, PEDRA_ESCURA)
    _ret(s, 9, 10, 1, 6, PEDRA_ESCURA)
    # realces
    for (x, w) in ((0, 5), (6, 6), (13, 3)):
        _ret(s, x, 5, w, 1, PEDRA_CLARA)
    for (x, w) in ((3, 6), (10, 6), (0, 2)):
        _ret(s, x, 11, w, 1, PEDRA_CLARA)
    # bordas do bloco
    _ret(s, 0, 15, 16, 1, (54, 62, 88))
    _ret(s, 15, 0, 1, 16, (54, 62, 88))
    _neve_topo(s, PERFIL_NEVE_B, cor_borda=PEDRA_ESCURA)
    return s


# ---------------------------------------------------------------- pilares (2 tiles de largura)
def _faixa_gelo(x, w):
    """Cor da faceta de gelo na coluna ``x`` de um pilar com ``w`` pixels."""
    t = x / (w - 1)
    if t < 0.08:
        return NEVE
    if t < 0.22:
        return GELO_CLARO
    if t < 0.30:
        return NEVE_SOMBRA
    if t < 0.5:
        return GELO_CLARO
    if t < 0.62:
        return CIANO if False else GELO
    if t < 0.78:
        return GELO
    if t < 0.9:
        return AZUL_GLACIAL
    return AZUL


def t_pilar_topo():
    s = _novo(32, 16)
    # cabeça (capitel) y 4..15, largura total
    for y in range(4, 16):
        for x in range(32):
            c = _faixa_gelo(x, 32)
            if y == 4:
                c = _mix(c[:3], NEVE, 0.6)
            if y >= 13:
                c = _mix(c[:3], AZUL_ESCURO, 0.25 * (y - 12))
            s.set_at((x, y), c)
    # realces verticais (facetas)
    for y in range(6, 13):
        _px(s, 7, y, NEVE)
        _px(s, 21, y, NEVE_SOMBRA)
        _px(s, 13, y, GELO_CLARO)
    _px(s, 7, 6, (255, 255, 255, 255))
    for (x, y) in ((10, 8), (17, 10), (25, 7)):
        _px(s, x, y, CIANO)
    # contornos do capitel
    for y in range(4, 16):
        s.set_at((0, y), CONTORNO)
        s.set_at((31, y), CONTORNO)
    _ret(s, 0, 15, 32, 1, CONTORNO)
    _ret(s, 0, 4, 32, 1, CONTORNO)
    # neve no topo (montinho + sobra pendurada)
    for x in range(32):
        altura = 3 + int(round(1.4 * math.sin(math.pi * (x + 0.5) / 32.0)))
        alt_total = 4 + altura
        topo = 4 - altura
        for y in range(max(0, topo), 6 + (1 if x % 4 in (1, 2) else 0)):
            c = NEVE
            if y >= 5:
                c = NEVE_SOMBRA
            _px(s, x, y, c)
        # borda escura superior do monte
        if topo - 1 >= 0:
            _px(s, x, topo - 1, CONTORNO)
    _px(s, 0, 4, CONTORNO)
    _px(s, 31, 4, CONTORNO)
    for (x, y) in ((6, 1), (13, 1), (20, 2), (26, 1)):
        _px(s, x, y, (255, 255, 255, 255))
    # sombra do capitel sobre o corpo (não há corpo aqui; só base escura)
    return s


def t_pilar_corpo():
    s = _novo(32, 16)
    for y in range(16):
        for x in range(1, 31):
            c = _faixa_gelo(x - 1, 30)
            s.set_at((x, y), c)
    # facetas: linhas diagonais de brilho
    for y in range(16):
        _px(s, 5, y, NEVE if y % 8 not in (3, 4) else GELO_CLARO)
        _px(s, 6, y, GELO_CLARO)
        _px(s, 16, y, GELO if y % 5 else CIANO)
        _px(s, 24, y, AZUL_GLACIAL)
    for (x, y) in ((9, 3), (10, 4), (11, 5), (20, 11), (21, 12), (22, 13), (12, 12), (13, 13)):
        _px(s, x, y, NEVE_SOMBRA)
    _px(s, 5, 2, (255, 255, 255, 255))
    # contornos laterais
    for y in range(16):
        s.set_at((1, y), CONTORNO)
        s.set_at((30, y), CONTORNO)
        s.set_at((2, y), _mix(NEVE, GELO_CLARO, 0.3))
        s.set_at((29, y), AZUL)
    return s


def _metade(folha, esquerda):
    s = _novo()
    s.blit(folha, (0, 0), (0 if esquerda else 16, 0, 16, 16))
    return s


# ---------------------------------------------------------------- castelo
def _tijolos_castelo(s, y0, y1, rng, cores_tijolo, junta):
    """Preenche linhas y0..y1-1 com tijolos 8x4 em fiadas alternadas (tileável)."""
    fiada = 0
    y = y0
    while y < y1:
        deslocamento = 0 if (fiada % 2 == 0) else 4
        alt = min(4, y1 - y)
        for bx in range(-8, 16, 8):
            x = bx + deslocamento
            cor = cores_tijolo[rng.randrange(len(cores_tijolo))]
            for yy in range(alt):
                for xx in range(8):
                    c = cor
                    if yy == 0:
                        c = _mix(cor, GELO_CLARO, 0.28)
                    elif yy == alt - 2 and alt == 4:
                        c = _mix(cor, NOITE, 0.15)
                    if xx == 0 or yy == alt - 1:
                        c = junta
                    elif xx == 7:
                        c = _mix(cor, NOITE, 0.3)
                    if rng.random() < 0.08:
                        c = _mix(c[:3], ROXO_GELO, 0.25)
                    _px(s, x + xx, y + yy, c)
        y += 4
        fiada += 1


def t_tijolo_castelo():
    s = _novo()
    rng = random.Random(41)
    cores = [AZUL, (54, 52, 130), ROXO_ESCURO, (44, 60, 140)]
    _tijolos_castelo(s, 0, 16, rng, cores, (126, 152, 204))
    # neve acumulada nas juntas (pontos)
    for (x, y) in ((3, 3), (11, 7), (6, 11), (14, 15)):
        _px(s, x, y, NEVE_SOMBRA)
    return s


def t_topo_castelo():
    s = _novo()
    rng = random.Random(43)
    cores = [AZUL, (54, 52, 130), ROXO_ESCURO, (44, 60, 140)]
    _tijolos_castelo(s, 6, 16, rng, cores, (126, 152, 204))
    # ameia: merlão x 2..9, y 0..5 (pedra clara) com neve no topo
    for y in range(0, 6):
        for x in range(2, 10):
            c = _mix(AZUL_GLACIAL, AZUL, y / 5)
            if x == 2:
                c = _mix(c[:3], GELO_CLARO, 0.35)
            if x == 9:
                c = _mix(c[:3], NOITE, 0.35)
            _px(s, x, y, c)
    _ret(s, 2, 0, 8, 2, NEVE)
    _ret(s, 2, 2, 8, 1, NEVE_SOMBRA)
    _px(s, 3, 3, NEVE_SOMBRA)
    _px(s, 7, 3, NEVE_SOMBRA)
    # janelinha/seteira dourada
    _ret(s, 5, 3, 1, 3, NOITE)
    _px(s, 6, 4, _mix(OURO_ESCURO, NOITE, 0.4))
    # neve no piso entre merlões
    _ret(s, 10, 5, 8 - 2, 1, NEVE_SOMBRA)
    _ret(s, 0, 5, 2, 1, NEVE_SOMBRA)
    _ret(s, 10, 6, 6, 1, GELO_CLARO)
    _ret(s, 0, 6, 2, 1, GELO_CLARO)
    # sombra sob o piso
    _ret(s, 10, 7, 6, 1, _mix(AZUL, NOITE, 0.4))
    _ret(s, 0, 7, 2, 1, _mix(AZUL, NOITE, 0.4))
    return s


def t_chao_castelo():
    s = _novo()
    rng = random.Random(47)
    for y in range(16):
        for x in range(16):
            t = y / 15
            c = _mix((150, 188, 236), (84, 118, 196), t)
            # sutil mármore
            if rng.random() < 0.07:
                c = _mix(c[:3], NEVE, 0.35)
            s.set_at((x, y), c)
    # placas polidas (juntas)
    _ret(s, 0, 9, 16, 1, (70, 98, 172))
    _ret(s, 7, 3, 1, 6, (70, 98, 172))
    _ret(s, 14, 10, 1, 6, (70, 98, 172))
    _ret(s, 0, 10, 16, 1, (170, 206, 246))
    # veios e brilho
    for (x, y) in ((2, 5), (3, 6), (4, 6), (5, 7), (10, 12), (11, 13), (12, 13), (13, 14)):
        _px(s, x, y, (190, 220, 250, 255))
    for i in range(4):
        _px(s, 9 + i, 6 - i, NEVE)
    _px(s, 3, 12, NEVE)
    # detalhe dourado fino no topo
    _ret(s, 0, 0, 16, 1, OURO)
    _ret(s, 0, 1, 16, 1, OURO_ESCURO)
    _ret(s, 0, 2, 16, 1, _mix((150, 188, 236), NEVE, 0.4))
    for x in range(0, 16, 4):
        _px(s, x + 1, 0, (255, 240, 170, 255))
    _ret(s, 0, 15, 16, 1, (58, 80, 160))
    return s


# ---------------------------------------------------------------- perigos
def t_espinhos_gelo():
    s = _novo()
    # perfis das 4 pontas (altura por coluna, base 4px de largura)
    pontas = [([2, 5, 8, 4], 2), ([3, 8, 5, 2], 1), ([2, 6, 7, 3], 2), ([3, 7, 8, 2], 2)]
    for k, (alturas, ap) in enumerate(pontas):
        for c, alt in enumerate(alturas):
            x = k * 4 + c
            for i in range(alt):
                y = 15 - i
                # cor por posição: esquerda clara, direita escura, ponta branca
                if i >= alt - 2:
                    cor = NEVE
                elif c < ap:
                    cor = GELO_CLARO
                elif c == ap:
                    cor = _mix(GELO_CLARO, GELO, 0.3)
                else:
                    cor = GELO
                if i < 2:
                    cor = _mix(cor[:3], AZUL_GLACIAL, 0.55)
                _px(s, x, y, cor)
    # brilho central
    for (x, y) in ((2, 10), (2, 11), (5, 9), (5, 10), (10, 10), (14, 9)):
        _px(s, x, y, (255, 255, 255, 255))
    # contorno (só dentro da metade inferior)
    copia = s.copy()
    for y in range(7, 16):
        for x in range(16):
            if copia.get_at((x, y)).a == 0:
                for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + ddx, y + ddy
                    if 0 <= nx < 16 and 0 <= ny < 16 and copia.get_at((nx, ny)).a != 0:
                        s.set_at((x, y), CONTORNO)
                        break
    return s


def t_agua(f):
    s = _novo()
    rng = random.Random(61)
    fase = f / 3.0
    for y in range(16):
        for x in range(16):
            t = y / 15
            c = _mix((16, 86, 112), (8, 40, 70), t)
            if rng.random() < 0.12:
                c = _mix(c[:3], (14, 110, 130), 0.5)
            s.set_at((x, y), c)
    # ondas (periodicidade horizontal 16 -> sem emendas)
    for x in range(16):
        y_onda = 2 + int(round(1.2 * math.sin(2 * math.pi * (x / 16.0 * 2 + fase))))
        for y in range(0, y_onda):
            s.set_at((x, y), _mix((22, 120, 146), (16, 86, 112), y / 3))
        _px(s, x, y_onda, TURQUESA)
        _px(s, x, y_onda + 1, _mix(TURQUESA, (10, 60, 90), 0.5))
    # ondulações internas
    for (bx, by) in ((2, 8), (10, 12), (6, 5)):
        xx = (bx + f * 3) % 16
        for dx in range(3):
            _px(s, (xx + dx) % 16, by + (1 if dx == 1 else 0), (30, 130, 156, 255))
    # blocos de gelo flutuando
    for (bx, by, w, h) in ((1, 1, 4, 3), (9, 2, 3, 2)):
        xx = (bx + f) % 16
        for dy in range(h):
            for dx in range(w):
                yy = by + dy + (1 if f == 1 and bx == 1 else 0)
                c = NEVE if dy == 0 else (GELO_CLARO if dy < h - 1 else GELO)
                _px(s, (xx + dx) % 16, yy, c)
    # faíscas de luz
    _px(s, (4 + f * 5) % 16, 9, (120, 220, 236, 255))
    _px(s, (12 + f * 3) % 16, 13, (90, 190, 214, 255))
    return s


def t_estalactite():
    s = _novo()
    # teto de pedra-gelo (2 linhas)
    for x in range(16):
        s.set_at((x, 0), AZUL)
        s.set_at((x, 1), _mix(AZUL, GELO, 0.4 + 0.2 * ((x * 7) % 3 == 0)))
    # estalactite grande central (colunas 3..12) e pequenas laterais
    perfis = {}
    larg = [(3, 1), (4, 3), (5, 5), (6, 6), (7, 7), (8, 7), (9, 6), (10, 5), (11, 3), (12, 1)]
    for (x, h) in larg:
        perfis[x] = max(perfis.get(x, 0), h + 1)
    for (x, h) in ((0, 2), (1, 4), (2, 3), (13, 3), (14, 5), (15, 3)):
        perfis[x] = max(perfis.get(x, 0), h + 1)
    for x, h in perfis.items():
        for y in range(1, 2 + h):
            if y == 1 + h:
                cor = NEVE
            elif x <= 6 or x in (0, 1, 2):
                cor = GELO_CLARO
            else:
                cor = GELO
            if y < 3:
                cor = _mix(cor[:3], AZUL, 0.4)
            _px(s, x, y, cor)
    for (x, y) in ((6, 3), (6, 4), (6, 5), (7, 4), (1, 3)):
        _px(s, x, y, NEVE)
    for (x, y) in ((9, 5), (10, 4)):
        _px(s, x, y, AZUL_GLACIAL)
    # contorno
    copia = s.copy()
    for y in range(0, 10):
        for x in range(16):
            if copia.get_at((x, y)).a == 0:
                for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + ddx, y + ddy
                    if 0 <= nx < 16 and 0 <= ny < 16 and copia.get_at((nx, ny)).a != 0:
                        s.set_at((x, y), CONTORNO)
                        break
    return s


# ---------------------------------------------------------------- caverna
CAV_A = (74, 70, 128)
CAV_B = (50, 48, 98)
CAV_CL = (104, 104, 164)
CAV_ES = (34, 32, 72)


def t_neve_caverna():
    s = _novo()
    rng = random.Random(71)
    _ruido(s, CAV_A, CAV_B, rng, claro=CAV_CL, escuro=CAV_ES, p_claro=0.13, p_escuro=0.13)
    # lascas de pedra
    _ret(s, 0, 8, 6, 1, CAV_ES)
    _ret(s, 9, 11, 7, 1, CAV_ES)
    _ret(s, 3, 13, 3, 1, CAV_CL)
    _ret(s, 10, 9, 4, 1, CAV_CL)
    # geada
    for (x, y) in ((2, 6), (7, 7), (13, 8), (5, 11), (12, 14), (1, 12)):
        _px(s, x, y, GELO_CLARO)
    for (x, y) in ((3, 9), (11, 12)):
        _px(s, x, y, NEVE)
    perfil = [2, 3, 2, 2, 3, 3, 2, 1, 2, 3, 3, 2, 2, 3, 2, 2]
    _neve_topo(s, perfil, cor_borda=CAV_CL)
    _ret(s, 0, 15, 16, 1, CAV_ES)
    return s


def _pedra_caverna_base(rng):
    s = _novo()
    _ruido(s, (52, 52, 100), (40, 40, 82), rng, claro=(72, 72, 128), escuro=(30, 30, 66),
           p_claro=0.14, p_escuro=0.14)
    # veios
    for (x, y) in ((0, 4), (1, 4), (2, 5), (3, 5), (4, 6), (5, 6)):
        _px(s, x, y, (28, 26, 62))
        _px(s, x, y - 1, (78, 76, 134))
    for (x, y) in ((9, 11), (10, 11), (11, 10), (12, 10), (13, 9), (14, 9), (15, 9)):
        _px(s, x, y, (28, 26, 62))
        _px(s, x, y - 1, (78, 76, 134))
    for (x, y) in ((7, 1), (12, 3), (3, 13), (14, 14)):
        _px(s, x, y, (96, 100, 168))
    _px(s, 6, 9, (70, 190, 210))
    return s


def t_pedra_caverna():
    return _pedra_caverna_base(random.Random(81))


def t_parede_rachada(pulso=0):
    """Pedra com uma grande rachadura luminosa (pulsa devagar): a pista visual do segredo."""
    s = _pedra_caverna_base(random.Random(81))
    brilho = ((170, 240, 255), (225, 252, 255))[pulso]
    halo = ((60, 150, 195), (90, 190, 225))[pulso]
    principal = [(8, 0), (8, 1), (7, 2), (7, 3), (8, 4), (9, 5), (9, 6), (8, 7), (7, 8), (7, 9),
                 (8, 10), (9, 11), (9, 12), (8, 13), (8, 14), (8, 15)]
    ramos = [(6, 5), (5, 5), (4, 6), (3, 6), (10, 11), (11, 11), (12, 12), (13, 12), (6, 9), (5, 10)]
    for (x, y) in principal + ramos:
        for dx in (-1, 1):
            _px(s, x + dx, y, halo)
    for (x, y) in principal + ramos:
        _px(s, x, y, brilho)
    return s


def t_cristal_luminoso(f):
    s = _novo()
    rng = random.Random(91)
    _ruido(s, (50, 50, 98), (38, 38, 80), rng, claro=(70, 70, 124), escuro=(28, 28, 62),
           p_claro=0.12, p_escuro=0.14)
    inten = [0.45, 1.0, 0.7][f]
    # halos
    centros = [(5, 6, 5.5, CIANO), (11, 10, 5.0, ROXO_GELO)]
    for y in range(16):
        for x in range(16):
            for (cx, cy, r, cor) in centros:
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if d < r:
                    c = s.get_at((x, y))
                    s.set_at((x, y), _mix(c[:3], cor, 0.38 * inten * (1 - d / r)))

    def gema(cx, cy, pts, claro, medio, escuro):
        for (dx, dy, k) in pts:
            _px(s, cx + dx, cy + dy, (claro, medio, escuro)[k])
    cian = (_mix(CIANO, NEVE, 0.5 * inten), _mix(CIANO, TURQUESA, 0.2), _mix(TURQUESA, AZUL, 0.5))
    roxo = (_mix(ROXO_GELO, NEVE, 0.45 * inten), ROXO_GELO, ROXO)
    # cristal ciano (alto, inclinado)
    pts_c = [(0, -3, 0), (-1, -2, 0), (0, -2, 1), (-1, -1, 0), (0, -1, 1), (1, -1, 2), (-1, 0, 1),
             (0, 0, 1), (1, 0, 2), (-1, 1, 1), (0, 1, 2), (1, 1, 2), (-1, 2, 2), (0, 2, 2)]
    for (dx, dy, k) in pts_c:
        _px(s, 5 + dx, 6 + dy, cian[k])
    # cristal roxo (menor)
    pts_r = [(0, -2, 0), (-1, -1, 0), (0, -1, 1), (1, -1, 2), (-1, 0, 1), (0, 0, 1), (1, 0, 2),
             (0, 1, 2), (1, 1, 2), (-1, 1, 2)]
    for (dx, dy, k) in pts_r:
        _px(s, 11 + dx, 10 + dy, roxo[k])
    # cristalzinho extra
    _px(s, 12, 3, roxo[0])
    _px(s, 12, 4, roxo[1])
    _px(s, 2, 12, cian[1])
    _px(s, 2, 13, cian[2])
    # brilhos
    if f == 1:
        for (x, y) in ((4, 3), (10, 7)):
            _px(s, x, y, (255, 255, 255, 255))
        _px(s, 5, 4, (255, 255, 255, 255))
    elif f == 2:
        _px(s, 4, 4, NEVE)
        _px(s, 12, 8, NEVE)
    return s


# ---------------------------------------------------------------- ponte
def t_ponte_gelo():
    s = _novo()
    # tábuas (y 2..7), com 4 px de largura e juntas
    for x in range(16):
        junta = x % 4 == 0
        for y in range(3, 7):
            if junta:
                c = MADEIRA_ESCURA
            elif y == 3:
                c = _mix(MADEIRA, NEVE_SOMBRA, 0.25)
            elif y == 6:
                c = MADEIRA_ESCURA
            else:
                c = MADEIRA if (x + y) % 5 else _mix(MADEIRA, MADEIRA_ESCURA, 0.4)
            _px(s, x, y, c)
        # gelo / neve sobre as tábuas
        _px(s, x, 2, NEVE if x % 4 else NEVE_SOMBRA)
        _px(s, x, 7, _mix(MADEIRA_ESCURA, CONTORNO, 0.5))
    # geada nas tábuas
    for (x, y) in ((2, 3), (6, 3), (7, 3), (13, 3)):
        _px(s, x, y, GELO_CLARO)
    # pregos
    for x in (1, 5, 9, 13):
        _px(s, x, 5, PEDRA_CLARA)
    # sincelos
    for (x, h) in ((2, 2), (6, 1), (10, 3), (14, 1)):
        for i in range(h):
            _px(s, x, 8 + i, GELO_CLARO if i < h - 1 else NEVE)
    return s


def t_gelo_profundo():
    s = _novo()
    rng = random.Random(101)
    _ruido(s, (36, 84, 170), (24, 56, 128), rng, claro=(70, 130, 210), escuro=(18, 40, 100),
           p_claro=0.13, p_escuro=0.16)
    # fraturas
    for (x, y) in ((2, 1), (3, 2), (3, 3), (4, 4), (5, 5), (5, 6), (6, 7)):
        _px(s, x, y, (14, 28, 80))
        _px(s, x + 1, y, (120, 190, 240))
    for (x, y) in ((9, 8), (10, 9), (11, 9), (11, 10), (12, 11), (13, 12), (13, 13), (14, 14)):
        _px(s, x, y, (14, 28, 80))
        _px(s, x - 1, y, (96, 168, 232))
    for (x, y) in ((8, 2), (9, 3), (10, 3), (11, 4)):
        _px(s, x, y, (110, 180, 240))
    # brilhos
    for (x, y) in ((12, 2), (2, 11), (7, 12)):
        _px(s, x, y, GELO_CLARO)
    _px(s, 12, 1, CIANO)
    return s


# ---------------------------------------------------------------- montagem
def gerar():
    lw = lh = T
    pt = t_pilar_topo()
    pc = t_pilar_corpo()
    linhas = [
        ("neve", [t_neve()], 0.18),
        ("solo_congelado", [t_solo_congelado()], 0.18),
        ("bloco_gelo", [t_bloco_gelo()], 0.18),
        ("cristal", [t_cristal(i) for i in (0, 1, 2, 1)], 0.2),
        ("cristal_usado", [t_cristal_usado()], 0.18),
        ("bloco_pedra", [t_bloco_pedra()], 0.18),
        ("pilar_topo_esq", [_metade(pt, True)], 0.18),
        ("pilar_topo_dir", [_metade(pt, False)], 0.18),
        ("pilar_corpo_esq", [_metade(pc, True)], 0.18),
        ("pilar_corpo_dir", [_metade(pc, False)], 0.18),
        ("tijolo_castelo", [t_tijolo_castelo()], 0.18),
        ("espinhos_gelo", [t_espinhos_gelo()], 0.18),
        ("agua_gelida", [t_agua(i) for i in range(3)], 0.18),
        ("estalactite", [t_estalactite()], 0.18),
        ("neve_caverna", [t_neve_caverna()], 0.18),
        ("pedra_caverna", [t_pedra_caverna()], 0.18),
        ("cristal_luminoso", [t_cristal_luminoso(i) for i in range(3)], 0.25),
        ("ponte_gelo", [t_ponte_gelo()], 0.18),
        ("parede_rachada", [t_parede_rachada(0), t_parede_rachada(1)], 0.7),
        ("gelo_profundo", [t_gelo_profundo()], 0.18),
        ("chao_castelo", [t_chao_castelo()], 0.18),
        ("topo_castelo", [t_topo_castelo()], 0.18),
    ]
    folha = nova_folha(4, len(linhas), lw, lh)
    animacoes = {}
    for i, (nome, quadros, dur) in enumerate(linhas):
        for j, q in enumerate(quadros):
            folha.blit(q, (j * lw, i * lh))
        animacoes[nome] = anim(i, len(quadros), dur)
    salvar_folha("blocos/tileset", "tileset.png", folha, lw, lh, animacoes, escala=3)
    print(f"tileset: {len(linhas)} linhas gravadas")


if __name__ == "__main__":
    iniciar_pygame()
    gerar()
