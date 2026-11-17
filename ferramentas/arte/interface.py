"""Gerador dos ícones e do logo da interface (recursos/interface/*.png).

Os ícones são 16x16 reais (o HUD amplia 2x). O logo é pixel art 160x47 ampliada 4x (640x188).

    python ferramentas/arte/interface.py
"""
import math
import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ferramentas.arte.base import (  # noqa: E402
    AZUL, AZUL_ESCURO, AZUL_GLACIAL, CIANO, CONTORNO, GELO, GELO_CLARO, LARANJA, LARANJA_ESCURO,
    NEVE, NEVE_SOMBRA, NOITE, OURO, OURO_ESCURO, PEDRA, PEDRA_CLARA, PEDRA_ESCURA, ROSA,
    ROSA_ESCURO, ROXO, ROXO_GELO, TURQUESA, iniciar_pygame, pygame, salvar_imagem,
)
from ferramentas.arte.inimigos import (  # noqa: E402
    contorno, elipse, esfera, linha, misturar_cor, novo, poli, px, pxs, retangulo,
)
from ferramentas.arte.objetos import FRAG, _coracao_mascara, cristal  # noqa: E402

BRANCO = (255, 255, 255)


def icone_moeda():
    return cristal(0)


def icone_vida():
    s = novo(16, 16)
    _coracao_mascara(s, 8, 6.4, 1.6, ROSA_ESCURO)
    _coracao_mascara(s, 7.7, 6.0, 1.38, ROSA)
    pxs(s, [(4, 4), (5, 3), (4, 5)], BRANCO)
    retangulo(s, 3, 2, 4, 1, GELO_CLARO)                    # geada no topo
    retangulo(s, 9, 2, 4, 1, GELO_CLARO)
    pxs(s, [(2, 4), (13, 4), (12, 9), (3, 8)], CIANO)       # cristais de gelo na borda
    pxs(s, [(7, 13), (8, 13)], ROSA_ESCURO)
    return contorno(s)


def icone_relogio():
    s = novo(16, 16)
    esfera(s, 8, 8.5, 6.6, 6.6, NEVE, BRANCO, GELO_CLARO)
    elipse(s, 8, 8.5, 5.0, 5.0, (226, 244, 255))
    for k in range(12):                                      # marcas
        a = k * math.pi / 6
        px(s, 8 + math.cos(a) * 4.4, 8.5 + math.sin(a) * 4.4, AZUL_GLACIAL)
    linha(s, (8, 8), (8, 4), AZUL_ESCURO)                    # ponteiro grande
    linha(s, (8, 8), (11, 9), AZUL)                          # ponteiro pequeno
    px(s, 8, 8, OURO)
    poli(s, [(6, 0), (8, -1), (10, 0), (8, 2)], CIANO)       # cristal no topo
    pxs(s, [(2, 3), (13, 3)], CIANO)
    return contorno(s)


def seta():
    """Ponteiro de menu: seta em forma de cristal apontando para a direita."""
    s = novo(16, 16)
    poli(s, [(2, 5), (9, 5), (9, 1), (15, 8), (9, 15), (9, 11), (2, 11)], CIANO)
    poli(s, [(2, 5), (9, 5), (9, 1), (15, 8), (9, 8), (2, 8)], (200, 250, 255))
    poli(s, [(2, 8), (9, 8), (15, 8), (9, 15), (9, 11), (2, 11)], TURQUESA)
    pxs(s, [(4, 6), (5, 6), (10, 4)], BRANCO)
    return contorno(s, AZUL_ESCURO)


def icone_fragmento(n, vazio=False):
    s = novo(16, 16)
    v = FRAG[n] if n else FRAG[1]
    pts = {"longo": [(8, 0), (11, 5), (10, 13), (8, 15), (6, 13), (5, 5)],
           "largo": [(8, 1), (13, 6), (11, 12), (8, 14), (5, 12), (3, 6)],
           "duplo": [(8, 0), (10, 5), (13, 8), (10, 11), (8, 15), (6, 11), (3, 8), (6, 5)]}[v["forma"]]
    if vazio:
        poli(s, pts, (30, 46, 96, 200))
        for a, b in zip(pts, pts[1:] + pts[:1]):
            linha(s, a, b, (90, 120, 190))
        pxs(s, [(8, 7), (8, 8), (8, 9)], (90, 120, 190))
        return s
    poli(s, pts, v["base"])
    poli(s, [p for p in pts if p[0] <= 8] + [(8, 8)], v["claro"])
    poli(s, [(8, 4), (pts[1][0], pts[1][1] + 1), (8, 14)], v["escuro"])
    linha(s, (8, 2), (8, 13), v["claro"])
    pxs(s, [(6, 4), (6, 5)], BRANCO)
    return contorno(s, misturar_cor(CONTORNO, v["escuro"], 0.25))


def icone_cadeado():
    s = novo(16, 16)
    pygame.draw.arc(s, PEDRA_CLARA, (4, 1, 8, 10), 0, math.pi, 2)
    retangulo(s, 4, 5, 2, 4, PEDRA_CLARA)
    retangulo(s, 10, 5, 2, 4, PEDRA_ESCURA)
    retangulo(s, 3, 8, 10, 7, OURO)
    retangulo(s, 3, 8, 10, 1, (255, 236, 150))
    retangulo(s, 3, 14, 10, 1, OURO_ESCURO)
    retangulo(s, 12, 9, 1, 5, OURO_ESCURO)
    retangulo(s, 7, 10, 2, 2, CONTORNO)
    px(s, 8, 12, CONTORNO)
    pxs(s, [(2, 3), (13, 2)], CIANO)
    return contorno(s)


def icone_check():
    s = novo(16, 16)
    esfera(s, 8, 8, 6.6, 6.6, TURQUESA, (110, 226, 220), (22, 120, 140))
    linha(s, (4, 8), (7, 11), BRANCO)
    linha(s, (4, 9), (7, 12), BRANCO)
    linha(s, (7, 11), (12, 5), BRANCO)
    linha(s, (7, 12), (12, 6), BRANCO)
    return contorno(s)


# ---------------------------------------------------------------- logo
def _mascara_letra(letra, x0, y0, larg=36, alt=34, esp=10):
    """Máscara (superfície) de uma letra grossa, desenhada em resolução lógica."""
    m = pygame.Surface((160, 47), pygame.SRCALPHA)
    c = BRANCO
    if letra == "T":
        retangulo(m, x0, y0, larg, esp, c)
        retangulo(m, x0 + larg // 2 - esp // 2 - 1, y0, esp + 2, alt, c)
    elif letra == "U":
        retangulo(m, x0, y0, esp + 1, alt - 6, c)
        retangulo(m, x0 + larg - esp - 1, y0, esp + 1, alt - 6, c)
        elipse(m, x0 + larg / 2, y0 + alt - 15, larg / 2, 15, c)
        elipse(m, x0 + larg / 2, y0 + alt - 15, larg / 2 - esp - 1, 15 - esp - 1, (0, 0, 0, 0))
        retangulo(m, x0 + esp + 1, y0, larg - 2 * esp - 2, alt - 16, (0, 0, 0, 0))
    elif letra == "X":
        poli(m, [(x0, y0), (x0 + esp + 2, y0), (x0 + larg, y0 + alt), (x0 + larg - esp - 2, y0 + alt)], c)
        poli(m, [(x0 + larg, y0), (x0 + larg - esp - 2, y0), (x0, y0 + alt), (x0 + esp + 2, y0 + alt)], c)
    return m


def logo():
    W, H = 160, 47
    s = novo(W, H)
    letras = [("T", 14), ("U", 62), ("X", 110)]
    total = pygame.Surface((W, H), pygame.SRCALPHA)
    for l, x0 in letras:
        total.blit(_mascara_letra(l, x0, 8), (0, 0))
    # sombra projetada
    sombra = novo(W, H)
    for y in range(H - 3):
        for x in range(W - 3):
            if total.get_at((x, y)).a:
                sombra.set_at((x + 3, y + 3), (14, 22, 64, 255))
    s.blit(sombra, (0, 0))
    # preenchimento com degradê vertical (neve → ciano → azul) e bisel
    for y in range(H):
        for x in range(W):
            if not total.get_at((x, y)).a:
                continue
            t = (y - 8) / 34.0
            if t < 0.2:
                cor = misturar_cor(BRANCO, (200, 244, 255), t / 0.2)
            elif t < 0.65:
                cor = misturar_cor((200, 244, 255), CIANO, (t - 0.2) / 0.45)
            else:
                cor = misturar_cor(CIANO, GELO, (t - 0.65) / 0.35)
            # faceta: faixa diagonal mais clara
            if (x + y) % 17 in (0, 1):
                cor = misturar_cor(cor, BRANCO, 0.45)
            # borda interna: luz no topo/esquerda, sombra embaixo/direita
            def vazio(dx, dy):
                xx, yy = x + dx, y + dy
                return not (0 <= xx < W and 0 <= yy < H and total.get_at((xx, yy)).a)
            if vazio(0, -1) or vazio(-1, 0):
                cor = BRANCO
            elif vazio(0, 1) or vazio(1, 0):
                cor = AZUL_GLACIAL
            s.set_at((x, y), cor)
    # contorno escuro
    copia = s.copy()
    for y in range(H):
        for x in range(W):
            if copia.get_at((x, y)).a:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < W and 0 <= yy < H and copia.get_at((xx, yy)).a and \
                        copia.get_at((xx, yy)) != (14, 22, 64, 255):
                    s.set_at((x, y), CONTORNO)
                    break
    # neve acumulada sobre as letras (topo) com gotas
    rng = random.Random(3)
    for l, x0 in letras:
        for x in range(x0 - 1, x0 + 38):
            for y in range(4, 16):
                if s.get_at((x, y)).a and s.get_at((x, y - 1)).a == 0 or (s.get_at((x, y)).a and y == 8):
                    h = 2 + int(2 * math.sin(x * 0.9) + rng.random() * 1.5)
                    for k in range(h):
                        if 0 <= y - k < H:
                            s.set_at((x, y - k), BRANCO)
                    if rng.random() < 0.2:
                        for k in range(1, 3):
                            if s.get_at((x, y + k)).a:
                                s.set_at((x, y + k), NEVE)
                    break
    # estilhaços de cristal nas laterais
    for cx, base, h, cor_c in ((4, 41, 20, CIANO), (9, 43, 13, GELO_CLARO), (152, 41, 18, ROXO_GELO), (147, 43, 12, CIANO)):
        poli(s, [(cx - 3, base), (cx - 2, base - h * 0.6), (cx, base - h), (cx + 3, base - h * 0.6), (cx + 3, base)], cor_c)
        poli(s, [(cx - 3, base), (cx - 2, base - h * 0.6), (cx, base - h), (cx, base)], BRANCO)
        linha(s, (cx + 3, base), (cx + 3, base - h * 0.6), AZUL_GLACIAL)
    # faíscas
    for x, y in ((36, 4), (84, 3), (130, 5), (60, 42), (118, 41), (22, 6), (146, 8)):
        pxs(s, [(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], BRANCO)
    return pygame.transform.scale(s, (W * 4, H * 4))


# ---------------------------------------------------------------- geração
def gerar():
    salvar_imagem("interface/icone_moeda.png", icone_moeda())
    salvar_imagem("interface/icone_vida.png", icone_vida())
    salvar_imagem("interface/icone_relogio.png", icone_relogio())
    salvar_imagem("interface/seta.png", seta())
    for n in (1, 2, 3):
        salvar_imagem(f"interface/icone_fragmento_{n}.png", icone_fragmento(n))
    salvar_imagem("interface/icone_fragmento_vazio.png", icone_fragmento(1, vazio=True))
    salvar_imagem("interface/icone_cadeado.png", icone_cadeado())
    salvar_imagem("interface/icone_check.png", icone_check())
    salvar_imagem("interface/logo.png", logo())
    print("Interface gerada (ícones 16x16 + logo 640x188).")


if __name__ == "__main__":
    iniciar_pygame()
    gerar()
