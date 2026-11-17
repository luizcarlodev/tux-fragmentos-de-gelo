"""Gerador dos objetos do jogo (recursos/objetos/*) e do Tux filhote (segredo).

    python ferramentas/arte/objetos.py
"""
import math
import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ferramentas.arte.base import (  # noqa: E402
    AZUL, AZUL_ESCURO, AZUL_GLACIAL, CIANO, CONTORNO, GELO, GELO_CLARO, LARANJA,
    LARANJA_ESCURO, MADEIRA, MADEIRA_ESCURA, NEVE, NEVE_SOMBRA, NOITE, OURO, OURO_ESCURO,
    PEDRA, PEDRA_CLARA, PEDRA_ESCURA, ROSA, ROSA_ESCURO, ROXO, ROXO_ESCURO, ROXO_GELO,
    TURQUESA, VERMELHO, iniciar_pygame, pygame,
)
from ferramentas.arte.inimigos import (  # noqa: E402
    bloco, clarear, contorno, elipse, esfera, espelhar, linha, misturar_cor, montar, novo, poli,
    px, pxs, retangulo,
)

BRILHO = (255, 255, 255)


def _alfa(s, a):
    """Multiplica o alfa de todos os pixels da superfície."""
    for y in range(s.get_height()):
        for x in range(s.get_width()):
            c = s.get_at((x, y))
            if c.a:
                s.set_at((x, y), (c.r, c.g, c.b, int(c.a * a)))
    return s


def _coracao_mascara(s, cx, cy, escala, cor):
    """Desenha um coração (duas elipses + triângulo) centrado em cx, cy."""
    r = 2.6 * escala
    elipse(s, cx - r * 0.85, cy - r * 0.55, r, r * 0.95, cor)
    elipse(s, cx + r * 0.85, cy - r * 0.55, r, r * 0.95, cor)
    poli(s, [(cx - r * 1.85, cy - r * 0.2), (cx + r * 1.85, cy - r * 0.2), (cx, cy + r * 2.0)], cor)


# ================================================================ cristal (moeda)
def cristal(f):
    s = novo(16, 16)
    larg = (5, 3, 1, 3)[f]
    topo, base = 2, 14
    cores = ((CIANO, GELO_CLARO, TURQUESA) if f != 3 else (GELO_CLARO, CIANO, GELO))
    poli(s, [(8, topo), (8 + larg + 1, 8), (8, base), (8 - larg, 8)], cores[0])
    poli(s, [(8, topo), (8, base), (8 - larg, 8)], cores[1])                        # face clara
    poli(s, [(8, 8), (8 + larg + 1, 8), (8, base)], cores[2])                       # face escura
    if larg >= 3:
        linha(s, (8 - larg + 1, 8), (8 + larg, 8), NEVE)                           # aresta central
        px(s, 8 - larg // 2 - 1, 5, BRILHO)
        px(s, 8 - larg // 2, 4, BRILHO)
    pxs(s, [(2, 3 + f % 2), (13, 11 - f % 2)], NEVE)                                  # faíscas
    return contorno(s)


# ================================================================ itens
def coracao_gelo():
    s = novo(16, 16)
    _coracao_mascara(s, 8, 6.2, 1.55, ROSA_ESCURO)
    _coracao_mascara(s, 7.6, 5.8, 1.35, ROSA)
    pxs(s, [(4, 4), (5, 3), (4, 5)], BRILHO)
    pxs(s, [(10, 4), (11, 5)], (255, 220, 235))
    retangulo(s, 3, 2, 3, 1, GELO_CLARO)                                              # geada
    retangulo(s, 10, 2, 3, 1, GELO_CLARO)
    pxs(s, [(7, 13), (8, 13)], ROSA_ESCURO)
    px(s, 12, 3, CIANO)
    return contorno(s)


def cristal_magico(f):
    s = novo(16, 16)
    r = 6 if f == 0 else 5
    poli(s, [(8, 8 - r - 1), (9.5, 6.5), (8 + r + 1, 8), (9.5, 9.5), (8, 8 + r + 1), (6.5, 9.5), (8 - r - 1, 8), (6.5, 6.5)],
         ROXO_GELO)
    poli(s, [(8, 8 - r - 1), (8, 8), (6.5, 6.5)], (205, 190, 255))
    poli(s, [(8, 8), (8 + r + 1, 8), (9.5, 9.5), (8, 8 + r + 1)], ROXO)
    elipse(s, 8, 8, 2.2, 2.2, OURO)
    px(s, 7, 7, BRILHO)
    pxs(s, [(2, 2), (13, 3), (3, 13), (13, 13)] if f == 0 else [(13, 2), (2, 4), (12, 13), (3, 12)], OURO)
    return contorno(s)


# ================================================================ totem (checkpoint)
def totem(aceso, f=0):
    s = novo(16, 32)
    base_c, luz_c, som_c = ((PEDRA, PEDRA_CLARA, PEDRA_ESCURA) if not aceso
                            else (GELO, GELO_CLARO, AZUL_GLACIAL))
    bloco(s, 2, 27, 12, 5, base_c, luz_c, som_c)                                      # base
    bloco(s, 4, 11, 8, 17, base_c, luz_c, som_c)                                      # fuste
    bloco(s, 3, 9, 10, 3, luz_c, NEVE if aceso else luz_c, som_c)                     # capitel
    retangulo(s, 3, 7, 10, 2, NEVE)                                                   # neve
    pxs(s, [(5, 9), (9, 9)], NEVE)
    # rosto de pinguim entalhado
    olho = (120, 255, 255) if aceso else PEDRA_ESCURA
    retangulo(s, 5, 14, 2, 2, olho)
    retangulo(s, 9, 14, 2, 2, olho)
    retangulo(s, 7, 17, 2, 2, LARANJA if aceso else PEDRA_ESCURA)
    retangulo(s, 6, 21, 4, 1, som_c)
    retangulo(s, 6, 23, 4, 1, som_c)
    if aceso:
        # chama de cristal azul no topo
        h = 5 if f == 0 else 6
        poli(s, [(8, 7 - h), (11, 7), (5, 7)], CIANO)
        poli(s, [(8, 7 - h + 2), (10, 7), (6, 7)], (200, 255, 255))
        px(s, 8, 6, BRILHO)
        pxs(s, [(3, 3 + f), (13, 4 - f)], (160, 255, 255))
        # brilho nas runas
        pxs(s, [(5, 25), (10, 25)], CIANO)
    else:
        poli(s, [(8, 3), (10, 7), (6, 7)], PEDRA_ESCURA)
    return contorno(s)


# ================================================================ altar
def altar(ativo, f=0):
    s = novo(32, 32)
    cor = (GELO, GELO_CLARO, AZUL_GLACIAL)
    bloco(s, 2, 26, 28, 6, *cor)
    bloco(s, 5, 21, 22, 6, *cor)
    bloco(s, 8, 15, 16, 7, *cor)
    retangulo(s, 6, 13, 20, 3, NEVE)                                                  # tampo nevado
    retangulo(s, 5, 14, 22, 1, GELO_CLARO)
    for x in (4, 7, 22, 25):
        retangulo(s, x, 28, 2, 2, AZUL_ESCURO)
    runa = (130, 255, 255) if ativo else AZUL
    for x in (11, 15, 19):
        retangulo(s, x, 18, 2, 3, runa)
        px(s, x + 1, 17, runa)
    pxs(s, [(8, 23), (10, 23), (21, 23), (23, 23)], runa)
    if ativo:
        # feixes de luz subindo + brilho
        for i, x in enumerate((9, 13, 17, 21)):
            h = 6 if (i + f) % 2 == 0 else 3
            retangulo(s, x, 12 - h, 1, h, (170, 250, 255))
        pxs(s, [(4 + 20 * f, 9), (27 - 20 * f, 6)], BRILHO)
    return contorno(s)


# ================================================================ fragmentos de gelo
FRAG = {
    1: dict(claro=(214, 250, 255), base=CIANO, escuro=GELO, aura=(120, 230, 255), forma="longo"),
    2: dict(claro=(230, 214, 255), base=ROXO_GELO, escuro=ROXO, aura=(180, 150, 255), forma="largo"),
    3: dict(claro=(255, 250, 220), base=OURO, escuro=OURO_ESCURO, aura=(255, 224, 120), forma="duplo"),
}


def fragmento(n, f):
    v = FRAG[n]
    s = novo(16, 16)
    pulso = (2.6, 3.2, 3.6, 3.2)[f]
    # aura pontilhada
    for y in range(16):
        for x in range(16):
            d = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
            if pulso + 3.2 <= d <= pulso + 4.4 and (x + y + f) % 3 == 0:
                s.set_at((x, y), (*v["aura"], 150))
    if v["forma"] == "longo":
        pts = [(8, 0), (11, 5), (10, 13), (8, 15), (6, 13), (5, 5)]
    elif v["forma"] == "largo":
        pts = [(8, 1), (13, 6), (11, 12), (8, 14), (5, 12), (3, 6)]
    else:
        pts = [(8, 0), (10, 5), (13, 8), (10, 11), (8, 15), (6, 11), (3, 8), (6, 5)]
    poli(s, pts, v["base"])
    metade = [p for p in pts if p[0] <= 8]
    poli(s, [(8, pts[0][1])] + metade + [(8, pts[-1][1] if pts[-1][0] == 8 else 15)][:1] + [(8, 8)], v["claro"])
    # lado escuro
    direita = [(8, 8)] + [p for p in pts if p[0] >= 8][::-1][:0] + [p for p in pts if p[0] > 8]
    poli(s, [(8, 4), (pts[1][0], pts[1][1] + 1), (8, 14)], v["escuro"])
    # facetas e brilho que desliza
    linha(s, (8, 2), (8, 13), v["claro"])
    gx = 6 + f
    px(s, gx, 4 + f, BRILHO)
    px(s, gx, 5 + f, BRILHO)
    # faíscas orbitando
    ang = f * math.pi / 2
    for k in range(3):
        a = ang + k * 2.09
        px(s, 8 + 7 * math.cos(a), 8 + 6.5 * math.sin(a), BRILHO)
    if v["forma"] == "duplo":
        pxs(s, [(8, 7), (8, 9)], BRILHO)
    return contorno(s, misturar_cor(CONTORNO, v["escuro"], 0.25))


# ================================================================ portal
def portal(estado, f=0):
    s = novo(32, 48)
    cx, cy = 16, 25
    # estrutura: arco de pedras de gelo
    for y in range(48):
        for x in range(32):
            dx, dy = (x + 0.5 - cx) / 14.0, (y + 0.5 - cy) / 23.0
            fora = dx * dx + dy * dy <= 1.0 if y < cy else abs(dx) <= 1.0
            if not fora:
                continue
            dxi, dyi = (x + 0.5 - cx) / 9.0, (y + 0.5 - cy) / 18.5
            dentro = (dxi * dxi + dyi * dyi <= 1.0) if y < cy else abs(dxi) <= 1.0
            if dentro:
                continue
            tom = GELO_CLARO if (x * 3 + y) % 11 < 3 else (GELO if (x + y // 3) % 5 else AZUL_GLACIAL)
            if x < 8 and y > 6:
                tom = GELO_CLARO if (y // 4) % 2 else GELO
            s.set_at((x, y), tom)
    for y in range(20, 48, 5):                                    # juntas de pedra
        retangulo(s, 0, y, 7, 1, AZUL)
        retangulo(s, 25, y, 7, 1, AZUL)
    retangulo(s, 0, 44, 32, 4, AZUL_GLACIAL)
    retangulo(s, 0, 44, 32, 1, GELO_CLARO)
    poli(s, [(14, 1), (16, 0), (18, 1), (16, 5)], CIANO)           # cristal no topo
    # interior
    for y in range(48):
        for x in range(32):
            dxi, dyi = (x + 0.5 - cx) / 9.0, (y + 0.5 - cy) / 18.5
            dentro = (dxi * dxi + dyi * dyi <= 1.0) if y < cy else (abs(dxi) <= 1.0 and y < 44)
            if not dentro:
                continue
            if estado == "fechado":
                s.set_at((x, y), (150, 196, 236) if (x + y) % 4 else (200, 230, 250))
            else:
                r = math.hypot(dxi, dyi * 0.7)
                ang = math.atan2(dyi, dxi)
                fase = f * math.pi / 2 if estado == "aberto" else f * math.pi / 3
                t = math.sin(ang * 2 + r * 9 - fase)
                if estado == "abrindo":
                    if r > (0.35 + 0.22 * f):
                        s.set_at((x, y), (150, 196, 236) if (x + y) % 4 else (200, 230, 250))
                        continue
                cor = (misturar_cor(NOITE, ROXO, 0.5 + 0.5 * t) if r > 0.45
                       else misturar_cor(CIANO, NEVE, 0.5 + 0.5 * t))
                if t > 0.82:
                    cor = NEVE
                s.set_at((x, y), cor)
    if estado == "fechado":
        linha(s, (10, 14), (21, 30), NEVE)
        linha(s, (21, 16), (11, 33), NEVE)
    return contorno(s)


# ================================================================ castelo de gelo
def castelo_gelo():
    s = novo(96, 80)
    corpo, luz, som = GELO, GELO_CLARO, AZUL_GLACIAL

    def torre(x, y, w, h, topo_h):
        bloco(s, x, y, w, h, corpo, luz, som)
        for i in range(0, h, 6):
            retangulo(s, x + 1, y + i, w - 2, 1, som)
        retangulo(s, x - 1, y - 2, w + 2, 3, luz)                                 # coroa
        for cx in range(x - 1, x + w, 4):
            retangulo(s, cx, y - 5, 2, 4, luz)                                    # ameias
        poli(s, [(x + w / 2 - 4, y - 5), (x + w / 2, y - 5 - topo_h), (x + w / 2 + 4, y - 5)], CIANO)
        poli(s, [(x + w / 2 - 4, y - 5), (x + w / 2, y - 5 - topo_h), (x + w / 2, y - 5)], (190, 245, 255))
        retangulo(s, x + w // 2 - 1, y + 5, 2, 5, OURO)                           # janela acesa
        px(s, x + w // 2, y + 4, OURO)

    # muralha central
    bloco(s, 18, 40, 60, 40, corpo, luz, som)
    for y in range(44, 80, 6):
        retangulo(s, 19, y, 58, 1, som)
    for x in range(18, 78, 4):
        retangulo(s, x, 35, 2, 5, luz)
        retangulo(s, x + 2, 36, 2, 4, corpo)
    retangulo(s, 18, 38, 60, 2, luz)
    # torres laterais e central
    torre(4, 32, 16, 48, 12)
    torre(76, 32, 16, 48, 12)
    torre(36, 12, 24, 68, 18)
    torre(22, 26, 10, 54, 8)
    torre(64, 26, 10, 54, 8)
    # torre central: janela grande e cristal de coroamento
    elipse(s, 48, 32, 4, 5, (255, 220, 120))
    linha(s, (48, 27), (48, 37), OURO_ESCURO)
    linha(s, (44, 32), (52, 32), OURO_ESCURO)
    # porta no centro da base
    retangulo(s, 40, 58, 16, 22, NOITE)
    elipse(s, 48, 58, 8, 6, NOITE)
    retangulo(s, 40, 58, 16, 22, NOITE)
    for x in range(41, 55, 3):
        retangulo(s, x, 56, 1, 24, AZUL_ESCURO)
    retangulo(s, 38, 74, 20, 6, som)
    retangulo(s, 38, 74, 20, 1, luz)
    # estalactites sobre a porta e neve
    for x in (40, 44, 48, 52):
        poli(s, [(x, 52), (x + 3, 52), (x + 1.5, 58 + (x % 3))], NEVE)
    for x in range(4, 92, 6):
        retangulo(s, x, 38 if 18 < x < 78 else 30, 3, 2, NEVE)
    pxs(s, [(10, 40), (84, 44), (30, 60), (68, 60)], (190, 245, 255))
    return contorno(s)


# ================================================================ plataforma de gelo
def plataforma_gelo():
    s = novo(48, 8)
    retangulo(s, 0, 1, 48, 5, GELO)
    retangulo(s, 0, 0, 48, 2, NEVE)
    retangulo(s, 0, 2, 48, 1, GELO_CLARO)
    retangulo(s, 0, 5, 48, 1, AZUL_GLACIAL)
    for x in range(3, 46, 8):
        retangulo(s, x, 3, 3, 1, GELO_CLARO)
    for x, h in ((4, 2), (13, 1), (22, 2), (33, 1), (41, 2)):
        poli(s, [(x, 6), (x + 3, 6), (x + 1.5, 6 + h)], GELO_CLARO)
    contornar_ = contorno(s)
    return contornar_


# ================================================================ projétil de gelo
def projetil_gelo(f):
    s = novo(8, 8)
    ang = f * math.pi / 4
    c, sn = math.cos(ang), math.sin(ang)
    pts = []
    for (x, y) in [(0, -3.4), (1.1, 0), (0, 3.4), (-1.1, 0)]:
        pts.append((3.5 + x * c - y * sn, 3.5 + x * sn + y * c))
    poli(s, pts, CIANO)
    px(s, 3 + (f % 2), 3, NEVE)
    px(s, 3, 3 + (f % 2), NEVE)
    return contorno(s, AZUL)


# ================================================================ coração do final
def coracao_final(f):
    s = novo(16, 16)
    b = 0 if f == 0 else 1
    _coracao_mascara(s, 8, 6.4 + b, 1.5, ROSA_ESCURO)
    _coracao_mascara(s, 7.8, 6.1 + b, 1.28, ROSA)
    pxs(s, [(4, 4 + b), (5, 3 + b)], BRILHO)
    pxs(s, [(2, 2 + f * 3), (13, 3 + (1 - f) * 3), (8, 14)], (255, 220, 240))
    return contorno(s)


# ================================================================ prisão de gelo (sobre a princesa)
def prisao(estado, f=0):
    s = novo(24, 32)
    claro = (190, 235, 255, 120)
    borda = (235, 250, 255, 210)
    sombra = (96, 160, 230, 150)

    def bloco_translucido(alfa=1.0):
        t = novo(24, 32)
        poli(t, [(3, 31), (1, 8), (4, 3), (8, 1), (16, 1), (20, 3), (23, 8), (21, 31)], claro)
        poli(t, [(3, 31), (1, 8), (4, 3), (6, 4), (5, 31)], borda)
        poli(t, [(19, 31), (21, 8), (20, 3), (18, 4), (19, 31)], sombra)
        retangulo(t, 3, 30, 19, 2, sombra)
        poli(t, [(6, 1), (8, -1), (10, 1)], borda)
        poli(t, [(14, 1), (17, -2), (18, 2)], borda)
        return _alfa(t, alfa)
    if estado == "intacta":
        s.blit(bloco_translucido(), (0, 0))
        pos = 8 + f * 5
        linha(s, (pos, 6), (pos - 4, 20), (255, 255, 255, 190))
        linha(s, (pos + 3, 8), (pos - 1, 22), (255, 255, 255, 120))
        pxs(s, [(5, 5), (18, 12)], BRILHO)
        return s
    if estado == "rachando":
        s.blit(bloco_translucido(), (0, 0))
        rachas = [[(12, 2), (10, 9), (13, 15), (9, 24)], [(10, 9), (4, 12), (3, 18)],
                  [(13, 15), (19, 18), (20, 26)]]
        n = 2 if f == 0 else 3
        for r in rachas[:n]:
            for a, b in zip(r, r[1:]):
                linha(s, a, b, (255, 255, 255, 240))
        px(s, 12 + f, 6, (255, 255, 255))
        return s
    # estilhaçando: cacos voando (4 quadros), esmaecendo
    rng = random.Random(7)
    dist = (3, 7, 11, 14)[f]
    alfa = (230, 200, 150, 90)[f]
    for i in range(14):
        ang = i * 0.45 + rng.random() * 0.3
        cx = 12 + math.cos(ang) * dist * (0.6 + rng.random() * 0.7)
        cy = 16 + math.sin(ang) * dist * 1.1 + f * 2
        tam = 2 + (i % 3)
        poli(s, [(cx, cy - tam), (cx + tam, cy + 1), (cx - 1, cy + tam)], (190, 235, 255, alfa))
        px(s, cx, cy, (255, 255, 255, alfa))
    return s


# ================================================================ chave mágica
def chave_magica(f):
    s = novo(16, 16)
    # argola com os três fragmentos
    elipse(s, 5, 5, 4.4, 4.4, OURO)
    elipse(s, 5, 5, 2.4, 2.4, (0, 0, 0, 0))
    px(s, 5, 2, CIANO); px(s, 3, 6, ROXO_GELO); px(s, 7, 6, (255, 244, 190))
    s.set_at((5, 4), (0, 0, 0, 0)); s.set_at((4, 5), (0, 0, 0, 0)); s.set_at((5, 5), (0, 0, 0, 0)); s.set_at((6, 5), (0, 0, 0, 0))
    retangulo(s, 4, 3, 2, 1, CIANO)
    retangulo(s, 2, 5, 1, 2, ROXO_GELO)
    retangulo(s, 8, 5, 1, 2, (255, 244, 190))
    # haste e dentes
    linha(s, (8, 8), (14, 14), OURO)
    linha(s, (9, 8), (15, 14), OURO_ESCURO)
    retangulo(s, 11, 13, 2, 2, OURO)
    retangulo(s, 13, 11, 2, 2, OURO)
    pxs(s, [(9, 9), (10, 10)], (255, 250, 200))
    off = 0 if f == 0 else 1
    pxs(s, [(1 + off * 11, 1), (14 - off * 3, 3), (2, 13 - off * 2)], BRILHO)
    return contorno(s)


# ================================================================ lembrança (segredo)
def lembranca(f):
    s = novo(16, 16)
    r = (4.4, 5.0, 5.4, 5.0)[f]
    for y in range(16):
        for x in range(16):
            d = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
            if r + 0.6 < d <= r + 2.0 and (x * 2 + y + f) % 3 != 0:
                s.set_at((x, y), (255, 224, 130, 110))
    esfera(s, 8, 8, r, r, OURO, (255, 245, 190), OURO_ESCURO)
    # coração minúsculo no interior
    pxs(s, [(7, 7), (9, 7), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (7, 9), (8, 9), (9, 9), (8, 10)], (255, 255, 255, 230))
    ang = f * math.pi / 2
    for k in range(3):
        a = ang + k * 2.1
        px(s, 8 + 7 * math.cos(a), 8 + 7 * math.sin(a), BRILHO)
    return contorno(s, OURO_ESCURO)


# ================================================================ Tux filhote
BEBE = (150, 156, 176)
BEBE_LUZ = (196, 202, 220)
BEBE_SOMBRA = (104, 110, 136)


def tux_filhote(estado, f=0):
    s = novo(16, 16)
    bob = 1 if (estado == "andando" and f % 2) else 0
    piscar = estado == "parado" and f == 1
    ciclo = f % 4
    for x0, alto in ((4, ciclo == 0), (9, ciclo == 2)):
        yb = 14 if alto and estado == "andando" else 15
        retangulo(s, x0, yb, 3, 1, LARANJA)
    esfera(s, 8, 9.4 + bob, 5.6, 5.8, BEBE, BEBE_LUZ, BEBE_SOMBRA)          # penugem
    elipse(s, 9, 10.8 + bob, 3.4, 3.6, (240, 242, 250))
    retangulo(s, 2, 9 + bob, 2, 3, BEBE_SOMBRA)                              # asinha
    retangulo(s, 12, 9 + bob, 2, 3, BEBE_SOMBRA)
    # olhos grandes
    if piscar:
        retangulo(s, 6, 6 + bob, 2, 1, CONTORNO)
        retangulo(s, 10, 6 + bob, 2, 1, CONTORNO)
    else:
        retangulo(s, 6, 5 + bob, 2, 3, CONTORNO)
        retangulo(s, 10, 5 + bob, 2, 3, CONTORNO)
        pxs(s, [(6, 5 + bob), (10, 5 + bob)], BRILHO)
    retangulo(s, 8, 8 + bob, 3, 1, LARANJA)                                  # biquinho
    retangulo(s, 9, 9 + bob, 2, 1, LARANJA_ESCURO)
    pxs(s, [(7, 2 + bob), (8, 1 + bob), (9, 2 + bob)], BEBE_LUZ)             # tufinho
    pxs(s, [(5, 8 + bob), (12, 8 + bob)], (255, 180, 190))                  # bochechas
    return contorno(s)


# ================================================================ geração
def gerar():
    montar("objetos/cristal", "cristal.png", 16, 16,
           [("girando", [cristal(i) for i in range(4)], 0.10, True)], caixa=(30, 38))
    montar("objetos/coracao_gelo", "coracao_gelo.png", 16, 16,
           [("parado", [coracao_gelo()], 0.12, True)], caixa=(40, 40))
    montar("objetos/cristal_magico", "cristal_magico.png", 16, 16,
           [("brilho", [cristal_magico(0), cristal_magico(1)], 0.12, True)], caixa=(40, 40))
    montar("objetos/totem", "totem.png", 16, 32, [
        ("baixada", [totem(False)], 0.12, True),
        ("levantada", [totem(True, 0), totem(True, 1)], 0.20, True)], caixa=(40, 96))
    montar("objetos/altar", "altar.png", 32, 32, [
        ("parado", [altar(False)], 0.12, True),
        ("ativo", [altar(True, 0), altar(True, 1)], 0.20, True)])
    montar("objetos/fragmento_de_gelo", "fragmento_de_gelo.png", 16, 16,
           [(f"fragmento_{n}", [fragmento(n, i) for i in range(4)], 0.12, True) for n in (1, 2, 3)],
           caixa=(42, 42))
    montar("objetos/portal", "portal.png", 32, 48, [
        ("fechado", [portal("fechado")], 0.12, True),
        ("abrindo", [portal("abrindo", i) for i in range(4)], 0.12, False),
        ("aberto", [portal("aberto", i) for i in range(4)], 0.12, True)])
    montar("objetos/castelo_gelo", "castelo_gelo.png", 96, 80,
           [("parado", [castelo_gelo()], 0.12, True)])
    montar("objetos/plataforma_gelo", "plataforma_gelo.png", 48, 8,
           [("parada", [plataforma_gelo()], 0.12, True)], caixa=(144, 24))
    montar("objetos/projetil_gelo", "projetil_gelo.png", 8, 8,
           [("girando", [projetil_gelo(i) for i in range(4)], 0.08, True)], caixa=(20, 20))
    montar("objetos/coracao", "coracao.png", 16, 16,
           [("flutuando", [coracao_final(0), coracao_final(1)], 0.30, True)])
    montar("objetos/prisao_de_gelo", "prisao_de_gelo.png", 24, 32, [
        ("intacta", [prisao("intacta", 0), prisao("intacta", 1)], 0.5, True),
        ("rachando", [prisao("rachando", 0), prisao("rachando", 1)], 0.12, True),
        ("estilhacando", [prisao("estilhacando", i) for i in range(4)], 0.08, False)])
    montar("objetos/chave_magica", "chave_magica.png", 16, 16,
           [("brilho", [chave_magica(0), chave_magica(1)], 0.20, True)])
    montar("objetos/lembranca", "lembranca.png", 16, 16,
           [("brilhando", [lembranca(i) for i in range(4)], 0.15, True)], caixa=(40, 40))
    montar("personagens/tux_filhote", "personagem.png", 16, 16, [
        ("parado", [tux_filhote("parado", 0), tux_filhote("parado", 1)], 0.4, True),
        ("andando", [tux_filhote("andando", i) for i in range(4)], 0.12, True)], caixa=(34, 44))
    print("Objetos gerados.")


if __name__ == "__main__":
    iniciar_pygame()
    gerar()
