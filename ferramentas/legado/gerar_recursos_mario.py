"""Gerador dos recursos provisórios do jogo (sprites PNG, cenários e sons).

Execute uma vez (os arquivos já acompanham o projeto) para recriar tudo:

    python ferramentas/gerar_recursos.py

Os sprites são desenhados em "pixel art" de baixa resolução (16x16, 16x22...)
e gravados em spritesheets PNG. O jogo os amplia (escala 3x) ao carregar.
Para trocar a arte basta substituir os PNGs mantendo o ``configuracao.json``
(ou ajustando-o, caso o tamanho dos quadros mude).
"""
import json
import math
import os
import random
import shutil
import wave
from array import array
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
RECURSOS = RAIZ / "recursos"
ESCALA = 3

# ---------------------------------------------------------------- paleta
TRANSP = (0, 0, 0, 0)
PRETO = (30, 20, 28)
BRANCO = (255, 255, 255)
PELE = (255, 208, 152)
PELE_ESC = (222, 160, 110)
CABELO = (110, 60, 30)
VERMELHO = (214, 44, 44)
VERMELHO_ESC = (150, 24, 34)
VERMELHO_CL = (245, 100, 90)
AZUL = (44, 88, 210)
AZUL_ESC = (28, 56, 150)
MARROM = (104, 60, 34)
AMARELO = (252, 222, 70)
OURO = (240, 180, 30)
OURO_ESC = (176, 112, 20)
VERDE = (60, 170, 70)
VERDE_ESC = (30, 110, 50)
VERDE_CL = (130, 220, 110)
TERRA = (150, 92, 48)
TERRA_ESC = (110, 64, 34)
ROSA = (250, 130, 190)
ROSA_ESC = (200, 80, 140)


# ---------------------------------------------------------------- utilitários
def nova_folha(colunas, linhas, lw, lh):
    return pygame.Surface((colunas * lw, linhas * lh), pygame.SRCALPHA)


def anim(linha, quadros, duracao=0.12, repetir=True, quadro_inicial=0):
    return {"linha": linha, "quadro_inicial": quadro_inicial, "quadros": quadros,
            "duracao_quadro": duracao, "repetir": repetir}


def salvar_folha(pasta, nome_png, folha, lw, lh, animacoes, escala=ESCALA, caixa=None):
    destino = RECURSOS / pasta
    destino.mkdir(parents=True, exist_ok=True)
    pygame.image.save(folha, str(destino / nome_png))
    cfg = {"arquivo": nome_png, "largura_quadro": lw, "altura_quadro": lh,
           "escala": escala, "animacoes": animacoes}
    if caixa:
        cfg["caixa_colisao"] = list(caixa)
    with open(destino / "configuracao.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def ret(s, ox, oy, x, y, w, h, cor):
    s.fill(cor, (ox + x, oy + y, w, h))


def pixel(s, ox, oy, x, y, cor):
    if 0 <= ox + x < s.get_width() and 0 <= oy + y < s.get_height():
        s.set_at((ox + x, oy + y), cor)


def clarear(s, rect, valor):
    s.fill((valor, valor, valor, 0), rect, special_flags=pygame.BLEND_RGB_ADD)


# ---------------------------------------------------------------- herói
def desenhar_heroi(s, ox, oy, pe=(0, 0), pd=(0, 0), be=(0, 0), bd=(0, 0),
                   cab=0, olhos="normal", incl=0, flash=False):
    """Desenha o herói provisório (16x22) olhando para a direita."""
    def r(x, y, w, h, c):
        ret(s, ox, oy, x, y, w, h, c)

    # braço de trás
    r(2 + be[0] + incl, 10 + be[1], 2, 4, VERMELHO_ESC)
    r(2 + be[0] + incl, 13 + be[1], 2, 2, (230, 230, 230))
    # pernas
    for (dx, el), x0, cor in ((pe, 4, AZUL_ESC), (pd, 8, AZUL)):
        r(x0 + dx, 15, 3, 5 - el, cor)
        bx = x0 + dx - 1 if x0 == 4 else x0 + dx
        r(bx, 20 - el, 4, 2, MARROM)
    # tronco
    ix = incl
    r(4 + ix, 9, 8, 6, VERMELHO)
    r(5 + ix, 11, 6, 5, AZUL)
    r(5 + ix, 9, 1, 3, AZUL)
    r(10 + ix, 9, 1, 3, AZUL)
    pixel(s, ox, oy, 6 + ix, 12, AMARELO)
    pixel(s, ox, oy, 9 + ix, 12, AMARELO)
    # braço da frente
    r(12 + bd[0] + incl, 10 + bd[1], 2, 4, VERMELHO)
    r(12 + bd[0] + incl, 13 + bd[1], 2, 2, BRANCO)
    # cabeça
    hx = ix
    r(5 + hx, 4 + cab, 7, 5, PELE)
    r(4 + hx, 4 + cab, 2, 4, CABELO)
    r(4 + hx, 1 + cab, 8, 3, VERMELHO)
    r(5 + hx, 1 + cab, 4, 1, VERMELHO_CL)
    r(9 + hx, 3 + cab, 5, 1, VERMELHO_ESC)
    pixel(s, ox, oy, 12 + hx, 6 + cab, PELE_ESC)
    r(10 + hx, 8 + cab, 2, 1, (176, 70, 60))
    if olhos == "normal":
        r(10 + hx, 5 + cab, 1, 2, PRETO)
    elif olhos == "fechado":
        r(9 + hx, 6 + cab, 2, 1, PRETO)
    elif olhos == "x":
        for (px_, py_) in ((9, 5), (11, 5), (10, 6), (9, 7), (11, 7)):
            pixel(s, ox, oy, px_ + hx, py_ + cab, PRETO)
    if flash:
        clarear(s, (ox, oy, 16, 22), 90)


def gerar_heroi():
    lw, lh = 16, 22
    f = nova_folha(4, 7, lw, lh)
    # linha 0: parado
    desenhar_heroi(f, 0, 0 * lh)
    desenhar_heroi(f, lw, 0 * lh, cab=1, be=(0, 1), bd=(0, 1))
    # linha 1: andando
    poses = [dict(pe=(-1, 0), pd=(1, 0), be=(1, 0), bd=(-1, 0)),
             dict(pe=(0, 0), pd=(0, 2), be=(0, 0), bd=(0, 0)),
             dict(pe=(1, 0), pd=(-1, 0), be=(-1, 0), bd=(1, 0)),
             dict(pe=(0, 2), pd=(0, 0), be=(0, 0), bd=(0, 0))]
    for i, p in enumerate(poses):
        desenhar_heroi(f, i * lw, 1 * lh, **p)
    # linha 2: correndo (inclinado, passadas largas)
    poses = [dict(pe=(-2, 0), pd=(2, 0), be=(2, -1), bd=(-2, 1), incl=1),
             dict(pe=(0, 0), pd=(0, 3), be=(0, 0), bd=(0, 0), incl=1),
             dict(pe=(2, 0), pd=(-2, 0), be=(-2, 1), bd=(2, -1), incl=1),
             dict(pe=(0, 3), pd=(0, 0), be=(0, 0), bd=(0, 0), incl=1)]
    for i, p in enumerate(poses):
        desenhar_heroi(f, i * lw, 2 * lh, **p)
    # linha 3: pulando / 4: caindo
    desenhar_heroi(f, 0, 3 * lh, pe=(-2, 1), pd=(2, 0), be=(-1, 0), bd=(1, -5), incl=1)
    desenhar_heroi(f, 0, 4 * lh, pe=(-1, 0), pd=(1, 1), be=(-1, -3), bd=(1, -3))
    # linha 5: morrendo
    desenhar_heroi(f, 0, 5 * lh, pe=(-1, 0), pd=(1, 0), be=(-1, -6), bd=(1, -6), olhos="x")
    desenhar_heroi(f, lw, 5 * lh, pe=(-2, 0), pd=(2, 1), be=(-2, -5), bd=(2, -5), olhos="x", cab=1)
    # linha 6: dano
    desenhar_heroi(f, 0, 6 * lh, pe=(-1, 0), pd=(1, 0), be=(-2, 0), bd=(2, -2), olhos="fechado", incl=-1)
    desenhar_heroi(f, lw, 6 * lh, pe=(-1, 0), pd=(1, 0), be=(-1, 1), bd=(1, 1), olhos="fechado", incl=-1, flash=True)
    salvar_folha("personagens/jogador", "personagem.png", f, lw, lh, {
        "parado": anim(0, 2, 0.5),
        "andando": anim(1, 4, 0.12),
        "correndo": anim(2, 4, 0.07),
        "pulando": anim(3, 1, 1.0),
        "caindo": anim(4, 1, 1.0),
        "morrendo": anim(5, 2, 0.15),
        "dano": anim(6, 2, 0.08),
    }, caixa=(34, 58))


# ---------------------------------------------------------------- princesa
def desenhar_princesa(s, ox, oy, bracos_cima=False, balanco=0):
    def r(x, y, w, h, c):
        ret(s, ox, oy, x, y, w, h, c)
    amarelo_cab = (250, 210, 80)
    r(3, 3, 10, 9, amarelo_cab)             # cabelo
    r(5, 4, 6, 6, PELE)                     # rosto
    r(5, 1, 6, 2, OURO)                     # coroa
    pixel(s, ox, oy, 5, 0, OURO); pixel(s, ox, oy, 8, 0, OURO); pixel(s, ox, oy, 10, 0, OURO)
    pixel(s, ox, oy, 8, 2, (60, 120, 230))
    r(6, 6, 1, 2, PRETO); r(9, 6, 1, 2, PRETO)
    r(7, 9, 2, 1, (200, 80, 80))
    r(5, 11, 6, 3, ROSA)                    # tronco
    # saia
    for i in range(8):
        r(4 - i // 3 + balanco, 14 + i, 8 + 2 * (i // 3), 1, ROSA if i % 2 == 0 else ROSA_ESC)
    r(3 + balanco, 21, 10, 1, ROSA_ESC)
    if bracos_cima:
        r(2, 6, 2, 6, PELE); r(12, 6, 2, 6, PELE)
    else:
        r(3, 11, 2, 4, PELE); r(11, 11, 2, 4, PELE)


def gerar_princesa():
    lw, lh = 16, 22
    f = nova_folha(2, 2, lw, lh)
    desenhar_princesa(f, 0, 0)
    desenhar_princesa(f, lw, 0, balanco=0)
    pixel(f, lw, 0, 8, 3, AMARELO)
    desenhar_princesa(f, 0, lh, bracos_cima=True)
    desenhar_princesa(f, lw, lh, bracos_cima=True, balanco=1)
    salvar_folha("personagens/princesa", "personagem.png", f, lw, lh, {
        "parada": anim(0, 2, 0.6), "feliz": anim(1, 2, 0.2)}, caixa=(34, 58))


# ---------------------------------------------------------------- inimigos
def desenhar_cogumelo(s, ox, oy, passo, esmagado=False):
    def r(x, y, w, h, c):
        ret(s, ox, oy, x, y, w, h, c)
    if esmagado:
        pygame.draw.ellipse(s, (170, 80, 40), (ox + 1, oy + 10, 14, 6))
        r(3, 13, 10, 2, PELE)
        r(4, 12, 2, 1, PRETO); r(10, 12, 2, 1, PRETO)
        return
    pygame.draw.ellipse(s, (170, 80, 40), (ox + 1, oy + 1, 14, 10))
    r(3, 3, 2, 2, (240, 210, 170)); r(10, 3, 3, 2, (240, 210, 170))
    r(4, 9, 8, 4, PELE)
    r(5, 8, 2, 2, BRANCO); r(9, 8, 2, 2, BRANCO)
    pixel(s, ox, oy, 6, 9, PRETO); pixel(s, ox, oy, 9, 9, PRETO)
    r(4, 7, 3, 1, PRETO); r(9, 7, 3, 1, PRETO)
    if passo == 0:
        r(3, 13, 4, 3, PRETO); r(9, 13, 4, 2, PRETO)
    else:
        r(3, 13, 4, 2, PRETO); r(9, 13, 4, 3, PRETO)


def desenhar_voador(s, ox, oy, asa):
    def r(x, y, w, h, c):
        ret(s, ox, oy, x, y, w, h, c)
    corpo = (130, 50, 160)
    # asas (0 = cima, 1 = meio, 2 = baixo)
    ay = {0: 1, 1: 5, 2: 9}[asa]
    pygame.draw.polygon(s, (90, 30, 120), [(ox + 5, oy + 8), (ox + 0, oy + ay), (ox + 6, oy + 6)])
    pygame.draw.polygon(s, (90, 30, 120), [(ox + 10, oy + 8), (ox + 15, oy + ay), (ox + 9, oy + 6)])
    pygame.draw.ellipse(s, corpo, (ox + 4, oy + 4, 8, 9))
    r(5, 7, 2, 2, BRANCO); r(9, 7, 2, 2, BRANCO)
    pixel(s, ox, oy, 6, 8, PRETO); pixel(s, ox, oy, 10, 8, PRETO)
    r(7, 10, 2, 2, (250, 220, 90))
    r(5, 3, 1, 2, corpo); r(10, 3, 1, 2, corpo)


def desenhar_perseguidor(s, ox, oy, passo, furioso=False, esmagado=False):
    def r(x, y, w, h, c):
        ret(s, ox, oy, x, y, w, h, c)
    casco = (200, 50, 40) if furioso else (60, 150, 80)
    casco_esc = (130, 20, 30) if furioso else (30, 100, 60)
    if esmagado:
        pygame.draw.ellipse(s, casco, (ox + 1, oy + 9, 14, 7))
        r(11, 12, 4, 3, (240, 210, 100))
        return
    # espinhos
    for sx in (3, 7, 11):
        pygame.draw.polygon(s, BRANCO, [(ox + sx, oy + 6), (ox + sx + 2, oy + 6), (ox + sx + 1, oy + 1)])
    pygame.draw.ellipse(s, casco, (ox + 1, oy + 5, 12, 9))
    pygame.draw.ellipse(s, casco_esc, (ox + 1, oy + 5, 12, 9), 1)
    r(4, 8, 2, 2, casco_esc); r(8, 8, 2, 2, casco_esc)
    r(11, 7, 4, 5, (240, 210, 100))                 # cabeça
    r(13, 8, 1, 2, BRANCO); pixel(s, ox, oy, 13, 9, PRETO)
    r(11, 7, 3, 1, PRETO if furioso else (200, 170, 70))
    if passo == 0:
        r(3, 13, 3, 3, (240, 210, 100)); r(9, 13, 3, 2, (240, 210, 100))
    else:
        r(3, 13, 3, 2, (240, 210, 100)); r(9, 13, 3, 3, (240, 210, 100))


def gerar_inimigos():
    lw = lh = 16
    f = nova_folha(4, 2, lw, lh)
    for i in range(4):
        desenhar_cogumelo(f, i * lw, 0, i % 2)
    desenhar_cogumelo(f, 0, lh, 0, esmagado=True)
    salvar_folha("inimigos/cogumelo", "inimigo.png", f, lw, lh, {
        "andando": anim(0, 4, 0.14), "esmagado": anim(1, 1, 1.0)}, caixa=(40, 40))

    f = nova_folha(4, 2, lw, lh)
    for i, a in enumerate((0, 1, 2, 1)):
        desenhar_voador(f, i * lw, 0, a)
    desenhar_voador(f, 0, lh, 2)
    salvar_folha("inimigos/voador", "inimigo.png", f, lw, lh, {
        "voando": anim(0, 4, 0.1), "esmagado": anim(1, 1, 1.0)}, caixa=(40, 36))

    f = nova_folha(4, 4, lw, lh)
    for i in range(4):
        desenhar_perseguidor(f, i * lw, 0, i % 2)
        desenhar_perseguidor(f, i * lw, lh, i % 2, furioso=True)
    desenhar_perseguidor(f, 0, 2 * lh, 0, esmagado=True)
    desenhar_perseguidor(f, 0, 3 * lh, 0, furioso=True, esmagado=True)
    salvar_folha("inimigos/perseguidor", "inimigo.png", f, lw, lh, {
        "andando": anim(0, 4, 0.14), "furioso": anim(1, 4, 0.07),
        "atordoado": anim(2, 1, 1.0), "esmagado": anim(3, 1, 1.0)}, caixa=(42, 42))


# ---------------------------------------------------------------- tileset
def tile_grama(s, ox, oy):
    ret(s, ox, oy, 0, 0, 16, 16, TERRA)
    for (x, y) in ((3, 8), (10, 11), (6, 13), (13, 7), (1, 12)):
        pixel(s, ox, oy, x, y, TERRA_ESC)
    ret(s, ox, oy, 0, 0, 16, 4, VERDE)
    ret(s, ox, oy, 0, 4, 16, 1, VERDE_ESC)
    for x in (1, 4, 8, 11, 14):
        ret(s, ox, oy, x, 4, 1, 2, VERDE_ESC)
    for x in (2, 7, 12):
        pixel(s, ox, oy, x, 1, VERDE_CL)


def tile_terra(s, ox, oy):
    ret(s, ox, oy, 0, 0, 16, 16, TERRA)
    for (x, y) in ((3, 3), (10, 5), (6, 10), (13, 12), (1, 14), (9, 1)):
        ret(s, ox, oy, x, y, 2, 1, TERRA_ESC)
    for (x, y) in ((5, 6), (12, 9), (2, 11)):
        pixel(s, ox, oy, x, y, (180, 120, 70))


def tile_tijolo(s, ox, oy):
    ret(s, ox, oy, 0, 0, 16, 16, (200, 90, 40))
    for y in (0, 5, 10, 15):
        ret(s, ox, oy, 0, y, 16, 1, (90, 36, 20))
    for y, xs in ((0, (7,)), (5, (3, 11)), (10, (7,))):
        for x in xs:
            ret(s, ox, oy, x, y, 1, 5, (90, 36, 20))
    for y in (1, 6, 11):
        ret(s, ox, oy, 0, y, 16, 1, (230, 130, 70))


GLIFO_INTERROGACAO = ["..###..", ".#...#.", ".....#.", "...##..", "...#...", ".......", "...#..."]


def tile_interrogacao(s, ox, oy, brilho):
    ret(s, ox, oy, 0, 0, 16, 16, (230, 160, 30))
    ret(s, ox, oy, 0, 0, 16, 1, (255, 220, 120))
    ret(s, ox, oy, 0, 0, 1, 16, (255, 220, 120))
    ret(s, ox, oy, 0, 15, 16, 1, (120, 60, 10))
    ret(s, ox, oy, 15, 0, 1, 16, (120, 60, 10))
    for (x, y) in ((2, 2), (13, 2), (2, 13), (13, 13)):
        pixel(s, ox, oy, x, y, (120, 60, 10))
    for j, linha in enumerate(GLIFO_INTERROGACAO):
        for i, c in enumerate(linha):
            if c == "#":
                pixel(s, ox, oy, 4 + i, 3 + j, (120, 60, 10))
                pixel(s, ox, oy, 3 + i, 2 + j, (255, 245, 190))
    if brilho:
        clarear(s, (ox + 1, oy + 1, 14, 14), brilho * 14)


def tile_usado(s, ox, oy):
    ret(s, ox, oy, 0, 0, 16, 16, (150, 110, 70))
    ret(s, ox, oy, 0, 0, 16, 1, (190, 150, 100))
    ret(s, ox, oy, 0, 0, 1, 16, (190, 150, 100))
    ret(s, ox, oy, 0, 15, 16, 1, (80, 50, 30))
    ret(s, ox, oy, 15, 0, 1, 16, (80, 50, 30))
    for (x, y) in ((2, 2), (13, 2), (2, 13), (13, 13)):
        pixel(s, ox, oy, x, y, (80, 50, 30))


def tile_solido(s, ox, oy):
    ret(s, ox, oy, 0, 0, 16, 16, (170, 170, 185))
    ret(s, ox, oy, 0, 0, 16, 2, (225, 225, 235))
    ret(s, ox, oy, 0, 0, 2, 16, (205, 205, 215))
    ret(s, ox, oy, 0, 14, 16, 2, (90, 90, 110))
    ret(s, ox, oy, 14, 0, 2, 16, (110, 110, 130))
    ret(s, ox, oy, 4, 4, 8, 8, (150, 150, 168))
    ret(s, ox, oy, 4, 4, 8, 1, (120, 120, 140))


def tile_tubo(s, ox, oy, topo, esquerda):
    verde, escuro, claro = (50, 180, 70), (20, 100, 40), (150, 235, 130)
    ini, fim = (0, 16) if topo else ((1, 16) if esquerda else (0, 15))
    ret(s, ox, oy, ini, 0, fim - ini, 16, verde)
    if esquerda:
        ret(s, ox, oy, ini, 0, 1, 16, escuro)
        ret(s, ox, oy, ini + 3, 0, 3, 16, claro)
    else:
        ret(s, ox, oy, fim - 1, 0, 1, 16, escuro)
        ret(s, ox, oy, fim - 5, 0, 2, 16, (30, 140, 55))
    if topo:
        ret(s, ox, oy, 0, 0, 16, 1, escuro)
        ret(s, ox, oy, 0, 15, 16, 1, escuro)


def tile_castelo(s, ox, oy):
    ret(s, ox, oy, 0, 0, 16, 16, (96, 80, 120))
    for y in (0, 5, 10, 15):
        ret(s, ox, oy, 0, y, 16, 1, (40, 28, 60))
    for y, xs in ((0, (5, 13)), (5, (1, 9)), (10, (5, 13))):
        for x in xs:
            ret(s, ox, oy, x, y, 1, 5, (40, 28, 60))
    for y in (1, 6, 11):
        ret(s, ox, oy, 0, y, 16, 1, (130, 112, 156))


def tile_espinhos(s, ox, oy):
    for i in range(3):
        x = 1 + i * 5
        pygame.draw.polygon(s, (200, 205, 215), [(ox + x, oy + 15), (ox + x + 5, oy + 15), (ox + x + 2, oy + 5)])
        pygame.draw.line(s, (120, 125, 140), (ox + x + 5, oy + 15), (ox + x + 2, oy + 5))
    ret(s, ox, oy, 0, 15, 16, 1, (80, 80, 95))


def tile_lava(s, ox, oy, fase):
    ret(s, ox, oy, 0, 0, 16, 16, (230, 80, 20))
    for x in range(16):
        onda = int(1.5 * math.sin((x + fase * 5) * 0.8)) + 2
        ret(s, ox, oy, x, 0, 1, onda, (255, 220, 90))
        ret(s, ox, oy, x, onda, 1, 2, (255, 150, 40))
    for (x, y) in ((3, 8), (11, 11), (7, 13)):
        pixel(s, ox, oy, (x + fase * 3) % 16, y, (255, 190, 70))


def gerar_tileset():
    lw = lh = 16
    nomes = ["grama", "terra", "tijolo", "interrogacao", "bloco_usado", "bloco_solido",
             "tubo_topo_esq", "tubo_topo_dir", "tubo_corpo_esq", "tubo_corpo_dir",
             "castelo_tijolo", "espinhos", "lava"]
    f = nova_folha(4, len(nomes), lw, lh)
    anims = {}
    for linha, nome in enumerate(nomes):
        y = linha * lh
        quadros = 1
        if nome == "grama": tile_grama(f, 0, y)
        elif nome == "terra": tile_terra(f, 0, y)
        elif nome == "tijolo": tile_tijolo(f, 0, y)
        elif nome == "interrogacao":
            quadros = 4
            for i, b in enumerate((0, 1, 2, 1)):
                tile_interrogacao(f, i * lw, y, b)
        elif nome == "bloco_usado": tile_usado(f, 0, y)
        elif nome == "bloco_solido": tile_solido(f, 0, y)
        elif nome == "tubo_topo_esq": tile_tubo(f, 0, y, True, True)
        elif nome == "tubo_topo_dir": tile_tubo(f, 0, y, True, False)
        elif nome == "tubo_corpo_esq": tile_tubo(f, 0, y, False, True)
        elif nome == "tubo_corpo_dir": tile_tubo(f, 0, y, False, False)
        elif nome == "castelo_tijolo": tile_castelo(f, 0, y)
        elif nome == "espinhos": tile_espinhos(f, 0, y)
        elif nome == "lava":
            quadros = 3
            for i in range(3):
                tile_lava(f, i * lw, y, i)
        anims[nome] = anim(linha, quadros, 0.18 if nome != "interrogacao" else 0.2)
    salvar_folha("blocos/tileset", "tileset.png", f, lw, lh, anims)


# ---------------------------------------------------------------- objetos
def gerar_objetos():
    lw = lh = 16
    # moeda
    f = nova_folha(4, 1, lw, lh)
    for i, larg in enumerate((10, 7, 3, 7)):
        x = 8 - larg // 2
        pygame.draw.ellipse(f, OURO_ESC, (i * lw + x, 1, larg, 14))
        if larg > 3:
            pygame.draw.ellipse(f, OURO, (i * lw + x + 1, 2, max(larg - 2, 1), 12))
            ret(f, i * lw, 0, 8 - 1, 5, 2, 6, (255, 235, 140))
    salvar_folha("objetos/moeda", "moeda.png", f, lw, lh, {"girando": anim(0, 4, 0.1)}, caixa=(30, 38))

    # cogumelo de vida
    f = nova_folha(1, 1, lw, lh)
    pygame.draw.ellipse(f, (40, 170, 70), (1, 1, 14, 10))
    ret(f, 0, 0, 3, 3, 3, 3, BRANCO); ret(f, 0, 0, 10, 3, 3, 3, BRANCO)
    ret(f, 0, 0, 4, 9, 8, 6, (255, 235, 200))
    ret(f, 0, 0, 6, 10, 1, 2, PRETO); ret(f, 0, 0, 9, 10, 1, 2, PRETO)
    salvar_folha("objetos/cogumelo_vida", "item.png", f, lw, lh, {"parado": anim(0, 1)}, caixa=(40, 40))

    # estrela
    f = nova_folha(2, 1, lw, lh)
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        raio = 7.5 if i % 2 == 0 else 3.2
        pts.append((8 + raio * math.cos(ang), 8.5 + raio * math.sin(ang)))
    for q in range(2):
        pygame.draw.polygon(f, AMARELO if q == 0 else (255, 250, 170), [(x + q * lw, y) for x, y in pts])
        pygame.draw.polygon(f, OURO_ESC, [(x + q * lw, y) for x, y in pts], 1)
        pixel(f, q * lw, 0, 6, 7, PRETO); pixel(f, q * lw, 0, 10, 7, PRETO)
    salvar_folha("objetos/estrela", "item.png", f, lw, lh, {"brilho": anim(0, 2, 0.12)}, caixa=(40, 40))

    # checkpoint (16x32)
    f = nova_folha(3, 2, 16, 32)
    def poste(ox, oy):
        ret(f, ox, oy, 3, 2, 2, 30, (180, 180, 195))
        pygame.draw.circle(f, OURO, (ox + 4, oy + 2), 2)
    poste(0, 0)
    pygame.draw.polygon(f, (120, 120, 140), [(5, 20), (13, 23), (5, 26)])
    for q in range(2):
        poste(16 * (q + 1), 0)
        ond = 1 if q else 0
        pygame.draw.polygon(f, (60, 130, 240), [(16 * (q + 1) + 5, 4), (16 * (q + 1) + 14, 7 + ond), (16 * (q + 1) + 5, 11)])
        pygame.draw.polygon(f, (240, 240, 255), [(16 * (q + 1) + 6, 6), (16 * (q + 1) + 10, 7 + ond), (16 * (q + 1) + 6, 8)])
    salvar_folha("objetos/checkpoint", "checkpoint.png", f, 16, 32, {
        "baixada": anim(0, 1), "levantada": anim(0, 2, 0.2, quadro_inicial=1)}, caixa=(40, 96))

    # mastro final (16x128)
    f = nova_folha(1, 1, 16, 128)
    ret(f, 0, 0, 7, 6, 2, 122, (200, 230, 200))
    ret(f, 0, 0, 8, 6, 1, 122, (110, 170, 120))
    pygame.draw.circle(f, OURO, (8, 4), 4)
    pygame.draw.circle(f, (255, 240, 150), (7, 3), 1)
    ret(f, 0, 0, 4, 124, 8, 4, (110, 110, 130))
    salvar_folha("objetos/mastro_final", "mastro.png", f, 16, 128, {"parado": anim(0, 1)}, caixa=(12, 384))

    # bandeira final
    f = nova_folha(2, 1, 16, 16)
    for q in range(2):
        o = q * 16
        pygame.draw.polygon(f, (40, 190, 90), [(o + 15, 1), (o + 1, 7 + q), (o + 15, 14)])
        pygame.draw.circle(f, BRANCO, (o + 10, 7 + q), 2)
    salvar_folha("objetos/bandeira_final", "bandeira.png", f, 16, 16, {"tremulando": anim(0, 2, 0.25)})

    # plataforma móvel (48x8)
    f = nova_folha(1, 1, 48, 8)
    ret(f, 0, 0, 0, 0, 48, 8, (130, 90, 60))
    ret(f, 0, 0, 0, 0, 48, 2, (200, 160, 110))
    ret(f, 0, 0, 0, 6, 48, 2, (70, 44, 30))
    for x in (4, 16, 28, 40):
        pixel(f, 0, 0, x, 4, (70, 44, 30))
    salvar_folha("objetos/plataforma_movel", "plataforma.png", f, 48, 8, {"parada": anim(0, 1)}, caixa=(144, 24))

    # projétil (8x8)
    f = nova_folha(4, 1, 8, 8)
    for i in range(4):
        pygame.draw.circle(f, (240, 90, 20), (i * 8 + 4, 4), 3)
        pygame.draw.circle(f, (255, 220, 80), (i * 8 + 4, 4), 1)
        ang = i * math.pi / 2
        pixel(f, i * 8, 0, 4 + int(3 * math.cos(ang)), 4 + int(3 * math.sin(ang)), (255, 240, 150))
    salvar_folha("objetos/projetil", "projetil.png", f, 8, 8, {"girando": anim(0, 4, 0.08)}, caixa=(20, 20))

    # coração
    f = nova_folha(2, 1, 16, 16)
    for q in range(2):
        o = q * 16
        pygame.draw.circle(f, (240, 50, 90), (o + 5, 6), 4)
        pygame.draw.circle(f, (240, 50, 90), (o + 11, 6), 4)
        pygame.draw.polygon(f, (240, 50, 90), [(o + 1, 8), (o + 15, 8), (o + 8, 15 - q)])
        pixel(f, o, 0, 4, 4, (255, 170, 190))
    salvar_folha("objetos/coracao", "coracao.png", f, 16, 16, {"flutuando": anim(0, 2, 0.3)})

    # castelo (96x80)
    f = nova_folha(1, 1, 96, 80)
    def tijolos(x, y, w, h, base, linha):
        ret(f, 0, 0, x, y, w, h, base)
        for yy in range(y, y + h, 5):
            ret(f, 0, 0, x, yy, w, 1, linha)
            for xx in range(x + ((yy - y) // 5 % 2) * 4, x + w, 8):
                ret(f, 0, 0, xx, yy, 1, min(5, y + h - yy), linha)
    base, linha = (150, 130, 170), (80, 60, 100)
    tijolos(24, 24, 48, 56, base, linha)           # corpo central
    tijolos(0, 36, 24, 44, base, linha)            # torre esquerda
    tijolos(72, 36, 24, 44, base, linha)           # torre direita
    for x0, y0, larg in ((0, 36, 24), (72, 36, 24), (24, 24, 48)):
        for x in range(x0, x0 + larg, 8):
            ret(f, 0, 0, x, y0 - 5, 5, 5, base)    # ameias
            ret(f, 0, 0, x, y0 - 5, 5, 1, (190, 170, 210))
    ret(f, 0, 0, 47, 4, 2, 15, (200, 200, 210))     # mastro da bandeira
    pygame.draw.polygon(f, (230, 60, 70), [(49, 4), (62, 8), (49, 12)])
    pygame.draw.ellipse(f, (30, 14, 40), (40, 50, 16, 20))   # porta (arco)
    ret(f, 0, 0, 40, 60, 16, 20, (30, 14, 40))
    for (x, y) in ((8, 50), (80, 50), (30, 36), (62, 36)):
        ret(f, 0, 0, x, y, 4, 7, (250, 220, 120))
        ret(f, 0, 0, x + 1, y + 1, 2, 5, (60, 40, 20))
    salvar_folha("objetos/castelo", "castelo.png", f, 96, 80, {"parado": anim(0, 1)})

    # efeitos
    f = nova_folha(1, 1, 8, 8)
    ret(f, 0, 0, 0, 0, 8, 8, (200, 90, 40))
    ret(f, 0, 0, 0, 3, 8, 1, (90, 36, 20))
    ret(f, 0, 0, 3, 0, 1, 4, (90, 36, 20))
    ret(f, 0, 0, 0, 0, 8, 1, (230, 130, 70))
    salvar_folha("efeitos/fragmento", "fragmento.png", f, 8, 8, {"parado": anim(0, 1)})

    f = nova_folha(3, 1, 16, 16)
    for i, rr in enumerate((3, 5, 7)):
        pygame.draw.circle(f, (255, 255, 255), (i * 16 + 8, 8), rr, 2 if i else 0)
        pygame.draw.circle(f, (255, 230, 150), (i * 16 + 8, 8), max(rr - 2, 1), 1)
    salvar_folha("efeitos/nuvem_poeira", "efeito.png", f, 16, 16,
                 {"explosao": anim(0, 3, 0.08, repetir=False)})

    f = nova_folha(4, 1, 16, 16)
    for i in range(4):
        tam = (2, 5, 7, 4)[i]
        pygame.draw.line(f, (255, 255, 200), (i * 16 + 8 - tam, 8), (i * 16 + 8 + tam, 8))
        pygame.draw.line(f, (255, 255, 200), (i * 16 + 8, 8 - tam), (i * 16 + 8, 8 + tam))
    salvar_folha("efeitos/brilho", "efeito.png", f, 16, 16, {"brilho": anim(0, 4, 0.07, repetir=False)})


# ---------------------------------------------------------------- decorações
def gerar_decoracoes():
    # arbusto 48x16
    f = nova_folha(1, 1, 48, 16)
    for cx, rr in ((10, 7), (22, 9), (35, 7)):
        pygame.draw.circle(f, VERDE_ESC, (cx, 16), rr)
    for cx, rr in ((10, 6), (22, 8), (35, 6)):
        pygame.draw.circle(f, VERDE, (cx, 16), rr)
    for (x, y) in ((8, 11), (20, 8), (33, 11), (26, 12)):
        pixel(f, 0, 0, x, y, VERDE_CL)
    salvar_folha("cenarios/decoracoes/arbusto", "arbusto.png", f, 48, 16, {"parado": anim(0, 1)})
    # árvore 32x64
    f = nova_folha(1, 1, 32, 64)
    ret(f, 0, 0, 13, 28, 6, 36, (100, 60, 30)); ret(f, 0, 0, 13, 28, 2, 36, (140, 90, 50))
    for cx, cy, rr in ((16, 14, 13), (8, 24, 9), (24, 24, 9), (16, 28, 8)):
        pygame.draw.circle(f, VERDE_ESC, (cx, cy), rr)
    for cx, cy, rr in ((16, 13, 11), (8, 23, 7), (24, 23, 7), (16, 27, 6)):
        pygame.draw.circle(f, VERDE, (cx, cy), rr)
    for (x, y) in ((12, 8), (20, 14), (6, 21), (22, 22), (15, 24)):
        pixel(f, 0, 0, x, y, VERDE_CL)
    salvar_folha("cenarios/decoracoes/arvore", "arvore.png", f, 32, 64, {"parado": anim(0, 1)})
    # placa 16x16
    f = nova_folha(1, 1, 16, 16)
    ret(f, 0, 0, 7, 8, 2, 8, (100, 60, 30))
    ret(f, 0, 0, 1, 2, 14, 8, (200, 150, 90))
    ret(f, 0, 0, 1, 2, 14, 1, (240, 200, 140))
    ret(f, 0, 0, 3, 5, 8, 2, (90, 50, 20))
    pygame.draw.polygon(f, (90, 50, 20), [(10, 3), (13, 6), (10, 9)])
    salvar_folha("cenarios/decoracoes/placa", "placa.png", f, 16, 16, {"parado": anim(0, 1)})
    # tocha 16x32 (2 quadros)
    f = nova_folha(2, 1, 16, 32)
    for q in range(2):
        o = q * 16
        ret(f, o, 0, 6, 14, 4, 18, (90, 60, 50))
        ret(f, o, 0, 4, 12, 8, 3, (150, 150, 165))
        alt = 9 + q * 2
        pygame.draw.polygon(f, (240, 100, 20), [(o + 4, 12), (o + 12, 12), (o + 8, 12 - alt - 2)])
        pygame.draw.polygon(f, (255, 210, 70), [(o + 6, 12), (o + 10, 12), (o + 8, 12 - alt + 2)])
    salvar_folha("cenarios/decoracoes/tocha", "tocha.png", f, 16, 32, {"acesa": anim(0, 2, 0.15)})
    # estandarte 16x32
    f = nova_folha(1, 1, 16, 32)
    ret(f, 0, 0, 1, 0, 14, 2, (170, 170, 185))
    ret(f, 0, 0, 2, 2, 12, 24, (140, 30, 60))
    pygame.draw.polygon(f, (140, 30, 60), [(2, 26), (14, 26), (8, 31)])
    pygame.draw.circle(f, AMARELO, (8, 12), 3)
    ret(f, 0, 0, 2, 2, 1, 24, (190, 60, 90))
    salvar_folha("cenarios/decoracoes/estandarte", "estandarte.png", f, 16, 32, {"parado": anim(0, 1)})


# ---------------------------------------------------------------- interface
def gerar_interface():
    destino = RECURSOS / "interface"
    destino.mkdir(parents=True, exist_ok=True)
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.circle(s, (240, 50, 90), (5, 6), 4); pygame.draw.circle(s, (240, 50, 90), (11, 6), 4)
    pygame.draw.polygon(s, (240, 50, 90), [(1, 8), (15, 8), (8, 15)])
    pixel(s, 0, 0, 4, 4, (255, 170, 190))
    pygame.image.save(s, str(destino / "icone_vida.png"))
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.ellipse(s, OURO_ESC, (3, 1, 10, 14)); pygame.draw.ellipse(s, OURO, (4, 2, 8, 12))
    ret(s, 0, 0, 7, 5, 2, 6, (255, 235, 140))
    pygame.image.save(s, str(destino / "icone_moeda.png"))
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.circle(s, (240, 240, 245), (8, 8), 7); pygame.draw.circle(s, (40, 40, 60), (8, 8), 7, 1)
    pygame.draw.line(s, (40, 40, 60), (8, 8), (8, 3)); pygame.draw.line(s, (40, 40, 60), (8, 8), (11, 10))
    pygame.image.save(s, str(destino / "icone_relogio.png"))
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.polygon(s, (255, 230, 80), [(2, 2), (14, 8), (2, 14)])
    pygame.draw.polygon(s, (150, 90, 10), [(2, 2), (14, 8), (2, 14)], 2)
    pygame.image.save(s, str(destino / "seta.png"))
    # fonte
    origem = Path(pygame.__file__).parent / "freesansbold.ttf"
    fontes = RECURSOS / "fontes"
    fontes.mkdir(parents=True, exist_ok=True)
    if origem.exists():
        shutil.copy(origem, fontes / "fonte_principal.ttf")


# ---------------------------------------------------------------- cenários
def gerar_cenarios():
    W, H = 1280, 720
    campo = RECURSOS / "cenarios" / "campo"
    castelo = RECURSOS / "cenarios" / "castelo"
    campo.mkdir(parents=True, exist_ok=True)
    castelo.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(7)

    def gradiente(topo, base):
        s = pygame.Surface((W, H))
        for y in range(H):
            t = y / (H - 1)
            pygame.draw.line(s, tuple(int(topo[i] + (base[i] - topo[i]) * t) for i in range(3)), (0, y), (W, y))
        return s

    # céu do campo
    s = gradiente((70, 150, 240), (190, 232, 255))
    for r_, a in ((90, 40), (70, 70), (50, 140)):
        g = pygame.Surface((300, 300), pygame.SRCALPHA)
        pygame.draw.circle(g, (255, 250, 200, a), (150, 150), r_)
        s.blit(g, (1050 - 150, 110 - 150))
    pygame.draw.circle(s, (255, 250, 210), (1050, 110), 36)
    pygame.image.save(s, str(campo / "ceu.png"))

    def nuvem(surf, cx, cy, esc, cor, sombra):
        for dx, dy, rr in ((-34, 6, 22), (-8, -8, 30), (24, 0, 26), (50, 8, 18), (6, 12, 26)):
            pygame.draw.circle(surf, sombra, (cx + int(dx * esc), cy + int(dy * esc) + 4), int(rr * esc))
        for dx, dy, rr in ((-34, 6, 22), (-8, -8, 30), (24, 0, 26), (50, 8, 18), (6, 12, 26)):
            pygame.draw.circle(surf, cor, (cx + int(dx * esc), cy + int(dy * esc)), int(rr * esc))

    s = pygame.Surface((W, H), pygame.SRCALPHA)
    for cx, cy, esc in ((170, 120, 1.0), (470, 210, 0.8), (700, 90, 1.2), (930, 240, 0.7), (1130, 150, 0.9)):
        nuvem(s, cx, cy, esc, (255, 255, 255, 235), (205, 225, 245, 235))
    pygame.image.save(s, str(campo / "nuvens.png"))

    def colinas(cor, cor_luz, base, amp1, f1, amp2, f2, fase, nome, arvores=False):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        for x in range(W):
            y = base + amp1 * math.sin(2 * math.pi * f1 * x / W + fase) + amp2 * math.sin(2 * math.pi * f2 * x / W)
            pygame.draw.line(s, cor, (x, int(y)), (x, H))
            pygame.draw.line(s, cor_luz, (x, int(y)), (x, int(y) + 3))
        pygame.image.save(s, str(campo / nome))

    colinas((130, 200, 175), (160, 225, 195), 470, 55, 2, 18, 5, 0.5, "colinas_longe.png")
    colinas((80, 170, 95), (120, 205, 110), 545, 38, 3, 12, 7, 1.7, "colinas_perto.png")

    # céu do castelo
    s = gradiente((24, 10, 52), (190, 70, 80))
    for _ in range(140):
        x, y = rnd.randrange(W), rnd.randrange(0, 380)
        c = rnd.choice([(255, 255, 255), (255, 240, 180), (200, 210, 255)])
        pygame.draw.rect(s, c, (x, y, 2, 2) if rnd.random() < 0.8 else (x, y, 3, 3))
    pygame.draw.circle(s, (250, 235, 200), (230, 130), 52)
    pygame.draw.circle(s, (225, 205, 175), (212, 118), 10)
    pygame.draw.circle(s, (225, 205, 175), (248, 150), 7)
    pygame.image.save(s, str(castelo / "ceu.png"))

    s = pygame.Surface((W, H), pygame.SRCALPHA)
    for cx, cy, esc in ((260, 190, 1.1), (640, 120, 0.9), (960, 260, 1.2), (1150, 140, 0.7)):
        nuvem(s, cx, cy, esc, (70, 36, 84, 200), (50, 22, 66, 200))
    pygame.image.save(s, str(castelo / "nuvens.png"))

    # muralha ao longe (silhuetas de torres) e pilares
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cor = (56, 28, 70)
    pygame.draw.rect(s, cor, (0, 520, W, H - 520))
    for x0, larg, alt in ((90, 80, 230), (340, 60, 280), (560, 100, 200), (820, 70, 300), (1050, 90, 240)):
        pygame.draw.rect(s, cor, (x0, 600 - alt, larg, alt + 120))
        for x in range(x0, x0 + larg, 20):
            pygame.draw.rect(s, cor, (x, 600 - alt - 14, 12, 14))
        pygame.draw.polygon(s, cor, [(x0 - 6, 600 - alt - 14), (x0 + larg + 6, 600 - alt - 14),
                                      (x0 + larg // 2, 600 - alt - 70)])
        pygame.draw.rect(s, (250, 200, 90), (x0 + larg // 2 - 4, 600 - alt + 30, 8, 14))
    pygame.image.save(s, str(castelo / "muralha_longe.png"))

    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cor, luz = (36, 16, 48), (62, 34, 78)
    for k in range(4):
        x0 = k * 320 + 110
        pygame.draw.rect(s, cor, (x0, 250, 100, H - 250))
        pygame.draw.rect(s, luz, (x0, 250, 10, H - 250))
        pygame.draw.rect(s, cor, (x0 - 14, 230, 128, 28))
        pygame.draw.rect(s, cor, (x0 - 14, 600, 128, 40))
        pygame.draw.rect(s, cor, (x0 + 100, 280, 120, 40))
    pygame.image.save(s, str(castelo / "pilares.png"))


# ---------------------------------------------------------------- sons
TAXA = 22050


def nota_hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def gerar_onda(tipo, freq, dur, vol=0.3, freq_fim=None, ataque=0.005, solta=0.04):
    n = int(TAXA * dur)
    saida = []
    fase = 0.0
    for i in range(n):
        t = i / n
        f = freq if freq_fim is None else freq + (freq_fim - freq) * t
        fase += f / TAXA
        p = fase % 1.0
        if tipo == "quadrada":
            v = 1.0 if p < 0.5 else -1.0
        elif tipo == "pulso":
            v = 1.0 if p < 0.25 else -1.0
        elif tipo == "triangulo":
            v = 4 * abs(p - 0.5) - 1
        elif tipo == "ruido":
            v = random.uniform(-1, 1)
        else:
            v = math.sin(2 * math.pi * p)
        env = 1.0
        seg = i / TAXA
        if seg < ataque:
            env = seg / ataque
        resto = dur - seg
        if resto < solta:
            env = min(env, resto / solta)
        saida.append(v * vol * env)
    return saida


def concatenar(*partes):
    r = []
    for p in partes:
        r.extend(p)
    return r


def salvar_wav(caminho, amostras):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    dados = array("h", [max(-32767, min(32767, int(a * 32767))) for a in amostras])
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TAXA)
        w.writeframes(dados.tobytes())


def gerar_efeitos_sonoros():
    pasta = RECURSOS / "sons" / "efeitos"
    random.seed(3)
    G = gerar_onda
    salvar_wav(pasta / "pulo.wav", G("quadrada", 330, 0.16, 0.22, 700))
    salvar_wav(pasta / "moeda.wav", concatenar(G("quadrada", 988, 0.06, 0.2), G("quadrada", 1319, 0.22, 0.2, solta=0.12)))
    salvar_wav(pasta / "dano.wav", concatenar(G("ruido", 0, 0.08, 0.25), G("quadrada", 420, 0.28, 0.22, 110)))
    salvar_wav(pasta / "derrota.wav", concatenar(*[G("pulso", nota_hz(m), 0.2, 0.22) for m in (72, 71, 70, 69, 64, 60)],
                                                 G("pulso", nota_hz(55), 0.5, 0.22, solta=0.3)))
    salvar_wav(pasta / "selecao.wav", G("quadrada", 660, 0.05, 0.18))
    salvar_wav(pasta / "confirmacao.wav", concatenar(G("quadrada", 660, 0.06, 0.2), G("quadrada", 990, 0.12, 0.2)))
    salvar_wav(pasta / "esmagar.wav", concatenar(G("quadrada", 260, 0.06, 0.25, 120), G("ruido", 0, 0.04, 0.12)))
    salvar_wav(pasta / "bloco_bater.wav", G("triangulo", 150, 0.1, 0.35, 90))
    salvar_wav(pasta / "bloco_quebrar.wav", concatenar(G("ruido", 0, 0.16, 0.3, solta=0.12), G("quadrada", 200, 0.05, 0.12, 80)))
    salvar_wav(pasta / "item_surge.wav", concatenar(*[G("quadrada", nota_hz(m), 0.06, 0.18) for m in (60, 64, 67, 72, 76, 79)]))
    salvar_wav(pasta / "vida_extra.wav", concatenar(*[G("quadrada", nota_hz(m), 0.09, 0.2) for m in (67, 76, 79, 84, 79, 84, 88)]))
    salvar_wav(pasta / "checkpoint.wav", concatenar(*[G("triangulo", nota_hz(m), 0.1, 0.35) for m in (65, 69, 72, 77)]))
    salvar_wav(pasta / "estrela.wav", concatenar(*[G("quadrada", nota_hz(m), 0.05, 0.16) for m in (84, 88, 91, 96, 91, 88, 84, 88, 91, 96)]))
    salvar_wav(pasta / "mastro.wav", G("quadrada", 900, 1.1, 0.2, 200, solta=0.2))
    salvar_wav(pasta / "projetil.wav", G("ruido", 0, 0.12, 0.16, solta=0.1))
    salvar_wav(pasta / "mensagem_erro.wav", concatenar(G("quadrada", 200, 0.1, 0.2), G("quadrada", 150, 0.16, 0.2)))


def compor(acordes, bpm, compassos_por_acorde, seed, oitava=72, tipo_mel="quadrada", vol_mel=0.13,
           vol_baixo=0.18, bateria=True, repeticoes=1, densidade=0.8):
    """Compositor simples: arpejos/melodia sobre uma progressão de acordes + baixo + chimbal."""
    rnd = random.Random(seed)
    colcheia = 60.0 / bpm / 2
    amostras_por = int(TAXA * colcheia)
    total_passos = len(acordes) * compassos_por_acorde * 8 * repeticoes
    saida = [0.0] * (total_passos * amostras_por + TAXA)
    ultima = None

    def misturar(onda, inicio):
        for i, v in enumerate(onda):
            if inicio + i < len(saida):
                saida[inicio + i] += v

    escala_maior = [0, 2, 4, 5, 7, 9, 11]
    passo = 0
    for _rep in range(repeticoes):
        for acorde in acordes:
            raiz, tons = acorde["raiz"], acorde["tons"]
            for _c in range(compassos_por_acorde):
                for k in range(8):
                    inicio = passo * amostras_por
                    # baixo
                    if k in (0, 3, 4, 6) if bateria else k in (0, 4):
                        nb = raiz - 24 + (12 if k == 6 else 0)
                        misturar(gerar_onda("triangulo", nota_hz(nb), colcheia * 0.9, vol_baixo), inicio)
                    # chimbal
                    if bateria and k % 2 == 1:
                        misturar(gerar_onda("ruido", 0, 0.03, 0.05, solta=0.02), inicio)
                    if bateria and k in (0, 4):
                        misturar(gerar_onda("sine", 110, 0.07, 0.25, 50), inicio)
                    # melodia
                    if rnd.random() < densidade:
                        if ultima is None or rnd.random() < 0.35:
                            alvo = raiz + 12 * 0 + rnd.choice(tons) + (oitava - 60)
                        else:
                            alvo = ultima + rnd.choice([-2, -1, 1, 2]) * (1 if rnd.random() < 0.6 else 2)
                        # puxa para dentro do alcance
                        alvo = max(oitava - 3, min(oitava + 14, alvo))
                        ultima = alvo
                        dur = colcheia * (1.9 if rnd.random() < 0.25 else 0.9)
                        misturar(gerar_onda(tipo_mel, nota_hz(alvo), dur, vol_mel), inicio)
                    passo += 1
    return saida


def gerar_musicas():
    pasta = RECURSOS / "sons" / "musicas"
    maior, menor = [0, 4, 7, 12], [0, 3, 7, 12]
    C, A, F, Gg = 48, 45, 41, 43
    menu = compor([{"raiz": C + 12, "tons": maior}, {"raiz": A + 12, "tons": menor},
                   {"raiz": F + 12, "tons": maior}, {"raiz": Gg + 12, "tons": maior}],
                  bpm=104, compassos_por_acorde=1, seed=11, oitava=72, tipo_mel="triangulo",
                  vol_mel=0.22, bateria=False, repeticoes=2, densidade=0.7)
    salvar_wav(pasta / "menu.wav", menu)
    fase = compor([{"raiz": C + 12, "tons": maior}, {"raiz": Gg + 12, "tons": maior},
                   {"raiz": A + 12, "tons": menor}, {"raiz": F + 12, "tons": maior},
                   {"raiz": C + 12, "tons": maior}, {"raiz": Gg + 12, "tons": maior},
                   {"raiz": F + 12, "tons": maior}, {"raiz": Gg + 12, "tons": maior}],
                  bpm=148, compassos_por_acorde=1, seed=23, oitava=74, tipo_mel="quadrada",
                  vol_mel=0.11, bateria=True, repeticoes=2, densidade=0.85)
    salvar_wav(pasta / "fase.wav", fase)
    castelo = compor([{"raiz": A + 12, "tons": menor}, {"raiz": F + 12, "tons": maior},
                      {"raiz": Gg + 12, "tons": maior}, {"raiz": 40 + 12, "tons": menor}],
                     bpm=132, compassos_por_acorde=1, seed=5, oitava=69, tipo_mel="pulso",
                     vol_mel=0.12, vol_baixo=0.22, bateria=True, repeticoes=3, densidade=0.9)
    salvar_wav(pasta / "castelo.wav", castelo)
    # fanfarra de conclusão (sem repetição)
    G = gerar_onda
    notas = [(72, .15), (72, .15), (72, .15), (72, .45), (68, .45), (70, .45), (72, .3), (70, .15), (72, 1.2)]
    mel = concatenar(*[G("quadrada", nota_hz(m), d * 0.95, 0.2) for m, d in notas])
    acorde = [0.0] * len(mel)
    for m in (60, 64, 67):
        onda = G("triangulo", nota_hz(m), len(mel) / TAXA, 0.12, solta=0.5)
        for i, v in enumerate(onda[:len(acorde)]):
            acorde[i] += v
    salvar_wav(pasta / "conclusao.wav", [a + b for a, b in zip(mel, acorde)])


def principal():
    pygame.init()
    pygame.display.set_mode((1, 1))
    print("Gerando personagens...")
    gerar_heroi(); gerar_princesa(); gerar_inimigos()
    print("Gerando blocos, objetos e decorações...")
    gerar_tileset(); gerar_objetos(); gerar_decoracoes(); gerar_interface()
    print("Gerando cenários...")
    gerar_cenarios()
    print("Gerando sons...")
    gerar_efeitos_sonoros(); gerar_musicas()
    print("Recursos gerados em", RECURSOS)


if __name__ == "__main__":
    principal()
