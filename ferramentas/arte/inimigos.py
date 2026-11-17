"""Gerador dos inimigos glaciais (recursos/inimigos/*) + helpers de desenho compartilhados.

Criaturas: Criatura de Neve (16x16), Pinguim Selvagem (16x16), Morcego Glacial (16x16) e
Golem de Gelo (24x24). Todos olham para a DIREITA e apoiam os pés na borda inferior.
Os helpers (elipse, esfera, bloco, poli, montar...) também são usados por objetos.py,
efeitos.py, decoracoes.py e interface.py.

    python ferramentas/arte/inimigos.py
"""
import math
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ferramentas.arte.base import (  # noqa: E402
    AZUL, AZUL_ESCURO, AZUL_GLACIAL, CIANO, CONTORNO, GELO, GELO_CLARO, LARANJA,
    LARANJA_ESCURO, MADEIRA, MADEIRA_ESCURA, NEVE, NEVE_SOMBRA, NOITE, OURO, OURO_ESCURO,
    PEDRA, PEDRA_CLARA, PEDRA_ESCURA, ROXO, ROXO_ESCURO, ROXO_GELO, TURQUESA, VERMELHO,
    anim, contornar, iniciar_pygame, nova_folha, pygame, salvar_folha,
)


# ================================================================ helpers de desenho
def novo(w, h):
    """Superfície transparente de um quadro."""
    return pygame.Surface((w, h), pygame.SRCALPHA)


def px(s, x, y, cor):
    x, y = int(x), int(y)
    if 0 <= x < s.get_width() and 0 <= y < s.get_height():
        s.set_at((x, y), cor)


def pxs(s, pontos, cor):
    for x, y in pontos:
        px(s, x, y, cor)


def retangulo(s, x, y, w, h, cor):
    s.fill(cor, (int(x), int(y), int(w), int(h)))


def linha(s, a, b, cor):
    pygame.draw.line(s, cor, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])))


def poli(s, pontos, cor):
    pygame.draw.polygon(s, cor, [(int(x), int(y)) for x, y in pontos])


def elipse(s, cx, cy, rx, ry, cor):
    """Elipse preenchida pixel a pixel (centros de pixel em x+0.5, y+0.5)."""
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                px(s, x, y, cor)


def esfera(s, cx, cy, rx, ry, base, luz, sombra, lim_luz=0.42, lim_sombra=-0.30):
    """Elipse sombreada em 3 tons (luz vindo do alto à esquerda)."""
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if nx * nx + ny * ny <= 1.0:
                d = -0.55 * nx - 0.65 * ny
                px(s, x, y, luz if d > lim_luz else (sombra if d < lim_sombra else base))


def bloco(s, x, y, w, h, base, luz, sombra):
    """Retângulo com bisel (luz em cima/esquerda, sombra embaixo/direita)."""
    retangulo(s, x, y, w, h, base)
    retangulo(s, x, y, w, 1, luz)
    retangulo(s, x, y, 1, h, luz)
    retangulo(s, x, y + h - 1, w, 1, sombra)
    retangulo(s, x + w - 1, y, 1, h, sombra)


def misturar_cor(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def clarear(s, t):
    """Mistura os pixels opacos com branco (efeito de 'flash')."""
    for y in range(s.get_height()):
        for x in range(s.get_width()):
            c = s.get_at((x, y))
            if c.a:
                s.set_at((x, y), (*misturar_cor(c[:3], (255, 255, 255), t), c.a))


def espelhar(s):
    return pygame.transform.flip(s, True, False)


def contorno(s, cor=CONTORNO):
    contornar(s, (0, 0, s.get_width(), s.get_height()), cor)
    return s


def montar(pasta, arquivo, lw, lh, linhas, caixa=None, escala=3):
    """Monta e grava a spritesheet. ``linhas``: [(nome_anim, [quadros], duracao, repetir)]."""
    colunas = max(len(q) for _, q, _, _ in linhas)
    folha = nova_folha(colunas, len(linhas), lw, lh)
    animacoes = {}
    for i, (nome, quadros, dur, repetir) in enumerate(linhas):
        for j, q in enumerate(quadros):
            folha.blit(q, (j * lw, i * lh))
        animacoes[nome] = anim(i, len(quadros), dur, repetir)
    salvar_folha(pasta, arquivo, folha, lw, lh, animacoes, escala=escala, caixa=caixa)


# ================================================================ Criatura de Neve
def _olho_x(s, x, y, cor=CONTORNO):
    pxs(s, [(x, y), (x + 2, y), (x + 1, y + 1), (x, y + 2), (x + 2, y + 2)], cor)


def criatura_de_neve(f=0, esmagado=False):
    s = novo(16, 16)
    if esmagado:
        elipse(s, 8, 12.6, 6.8, 3.0, NEVE_SOMBRA)
        esfera(s, 8, 12.2, 6.5, 2.7, NEVE, NEVE, NEVE_SOMBRA)
        pxs(s, [(2, 11), (1, 10), (13, 11), (14, 10)], MADEIRA)           # galhos achatados
        _olho_x(s, 4, 11)
        _olho_x(s, 9, 11)
        pxs(s, [(5, 8), (10, 8), (6, 8), (9, 8)], CIANO)                   # chifres de gelo caídos
        return contorno(s)
    bob = (0, 1, 0, 1)[f]
    # pés (desenhados antes do corpo)
    esq_alto, dir_alto = f == 0, f == 2
    for x0, alto in ((4, esq_alto), (9, dir_alto)):
        yb = 13 if alto else 14
        retangulo(s, x0, yb, 3, 2, AZUL_GLACIAL)
        retangulo(s, x0, yb, 3, 1, GELO)
    # galhos (braços)
    sw = (-2, 0, 2, 0)[f]
    linha(s, (3, 9 + bob), (1, 8 + bob + sw), MADEIRA)
    linha(s, (12, 9 + bob), (14, 8 + bob - sw), MADEIRA)
    pxs(s, [(1, 7 + bob + sw), (14, 7 + bob - sw)], MADEIRA_ESCURA)
    # corpo de neve compactada
    esfera(s, 8, 8.6 + bob, 5.6, 5.4, NEVE, (255, 255, 255), NEVE_SOMBRA)
    # chifres de gelo
    pxs(s, [(5, 3 + bob), (5, 2 + bob), (10, 3 + bob), (10, 2 + bob)], GELO_CLARO)
    pxs(s, [(5, 1 + bob), (10, 1 + bob)], CIANO)
    # rosto emburrado
    pxs(s, [(4, 5 + bob), (5, 6 + bob), (11, 5 + bob), (10, 6 + bob)], CONTORNO)     # sobrancelhas
    retangulo(s, 5, 7 + bob, 2, 2, CONTORNO)
    retangulo(s, 9, 7 + bob, 2, 2, CONTORNO)
    px(s, 5, 7 + bob, CIANO)
    px(s, 9, 7 + bob, CIANO)
    pxs(s, [(6, 11 + bob), (7, 12 + bob), (8, 11 + bob), (9, 12 + bob)], CONTORNO)   # boca zigue-zague
    pxs(s, [(7, 11 + bob), (9, 11 + bob)], NEVE_SOMBRA)
    return contorno(s)


# ================================================================ Pinguim Selvagem
CINZA = (118, 108, 124)
CINZA_LUZ = (160, 150, 168)
CINZA_SOMBRA = (78, 72, 92)
CREME = (226, 210, 190)
CREME_SOMBRA = (190, 170, 160)
OLHO_RUBI = (255, 70, 60)


def pinguim_selvagem(estado="andando", f=0):
    s = novo(16, 16)
    if estado == "esmagado":
        elipse(s, 8, 12.8, 6.8, 2.8, CINZA_SOMBRA)
        esfera(s, 8, 12.4, 6.4, 2.5, CINZA, CINZA_LUZ, CINZA_SOMBRA)
        elipse(s, 9, 13.3, 3, 1.2, CREME)
        _olho_x(s, 9, 11, VERMELHO)
        pxs(s, [(5, 9), (6, 8), (7, 9)], VERMELHO)                        # crista amassada
        retangulo(s, 12, 12, 3, 1, LARANJA)
        retangulo(s, 1, 14, 2, 1, LARANJA_ESCURO)
        return contorno(s)
    furioso = estado == "furioso"
    lean = 1 if furioso else 0
    bob = 0 if f % 2 == 0 else 1
    if estado == "atordoado":
        lean, bob = -1, 0
    # pés
    ciclo = f % 4
    fx = ((4, 8), (5, 9), (6, 9), (5, 8))[ciclo] if estado != "atordoado" else (4, 9)
    for x0 in fx:
        yb = 15 if (ciclo % 2 == 0 or estado == "atordoado") else 14
        retangulo(s, x0 + lean, yb, 3, 1, LARANJA_ESCURO)
        px(s, x0 + lean + 2, yb - 1 if yb == 15 else yb - 1, LARANJA_ESCURO)
    # asa de trás
    if furioso:
        linha(s, (4 + lean, 8 + bob), (0 + lean, 6 + bob + (f % 2)), CINZA_SOMBRA)
        linha(s, (4 + lean, 9 + bob), (1 + lean, 8 + bob + (f % 2)), CINZA_SOMBRA)
        pxs(s, [(0, 10), (0, 12)], (255, 255, 255, 90))                     # riscos de velocidade
    else:
        retangulo(s, 3 + lean, 8 + bob, 2, 4, CINZA_SOMBRA)
    # corpo
    esfera(s, 8 + lean, 9 + bob, 4.8, 6.0, CINZA, CINZA_LUZ, CINZA_SOMBRA)
    elipse(s, 9.0 + lean, 10.4 + bob, 3.2, 4.4, (236, 240, 248))
    elipse(s, 8.4 + lean, 12.4 + bob, 2.4, 2.4, (206, 214, 232))
    # asa da frente (nadadeira escura)
    linha(s, (7 + lean, 9 + bob), (5 + lean, 12 + bob), CINZA_SOMBRA)
    # penacho amarelo de pinguim-rochedo, varrido para trás
    for i, (x, y) in enumerate([(9, 2), (8, 1), (7, 1), (6, 2), (5, 2), (4, 3), (9, 1), (3, 4)]):
        px(s, x + lean, y + bob, OURO if i % 2 == 0 else LARANJA)
    for x, y in [(8, 2), (7, 2), (6, 3), (5, 3)]:
        px(s, x + lean, y + bob, LARANJA_ESCURO)
    # olho furioso
    ex = 9 + lean
    olho = OLHO_RUBI if (f % 2 == 0 or not furioso) else (255, 190, 90)
    if estado == "atordoado":
        _olho_x(s, ex - 1, 4 + bob, CONTORNO)
    else:
        retangulo(s, ex, 5 + bob, 2, 2, olho)
        px(s, ex + 1, 5 + bob, NEVE)
        pxs(s, [(ex - 1, 3 + bob), (ex, 4 + bob), (ex + 1, 4 + bob), (ex + 2, 5 + bob)], CONTORNO)  # sobrancelha
    px(s, ex - 1, 6 + bob, NEVE)                                           # cicatriz
    px(s, ex - 1, 7 + bob, NEVE)
    # bico
    bx = 11 + lean
    aberto = furioso and f % 2 == 0
    if estado == "atordoado":
        retangulo(s, bx, 7 + bob, 3, 1, LARANJA)
        retangulo(s, bx, 8 + bob, 2, 1, LARANJA_ESCURO)
    else:
        retangulo(s, bx, 6 + bob, 4, 1, LARANJA)
        retangulo(s, bx, 7 + bob, 3 if aberto else 0, 1, CONTORNO)
        retangulo(s, bx, 8 + bob if aberto else 7 + bob, 3, 1, LARANJA_ESCURO)
        if aberto:
            px(s, bx + 1, 7 + bob, NEVE)
    if estado == "atordoado":
        a = (0, 1, 2)
        for i, ang in enumerate((0.0, 2.1, 4.2)):
            ang += 0
            px(s, 8 + int(4 * math.cos(ang)) + lean, 1 + int(1.2 * math.sin(ang)), OURO)
    return contorno(s)


# ================================================================ Morcego Glacial
MORC_CORPO = (96, 82, 170)
MORC_LUZ = (140, 126, 214)
MORC_ASA = (126, 196, 236)
MORC_ASA_OSSO = (60, 80, 170)


def _asa(s, ponta):
    pts = [(5, 6), (0, ponta), (1, ponta + 3), (3, ponta + 2), (4, ponta + 4), (5, 10)]
    poli(s, pts, MORC_ASA)
    linha(s, (5, 7), (0, ponta), MORC_ASA_OSSO)
    linha(s, (5, 8), (3, ponta + 2), MORC_ASA_OSSO)
    px(s, 1, ponta + 1, NEVE)


def morcego_glacial(f=0, esmagado=False):
    s = novo(16, 16)
    if esmagado:
        poli(s, [(1, 13), (4, 10), (8, 12), (12, 10), (15, 13), (13, 15), (3, 15)], MORC_ASA)
        linha(s, (4, 11), (3, 14), MORC_ASA_OSSO)
        linha(s, (11, 11), (12, 14), MORC_ASA_OSSO)
        elipse(s, 8, 12.4, 3, 2.2, MORC_CORPO)
        _olho_x(s, 5, 11, CIANO)
        _olho_x(s, 9, 11, CIANO)
        return contorno(s)
    ponta = (1, 6, 11, 6)[f]
    bob = (0, 1, 2, 1)[f]
    esq = novo(16, 16)
    _asa(esq, ponta)
    s.blit(esq, (0, 0))
    s.blit(espelhar(esq), (0, 0))
    # orelhas
    poli(s, [(5, 2 + bob), (6, 5 + bob), (4, 5 + bob)], MORC_CORPO)
    poli(s, [(10, 2 + bob), (11, 5 + bob), (9, 5 + bob)], MORC_CORPO)
    px(s, 5, 4 + bob, ROXO_GELO)
    px(s, 10, 4 + bob, ROXO_GELO)
    esfera(s, 8, 9.2 + bob, 2.9, 3.6, MORC_CORPO, MORC_LUZ, ROXO_ESCURO)
    esfera(s, 8, 6.4 + bob, 3.0, 2.7, MORC_CORPO, MORC_LUZ, ROXO_ESCURO)
    elipse(s, 8, 10.2 + bob, 1.4, 2.2, (200, 190, 240))                    # peito frio
    # olhos ciano brilhantes e presas
    pxs(s, [(6, 6 + bob), (9, 6 + bob)], (150, 255, 255))
    pxs(s, [(6, 5 + bob), (9, 5 + bob), (7, 5 + bob), (8, 5 + bob)], CONTORNO)   # sobrancelha
    pxs(s, [(6, 6 + bob), (9, 6 + bob)], (150, 255, 255))
    pxs(s, [(7, 8 + bob), (9, 8 + bob)], NEVE)                             # presas
    # pezinhos
    pxs(s, [(7, 13 + bob), (9, 13 + bob)], PEDRA_CLARA)
    return contorno(s)


# ================================================================ Golem de Gelo
G_BASE = (96, 176, 232)
G_LUZ = (182, 232, 252)
G_SOMBRA = (46, 98, 182)
G_ESCURO = (28, 56, 130)


def _gelo_bloco(s, x, y, w, h):
    bloco(s, x, y, w, h, G_BASE, G_LUZ, G_SOMBRA)


def golem_de_gelo(estado="andando", f=0):
    s = novo(24, 24)
    if estado == "esmagado":
        for (x, y, w, h) in [(2, 20, 7, 4), (9, 21, 6, 3), (15, 19, 7, 5), (6, 17, 5, 4), (13, 16, 4, 4)]:
            _gelo_bloco(s, x, y, w, h)
        poli(s, [(4, 16), (6, 12), (8, 16)], G_LUZ)
        poli(s, [(17, 15), (19, 11), (21, 15)], G_BASE)
        pxs(s, [(11, 19), (12, 19)], OURO)                                  # núcleo apagado
        return contorno(s)
    furioso = estado == "furioso"
    dano = estado == "dano"
    bob = (0, 1, 0, 1)[f % 4]
    cicl = f % 4
    perna_e = (0, -1, 0, 0)[cicl] if not furioso else (0, -1, 0, -1)[cicl]
    perna_d = (0, 0, 0, -1)[cicl] if not furioso else (-1, 0, -1, 0)[cicl]
    if dano:
        bob, perna_e, perna_d = 1, 0, 0
    # pernas
    _gelo_bloco(s, 6, 18 + perna_e, 5, 6 - perna_e)
    _gelo_bloco(s, 13, 18 + perna_d, 5, 6 - perna_d)
    # braços
    if furioso:
        up = (0, -1, 0, -1)[cicl]
        _gelo_bloco(s, 0, 3 + up, 4, 9)          # braços erguidos
        _gelo_bloco(s, 20, 3 + up, 4, 9)
        _gelo_bloco(s, -0, 1 + up, 5, 4)
        _gelo_bloco(s, 19, 1 + up, 5, 4)
    else:
        sw = (-1, 0, 1, 0)[cicl]
        _gelo_bloco(s, 0, 10 + bob - sw, 4, 8)
        _gelo_bloco(s, 20, 10 + bob + sw, 4, 8)
        _gelo_bloco(s, 0, 16 + bob - sw, 5, 5)   # punhos
        _gelo_bloco(s, 19, 16 + bob + sw, 5, 5)
    # tronco
    poli(s, [(4, 9 + bob), (19, 9 + bob), (18, 19 + bob), (5, 19 + bob)], G_BASE)
    retangulo(s, 5, 9 + bob, 14, 2, G_LUZ)
    retangulo(s, 4, 11 + bob, 2, 7, G_LUZ)
    retangulo(s, 16, 12 + bob, 3, 7, G_SOMBRA)
    retangulo(s, 5, 18 + bob, 13, 1, G_ESCURO)
    # rachaduras
    linha(s, (8, 12 + bob), (10, 15 + bob), G_ESCURO)
    linha(s, (15, 11 + bob), (14, 14 + bob), G_ESCURO)
    # núcleo
    nucleo = (255, 130, 60) if furioso else OURO
    elipse(s, 12, 14 + bob, 2.3, 2.3, nucleo)
    px(s, 11, 13 + bob, NEVE)
    # ombros de cristal
    poli(s, [(3, 9 + bob), (5, 4 + bob), (7, 9 + bob)], G_LUZ)
    poli(s, [(16, 9 + bob), (18, 4 + bob), (20, 9 + bob)], G_BASE)
    # cabeça
    _gelo_bloco(s, 9, 3 + bob, 7, 6)
    olho = (255, 120, 50) if furioso else (140, 255, 255)
    retangulo(s, 10, 5 + bob, 2, 2, olho)
    retangulo(s, 13, 5 + bob, 2, 2, olho)
    pxs(s, [(10, 4 + bob), (11, 4 + bob), (13, 4 + bob), (14, 4 + bob)], G_ESCURO)
    retangulo(s, 11, 8 + bob, 3, 1, G_ESCURO)
    poli(s, [(11, 3 + bob), (12, 0 + bob), (14, 3 + bob)], G_LUZ)           # cristal na testa
    if dano:
        clarear(s, 0.55)
        linha(s, (7, 10), (12, 17), (255, 255, 255))
        linha(s, (15, 9), (11, 16), (255, 255, 255))
    return contorno(s)


# ================================================================ geração
def gerar():
    montar("inimigos/criatura_de_neve", "inimigo.png", 16, 16, [
        ("andando", [criatura_de_neve(i) for i in range(4)], 0.14, True),
        ("esmagado", [criatura_de_neve(esmagado=True)], 1.0, True)], caixa=(40, 40))
    montar("inimigos/pinguim_selvagem", "inimigo.png", 16, 16, [
        ("andando", [pinguim_selvagem("andando", i) for i in range(4)], 0.14, True),
        ("furioso", [pinguim_selvagem("furioso", i) for i in range(4)], 0.07, True),
        ("atordoado", [pinguim_selvagem("atordoado")], 1.0, True),
        ("esmagado", [pinguim_selvagem("esmagado")], 1.0, True)], caixa=(42, 42))
    montar("inimigos/morcego_glacial", "inimigo.png", 16, 16, [
        ("voando", [morcego_glacial(i) for i in range(4)], 0.10, True),
        ("esmagado", [morcego_glacial(esmagado=True)], 1.0, True)], caixa=(40, 36))
    montar("inimigos/golem_de_gelo", "inimigo.png", 24, 24, [
        ("andando", [golem_de_gelo("andando", i) for i in range(4)], 0.20, True),
        ("furioso", [golem_de_gelo("furioso", i) for i in range(4)], 0.10, True),
        ("dano", [golem_de_gelo("dano")], 1.0, True),
        ("esmagado", [golem_de_gelo("esmagado")], 1.0, True)], caixa=(60, 66))
    print("Inimigos gerados (criatura_de_neve, pinguim_selvagem, morcego_glacial, golem_de_gelo).")


if __name__ == "__main__":
    iniciar_pygame()
    gerar()
