"""Gerador das decorações de cenário (recursos/cenarios/decoracoes/*).

Cada decoração é uma pasta ``<nome>/<nome>.png`` + ``configuracao.json``. Convenção: a BASE do
sprite encosta na borda inferior (exceto ``estalactite_frente``, ancorada no TOPO).

    python ferramentas/arte/decoracoes.py
"""
import math
import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ferramentas.arte.base import (  # noqa: E402
    AZUL, AZUL_ESCURO, AZUL_GLACIAL, CIANO, CONTORNO, GELO, GELO_CLARO, LARANJA, LARANJA_ESCURO,
    MADEIRA, MADEIRA_ESCURA, NEVE, NEVE_SOMBRA, NOITE, OURO, OURO_ESCURO, PEDRA, PEDRA_CLARA,
    PEDRA_ESCURA, ROSA_ESCURO, ROXO, ROXO_ESCURO, ROXO_GELO, TURQUESA, VERDE_PINHEIRO,
    VERDE_PINHEIRO_ESC, VERMELHO, iniciar_pygame,
)
from ferramentas.arte.inimigos import (  # noqa: E402
    bloco, contorno, elipse, esfera, linha, misturar_cor, montar, novo, poli, px, pxs, retangulo,
)

BRANCO = (255, 255, 255)
CAV_A, CAV_B, CAV_CL, CAV_ES = (74, 70, 128), (50, 48, 98), (104, 104, 164), (34, 32, 72)


def _salvar(nome, lw, lh, quadros, anim_nome="parado", dur=0.12):
    montar(f"cenarios/decoracoes/{nome}", f"{nome}.png", lw, lh,
           [(anim_nome, quadros, dur, True)])


# ---------------------------------------------------------------- pinheiros
def pinheiro(cor, luz, neve, neve_som, tronco, vento=0):
    s = novo(32, 64)
    retangulo(s, 14 + vento // 2, 54, 4, 10, tronco)
    retangulo(s, 14 + vento // 2, 54, 1, 10, misturar_cor(tronco, (255, 255, 255), 0.2))
    tiers = [(44, 59, 15), (34, 49, 13), (24, 39, 11), (14, 29, 9), (4, 19, 6)]
    for i, (y0, y1, hw) in enumerate(reversed(tiers)):
        # i = 0 é o tier do topo; deslocamento pelo vento aumenta com a altura relativa
        pass
    for k, (y0, y1, hw) in enumerate(tiers):
        alto = 4 - k
        ax = 16 + vento * alto // 4
        bx = 16 + vento * (alto - 1) // 4 if alto else ax
        poli(s, [(ax, y0), (16 + hw + vento * max(0, alto - 1) // 4, y1), (16 - hw + vento * max(0, alto - 1) // 4, y1)], cor)
        # lado iluminado (esquerda)
        poli(s, [(ax, y0), (ax, y1), (16 - hw + vento * max(0, alto - 1) // 4, y1)], luz)
        # barra de sombra embaixo
        retangulo(s, 16 - hw + 1 + vento * max(0, alto - 1) // 4, y1 - 1, 2 * hw - 1, 1, misturar_cor(cor, (0, 0, 0), 0.35))
        # neve sobre o galho
        yn = y0 + int((y1 - y0) * 0.62)
        hwn = int(hw * 0.62)
        poli(s, [(ax, y0), (ax + hwn, yn), (ax - hwn, yn)], neve)
        poli(s, [(ax, y0), (ax + hwn, yn), (ax, yn)], neve_som)
        for dx in range(-hwn, hwn + 1, 3):                                  # bordas irregulares
            px(s, ax + dx, yn + (1 if dx % 2 else 0), neve)
        pxs(s, [(ax - hw + 2 + 0, y1 - 2), (ax + hw - 3, y1 - 2)], neve)
    return contorno(s)


def arbusto_nevado():
    s = novo(48, 16)
    for cx, cy, rx, ry in ((11, 10.5, 9.5, 5.8), (36, 11, 9, 5.2), (24, 8.2, 11, 7.2)):
        esfera(s, cx, cy, rx, ry, VERDE_PINHEIRO, (62, 150, 130), VERDE_PINHEIRO_ESC)
    for cx, cy, rx, ry in ((11, 7.2, 7.8, 3.2), (36, 8.4, 7, 2.8), (24, 4.6, 8.5, 3.2)):
        elipse(s, cx, cy, rx, ry, NEVE)
        elipse(s, cx + 1, cy + 1.1, rx * 0.8, ry * 0.5, NEVE_SOMBRA)
    pxs(s, [(8, 11), (14, 12), (22, 10), (30, 11), (38, 12), (42, 10)], ROSA_ESCURO)    # frutinhas
    retangulo(s, 0, 15, 48, 1, NEVE_SOMBRA)
    return contorno(s)


def placa():
    s = novo(16, 16)
    retangulo(s, 7, 6, 2, 10, MADEIRA)
    retangulo(s, 7, 6, 1, 10, MADEIRA_ESCURA)
    bloco(s, 1, 1, 14, 7, MADEIRA, (166, 118, 78), MADEIRA_ESCURA)
    pxs(s, [(4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 3), (9, 5), (10, 4)], (60, 40, 30))  # seta entalhada
    pxs(s, [(10, 4), (11, 4)], (60, 40, 30))
    retangulo(s, 0, 0, 16, 1, NEVE)
    retangulo(s, 1, 1, 6, 1, NEVE)
    pxs(s, [(3, 8), (7, 8), (11, 9)], CIANO)
    pxs(s, [(3, 9), (11, 10)], GELO_CLARO)
    retangulo(s, 5, 15, 6, 1, NEVE_SOMBRA)
    return contorno(s)


def tocha(f):
    s = novo(16, 32)
    bloco(s, 3, 27, 10, 5, GELO, GELO_CLARO, AZUL_GLACIAL)
    bloco(s, 5, 14, 6, 14, GELO, GELO_CLARO, AZUL_GLACIAL)
    bloco(s, 3, 11, 10, 4, GELO_CLARO, NEVE, GELO)
    retangulo(s, 4, 10, 8, 1, PEDRA_ESCURA)
    h = 8 if f == 0 else 10
    poli(s, [(8, 10 - h), (12, 9), (4, 9)], CIANO)
    poli(s, [(8, 10 - h + 3), (10.5, 9), (5.5, 9)], (190, 250, 255))
    poli(s, [(8, 10 - h + 6), (9, 9), (7, 9)], BRANCO)
    pxs(s, [(3 + f * 9, 2), (13 - f * 8, 4)], (160, 255, 255))
    retangulo(s, 5, 15, 6, 1, NEVE)
    return contorno(s)


def estandarte():
    s = novo(16, 32)
    retangulo(s, 0, 0, 16, 2, OURO)
    retangulo(s, 0, 0, 16, 1, (255, 236, 150))
    pxs(s, [(0, 2), (15, 2)], OURO_ESCURO)
    poli(s, [(2, 2), (13, 2), (13, 26), (7.5, 22), (2, 26)], AZUL)
    poli(s, [(2, 2), (7, 2), (7, 22), (2, 26)], AZUL_GLACIAL)
    retangulo(s, 2, 2, 1, 24, OURO)
    retangulo(s, 13, 2, 1, 24, OURO)
    # emblema: floco de gelo
    cx, cy = 8, 11
    for k in range(6):
        ang = k * math.pi / 3
        linha(s, (cx, cy), (cx + math.cos(ang) * 4, cy + math.sin(ang) * 4), NEVE)
        mx, my = cx + math.cos(ang) * 2.5, cy + math.sin(ang) * 2.5
        for da in (-0.8, 0.8):
            linha(s, (mx, my), (mx + math.cos(ang + da) * 1.6, my + math.sin(ang + da) * 1.6), GELO_CLARO)
    px(s, cx, cy, OURO)
    pxs(s, [(4, 27), (7, 24), (10, 27)], CIANO)                                  # pingentes de gelo
    pxs(s, [(4, 28), (10, 28)], GELO_CLARO)
    return contorno(s)


# ---------------------------------------------------------------- cristais e pedras
def _cristal(s, cx, by, w, h, tilt, c_esq, c_dir, c_ponta, luz=None):
    ax = cx + tilt
    poli(s, [(cx - w, by), (cx - w * 0.8, by - h * 0.65), (ax, by - h), (cx + w * 0.8, by - h * 0.65), (cx + w, by)], c_dir)
    poli(s, [(cx - w, by), (cx - w * 0.8, by - h * 0.65), (ax, by - h), (ax - 1, by - h * 0.3), (cx - 1, by)], c_esq)
    poli(s, [(cx - w * 0.8, by - h * 0.65), (ax, by - h), (cx + w * 0.8, by - h * 0.65)], c_ponta)
    if luz:
        linha(s, (cx - w * 0.5, by - 2), (cx - w * 0.55, by - h * 0.6), luz)


def cristal_grande(f):
    s = novo(32, 48)
    elipse(s, 16, 44.5, 13.5, 3.6, PEDRA)
    elipse(s, 14, 43.8, 9, 2.2, PEDRA_CLARA)
    _cristal(s, 8, 44, 5, 22, -3, (96, 190, 240), (40, 140, 200), (170, 232, 255), BRANCO)
    _cristal(s, 24, 44, 5, 20, 3, (170, 150, 245), ROXO, (214, 200, 255), (235, 225, 255))
    _cristal(s, 16, 45, 7, 40, 1, (110, 214, 250), (46, 150, 210), (190, 244, 255), BRANCO)
    pontos = [(11, 9, 5), (20, 14, 8), (9, 20, 14), (23, 6, 18)]
    for i, (x, y, _) in enumerate(pontos):
        if (i + f) % 2 == 0:
            pxs(s, [(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], BRANCO)
    retangulo(s, 14 + f, 10 + f * 3, 1, 8, (255, 255, 255, 200))
    return contorno(s)


def estalagmite():
    s = novo(16, 32)
    poli(s, [(8, 1), (15, 31), (1, 31)], CAV_A)
    poli(s, [(8, 1), (1, 31), (6, 31)], CAV_CL)
    poli(s, [(8, 1), (15, 31), (11, 31)], CAV_B)
    for y in (10, 17, 23):
        retangulo(s, 8 - (y // 4), y, y // 2, 1, CAV_ES)
    poli(s, [(8, 1), (10, 8), (6, 8)], GELO_CLARO)                               # ponta gelada
    pxs(s, [(8, 4), (7, 6)], BRANCO)
    retangulo(s, 0, 30, 16, 2, NEVE_SOMBRA)
    return contorno(s)


def pedra_gelada():
    s = novo(32, 16)
    esfera(s, 16, 10.5, 15.4, 7.2, PEDRA, PEDRA_CLARA, PEDRA_ESCURA)
    elipse(s, 14, 5.4, 11, 3.0, NEVE)
    elipse(s, 17, 6.4, 9, 1.6, NEVE_SOMBRA)
    pxs(s, [(6, 11), (7, 12), (20, 10), (25, 12), (27, 10)], CIANO)               # veios de gelo
    pxs(s, [(8, 11), (24, 11)], GELO_CLARO)
    retangulo(s, 2, 15, 28, 1, NEVE_SOMBRA)
    return contorno(s)


def boneco_de_neve():
    s = novo(16, 32)
    esfera(s, 8, 25, 6.5, 6.5, NEVE, BRANCO, NEVE_SOMBRA)
    esfera(s, 8, 15.5, 5.0, 5.0, NEVE, BRANCO, NEVE_SOMBRA)
    esfera(s, 8, 8.6, 4.0, 4.0, NEVE, BRANCO, NEVE_SOMBRA)
    # braços de galho
    linha(s, (3, 15), (0, 11), MADEIRA)
    linha(s, (13, 15), (15, 18), MADEIRA)
    pxs(s, [(0, 10), (1, 11), (15, 19)], MADEIRA_ESCURA)
    # cartola
    retangulo(s, 4, 3, 9, 1, NOITE)
    retangulo(s, 5, 0, 7, 3, NOITE)
    retangulo(s, 5, 2, 7, 1, VERMELHO)
    # rosto
    pxs(s, [(6, 8), (10, 8)], CONTORNO)
    retangulo(s, 9, 9, 4, 1, LARANJA)
    px(s, 12, 9, LARANJA_ESCURO)
    pxs(s, [(6, 11), (7, 12), (8, 12), (9, 12)], CONTORNO)
    # cachecol
    retangulo(s, 4, 12, 9, 2, VERMELHO)
    retangulo(s, 4, 12, 9, 1, (255, 120, 120))
    retangulo(s, 10, 14, 2, 5, VERMELHO)
    # botões
    pxs(s, [(8, 17), (8, 20), (8, 24), (8, 28)], CONTORNO)
    return contorno(s)


def estatua_pinguim():
    s = novo(16, 32)
    bloco(s, 1, 25, 14, 7, PEDRA, PEDRA_CLARA, PEDRA_ESCURA)
    bloco(s, 3, 22, 10, 4, PEDRA_CLARA, NEVE_SOMBRA, PEDRA)
    # silhueta do pinguim (gelo polido)
    esfera(s, 8, 14.5, 5.2, 8.6, GELO_CLARO, NEVE, GELO)
    elipse(s, 8.6, 16, 3.0, 5.6, NEVE)
    esfera(s, 8, 6.6, 3.6, 3.4, GELO_CLARO, NEVE, GELO)
    poli(s, [(4, 12), (1, 7), (3, 6), (5, 11)], GELO)                            # nadadeira erguida
    poli(s, [(12, 13), (14, 17), (13, 18), (11, 14)], GELO)
    pxs(s, [(6, 6), (10, 6)], CONTORNO)
    retangulo(s, 10, 8, 3, 1, PEDRA_CLARA)
    # cachecol dourado esculpido
    retangulo(s, 4, 10, 9, 1, OURO)
    retangulo(s, 10, 11, 2, 4, OURO_ESCURO)
    # detalhes do pedestal: lua crescente e rachadura sutil
    pxs(s, [(7, 28), (6, 29), (6, 30), (7, 31), (8, 31)], OURO_ESCURO)
    pxs(s, [(12, 26), (12, 27), (11, 28)], PEDRA_ESCURA)
    px(s, 8, 1, BRANCO)
    return contorno(s)


def cristal_luminoso(f):
    s = novo(16, 32)
    # halo pulsante (alfa)
    raio = (7.5, 9.0, 10.5)[f]
    for y in range(32):
        for x in range(16):
            d = math.hypot((x + 0.5 - 8) * 1.2, (y + 0.5 - 17) * 0.55)
            if d <= raio and (x + y) % 2 == 0 and d > 4:
                s.set_at((x, y), (170, 150, 255, 55 + 25 * f))
    claro = misturar_cor((160, 140, 255), (255, 255, 255), 0.15 * f)
    poli(s, [(8, 1), (12, 10), (13, 31), (3, 31), (4, 10)], ROXO)
    poli(s, [(8, 1), (4, 10), (3, 31), (7, 31), (7.5, 8)], claro)
    poli(s, [(8, 1), (12, 10), (13, 31), (10, 31), (9, 8)], ROXO_ESCURO)
    linha(s, (6, 12), (6, 28), (230, 220, 255))
    pxs(s, [(8, 4 + f * 3), (7, 5 + f * 3)], BRANCO)
    poli(s, [(1, 31), (5, 22), (6, 31)], (96, 190, 240))                         # cristalzinho ciano
    poli(s, [(10, 31), (14, 24), (15, 31)], (96, 190, 240))
    return contorno(s)


def pilar_castelo():
    s = novo(16, 64)
    bloco(s, 0, 0, 16, 6, GELO_CLARO, NEVE, GELO)
    retangulo(s, 0, 0, 16, 2, NEVE)
    bloco(s, 3, 6, 10, 52, GELO, GELO_CLARO, AZUL_GLACIAL)
    for x in (6, 9):
        retangulo(s, x, 8, 1, 48, AZUL_GLACIAL)
    for y in (14, 30, 46):
        bloco(s, 2, y, 12, 3, GELO_CLARO, NEVE, GELO)
    bloco(s, 0, 58, 16, 6, GELO_CLARO, NEVE, GELO)
    pxs(s, [(8, 22), (5, 38), (10, 50)], BRANCO)
    return contorno(s)


def estalactite_frente():
    """Ancorada no TOPO do quadro (pendura-se no teto)."""
    s = novo(16, 32)
    poli(s, [(0, 0), (16, 0), (12, 14), (9, 31), (7, 14), (4, 10)], CAV_B)
    poli(s, [(0, 0), (6, 0), (7, 14), (9, 31), (4, 10)], CAV_A)
    poli(s, [(9, 31), (10, 22), (8, 24)], GELO_CLARO)
    retangulo(s, 0, 0, 16, 2, CAV_ES)
    pxs(s, [(5, 5), (6, 10), (10, 6)], GELO)
    pxs(s, [(9, 29), (9, 30)], BRANCO)
    poli(s, [(1, 0), (4, 0), (2, 9)], (84, 80, 150))
    return contorno(s, CAV_ES)


def neve_frente():
    s = novo(48, 16)
    for x in range(48):
        h = int(6 + 2.4 * math.sin(x * 0.28) + 1.6 * math.sin(x * 0.71 + 1))
        for y in range(16 - h, 16):
            t = (y - (16 - h)) / max(1, h)
            cor = BRANCO if t < 0.25 else (NEVE if t < 0.55 else NEVE_SOMBRA)
            s.set_at((x, y), cor)
        s.set_at((x, 16 - h), GELO_CLARO)
    pxs(s, [(7, 10), (19, 9), (33, 11), (41, 9)], CIANO)
    return s


# ---------------------------------------------------------------- geração
def gerar():
    _salvar("pinheiro_nevado", 32, 64, [pinheiro(VERDE_PINHEIRO, (52, 140, 124), NEVE, NEVE_SOMBRA, MADEIRA_ESCURA)])
    _salvar("pinheiro_tempestade", 32, 64,
            [pinheiro((38, 56, 108), (64, 92, 156), (196, 210, 244), (140, 158, 210), (50, 42, 70), vento=3)])
    _salvar("arbusto_nevado", 48, 16, [arbusto_nevado()])
    _salvar("placa_gelo", 16, 16, [placa()])
    _salvar("tocha_gelo", 16, 32, [tocha(0), tocha(1)], "acesa", 0.15)
    _salvar("estandarte_gelo", 16, 32, [estandarte()])
    _salvar("cristal_grande", 32, 48, [cristal_grande(0), cristal_grande(1)], "parado", 0.4)
    _salvar("estalagmite", 16, 32, [estalagmite()])
    _salvar("pedra_gelada", 32, 16, [pedra_gelada()])
    _salvar("boneco_de_neve", 16, 32, [boneco_de_neve()])
    _salvar("estatua_pinguim", 16, 32, [estatua_pinguim()])
    _salvar("cristal_luminoso", 16, 32, [cristal_luminoso(i) for i in range(3)], "brilho", 0.2)
    _salvar("pilar_castelo", 16, 64, [pilar_castelo()])
    _salvar("estalactite_frente", 16, 32, [estalactite_frente()])
    _salvar("neve_frente", 48, 16, [neve_frente()])
    print("Decorações geradas (15).")


if __name__ == "__main__":
    iniciar_pygame()
    gerar()
