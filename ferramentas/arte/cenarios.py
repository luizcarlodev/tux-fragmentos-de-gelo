"""Gerador procedural dos cenários (fundos com parallax) do tema glacial.

Grava PNGs 1280x720 em ``recursos/cenarios/<tema>/`` e as miniaturas da seleção de fases em
``recursos/interface/``. As camadas que rolam são perfeitamente tileáveis na horizontal:
todo ruído/onda é periódico em x (períodos que dividem 1280) e os objetos desenhados
perto da borda são repetidos deslocados em -1280/+1280.
"""
import math
import random

import numpy as np

from ferramentas.arte.base import (CIANO, GELO_CLARO, NEVE, OURO, ROXO_GELO, RECURSOS, TURQUESA,
                                   iniciar_pygame, pygame, salvar_imagem)

W, H = 1280, 720
_cache_brilho = {}


# ---------------------------------------------------------------- utilidades numéricas
def ss(a, b, x):
    """smoothstep de a..b."""
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def ruido(cx, cy, seed):
    """Ruído de valor 2D (H, W) em [0,1], periódico em x (cx deve dividir 1280)."""
    nx, ny = W // cx, H // cy + 2
    g = np.random.default_rng(seed).random((ny, nx)).astype(np.float32)
    xs = np.arange(W, dtype=np.float32) / cx
    ys = np.arange(H, dtype=np.float32) / cy
    xi, yi = xs.astype(int), ys.astype(int)
    fx, fy = xs - xi, ys - yi
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    x0, x1 = xi % nx, (xi + 1) % nx
    ga, gb = g[yi], g[yi + 1]
    topo = ga[:, x0] + (ga[:, x1] - ga[:, x0]) * fx[None, :]
    base = gb[:, x0] + (gb[:, x1] - gb[:, x0]) * fx[None, :]
    return topo + (base - topo) * fy[:, None]


def fbm(cx, cy, seed, oitavas=4):
    total, amp, soma = 0.0, 1.0, 0.0
    for o in range(oitavas):
        total = total + ruido(cx, cy, seed + o * 17) * amp
        soma += amp
        amp *= 0.5
        if W % max(1, cx // 2) == 0 and cx // 2 >= 2:
            cx //= 2
        cy = max(2, cy // 2)
    return total / soma


def cadeia(base, amp, freqs, seed, decaimento=0.7):
    """Linha de cumeada (y por coluna, periódica) com picos agudos."""
    rng = np.random.default_rng(seed)
    xs = np.arange(W) / W * 2 * np.pi
    h = np.zeros(W)
    for i, f in enumerate(freqs):
        h += (decaimento ** i) * (1 - np.abs(np.sin(f * xs + rng.random() * 6.28)))
    h = (h - h.min()) / (h.max() - h.min())
    return base - amp * h


def lerp(a, b, t):
    return a + (b - a) * t


def gradiente(paradas, h=H):
    """Array (h,1,3) a partir de [(y, cor), ...]."""
    ys = [p[0] for p in paradas]
    y = np.arange(h)
    canais = [np.interp(y, ys, [p[1][c] for p in paradas]) for c in range(3)]
    return np.stack(canais, axis=-1)[:, None, :].astype(np.float32)


def para_superficie(rgb, alfa=None):
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    if alfa is None:
        return pygame.image.frombuffer(np.ascontiguousarray(rgb).tobytes(), (W, H), "RGB").copy()
    a = np.clip(alfa * 255, 0, 255).astype(np.uint8)
    dados = np.dstack([rgb, a])
    return pygame.image.frombuffer(np.ascontiguousarray(dados).tobytes(), (W, H), "RGBA").copy()


def em_array(s):
    """Superfície RGBA -> (rgb float (H,W,3), alfa float (H,W) 0..1)."""
    a = np.frombuffer(pygame.image.tobytes(s, "RGBA"), dtype=np.uint8).reshape(H, W, 4)
    return a[..., :3].astype(np.float32), a[..., 3].astype(np.float32) / 255.0


def nova():
    return pygame.Surface((W, H), pygame.SRCALPHA)


def blit_x(dst, src, x, y=0):
    """Blit repetido em -W/0/+W para manter a emenda."""
    for d in (-W, 0, W):
        dst.blit(src, (x + d, y))


# ---------------------------------------------------------------- desenho com repetição
def poligono(s, cor, pts, borda=None):
    for d in (-W, 0, W):
        p = [(x + d, y) for x, y in pts]
        xs = [q[0] for q in p]
        if max(xs) < -2 or min(xs) > W + 2:
            continue
        pygame.draw.polygon(s, cor, p)
        if borda:
            pygame.draw.polygon(s, borda, p, 1)


def retangulo(s, cor, x, y, w, h):
    for d in (-W, 0, W):
        if x + d + w < 0 or x + d > W:
            continue
        s.fill(cor, (round(x + d), round(y), max(1, round(w)), max(1, round(h))))


def linha(s, cor, a, b, larg=1):
    for d in (-W, 0, W):
        pygame.draw.line(s, cor, (a[0] + d, a[1]), (b[0] + d, b[1]), larg)


def brilho(s, cx, cy, raio, cor, forca=1.0, expoente=2.0):
    """Halo radial suave, repetido para tileabilidade."""
    chave = (raio, cor, round(forca, 3), expoente)
    if chave not in _cache_brilho:
        n = raio * 2
        yy, xx = np.mgrid[0:n, 0:n]
        d = np.sqrt((xx - raio) ** 2 + (yy - raio) ** 2) / raio
        al = np.clip(1 - d, 0, 1) ** expoente * forca
        dados = np.zeros((n, n, 4), np.uint8)
        dados[..., :3] = cor
        dados[..., 3] = np.clip(al * 255, 0, 255)
        _cache_brilho[chave] = pygame.image.frombuffer(dados.tobytes(), (n, n), "RGBA").copy()
    blit_x(s, _cache_brilho[chave], cx - raio, cy - raio)


def nevoa(s, y0, y1, cor, forca, seed, cx=160, cy=40):
    """Faixa de névoa (ruído) entre y0 e y1 com bordas suaves."""
    n = fbm(cx, cy, seed, 4)
    y = np.arange(H)[:, None]
    meio, meia = (y0 + y1) / 2, (y1 - y0) / 2
    env = np.clip(1 - np.abs(y - meio) / meia, 0, 1)
    al = np.clip((n - 0.35) * 2.2, 0, 1) * env * forca
    rgb = np.empty((H, W, 3), np.float32)
    rgb[:] = cor
    s.blit(para_superficie(rgb, al), (0, 0))


# ---------------------------------------------------------------- montanhas com relevo
def montanha(cumeada, neve_luz, neve_sombra, rocha_luz, rocha_sombra, neve_prof, bruma, bruma_forca,
             seed, listras=None, base_y=None):
    """Retorna (rgb, alfa) de um relevo sombreado sob ``cumeada``."""
    neve_luz, neve_sombra, rocha_luz, rocha_sombra = (
        np.array(c, np.float32) for c in (neve_luz, neve_sombra, rocha_luz, rocha_sombra))
    X = np.arange(W)[None, :]
    Y = np.arange(H)[:, None].astype(np.float32)
    R = cumeada[None, :]
    prof = Y - R
    alfa = np.clip(prof + 1.0, 0, 1)
    suave = (np.roll(cumeada, -5) - np.roll(cumeada, 5)) / 10.0
    suave = (suave + np.roll(suave, 2) + np.roll(suave, -2)) / 3.0
    xs = (X + (np.clip(prof, 0, None) * 0.35).astype(int)) % W
    cara = suave[xs]
    ruga = fbm(10, 160, seed, 3)
    luz = np.clip(0.5 + cara * 0.55 + (ruga - 0.5) * 0.7, 0, 1)
    rn = fbm(40, 60, seed + 5, 3)
    limite = neve_prof * (0.6 + 0.9 * rn)
    neve = ss(0, 1, (limite - prof) / 14.0 + 0.0) * 1.0
    neve = np.clip(neve + ss(0.55, 0.8, ruga) * 0.0, 0, 1)
    rocha = rocha_sombra + (rocha_luz - rocha_sombra) * luz[..., None]
    nv = neve_sombra + (neve_luz - neve_sombra) * luz[..., None]
    rgb = rocha + (nv - rocha) * neve[..., None]
    if listras is not None:
        li = ss(0.58, 0.72, fbm(20, 90, seed + 9, 3)) * 0.55
        rgb = rgb + (np.array(listras, np.float32) - rgb) * li[..., None] * ss(0, 40, prof)[..., None]
    h = bruma_forca * (0.35 + 0.65 * np.clip(prof / 320.0, 0, 1))
    rgb = rgb + (np.array(bruma, np.float32) - rgb) * h[..., None]
    return rgb, alfa


def camada_de(rgb, alfa):
    return para_superficie(rgb, alfa)


# ---------------------------------------------------------------- vegetação e cristais
def pinheiro(s, x, y, h, cor, cor_luz, neve=NEVE, vento=0.0, tiers=6):
    """Pinheiro em silhueta com neve nos galhos; ``vento`` desloca o topo (curvado)."""
    larg = h * 0.34
    tronco = max(2, h * 0.05)
    retangulo(s, cor, x - tronco / 2, y - h * 0.12, tronco, h * 0.14)
    for i in range(tiers):
        t0 = i / tiers
        topo_y = y - h * (0.12 + 0.88 * (t0 + 1.0 / tiers * 1.5))
        base_y = y - h * (0.08 + 0.88 * t0)
        topo_y = max(topo_y, y - h)
        w = larg * (1 - t0 * 0.8) * 0.5 + 1.5
        off_b = vento * h * (t0 ** 1.6)
        off_t = vento * h * (min(1, t0 + 1.2 / tiers) ** 1.6)
        pts = [(x - w + off_b, base_y), (x + off_t, topo_y), (x + w + off_b, base_y),
               (x + w * 0.35 + off_b, base_y - h * 0.03), (x - w * 0.35 + off_b, base_y - h * 0.03)]
        poligono(s, cor, pts)
        if neve:
            m = [(x - w * 0.55 + off_b, base_y - h * 0.045), (x + off_t, topo_y),
                 (x + w * 0.1 + off_b, base_y - h * 0.045 - h * 0.02)]
            poligono(s, cor_luz, m)


def cristal(s, cx, by, w, h, tilt, c_esq, c_dir, c_ponta, c_luz=None):
    """Prisma de cristal (duas faces + ponta)."""
    ys = by - h
    ls = (cx - w / 2 + tilt * 0.9, ys)
    rs = (cx + w / 2 + tilt * 0.9, ys)
    tip = (cx + tilt + w * 0.05, ys - w * 0.85)
    bc = (cx + w * 0.12, by)
    bl, br = (cx - w / 2, by), (cx + w / 2, by)
    poligono(s, c_esq, [bl, ls, tip, bc])
    poligono(s, c_dir, [bc, tip, rs, br])
    poligono(s, c_ponta, [ls, tip, (cx + w * 0.05 + tilt, ys)])
    if c_luz:
        linha(s, c_luz, (bl[0] + 1, by - 2), (ls[0] + 1, ys + 1), 1)
        linha(s, c_luz, (ls[0] + 1, ys), tip, 1)


def faiscas(s, qtd, seed, y0, y1, cor=(255, 255, 255), raio=(1, 2)):
    rng = random.Random(seed)
    for _ in range(qtd):
        x, y = rng.randrange(W), rng.randrange(y0, y1)
        r = rng.randint(*raio)
        pygame.draw.line(s, cor + (230,), (x - r, y), (x + r, y))
        pygame.draw.line(s, cor + (230,), (x, y - r), (x, y + r))
        pygame.draw.rect(s, (255, 255, 255, 255), (x, y, 1, 1))


# ================================================================ GELEIRA
def _aurora(rgb, Y, X, seed, base_y, forca, bandas=3, cores=((110, 236, 214), (176, 150, 246))):
    rng = np.random.default_rng(seed)
    xs = X / W * 2 * np.pi
    raios = fbm(5, 220, seed, 2)
    for k in range(bandas):
        ph = rng.random(3) * 6.28
        yc = base_y + k * 62 + 38 * np.sin(2 * xs + ph[0]) + 18 * np.sin(5 * xs + ph[1]) + 9 * np.sin(11 * xs + ph[2])
        d = Y - yc
        sd = np.where(d > 0, 12.0, 70.0 + 10 * k)
        inten = np.exp(-(d / sd) ** 2) * (0.55 + 0.9 * raios)
        t = np.clip(-d / 140.0, 0, 1)[..., None]
        col = np.array(cores[0], np.float32) + (np.array(cores[1], np.float32) - np.array(cores[0], np.float32)) * t
        rgb += (col - rgb) * (np.clip(inten, 0, 1) * forca)[..., None]
    return rgb


def _ceu_geleira():
    rgb = np.repeat(gradiente([(0, (84, 142, 212)), (260, (130, 190, 236)), (520, (204, 228, 246)),
                               (640, (232, 243, 252)), (720, (236, 245, 253))]), W, axis=1)
    Y = np.arange(H)[:, None].astype(np.float32)
    X = np.arange(W)[None, :].astype(np.float32)
    rgb = _aurora(rgb, Y, X, 3, 170, 0.34)
    # sol pálido e halo
    d = np.sqrt((X - 930) ** 2 + (Y - 190) ** 2)
    rgb += (np.array([255, 250, 238], np.float32) - rgb) * (np.exp(-d / 110.0) * 0.55)[..., None]
    anel = np.exp(-((d - 170) / 3.0) ** 2) * 0.25
    rgb += (np.array([255, 255, 255], np.float32) - rgb) * anel[..., None]
    disco = np.clip(36 - d, 0, 1)
    rgb += (np.array([255, 253, 244], np.float32) - rgb) * disco[..., None]
    # poeira de diamante
    rng = np.random.default_rng(8)
    for _ in range(120):
        x, y = rng.integers(0, W), rng.integers(0, 520)
        rgb[y, x] = rgb[y, x] + (255 - rgb[y, x]) * rng.uniform(0.3, 0.7)
    return para_superficie(rgb)


def _nuvens_finas(seed, y0, y1, cor_luz, cor_sombra, forca, cx=200, cy=14, limiar=0.52, alfa_max=0.9):
    n = 0.6 * ruido(cx, cy, seed) + 0.4 * fbm(cx // 4, max(4, cy // 2), seed + 3, 3)
    y = np.arange(H)[:, None]
    meio, meia = (y0 + y1) / 2, (y1 - y0) / 2
    env = np.clip(1 - np.abs(y - meio) / meia, 0, 1) ** 0.6
    dens = n * (0.4 + 0.8 * env)
    al = ss(limiar, limiar + 0.14, dens) * alfa_max * forca
    sup = np.roll(dens, 5, axis=0)
    luz = np.clip(0.5 + (dens - sup) * 6, 0, 1)
    rgb = np.array(cor_sombra, np.float32) + (np.array(cor_luz, np.float32) - np.array(cor_sombra, np.float32)) * luz[..., None]
    return para_superficie(rgb, al)


def _nuvens_geleira():
    s = nova()
    s.blit(_nuvens_finas(21, 60, 300, (255, 255, 255), (196, 218, 240), 1.0, 320, 18, 0.5), (0, 0))
    s.blit(_nuvens_finas(33, 150, 420, (250, 253, 255), (200, 222, 244), 0.8, 160, 10, 0.54), (0, 0))
    return s


def _longe_geleira():
    rgb = np.zeros((H, W, 3), np.float32)
    alfa = np.zeros((H, W), np.float32)
    bruma = (214, 232, 248)
    def junta(rgb, alfa, r2, a2):
        novo_a = a2 + alfa * (1 - a2)
        rgb = (r2 * a2[..., None] + rgb * (alfa * (1 - a2))[..., None]) / np.maximum(novo_a, 1e-4)[..., None]
        return rgb, novo_a
    cum1 = cadeia(410, 250, [3, 5, 8, 13, 21, 34], 5, 0.74)
    r, a = montanha(cum1, (236, 246, 255), (176, 206, 238), (136, 168, 214), (96, 128, 190), 190, bruma, 0.55, 11)
    rgb, alfa = junta(rgb, alfa, r, a)
    cum2 = cadeia(500, 200, [4, 7, 11, 18, 29, 40], 9, 0.72)
    r, a = montanha(cum2, (244, 250, 255), (184, 212, 242), (120, 156, 208), (82, 116, 184), 150, bruma, 0.35, 23)
    rgb, alfa = junta(rgb, alfa, r, a)
    # fundo preenchido até embaixo (cor azul-gélida para nao vazar)
    s = para_superficie(rgb, alfa)
    return s


def _pinheirais(s, cumeada, seed, qtd, hmin, hmax, cor, cor_luz, vento=0.0, ofs=0):
    rng = random.Random(seed)
    for _ in range(qtd):
        x = rng.randrange(W)
        y = int(cumeada[x]) + rng.randint(ofs, ofs + 26)
        h = rng.randint(hmin, hmax)
        pinheiro(s, x, y, h, cor, cor_luz, vento=vento)


def _perto_geleira():
    s = nova()
    bruma = (200, 224, 246)
    # encosta de trás: geleira clara
    cum_a = cadeia(470, 120, [2, 3, 6, 10, 17], 31, 0.62)
    r, a = montanha(cum_a, (246, 251, 255), (160, 200, 238), (120, 170, 220), (80, 128, 200), 900, bruma, 0.25, 41,
                    listras=(120, 196, 238))
    s.blit(para_superficie(r, a), (0, 0))
    _pinheirais(s, cum_a, 7, 22, 40, 70, (28, 78, 108), (222, 238, 252), 0.0, 2)
    # formações de gelo/cristais azuis sobre a encosta
    rng = random.Random(12)
    for _ in range(9):
        x = rng.randrange(W)
        y = int(cum_a[x]) + rng.randint(8, 30)
        for k in range(rng.randint(2, 4)):
            w = rng.randint(8, 16)
            cristal(s, x + k * rng.randint(6, 12) - 10, y + rng.randint(0, 6), w, rng.randint(26, 64),
                    rng.randint(-5, 5), (70, 150, 220), (150, 222, 252), (226, 248, 255), (240, 252, 255))
    # encosta da frente: neve densa, opaca até embaixo
    cum_b = cadeia(578, 52, [3, 5, 9, 14, 22], 44, 0.6)
    r, a = montanha(cum_b, (240, 248, 255), (140, 180, 226), (96, 146, 212), (60, 100, 176), 900, (190, 216, 244), 0.1, 52,
                    listras=(150, 210, 245))
    a = np.where(np.arange(H)[:, None] >= 640, 1.0, a)
    s.blit(para_superficie(r, a), (0, 0))
    _pinheirais(s, cum_b, 19, 15, 70, 118, (22, 62, 94), (226, 240, 253), 0.0, 4)
    # cristais pequenos na frente
    for _ in range(10):
        x = rng.randrange(W)
        y = int(cum_b[x]) + rng.randint(12, 36)
        cristal(s, x, y, rng.randint(7, 13), rng.randint(18, 40), rng.randint(-4, 4),
                (58, 150, 214), (140, 226, 252), (220, 250, 255), (245, 253, 255))
    faiscas(s, 26, 77, 440, 640, (255, 255, 255))
    return s


def gerar_geleira(pasta):
    saidas = {"ceu.png": _ceu_geleira(), "nuvens.png": _nuvens_geleira(),
              "montanhas_longe.png": _longe_geleira(), "montanhas_perto.png": _perto_geleira()}
    for nome, sup in saidas.items():
        salvar_imagem(f"cenarios/{pasta}/{nome}", sup)
    return saidas


# ================================================================ CAVERNAS
def _ceu_cavernas():
    rgb = np.repeat(gradiente([(0, (12, 10, 34)), (300, (26, 22, 62)), (560, (38, 34, 84)), (720, (22, 20, 56))]), W, axis=1)
    rocha = fbm(160, 96, 61, 5)
    rgb = rgb * (0.65 + 0.7 * rocha[..., None])
    Y = np.arange(H)[:, None].astype(np.float32)
    rgb += np.array([40, 30, 80], np.float32) * (np.exp(-((Y - 470) / 160.0) ** 2) * 0.35)[..., None]
    v = fbm(160, 160, 73, 3)
    cor_v = ruido(80, 80, 5)[..., None]
    cor = np.array((90, 220, 250), np.float32) * (1 - cor_v) + np.array((170, 130, 250), np.float32) * cor_v
    fino = np.exp(-((v - 0.5) / 0.016) ** 2)
    largo = np.exp(-((v - 0.5) / 0.07) ** 2)
    rgb += cor * (fino * 0.75 + largo * 0.12)[..., None]
    v2 = fbm(80, 120, 91, 3)
    rgb += np.array((110, 200, 240), np.float32) * (np.exp(-((v2 - 0.5) / 0.012) ** 2) * 0.45)[..., None]
    rgb *= (1.0 - 0.35 * ss(500, 720, Y))[..., None]
    return para_superficie(rgb)


def _pilar(s, x, w, cor, cor_luz, cor_sombra, rng):
    cintura = rng.uniform(0.55, 0.8)
    pts = [(x - w, 0), (x + w, 0), (x + w * cintura, 300), (x + w * rng.uniform(0.85, 1.1), H), (x - w * rng.uniform(0.85, 1.1), H),
           (x - w * cintura, 300)]
    poligono(s, cor, pts)
    poligono(s, cor_luz, [(x + w * 0.35, 0), (x + w, 0), (x + w * cintura, 300), (x + w * 0.2, 300)])
    poligono(s, cor_sombra, [(x - w, 0), (x - w * 0.5, 0), (x - w * 0.4, 300), (x - w * cintura, 300)])
    for _ in range(5):
        yy = rng.randrange(30, 700)
        linha(s, cor_sombra, (x - w * 0.6, yy), (x + w * 0.1, yy + rng.randint(-6, 6)), 1)


def _paredes_longe():
    s = nova()
    rng = random.Random(14)
    cores = ((46, 40, 100), (66, 58, 130), (32, 28, 76))
    pos = [90, 250, 430, 640, 800, 980, 1150]
    for x in pos:
        _pilar(s, x + rng.randint(-30, 30), rng.randint(36, 62), *cores, rng)
    # cristais grandes ao longe (menos saturados), com halos
    for x, y, cor in ((170, 650, "c"), (520, 640, "r"), (760, 660, "c"), (1010, 650, "r"), (1230, 650, "c"), (350, 660, "r")):
        if cor == "c":
            esq, dire, pon, hal = (50, 130, 170), (120, 210, 236), (200, 244, 255), (90, 200, 240)
        else:
            esq, dire, pon, hal = (90, 70, 160), (160, 132, 228), (214, 196, 255), (150, 110, 240)
        brilho(s, x, y - 120, 150, hal, 0.34, 1.6)
        for k in range(rng.randint(3, 5)):
            cristal(s, x + rng.randint(-50, 50), y + rng.randint(-6, 8), rng.randint(20, 36), rng.randint(110, 280),
                    rng.randint(-14, 14), esq, dire, pon, (235, 250, 255))
    nevoa(s, 330, 640, (120, 110, 210), 0.38, 8, 160, 60)
    nevoa(s, 520, 720, (90, 90, 190), 0.45, 18, 80, 50)
    faiscas(s, 24, 5, 80, 600, (190, 230, 255), (1, 2))
    return s


def _estalactites():
    rng = np.random.default_rng(29)
    X = np.arange(W)[None, :].astype(np.float32)
    Y = np.arange(H)[:, None].astype(np.float32)
    n = 28
    centros = np.sort(rng.uniform(0, W, n))
    larg = rng.uniform(22, 62, n)
    comp = rng.uniform(70, 340, n) * (0.5 + 0.5 * larg / 62)
    tipo = rng.random(n) < 0.55   # True: gelo
    prof = np.full((W,), 0.0, np.float32)
    idx = np.zeros(W, int)
    xs = np.arange(W)
    mel = np.zeros((W,), np.float32)
    desl = np.zeros((W,), np.float32)
    for i in range(n):
        d = xs - centros[i]
        d = (d + W / 2) % W - W / 2
        p = comp[i] * np.clip(1 - np.abs(d) / larg[i], 0, 1) ** 1.35
        melhor = p > prof
        prof = np.where(melhor, p, prof)
        idx = np.where(melhor, i, idx)
        desl = np.where(melhor, d / larg[i], desl)
    teto = 18 + 22 * fbm(40, 30, 3, 3)[0]
    teto = np.maximum(teto, prof)
    ate = teto[None, :]
    alfa = np.clip(ate - Y + 0.5, 0, 1)
    ice = tipo[idx][None, :]
    frac = np.clip(Y / np.maximum(ate, 1), 0, 1)
    lado = np.clip(0.5 + desl[None, :] * 0.5 * -1, 0, 1)   # lado direito mais claro
    luz = np.clip(0.55 - desl[None, :] * 0.55, 0, 1) + (fbm(10, 60, 4, 2) - 0.5) * 0.3
    # gelo
    g_esc, g_cl = np.array((44, 80, 150), np.float32), np.array((150, 226, 250), np.float32)
    # rocha
    r_esc, r_cl = np.array((38, 32, 82), np.float32), np.array((98, 86, 166), np.float32)
    t = np.clip(luz * 0.6 + frac * 0.55, 0, 1)[..., None]
    cor_g = g_esc + (g_cl - g_esc) * t
    cor_r = r_esc + (r_cl - r_esc) * np.clip(luz * 0.8 + frac * 0.2, 0, 1)[..., None]
    rgb = np.where(ice[..., None], cor_g, cor_r)
    # ponta brilhante
    ponta = ss(0.8, 1.0, frac) * ice
    rgb = rgb + (np.array((235, 252, 255), np.float32) - rgb) * (ponta * 0.8)[..., None]
    # teto escuro no topo
    rgb *= (0.55 + 0.45 * ss(0, 60, Y))[..., None]
    s = para_superficie(rgb, alfa)
    # brilhos e gotas
    for i in range(n):
        if tipo[i]:
            x = int(centros[i])
            y = int(comp[i]) - 6
            pygame.draw.line(s, (255, 255, 255, 255), (x % W, y), (x % W, y + 2))
    return s


def _cristais_perto():
    s = nova()
    rng = random.Random(33)
    # chão de rocha com estalagmites
    rg = np.random.default_rng(37)
    n = 22
    centros = np.sort(rg.uniform(0, W, n))
    larg = rg.uniform(22, 54, n)
    comp = rg.uniform(40, 150, n)
    xs = np.arange(W)
    prof = np.zeros(W)
    desl = np.zeros(W)
    for i in range(n):
        d = (xs - centros[i] + W / 2) % W - W / 2
        p = comp[i] * np.clip(1 - np.abs(d) / larg[i], 0, 1) ** 1.3
        m = p > prof
        prof = np.where(m, p, prof)
        desl = np.where(m, d / larg[i], desl)
    chao = 628 - 14 * fbm(40, 30, 7, 3)[0] * 2
    topo = chao - prof
    Y = np.arange(H)[:, None].astype(np.float32)
    alfa = np.clip(Y - topo[None, :] + 0.5, 0, 1)
    pf = np.clip((Y - topo[None, :]) / 120.0, 0, 1)
    luz = np.clip(0.5 + desl[None, :] * 0.5, 0, 1)
    esc, cl = np.array((26, 22, 64), np.float32), np.array((78, 70, 150), np.float32)
    rgb = esc + (cl - esc) * (np.clip(luz * 0.8 * (1 - pf) + 0.1, 0, 1))[..., None]
    rgb = rgb * (0.75 + 0.5 * fbm(40, 40, 8, 3)[..., None])
    alfa = np.where(Y >= 660, 1.0, alfa)
    s.blit(para_superficie(rgb, alfa), (0, 0))
    paleta = [((40, 140, 168), (110, 220, 244), (210, 250, 255), (96, 214, 240)),
              ((92, 70, 170), (168, 140, 240), (222, 206, 255), (150, 120, 240)),
              ((30, 160, 156), (96, 232, 214), (200, 255, 246), (80, 226, 210))]
    agrupamentos = [(80, 3), (250, 2), (420, 3), (610, 2), (800, 3), (990, 2), (1160, 3)]
    for x0, k in agrupamentos:
        pal = paleta[rng.randrange(3)]
        by = int(chao[x0 % W] - prof[x0 % W]) + 14
        brilho(s, x0, by - 70, 130, pal[3], 0.34, 1.7)
        for j in range(k):
            cx = x0 + rng.randint(-34, 34)
            h = rng.randint(70, 190) if j == 0 else rng.randint(40, 130)
            cristal(s, cx, by + rng.randint(0, 8), rng.randint(16, 30), h, rng.randint(-12, 12),
                    pal[0], pal[1], pal[2], (245, 253, 255))
    # estalagmites de gelo com pontas claras
    for _ in range(10):
        x = rng.randrange(W)
        by = int(chao[x % W] - prof[x % W]) + 16
        w = rng.randint(10, 20)
        h = rng.randint(30, 80)
        poligono(s, (70, 130, 200), [(x - w, by), (x, by - h), (x + w * 0.2, by)])
        poligono(s, (170, 232, 252), [(x + w * 0.2, by), (x, by - h), (x + w, by)])
    faiscas(s, 34, 91, 430, 650, (200, 245, 255))
    nevoa(s, 500, 700, (80, 120, 220), 0.4, 13, 160, 40)
    # base opaca (neblina por cima do chão)
    return s


def gerar_cavernas(pasta):
    saidas = {"ceu.png": _ceu_cavernas(), "paredes_longe.png": _paredes_longe(),
              "estalactites.png": _estalactites(), "cristais_perto.png": _cristais_perto()}
    for nome, sup in saidas.items():
        salvar_imagem(f"cenarios/{pasta}/{nome}", sup)
    return saidas


# ================================================================ CASTELO
PAL_TEMPESTADE = dict(corpo=(52, 66, 138), luz=(104, 134, 206), sombra=(32, 40, 98), tel=(46, 54, 124),
                      tel_luz=(100, 140, 214), neve=(222, 236, 255), janela=OURO, brilho=(255, 200, 90))
PAL_DISTANTE = dict(corpo=(46, 54, 118), luz=(72, 90, 160), sombra=(34, 40, 92), tel=(40, 46, 108),
                    tel_luz=(70, 92, 160), neve=(150, 170, 220), janela=OURO, brilho=(255, 200, 90))
PAL_MENU = dict(corpo=(160, 208, 244), luz=(232, 246, 255), sombra=(104, 150, 218), tel=(90, 150, 230),
                tel_luz=(196, 232, 255), neve=(255, 255, 255), janela=OURO, brilho=(255, 214, 110))

# (x, largura, altura do corpo, altura do telhado)
TORRES = [(-124, 18, 46, 32), (-92, 16, 66, 46), (-66, 20, 84, 58), (-40, 16, 104, 58), (-16, 12, 120, 56),
          (0, 30, 94, 78), (16, 12, 114, 60), (40, 16, 100, 62), (66, 20, 88, 54), (92, 16, 60, 48), (124, 18, 50, 30)]


def castelo(s, cx, by, esc, pal, detalhe=2, seed=3):
    """Castelo de gelo monumental (torres pontudas, muralhas, janelas acesas)."""
    rng = random.Random(seed)
    def P(x, y):
        return (cx + x * esc, by + y * esc)
    def Q(pts):
        return [P(x, y) for x, y in pts]
    janelas = []
    # muralha de fundo
    poligono(s, pal["sombra"], Q([(-132, 0), (-132, -30), (132, -30), (132, 0)]))
    # torres (as altas primeiro)
    for (x, w, h, hr) in sorted(TORRES, key=lambda t: -t[2]):
        h = h * rng.uniform(0.94, 1.06)
        half = w / 2
        poligono(s, pal["corpo"], Q([(x - half, 0), (x - half, -h), (x + half, -h), (x + half, 0)]))
        poligono(s, pal["sombra"], Q([(x - half, 0), (x - half, -h), (x - half * 0.25, -h), (x - half * 0.25, 0)]))
        poligono(s, pal["luz"], Q([(x + half * 0.55, 0), (x + half * 0.55, -h), (x + half, -h), (x + half, 0)]))
        # coroamento (corbel + ameias)
        poligono(s, pal["luz"], Q([(x - half - 2, -h), (x - half - 2, -h - 4), (x + half + 2, -h - 4), (x + half + 2, -h)]))
        nm = max(2, int(w // 5))
        for m in range(nm):
            mx = x - half - 2 + m * (w + 4) / nm
            poligono(s, pal["corpo"], Q([(mx, -h - 4), (mx, -h - 7), (mx + (w + 4) / nm * 0.55, -h - 7), (mx + (w + 4) / nm * 0.55, -h - 4)]))
        # telhado
        ap = (x + 0.0, -h - 7 - hr)
        poligono(s, pal["tel"], Q([(x - half - 3, -h - 7), ap, (x, -h - 7)]))
        poligono(s, pal["tel_luz"], Q([(x, -h - 7), ap, (x + half + 3, -h - 7)]))
        if detalhe >= 2:
            poligono(s, pal["neve"], Q([(x + half * 0.6, -h - 7 - hr * 0.5), ap, (x + half * 0.3, -h - 7 - hr * 0.62)]))
            linha(s, pal["neve"], P(x, -h - 7 - hr), P(x, -h - 7 - hr - 9), max(1, int(esc * 0.4)))
            linha(s, pal["janela"], P(x, -h - 7 - hr - 9), P(x + 3, -h - 7 - hr - 7), max(1, int(esc * 0.4)))
        # janelas
        n_j = 2 if h < 80 else 3
        for j in range(n_j):
            jy = -h * (0.78 - j * 0.24)
            if rng.random() < 0.8:
                janelas.append((x + rng.uniform(-1, 1), jy, 3.0 if w >= 16 else 2.4))
        if detalhe >= 2:
            # tijolos
            for b in range(int(h // 10)):
                yy = -b * 10 - 6
                linha(s, pal["sombra"], P(x - half, yy), P(x + half, yy), 1)
    # muralha frontal com ameias
    poligono(s, pal["corpo"], Q([(-134, 0), (-134, -26), (134, -26), (134, 0)]))
    poligono(s, pal["luz"], Q([(-134, -26), (-134, -29), (134, -29), (134, -26)]))
    nmer = 44
    for m in range(nmer):
        mx = -134 + m * 268 / nmer
        poligono(s, pal["corpo"], Q([(mx, -29), (mx, -33), (mx + 268 / nmer * 0.55, -33), (mx + 268 / nmer * 0.55, -29)]))
    poligono(s, pal["sombra"], Q([(-134, 0), (-134, -8), (134, -8), (134, 0)]))
    # portão em arco com luz dourada
    arco = [(-11, 0), (-11, -14), (-8, -20), (0, -24), (8, -20), (11, -14), (11, 0)]
    poligono(s, (30, 30, 70), Q(arco))
    poligono(s, pal["janela"], Q([(-8, 0), (-8, -12), (-5, -17), (0, -19), (5, -17), (8, -12), (8, 0)]))
    poligono(s, (255, 236, 160), Q([(-4, 0), (-4, -10), (0, -14), (4, -10), (4, 0)]))
    for k in range(-4, 5):
        linha(s, (30, 30, 70), P(k * 2, 0), P(k * 2, -19), 1)
    # janelas da muralha
    for k in range(-13, 14):
        if abs(k) > 2 and k % 2 == 0 and rng.random() < 0.8:
            janelas.append((k * 9.5, -17, 2.2))
    # janelas e brilho
    for (jx, jy, jw) in janelas:
        jx0, jy0 = P(jx, jy)
        w = max(2, jw * esc)
        h = max(3, jw * 1.7 * esc)
        if detalhe >= 2:
            brilho(s, int(jx0), int(jy0), int(max(6, w * 3.2)), pal["brilho"], 0.5, 1.8)
        retangulo(s, pal["janela"], jx0 - w / 2, jy0 - h / 2, w, h)
        retangulo(s, (255, 244, 190), jx0 - w / 4, jy0 - h / 2 + h * 0.15, max(1, w / 2), max(1, h * 0.55))
        if detalhe >= 2 and esc > 2:
            pygame.draw.rect(s, pal["sombra"], (round(jx0 - w / 2 - 1), round(jy0 - h / 2 - 1), round(w + 2), round(h + 2)), 1)
    # pontes/passarelas aéreas entre torres
    if detalhe >= 2:
        for (xa, xb, ya) in ((-92, -66, -52), (66, 92, -46), (-40, -16, -78), (16, 40, -74)):
            pts = [P(xa + 8, ya), P((xa + xb) / 2, ya - 8), P(xb - 8, ya)]
            pygame.draw.lines(s, pal["luz"], False, pts, max(2, int(esc * 1.2)))
    # gelo pendendo das ameias
    if detalhe >= 2:
        for m in range(0, 36):
            mx = -132 + m * 7.4 + rng.uniform(-1, 1)
            if abs(mx) < 12:
                continue
            ln = rng.uniform(3, 9)
            poligono(s, (190, 232, 252), Q([(mx, -8), (mx + 2, -8), (mx + 1, -8 + ln)]))


def _monte_sob(cx, base_y, largura, alt, seed, bruma=(86, 84, 150), forca=0.0, cores=None):
    """Relevo de montanha centrado em cx (retorna rgb, alfa)."""
    xs = np.arange(W)
    d = np.abs(xs - cx) / (largura / 2.0)
    perfil = np.clip(1 - d, 0, 1) ** 0.8
    rng = np.random.default_rng(seed)
    ph = 2 * np.pi * xs / W
    ru = 14 * np.sin(5 * ph + rng.random() * 6) + 9 * np.sin(11 * ph + rng.random() * 6) + 5 * np.sin(23 * ph + rng.random() * 6)
    cum = base_y - alt * perfil + ru * (perfil > 0.02) * perfil ** 0.3
    cum = np.where(perfil <= 0, H + 10, cum)
    c = cores or ((236, 246, 255), (140, 164, 220), (90, 100, 170), (44, 52, 112))
    return montanha(cum, c[0], c[1], c[2], c[3], 220, bruma, forca, seed + 1), cum


def _ceu_castelo():
    rgb = np.repeat(gradiente([(0, (10, 8, 30)), (240, (28, 24, 72)), (480, (58, 54, 116)), (660, (96, 92, 156)), (720, (96, 92, 156))]), W, axis=1)
    Y = np.arange(H)[:, None].astype(np.float32)
    X = np.arange(W)[None, :].astype(np.float32)
    mancha = fbm(320, 110, 5, 5)
    rgb = rgb * (0.7 + 0.6 * mancha[..., None])
    # estrelas
    rng = np.random.default_rng(4)
    for _ in range(150):
        x, y = rng.integers(0, W), rng.integers(0, 340)
        rgb[y, x] += (np.array([225, 235, 255]) - rgb[y, x]) * rng.uniform(0.3, 0.9)
    # clarão de relâmpago distante
    d = np.sqrt(((X - 300) / 1.5) ** 2 + (Y - 250) ** 2)
    rgb += np.array((150, 170, 255), np.float32) * (np.exp(-d / 120.0) * 0.4)[..., None]
    d2 = np.sqrt((X - 240) ** 2 + ((Y - 220) / 0.5) ** 2)
    rgb += np.array((140, 150, 255), np.float32) * (np.exp(-((d2) / 40.0)) * 0.18)[..., None]
    # lua gelada
    cxl, cyl = 1030, 150
    d = np.sqrt((X - cxl) ** 2 + (Y - cyl) ** 2)
    rgb += np.array((150, 190, 255), np.float32) * (np.exp(-d / 90.0) * 0.45)[..., None]
    disco = np.clip(48 - d, 0, 1)
    textura = fbm(40, 40, 7, 3)
    lua = np.array((226, 242, 255), np.float32) * (0.82 + 0.28 * textura[..., None])
    rgb += (lua - rgb) * disco[..., None]
    return para_superficie(rgb)


def _nuvens_castelo():
    n = 0.55 * fbm(320, 70, 12, 4) + 0.45 * fbm(160, 50, 13, 4)
    Y = np.arange(H)[:, None].astype(np.float32)
    env = np.clip(1 - np.abs(Y - 200) / 190, 0, 1) ** 0.5
    d = n * (0.45 + 0.75 * env)
    al = ss(0.46, 0.62, d) * 0.92
    sup = np.roll(d, 10, axis=0)
    luz = np.clip((d - sup) * 7 + 0.12, 0, 1)
    escuro, claro = np.array((26, 24, 66), np.float32), np.array((120, 126, 204), np.float32)
    rgb = escuro + (claro - escuro) * luz[..., None] * 0.85
    # relâmpago nas bordas
    X = np.arange(W)[None, :]
    flash = np.exp(-(((X - 300 + 640) % W - 640) / 220.0) ** 2) * 0.5
    rgb += np.array((120, 130, 255), np.float32) * (luz * flash)[..., None] * 0.7
    return para_superficie(rgb, al)


def _longe_castelo():
    def junta(rgb, alfa, r2, a2):
        novo_a = a2 + alfa * (1 - a2)
        rgb = (r2 * a2[..., None] + rgb * (alfa * (1 - a2))[..., None]) / np.maximum(novo_a, 1e-4)[..., None]
        return rgb, novo_a
    rgb = np.zeros((H, W, 3), np.float32)
    alfa = np.zeros((H, W), np.float32)
    bruma = (76, 76, 140)
    cum1 = cadeia(500, 420, [2, 3, 5, 8, 13, 22], 17, 0.7)
    r, a = montanha(cum1, (176, 196, 244), (96, 108, 184), (72, 80, 150), (40, 44, 104), 240, bruma, 0.45, 61)
    rgb, alfa = junta(rgb, alfa, r, a)
    cum2 = cadeia(590, 300, [3, 4, 7, 11, 18, 31], 19, 0.7)
    r, a = montanha(cum2, (150, 170, 226), (80, 90, 166), (54, 60, 126), (30, 32, 84), 170, (60, 60, 120), 0.3, 71)
    rgb, alfa = junta(rgb, alfa, r, a)
    return para_superficie(rgb, alfa)


def _castelo_distante():
    s = nova()
    (r, a), cum = _monte_sob(640, 640, 760, 235, 5, bruma=(70, 70, 134), forca=0.35,
                              cores=((150, 170, 226), (84, 94, 170), (56, 62, 128), (32, 34, 88)))
    # platô achatado sob o castelo
    s.blit(para_superficie(r, a), (0, 0))
    brilho(s, 640, 360, 260, (110, 130, 230), 0.25, 1.5)
    castelo(s, 640, 446, 1.35, PAL_DISTANTE, detalhe=1, seed=4)
    # base do platô cobrindo o pé do castelo
    sb = nova()
    poligono(sb, (50, 56, 118), [(640 - 210, 452), (640 + 210, 452), (640 + 260, 520), (640 - 260, 520)])
    s.blit(sb, (0, 0))
    r2, a2 = _monte_sob(640, 720, 900, 300, 8, bruma=(70, 70, 134), forca=0.3,
                        cores=((150, 170, 226), (84, 94, 170), (56, 62, 128), (32, 34, 88)))[0]
    a2 = a2 * (np.arange(H)[:, None] > 470)
    s.blit(para_superficie(r2, a2), (0, 0))
    return s


def _castelo_proximo():
    s = nova()
    brilho(s, 640, 330, 520, (110, 130, 240), 0.22, 1.4)
    castelo(s, 640, 590, 3.2, PAL_TEMPESTADE, detalhe=2, seed=6)
    # montículo rochoso/nevado na base
    xs = np.arange(W)
    d = np.clip((np.abs(xs - 640) - 440) / 210.0, 0, 1)
    ph = 2 * np.pi * xs / W
    cum = 596 + 112 * d * d * (3 - 2 * d) + 6 * np.sin(9 * ph) + 4 * np.sin(23 * ph)
    r, a = montanha(cum, (214, 230, 252), (110, 128, 200), (70, 80, 150), (36, 40, 98), 200, (50, 52, 112), 0.0, 81)
    a = np.where(np.arange(H)[:, None] >= 700, 1.0, a)
    s.blit(para_superficie(r, a), (0, 0))
    faiscas(s, 18, 3, 120, 560, (255, 230, 160))
    return s


def _pinheiros_tempestade():
    s = nova()
    # pontes congeladas distantes (arcos) entre pilares
    rng = random.Random(41)
    cor_p = (62, 74, 144)
    cor_l = (118, 142, 214)
    for xa, xb, ya in ((70, 330, 360), (520, 800, 420), (930, 1230, 380)):
        w = xb - xa
        for pil in (xa, xb):
            poligono(s, cor_p, [(pil - 10, ya), (pil + 10, ya), (pil + 16, 720), (pil - 16, 720)])
            poligono(s, cor_l, [(pil + 2, ya), (pil + 10, ya), (pil + 16, 720), (pil + 6, 720)])
        pygame.draw.rect(s, cor_l, (xa, ya - 3, w, 4))
        for k in range(0, 4):
            ax = xa + w * (k + 0.5) / 4
            pygame.draw.arc(s, cor_p, (ax - w / 8, ya, w / 4, 44), 0, math.pi, 4)
        for k in range(0, int(w), 14):
            retangulo(s, cor_l, xa + k, ya - 9, 2, 7)
        pygame.draw.line(s, cor_l, (xa, ya - 9), (xb, ya - 9), 1)
    # cumeada nevada ao fundo e pinheiros curvados
    cum = cadeia(560, 90, [3, 6, 10, 17, 27], 53, 0.6)
    r, a = montanha(cum, (140, 150, 210), (60, 66, 140), (46, 50, 112), (22, 24, 70), 40, (40, 40, 100), 0.1, 91)
    a = np.where(np.arange(H)[:, None] >= 655, 1.0, a)
    s.blit(para_superficie(r, a), (0, 0))
    for _ in range(16):
        x = rng.randrange(W)
        y = int(cum[x]) + rng.randint(2, 20)
        pinheiro(s, x, y, rng.randint(80, 150), (14, 16, 46), (84, 94, 160), vento=0.17 + rng.uniform(0, 0.1))
    cum2 = cadeia(640, 50, [4, 7, 12, 19], 57, 0.6)
    r, a = montanha(cum2, (110, 120, 190), (40, 44, 110), (30, 32, 84), (14, 14, 46), 20, (30, 30, 80), 0.0, 93)
    a = np.where(np.arange(H)[:, None] >= 664, 1.0, a)
    s.blit(para_superficie(r, a), (0, 0))
    for _ in range(12):
        x = rng.randrange(W)
        y = int(cum2[x]) + rng.randint(2, 14)
        pinheiro(s, x, y, rng.randint(110, 190), (10, 11, 34), (60, 68, 130), vento=0.2 + rng.uniform(0, 0.1))
    # flocos / neve soprada
    for _ in range(60):
        x, y = rng.randrange(W), rng.randrange(100, 640)
        pygame.draw.line(s, (200, 214, 245, 150), (x, y), (x - rng.randint(4, 9), y + 1))
    return s


def gerar_castelo(pasta):
    saidas = {"ceu.png": _ceu_castelo(), "nuvens.png": _nuvens_castelo(), "montanhas_longe.png": _longe_castelo(),
              "castelo_distante.png": _castelo_distante(), "castelo_proximo.png": _castelo_proximo(),
              "pinheiros_tempestade.png": _pinheiros_tempestade()}
    for nome, sup in saidas.items():
        salvar_imagem(f"cenarios/{pasta}/{nome}", sup)
    return saidas


# ================================================================ MENU
def _menu_castelo(ceu_geleira):
    s = nova()
    # aurora translúcida sobre o céu
    Y = np.arange(H)[:, None].astype(np.float32)
    X = np.arange(W)[None, :].astype(np.float32)
    fundo = np.zeros((H, W, 3), np.float32)
    acum = np.zeros((H, W), np.float32)
    rng = np.random.default_rng(15)
    xs = X / W * 2 * np.pi
    raios = fbm(5, 240, 33, 2)
    for k in range(3):
        ph = rng.random(3) * 6.28
        yc = 150 + k * 58 + 34 * np.sin(2 * xs + ph[0]) + 16 * np.sin(5 * xs + ph[1])
        dd = Y - yc
        sd = np.where(dd > 0, 14.0, 80.0)
        inten = np.exp(-(dd / sd) ** 2) * (0.5 + 0.9 * raios)
        t = np.clip(-dd / 150.0, 0, 1)[..., None]
        col = np.array((90, 240, 210), np.float32) + (np.array((180, 140, 250), np.float32) - np.array((90, 240, 210), np.float32)) * t
        w = np.clip(inten, 0, 1) * 0.42
        fundo = fundo * (1 - w[..., None]) + col * w[..., None]
        acum = acum + w * (1 - acum)
    s.blit(para_superficie(fundo / np.maximum(acum, 1e-4)[..., None], acum), (0, 0))
    brilho(s, 920, 330, 520, (170, 230, 255), 0.35, 1.5)
    # montanha nevada do castelo (à direita)
    cores = ((250, 253, 255), (166, 206, 242), (120, 156, 214), (76, 104, 176))
    (r, a), cum = _monte_sob(930, 700, 1180, 220, 7, bruma=(210, 232, 250), forca=0.0, cores=cores)
    s.blit(para_superficie(r, a), (0, 0))
    brilho(s, 930, 330, 380, (255, 244, 200), 0.18, 1.6)
    castelo(s, 930, 505, 2.35, PAL_MENU, detalhe=2, seed=9)
    # neve cobrindo o pé do castelo
    sb = nova()
    poligono(sb, (240, 250, 255), [(930 - 340, 506), (930 + 340, 506), (930 + 420, 560), (930 - 420, 560)])
    s.blit(sb, (0, 0))
    (r, a), cum = _monte_sob(930, 740, 1180, 160, 7, bruma=(210, 232, 250), forca=0.0, cores=cores)
    a = a * (np.arange(H)[:, None] > 500)
    s.blit(para_superficie(r, a), (0, 0))
    # colinas baixas à esquerda
    xs_ = np.arange(W)
    ph = 2 * np.pi * xs_ / W
    base = 650 + 22 * np.sin(2 * ph + 1) + 12 * np.sin(5 * ph) + 6 * np.sin(11 * ph)
    r, a = montanha(base, (250, 253, 255), (168, 206, 242), (140, 180, 228), (100, 140, 206), 900, (214, 232, 250), 0.0, 17)
    a = np.where(np.arange(H)[:, None] >= 690, 1.0, a)
    # esmaece a colina para a direita (a montanha do castelo domina)
    s.blit(para_superficie(r, a), (0, 0))
    _pinheirais(s, base, 5, 11, 50, 95, (28, 76, 108), (232, 244, 255), 0.0, 2)
    faiscas(s, 30, 21, 40, 600, (255, 255, 255))
    return s


# ================================================================ MINIATURAS
def _vinheta(img):
    w, h = img.get_size()
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    f = 1 - 0.38 * ss(0.65, 1.35, d)
    a = np.frombuffer(pygame.image.tobytes(img, "RGB"), np.uint8).reshape(h, w, 3).astype(np.float32)
    a = a * f[..., None]
    out = pygame.image.frombuffer(np.clip(a, 0, 255).astype(np.uint8).tobytes(), (w, h), "RGB").copy()
    pygame.draw.rect(out, (232, 244, 255), (0, 0, w, h), 2)
    pygame.draw.rect(out, (20, 36, 90), (0, 0, w, h), 1)
    return out


def _miniatura(camadas, nome, ordem):
    total = pygame.Surface((W, H))
    for k in ordem:
        total.blit(camadas[k], (0, 0))
    mini = pygame.transform.smoothscale(total, (384, 216))
    salvar_imagem(f"interface/{nome}", _vinheta(mini))


# ================================================================ SALÃO FINAL, CÂMARA SECRETA, EPÍLOGO
def _salao_fundo():
    """Parede de gelo do salão do castelo: arcadas altas com janelas abertas para a aurora (tileável)."""
    rgb = np.repeat(gradiente([(0, (14, 22, 66)), (380, (30, 50, 120)), (720, (58, 96, 172))]), W, axis=1)
    rgb = rgb * (0.86 + 0.28 * fbm(160, 80, 41, 4)[..., None])
    s = para_superficie(rgb).convert_alpha()
    sala = nova()
    for cx in (160, 480, 800, 1120):
        topo, raio = 110, 74
        for y in range(topo - raio, 470):
            if y < topo:
                meia = int(math.sqrt(max(0, raio * raio - (topo - y) ** 2)))
            else:
                meia = raio
            f = (y - (topo - raio)) / (470 - (topo - raio))
            cor = (int(34 + 90 * f), int(190 - 40 * f), int(210 - 60 * f))
            if y < 260:                                   # aurora violeta no alto da janela
                g = (1 - y / 260) * 0.55
                cor = tuple(int(cor[i] * (1 - g) + (176, 130, 240)[i] * g) for i in range(3))
            pygame.draw.line(sala, cor + (255,), (cx - meia, y), (cx + meia, y))
        pygame.draw.rect(sala, (170, 226, 250, 255), (cx - raio - 6, topo, 6, 360))
        pygame.draw.rect(sala, (170, 226, 250, 255), (cx + raio, topo, 6, 360))
        pygame.draw.arc(sala, (170, 226, 250, 255), (cx - raio - 6, topo - raio - 6, 2 * raio + 12, 2 * raio + 12),
                        0, math.pi, 6)
        pygame.draw.rect(sala, (170, 226, 250, 255), (cx - 3, topo - raio, 6, 420))           # trave central
        pygame.draw.rect(sala, (170, 226, 250, 255), (cx - raio - 12, 470, 2 * raio + 24, 12))   # peitoril
        brilho(sala, cx, 300, 230, (150, 226, 255), 0.32, 1.6)
    faiscas(sala, 34, 43, 60, 460, (230, 244, 255), (1, 1))
    s.blit(sala, (0, 0))
    return s


def _salao_pilares():
    """Colunas de gelo mais próximas (parallax), com capitel, base e brilho azulado."""
    s = nova()
    for cx in (0, 640):
        brilho(s, cx, 330, 150, (140, 220, 255), 0.22, 1.8)
        retangulo(s, (34, 60, 140, 255), cx - 38, 0, 76, H)
        retangulo(s, (84, 140, 220, 255), cx - 38, 0, 16, H)
        retangulo(s, (150, 214, 250, 255), cx - 30, 0, 4, H)
        retangulo(s, (20, 36, 96, 255), cx + 24, 0, 14, H)
        retangulo(s, (56, 100, 184, 255), cx - 54, 70, 108, 40)             # capitel
        retangulo(s, (150, 214, 250, 255), cx - 54, 70, 108, 5)
        retangulo(s, (56, 100, 184, 255), cx - 54, 560, 108, 60)            # base
        retangulo(s, (150, 214, 250, 255), cx - 54, 560, 108, 5)
        cristal(s, cx + 42, 560, 18, 42, 4, (120, 200, 250, 255), (70, 150, 230, 255), (220, 246, 255, 255))
    return s


def _camara_fundo():
    """Caverna secreta: violeta profundo com um halo dourado no centro (a lembrança)."""
    rgb = np.repeat(gradiente([(0, (16, 12, 44)), (400, (34, 26, 84)), (720, (52, 38, 112))]), W, axis=1)
    rgb = rgb * (0.82 + 0.36 * fbm(160, 90, 51, 4)[..., None])
    s = para_superficie(rgb).convert_alpha()
    sala = nova()
    brilho(sala, 640, 420, 460, (255, 214, 120), 0.30, 1.7)
    rng = random.Random(52)
    for x in range(0, W, 64):                                              # estalactites escuras no teto
        h = rng.randint(70, 190)
        poligono(sala, (22, 16, 60, 255), [(x - 30, 0), (x + 34, 0), (x + rng.randint(-6, 6), h)])
        poligono(sala, (48, 38, 104, 255), [(x - 4, 0), (x + 34, 0), (x + 6, h * 0.8)])
    faiscas(sala, 44, 53, 80, 620, (255, 224, 150), (1, 2))
    s.blit(sala, (0, 0))
    return s


def _camara_cristais():
    """Aglomerados de cristais violeta e dourados junto ao chão (camada próxima)."""
    s = nova()
    rng = random.Random(54)
    for cx in range(40, W, 150):
        for _ in range(3):
            dourado = rng.random() < 0.3
            esq, dir_, ponta = (((255, 214, 96, 255), (226, 150, 40, 255), (255, 244, 190, 255)) if dourado else
                                ((150, 130, 230, 255), (98, 78, 190, 255), (210, 200, 255, 255)))
            cristal(s, cx + rng.randint(-30, 30), 720, rng.randint(22, 38), rng.randint(60, 150),
                    rng.randint(-10, 10), esq, dir_, ponta)
    return s


def _epilogo_ceu():
    """Amanhecer sobre o Reino Glacial: o inverno eterno termina."""
    rgb = np.repeat(gradiente([(0, (36, 44, 116)), (260, (120, 104, 190)), (460, (255, 168, 150)),
                               (600, (255, 218, 160)), (720, (255, 236, 196))]), W, axis=1)
    X = np.arange(W)[None, :].astype(np.float32)
    Y = np.arange(H)[:, None].astype(np.float32)
    rgb = rgb * (0.94 + 0.12 * fbm(320, 100, 61, 4)[..., None])
    d = np.sqrt((X - 640) ** 2 + ((Y - 560) * 1.4) ** 2)
    rgb += np.array((255, 214, 120), np.float32) * (np.exp(-d / 240.0) * 0.55)[..., None]
    s = para_superficie(rgb).convert_alpha()
    sol = nova()
    pygame.draw.circle(sol, (255, 244, 200, 255), (640, 560), 64)
    brilho(sol, 640, 560, 200, (255, 236, 170), 0.6, 1.4)
    faiscas(sol, 40, 63, 10, 260, (255, 255, 255), (1, 1))
    s.blit(sol, (0, 0))
    return s


def gerar_interiores():
    saidas = {"salao/fundo.png": _salao_fundo(), "salao/pilares.png": _salao_pilares(),
              "camara/fundo.png": _camara_fundo(), "camara/cristais.png": _camara_cristais(),
              "epilogo/ceu.png": _epilogo_ceu()}
    for nome, sup in saidas.items():
        salvar_imagem(f"cenarios/{nome}", sup)


def gerar():
    random.seed(1234)
    gerar_interiores()
    g = gerar_geleira("geleira")
    c = gerar_cavernas("cavernas")
    k = gerar_castelo("castelo")
    salvar_imagem("cenarios/menu/menu_castelo.png", _menu_castelo(g["ceu.png"]))
    _miniatura(g, "regiao_geleira.png", ["ceu.png", "nuvens.png", "montanhas_longe.png", "montanhas_perto.png"])
    _miniatura(c, "regiao_cavernas.png", ["ceu.png", "paredes_longe.png", "estalactites.png", "cristais_perto.png"])
    _miniatura(k, "regiao_castelo.png", ["ceu.png", "nuvens.png", "montanhas_longe.png", "castelo_proximo.png",
                                         "pinheiros_tempestade.png"])
    print("Cenários gerados em", RECURSOS / "cenarios")


if __name__ == "__main__":
    iniciar_pygame()
    gerar()
