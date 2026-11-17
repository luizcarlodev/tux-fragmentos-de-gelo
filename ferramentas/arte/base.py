"""Utilitários e paleta compartilhados pelos geradores de arte e som (tema glacial).

Todos os módulos de ``ferramentas/arte`` gravam em ``recursos/`` usando estas funções.
A arte é desenhada em baixa resolução (ex.: 16x16) e o jogo amplia 3x ao carregar.
"""
import json
import math
import os
import random
import wave
from array import array
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent.parent
RECURSOS = RAIZ / "recursos"
ESCALA = 3

# ---------------------------------------------------------------- paleta glacial
TRANSP = (0, 0, 0, 0)
CONTORNO = (14, 22, 48)            # azul quase preto (contornos de sprites)
NEVE = (248, 252, 255)
NEVE_SOMBRA = (205, 226, 245)
GELO_CLARO = (170, 226, 250)
CIANO = (96, 214, 240)
TURQUESA = (40, 178, 196)
GELO = (84, 160, 222)
AZUL_GLACIAL = (56, 112, 196)
AZUL = (36, 72, 156)
AZUL_ESCURO = (22, 40, 104)
NOITE = (14, 22, 64)
ROXO_GELO = (150, 130, 230)
ROXO = (98, 78, 190)
ROXO_ESCURO = (58, 44, 130)
PEDRA = (122, 134, 156)
PEDRA_CLARA = (160, 172, 192)
PEDRA_ESCURA = (72, 82, 108)
OURO = (255, 206, 80)
OURO_ESCURO = (226, 138, 36)
LARANJA = (246, 150, 40)
LARANJA_ESCURO = (200, 98, 24)
ROSA = (255, 150, 190)
ROSA_ESCURO = (214, 92, 150)
VERMELHO = (226, 70, 80)
PRETO_PINGUIM = (30, 36, 62)       # corpo do Tux
PRETO_PINGUIM_CL = (52, 62, 98)
MADEIRA = (128, 86, 56)
MADEIRA_ESCURA = (84, 54, 38)
VERDE_PINHEIRO = (36, 112, 104)
VERDE_PINHEIRO_ESC = (22, 74, 80)


# ---------------------------------------------------------------- spritesheets
def nova_folha(colunas, linhas, lw, lh):
    """Superfície transparente para ``colunas`` x ``linhas`` quadros de ``lw`` x ``lh``."""
    return pygame.Surface((colunas * lw, linhas * lh), pygame.SRCALPHA)


def anim(linha, quadros, duracao=0.12, repetir=True, quadro_inicial=0):
    """Entrada do campo ``animacoes`` do ``configuracao.json``."""
    return {"linha": linha, "quadro_inicial": quadro_inicial, "quadros": quadros,
            "duracao_quadro": duracao, "repetir": repetir}


def salvar_folha(pasta, nome_png, folha, lw, lh, animacoes, escala=ESCALA, caixa=None):
    """Grava ``recursos/<pasta>/<nome_png>`` e o ``configuracao.json`` correspondente."""
    destino = RECURSOS / pasta
    destino.mkdir(parents=True, exist_ok=True)
    pygame.image.save(folha, str(destino / nome_png))
    cfg = {"arquivo": nome_png, "largura_quadro": lw, "altura_quadro": lh,
           "escala": escala, "animacoes": animacoes}
    if caixa:
        cfg["caixa_colisao"] = list(caixa)
    with open(destino / "configuracao.json", "w", encoding="utf-8") as arquivo:
        json.dump(cfg, arquivo, ensure_ascii=False, indent=2)


def salvar_imagem(caminho_relativo, superficie):
    """Grava um PNG solto em ``recursos/<caminho_relativo>``."""
    destino = RECURSOS / caminho_relativo
    destino.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(superficie, str(destino))


# ---------------------------------------------------------------- desenho
def ret(s, ox, oy, x, y, w, h, cor):
    s.fill(cor, (ox + x, oy + y, w, h))


def pixel(s, ox, oy, x, y, cor):
    if 0 <= ox + x < s.get_width() and 0 <= oy + y < s.get_height():
        s.set_at((ox + x, oy + y), cor)


def desenhar_ascii(s, ox, oy, linhas, paleta, dx=0, dy=0):
    """Desenha pixel art a partir de texto: cada caractere é uma cor de ``paleta``.

    ``.`` e espaço são transparentes. ``dx``/``dy`` deslocam o desenho inteiro.
    """
    for y, linha in enumerate(linhas):
        for x, c in enumerate(linha):
            if c in ". ":
                continue
            cor = paleta.get(c)
            if cor is not None:
                pixel(s, ox, oy, x + dx, y + dy, cor)


def contornar(s, rect, cor=CONTORNO):
    """Adiciona contorno de 1 px (4 direções) ao redor dos pixels opacos dentro de ``rect``."""
    x0, y0, w, h = rect
    copia = s.copy()
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if copia.get_at((x, y)).a != 0:
                continue
            for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + ddx, y + ddy
                if x0 <= nx < x0 + w and y0 <= ny < y0 + h and copia.get_at((nx, ny)).a != 0:
                    s.set_at((x, y), cor)
                    break


def degrade_vertical(largura, altura, cor_topo, cor_base):
    """Superfície RGB com degradê vertical."""
    s = pygame.Surface((largura, altura))
    for y in range(altura):
        t = y / max(1, altura - 1)
        s.fill(tuple(int(cor_topo[i] + (cor_base[i] - cor_topo[i]) * t) for i in range(3)), (0, y, largura, 1))
    return s


# ---------------------------------------------------------------- áudio
TAXA = 22050


def nota_hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def gerar_onda(tipo, freq, dur, vol=0.3, freq_fim=None, ataque=0.005, solta=0.04):
    """Onda simples: ``quadrada``, ``pulso``, ``triangulo``, ``ruido`` ou seno (qualquer outro nome)."""
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
    resultado = []
    for parte in partes:
        resultado.extend(parte)
    return resultado


def misturar(*partes):
    """Soma várias ondas (de tamanhos diferentes) em uma só."""
    tamanho = max(len(p) for p in partes)
    saida = [0.0] * tamanho
    for parte in partes:
        for i, v in enumerate(parte):
            saida[i] += v
    return saida


def salvar_wav(caminho, amostras):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    dados = array("h", [max(-32767, min(32767, int(a * 32767))) for a in amostras])
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TAXA)
        w.writeframes(dados.tobytes())


def iniciar_pygame():
    pygame.init()
    pygame.display.set_mode((1, 1))
