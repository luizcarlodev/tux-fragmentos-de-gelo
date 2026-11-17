"""Gerador procedural dos personagens: Tux (herói) e a Princesa do Gelo.

Os dois são pinguins desenhados em pixel art 16x22, olhando para a direita, com os
pés na última linha do quadro. O mesmo "molde" de pinguim é usado com estilos
(paletas e acessórios) diferentes para que pareçam um casal.

    python ferramentas/arte/personagens.py
"""
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ferramentas.arte.base import (  # noqa: E402
    CONTORNO, GELO_CLARO, CIANO, LARANJA, LARANJA_ESCURO, NEVE, NEVE_SOMBRA, OURO,
    OURO_ESCURO, PRETO_PINGUIM, PRETO_PINGUIM_CL, ROSA, ROSA_ESCURO, ROXO, ROXO_ESCURO,
    ROXO_GELO, VERMELHO, anim, contornar, desenhar_ascii, iniciar_pygame, nova_folha,
    pixel, pygame, salvar_folha,
)

LW, LH = 16, 22

# ---------------------------------------------------------------- estilos
TUX = dict(
    corpo=PRETO_PINGUIM, claro=PRETO_PINGUIM_CL, barriga=NEVE, barriga_s=NEVE_SOMBRA,
    bico=LARANJA, bico_e=LARANJA_ESCURO, pe=LARANJA, pe_e=LARANJA_ESCURO,
    c1=VERMELHO, c2=LARANJA, c_s=(160, 38, 60), rubor=(232, 112, 124),
    olho=NEVE, pupila=CONTORNO, boca=(120, 34, 56), dy=0, coroa=False, cilios=False,
)
PRINCESA = dict(
    corpo=(118, 140, 226), claro=(170, 188, 248), barriga=NEVE, barriga_s=(212, 226, 252),
    bico=(255, 176, 150), bico_e=(228, 112, 130), pe=(255, 160, 160), pe_e=(228, 112, 130),
    c1=ROXO, c2=ROXO_GELO, c_s=ROXO_ESCURO, rubor=(255, 140, 180),
    olho=NEVE, pupila=(40, 40, 110), boca=(150, 40, 80), dy=1, coroa=True, cilios=True,
)
# Princesa "gelada" (presa): tons mais pálidos e dessaturados
PRESA = dict(
    PRINCESA,
    corpo=(150, 176, 226), claro=(196, 218, 248), barriga=(238, 248, 255),
    barriga_s=(204, 226, 246), bico=(236, 206, 206), bico_e=(196, 160, 180),
    pe=(232, 200, 210), pe_e=(196, 160, 180), c1=(130, 120, 214), c2=(176, 168, 238),
    c_s=(96, 88, 170), rubor=(200, 170, 220),
)

CABECA = [
    ".....PPPPPP.....",
    "....PppPPPPP....",
    "...PPPPPPPPPP...",
    "...PPPPPPPPPP...",
    "...PPPPPPPPPP...",
    "...PPPPPPPPPP...",
    "...PPPPPPPPPOOO.",
    "...PPPPPPPPPoo..",
    "....PPPPPPPPP...",
]
CORPO = [
    "...PPPPPPPPPP...",
    "..PPPPPPWWWPP...",
    "..PPPPPWWWWPP...",
    ".PPPPPWWWWWWP...",
    ".PPPPPWwWWWWP...",
    ".PPPPPWwWWWWP...",
    ".PPPPPWwWWWWP...",
    ".PPPPPPWWWWPP...",
    "..PPPPPPPPPPP...",
    "...PPPPPPPPP....",
]
COROA = [
    ".......N........",
    ".....N.NCN.N....",
    ".....GGGCGGG....",
    "....YYYYYYYY....",
]

# Poses das nadadeiras: ((âncora, ponta) da perto, (âncora, ponta) da longe)
POSES = {
    "baixo": (((6, 11), (5, 16)), ((2, 12), (0, 16))),
    "meio": (((6, 11), (10, 15)), ((2, 12), (0, 15))),
    "frente": (((6, 11), (13, 13)), ((8, 12), (14, 15))),
    "tras": (((6, 11), (1, 14)), ((8, 12), (13, 14))),
    "cima": (((10, 12), (14, 4)), ((3, 12), (0, 5))),
    "aberta": (((10, 12), (14, 9)), ((3, 12), (0, 8))),
    "balanco_a": (((6, 11), (8, 16)), ((2, 12), (0, 15))),
    "balanco_b": (((6, 11), (3, 16)), ((2, 12), (0, 16))),
    "arma": (((7, 11), (2, 6)), ((2, 12), (0, 15))),
    "golpe": (((8, 11), (14, 11)), ((2, 12), (0, 15))),
    "golpe2": (((9, 11), (14, 14)), ((2, 12), (0, 15))),
    "abraco": (((7, 11), (14, 12)), ((9, 12), (14, 15))),
    "cruzada": (((6, 12), (10, 15)), ((8, 12), (12, 15))),
}


def _linha(a, b):
    n = max(abs(b[0] - a[0]), abs(b[1] - a[1]), 1)
    return [(round(a[0] + (b[0] - a[0]) * i / n), round(a[1] + (b[1] - a[1]) * i / n))
            for i in range(n + 1)]


def _nadadeira(s, ox, oy, a, b, cor, contorno=True):
    pts = _linha(a, b)
    horizontal = abs(b[0] - a[0]) > abs(b[1] - a[1])
    conj = set()
    for i, (x, y) in enumerate(pts):
        conj.add((x, y))
        if i < len(pts) - 1:
            conj.add((x, y + 1) if horizontal else (x + 1, y))
    if contorno:
        for (x, y) in list(conj):
            for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + ddx, y + ddy) not in conj:
                    pixel(s, ox, oy, x + ddx, y + ddy, CONTORNO)
    for (x, y) in conj:
        pixel(s, ox, oy, x, y, cor)


def _clarear(s, rect, valor):
    s.fill((valor, valor, valor, 0), rect, special_flags=pygame.BLEND_RGB_ADD)


def _paleta(e):
    return {"P": e["corpo"], "p": e["claro"], "W": e["barriga"], "w": e["barriga_s"],
            "O": e["bico"], "o": e["bico_e"], "N": NEVE, "C": CIANO, "G": GELO_CLARO,
            "Y": OURO}


def _olhos(s, ox, oy, e, hx, topo, tipo):
    """Olhos sobre a cabeça. ``topo`` é a linha absoluta do topo da cabeça."""
    for lado, ex in enumerate((6, 10)):
        x0, y0 = ex + hx, topo + 3

        def p(dx, dy, cor=e["olho"]):
            pixel(s, ox, oy, x0 + dx, y0 + dy, cor)

        if tipo in ("normal", "triste", "zangado"):
            for dx in (0, 1):
                for dy in (0, 1, 2):
                    p(dx, dy)
            p(1, 1, e["pupila"])
            p(1, 2, e["pupila"])
            if tipo == "triste":
                p(1 - lado, 0, e["corpo"])          # sobrancelha caída (cantos externos)
                p(lado, 3, GELO_CLARO)              # lágrima
                p(lado, 4, GELO_CLARO) if lado == 0 else None
        elif tipo == "feliz":
            p(0, 2)
            p(1, 1)
            p(2, 2)
            p(1, 2, e["corpo"])
        elif tipo == "piscar":
            for dx in (0, 1, 2):
                p(dx, 2)
        elif tipo == "x":
            for (dx, dy) in ((0, 0), (2, 0), (1, 1), (0, 2), (2, 2)):
                p(dx, dy)
        elif tipo == "apertado":
            if lado == 0:
                for (dx, dy) in ((0, 0), (1, 1), (0, 2)):
                    p(dx, dy)
            else:
                for (dx, dy) in ((2, 0), (1, 1), (2, 2)):
                    p(dx, dy)
        elif tipo == "surpreso":
            for dx in (0, 1):
                for dy in (-1, 0, 1, 2, 3):
                    p(dx, dy)
            p(1, 1, e["pupila"])
        elif tipo == "feliz_fechado":
            p(0, 2)
            p(1, 1)
            p(2, 2)
        if e["cilios"] and tipo not in ("x",):
            if lado == 0:
                p(-1, 0, CONTORNO)
                p(-1, -1, CONTORNO)
            else:
                p(2, -1, CONTORNO)
                p(2, 0, CONTORNO)


def desenhar_pinguim(s, ox, oy, e, hx=0, hy=0, bx=0, by=0, cy=0, olhos="normal", bico=0,
                     pose="baixo", pe=(0, 0), pd=(0, 0), cauda=("pende", 0), flash=False,
                     rubor=True, extras=None, cintila=0):
    """Desenha um pinguim 16x22 olhando para a direita.

    ``hx/hy`` deslocam só a cabeça, ``bx/by`` o corpo (e cachecol), ``cy`` tudo.
    ``pe``/``pd``: (dx, levantar) dos pés. ``cauda``: (modo, balanço) do cachecol.
    """
    dy = e["dy"] + cy
    topo = 2 + e["dy"] + (1 if e["coroa"] else 0) + hy + cy
    pal = _paleta(e)
    nf, nt = POSES[pose]
    ydy = dy + by

    def deslocar(par, ddx, ddy):
        return ((par[0][0] + ddx, par[0][1] + ddy), (par[1][0] + ddx, par[1][1] + ddy))

    # nadadeira de trás
    t = deslocar(nt, bx, ydy)
    _nadadeira(s, ox, oy, t[0], t[1], e["corpo"], contorno=False)
    # pés
    for (d, lev), x0 in ((pe, 3), (pd, 8)):
        y = 19 + e["dy"] + cy - lev
        desenhar_ascii(s, ox, oy, [".OOO", "OOOO"], pal, x0 + d, y)
        pixel(s, ox, oy, x0 + d + 3, y + 1, e["pe_e"])
    # corpo
    desenhar_ascii(s, ox, oy, CORPO, pal, bx, 9 + ydy)
    # nadadeira da frente
    n = deslocar(nf, bx, ydy)
    _nadadeira(s, ox, oy, n[0], n[1], e["claro"])
    # cabeça
    desenhar_ascii(s, ox, oy, CABECA, pal, hx, topo)
    if bico:
        for dx in (12, 13):
            pixel(s, ox, oy, dx + hx, topo + 7, e["boca"])
            pixel(s, ox, oy, dx + hx, topo + 8, e["bico_e"])
    if rubor:
        for dx in (8, 9):
            pixel(s, ox, oy, dx + hx, topo + 6, e["rubor"])
    _olhos(s, ox, oy, e, hx, topo, olhos)
    # cachecol: faixa no pescoço
    fy = 10 + ydy
    for x in range(2 + bx, 13 + bx):
        pixel(s, ox, oy, x, fy, e["c1"])
        pixel(s, ox, oy, x, fy + 1, e["c_s"])
    for x in (4, 8, 11):
        pixel(s, ox, oy, x + bx, fy, e["c2"])
    pixel(s, ox, oy, 3 + bx, fy + 1, e["c1"])
    # ponta curta na frente
    for i, c in enumerate((e["c1"], e["c2"])):
        pixel(s, ox, oy, 10 + bx, fy + 2 + i, c)
        pixel(s, ox, oy, 11 + bx, fy + 2 + i, e["c_s"])
    # cauda do cachecol (atrás, balança)
    modo, bal = cauda
    cores = [e["c1"], e["c1"], e["c2"], e["c1"], e["c2"]]
    for i in range(5):
        if modo == "voa":
            xx, yy = 3 + bx - i, fy + 1 - (i // 2) + (bal if i >= 2 else 0)
        else:
            xx = 3 + bx - round(i * 0.4) + round(bal * i / 4)
            yy = fy + 1 + i
        for k in (0, 1):
            pixel(s, ox, oy, xx + k, yy, cores[i] if k == 0 else e["c_s"] if i % 2 == 0 else cores[i])
    # coroa de cristal
    if e["coroa"]:
        cp = dict(pal)
        desenhar_ascii(s, ox, oy, COROA, cp, hx, topo - 2)
        if cintila:
            pixel(s, ox, oy, 8 + hx, topo - 3 + 1, NEVE)
            pixel(s, ox, oy, 9 + hx, topo - 2, NEVE)
            pixel(s, ox, oy, 7 + hx, topo - 2, NEVE)
    if extras:
        extras(s, ox, oy)
    contornar(s, (ox, oy, LW, LH))
    if flash:
        _clarear(s, (ox, oy, LW, LH), 110)


# ---------------------------------------------------------------- torpedo (dash)
TORPEDO = [
    ".........PPPP...",
    "......PPPPPPPP..",
    "..PPPPPPPPPEEPP.",
    ".PPPPPPPPPPEePOO",
    ".PPPPPPPPPPPPPOo",
    "..PpppPPPPPPPP..",
    "..PPWWWWWWWWWW..",
    "...WWwwWWWWWW...",
]


def desenhar_torpedo(s, ox, oy, e, f):
    """Pinguim deslizando de barriga (corpo alongado), com rastro de velocidade."""
    pal = _paleta(e)
    desenhar_ascii(s, ox, oy, TORPEDO, pal, 0, 13 + e["dy"])
    y = 13 + e["dy"]
    # pés para trás e cachecol esticado
    pixel(s, ox, oy, 1, y + 3, e["pe"])
    pixel(s, ox, oy, 0, y + 2, e["pe"])
    pixel(s, ox, oy, 1, y + 5, e["pe"])
    pixel(s, ox, oy, 0, y + 5, e["pe_e"])
    # nadadeira junto ao corpo
    for x in range(5, 10):
        pixel(s, ox, oy, x, y + 4, e["claro"])
    # cachecol (faixa no pescoço + ponta voando)
    for k in range(3):
        pixel(s, ox, oy, 9, y + 1 + k, e["c1"])
        pixel(s, ox, oy, 10, y + 1 + k, e["c_s"] if k == 2 else e["c2"] if k == 1 else e["c1"])
    ond = (0, 1)[f % 2]
    for i, c in enumerate((e["c1"], e["c2"], e["c1"], e["c2"])):
        pixel(s, ox, oy, 8 - i, y + ond - (i // 2) + (0 if i < 2 else 0), c)
        pixel(s, ox, oy, 8 - i, y + 1 + ond - (i // 2), e["c_s"])
    if e["cilios"]:
        pixel(s, ox, oy, 10, y + 1, CONTORNO)
    # rubor
    pixel(s, ox, oy, 10, y + 4, e["rubor"])
    contornar(s, (ox, oy, LW, LH))
    # rastro de velocidade e respingos de gelo
    azul = (190, 232, 252)
    traços = [(0, 12, 3), (3, 16, 2), (0, 19, 4)] if f == 0 else [(1, 12, 2), (0, 16, 3), (2, 19, 3)]
    for (x, yy, w) in traços:
        for k in range(w):
            pixel(s, ox, oy, x + k, yy + e["dy"] - 1, NEVE if k else azul)
    pixel(s, ox, oy, 12 + f, 20, NEVE)
    pixel(s, ox, oy, 3 - f, 20, azul)


# ---------------------------------------------------------------- Tux
def _faiscas(pts, cores=(OURO, NEVE)):
    def f(s, ox, oy):
        for i, (x, y) in enumerate(pts):
            pixel(s, ox, oy, x, y, cores[i % len(cores)])
    return f


def _golpe(frame):
    def f(s, ox, oy):
        c1, c2 = (NEVE, GELO_CLARO)
        if frame == 1:
            for (x, y) in ((14, 7), (15, 9)):
                pixel(s, ox, oy, x, y, c1)
        elif frame == 2:
            for (x, y) in ((15, 6), (15, 7), (14, 5), (15, 12), (15, 13), (14, 14)):
                pixel(s, ox, oy, x, y, c1 if (x + y) % 2 else c2)
    return f


def gerar_tux():
    e = TUX
    f = nova_folha(4, 10, LW, LH)

    def q(col, lin, **kw):
        desenhar_pinguim(f, col * LW, lin * LH, e, **kw)

    # 0 parado
    q(0, 0, olhos="normal", pose="baixo", cauda=("pende", 0))
    q(1, 0, olhos="piscar", pose="baixo", by=1, hy=0, cauda=("pende", 1))
    # 1 andando (gingado)
    q(0, 1, pose="balanco_a", pe=(-1, 0), pd=(1, 1), hx=0, cauda=("pende", 1))
    q(1, 1, pose="baixo", pe=(0, 0), pd=(0, 0), hx=-1, by=1, cauda=("pende", 0))
    q(2, 1, pose="balanco_b", pe=(1, 1), pd=(-1, 0), hx=0, cauda=("pende", -1))
    q(3, 1, pose="baixo", pe=(0, 0), pd=(0, 0), hx=-1, by=1, cauda=("pende", 0))
    # 2 correndo
    q(0, 2, pose="tras", pe=(-2, 0), pd=(2, 1), bx=-1, olhos="apertado", cauda=("voa", 0))
    q(1, 2, pose="tras", pe=(0, 1), pd=(0, 0), bx=-1, by=-1, olhos="apertado", cauda=("voa", 1))
    q(2, 2, pose="tras", pe=(2, 1), pd=(-2, 0), bx=-1, olhos="apertado", cauda=("voa", 0))
    q(3, 2, pose="tras", pe=(0, 0), pd=(0, 1), bx=-1, by=-1, olhos="apertado", cauda=("voa", -1))
    # 3 pulando / 4 caindo
    q(0, 3, pose="cima", cy=-1, olhos="feliz", bico=1, pe=(-1, 0), pd=(1, 0), cauda=("voa", 1))
    q(0, 4, pose="aberta", olhos="surpreso", bico=1, pe=(-1, 0), pd=(2, 0), hy=0, cauda=("voa", -1))
    # 5 morrendo
    q(0, 5, pose="cima", olhos="x", bico=1, cy=-1, cauda=("voa", 1),
      extras=_faiscas([(1, 2), (14, 3)], (NEVE, GELO_CLARO)))
    q(1, 5, pose="aberta", olhos="x", bico=1, by=1, hy=1, hx=-1, pe=(-1, 0), pd=(2, 0),
      cauda=("pende", 2))
    # 6 dano
    q(0, 6, pose="aberta", olhos="apertado", bico=1, hx=-1, bx=-1, pe=(-1, 0), pd=(1, 0),
      cauda=("voa", 1), extras=_faiscas([(14, 3), (15, 5), (13, 2)], (OURO, NEVE, LARANJA)))
    q(1, 6, pose="aberta", olhos="apertado", bico=1, hx=-1, bx=-1, pe=(-1, 0), pd=(1, 0),
      cauda=("voa", 0), flash=True)
    # 7 dash
    desenhar_torpedo(f, 0, 7 * LH, e, 0)
    desenhar_torpedo(f, LW, 7 * LH, e, 1)
    # 8 atacando
    q(0, 8, pose="arma", bx=-1, hx=-1, olhos="apertado", cauda=("voa", 0), pe=(-1, 0), pd=(0, 0))
    q(1, 8, pose="golpe", hx=0, bx=0, olhos="apertado", bico=1, cauda=("voa", 1), pe=(-1, 0),
      pd=(2, 0), extras=_golpe(1))
    q(2, 8, pose="golpe", hx=0, bx=0, olhos="apertado", bico=1, cauda=("voa", 0), pe=(-2, 0),
      pd=(2, 0), extras=_golpe(2))
    q(3, 8, pose="golpe2", hx=0, bx=0, olhos="normal", cauda=("pende", 1), pe=(-1, 0),
      pd=(1, 0))
    # 9 vitória
    q(0, 9, pose="baixo", by=1, olhos="feliz", bico=1, cauda=("pende", 1))
    q(1, 9, pose="cima", cy=-1, olhos="feliz", bico=1, cauda=("voa", 1),
      extras=_faiscas([(1, 2), (14, 2), (7, 1)]), pe=(-1, 0), pd=(1, 0))
    q(2, 9, pose="cima", cy=-1, olhos="feliz", bico=1, cauda=("voa", -1), hx=-1,
      extras=_faiscas([(14, 5), (2, 4), (9, 1)], (NEVE, OURO)), pe=(1, 0), pd=(-1, 0))
    q(3, 9, pose="aberta", by=1, olhos="feliz", bico=1, cauda=("pende", -1))

    animacoes = {
        "parado": anim(0, 2, 0.5),
        "andando": anim(1, 4, 0.12),
        "correndo": anim(2, 4, 0.07),
        "pulando": anim(3, 1, 1.0),
        "caindo": anim(4, 1, 1.0),
        "morrendo": anim(5, 2, 0.15),
        "dano": anim(6, 2, 0.08),
        "dash": anim(7, 2, 0.06),
        "atacando": anim(8, 4, 0.07, repetir=False),
        "vitoria": anim(9, 4, 0.15),
    }
    salvar_folha("personagens/tux", "personagem.png", f, LW, LH, animacoes, escala=3,
                 caixa=[34, 58])


# ---------------------------------------------------------------- Princesa
def _coracao(grande):
    def f(s, ox, oy):
        cor = ROSA
        if grande:
            for (x, y) in ((12, 1), (14, 1), (11, 2), (12, 2), (13, 2), (14, 2), (15, 2),
                           (12, 3), (13, 3), (14, 3), (13, 4)):
                pixel(s, ox, oy, x, y, cor)
        else:
            for (x, y) in ((13, 2), (15, 2), (13, 3), (14, 3), (15, 3), (14, 4)):
                pixel(s, ox, oy, x, y, cor)
    return f


def _gelo_fino(pontos):
    def f(s, ox, oy):
        for (x, y) in pontos:
            pixel(s, ox, oy, x, y, NEVE)
        for (x, y) in pontos[::2]:
            pixel(s, ox, oy, x + 1, y, GELO_CLARO)
    return f


def gerar_princesa():
    e = PRINCESA
    f = nova_folha(2, 5, LW, LH)

    def q(col, lin, estilo=e, **kw):
        desenhar_pinguim(f, col * LW, lin * LH, estilo, **kw)

    # 0 parada
    q(0, 0, pose="baixo", olhos="normal", cintila=1, cauda=("pende", 0))
    q(1, 0, pose="baixo", olhos="piscar", by=1, cauda=("pende", 1))
    # 1 feliz (pulinho)
    q(0, 1, pose="meio", olhos="feliz", bico=1, by=1, cauda=("pende", 1), cintila=1)
    q(1, 1, pose="cima", olhos="feliz", bico=1, cy=-1, cauda=("voa", 1),
      extras=_faiscas([(1, 3), (14, 2)], (NEVE, ROSA)), pe=(-1, 0), pd=(1, 0))
    # 2 presa (pálida, assustada)
    gel = _gelo_fino([(4, 15), (5, 17), (11, 14), (3, 13)])
    q(0, 2, PRESA, pose="cruzada", olhos="triste", cauda=("pende", 0), extras=gel)
    q(1, 2, PRESA, pose="cruzada", olhos="triste", hx=-1, bx=0, cauda=("pende", 1),
      extras=gel)
    # 3 livre
    q(0, 3, pose="aberta", olhos="feliz", bico=1, cy=0, cauda=("voa", 1), cintila=1,
      extras=_faiscas([(1, 3), (14, 3), (0, 9)], (NEVE, OURO)))
    # 4 abraçando
    q(0, 4, pose="abraco", olhos="feliz_fechado", bico=0, cauda=("pende", 0),
      extras=_coracao(False))
    q(1, 4, pose="abraco", olhos="feliz_fechado", bico=0, by=1, hx=-1, cauda=("pende", 1),
      extras=_coracao(True))

    animacoes = {
        "parada": anim(0, 2, 0.5),
        "feliz": anim(1, 2, 0.18),
        "presa": anim(2, 2, 0.6),
        "livre": anim(3, 1, 1.0),
        "abracando": anim(4, 2, 0.4),
    }
    salvar_folha("personagens/princesa", "personagem.png", f, LW, LH, animacoes, escala=3,
                 caixa=[34, 58])


def gerar():
    gerar_tux()
    gerar_princesa()
    print("Personagens gerados (tux, princesa).")


if __name__ == "__main__":
    iniciar_pygame()
    gerar()
