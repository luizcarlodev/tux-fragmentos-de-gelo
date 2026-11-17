"""Gerador de áudio provisório (músicas e efeitos) do tema glacial.

Tudo é sintetizado com numpy (sinos, celesta, pads, baixos, percussão suave) e gravado em
``recursos/sons/musicas`` e ``recursos/sons/efeitos`` como WAV mono de 16 bits.
As músicas em loop são renderizadas em buffer circular (eco e notas "dão a volta"), então
o final emenda no início sem estalo.

Uso:   python ferramentas/arte/sons.py
"""
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np  # noqa: E402

from ferramentas.arte.base import RECURSOS, TAXA, iniciar_pygame, nota_hz, salvar_wav  # noqa: E402

SR = TAXA
PASTA_MUSICAS = RECURSOS / "sons" / "musicas"
PASTA_EFEITOS = RECURSOS / "sons" / "efeitos"

PICO_MUSICA = 0.32
PICO_EFEITO = 0.45

# ====================================================================== síntese básica
SINO = [(1.0, 1.0, 2.2), (2.756, 0.45, 3.5), (5.404, 0.22, 6.0), (8.93, 0.10, 9.0)]
CELESTA = [(1.0, 1.0, 5.0), (2.0, 0.35, 7.0), (3.0, 0.15, 9.0), (4.0, 0.08, 12.0)]
HARPA = [(1.0, 1.0, 3.5), (2.0, 0.5, 4.5), (3.0, 0.3, 6.0), (4.0, 0.2, 8.0), (5.0, 0.1, 10.0)]


def tempo(d):
    return np.arange(int(SR * d)) / SR


def ataque_soltura(n, ataque=0.004, solta=0.05):
    """Envelope linear de ataque e soltura para um vetor de ``n`` amostras."""
    env = np.ones(n)
    na = max(1, min(n, int(SR * ataque)))
    ns = max(1, min(n, int(SR * solta)))
    env[:na] *= np.linspace(0, 1, na)
    env[-ns:] *= np.linspace(1, 0, ns)
    return env


def parciais(freq, dur, partes, ataque=0.003, solta=0.04):
    """Soma de senoides com decaimento exponencial (timbre de sino/celesta/harpa)."""
    t = tempo(dur)
    saida = np.zeros_like(t)
    for razao, amp, decaimento in partes:
        f = freq * razao
        if f > SR / 2.2:
            continue
        saida += amp * np.sin(2 * np.pi * f * t) * np.exp(-decaimento * t)
    return saida * ataque_soltura(len(t), ataque, solta) * 0.5


def sino(freq, dur=1.8):
    return parciais(freq, dur, SINO, 0.002, 0.08)


def celesta(freq, dur=1.2):
    return parciais(freq, dur, CELESTA, 0.002, 0.06)


def harpa(freq, dur=1.0):
    return parciais(freq, dur, HARPA, 0.002, 0.05)


def pad(freq, dur, ataque=0.5, solta=0.6, brilho=0.25):
    """Pad suave: senoides levemente desafinadas + oitava abaixo triangular, com tremolo lento."""
    t = tempo(dur + solta)
    s = (np.sin(2 * np.pi * freq * t) + np.sin(2 * np.pi * freq * 1.004 * t)
         + brilho * np.sin(2 * np.pi * freq * 2 * t) + 0.4 * np.sin(2 * np.pi * freq * 0.5 * t))
    s *= 1 + 0.08 * np.sin(2 * np.pi * 0.35 * t)
    env = np.ones_like(t)
    na = int(SR * ataque)
    env[:na] = np.linspace(0, 1, na)
    ns = int(SR * solta)
    env[-ns:] = np.linspace(1, 0, ns)
    return s * env * 0.3


def cordas(freq, dur, ataque=0.12, solta=0.25):
    """Cordas sintéticas (dente de serra suave) para o tema tenso do castelo."""
    t = tempo(dur + solta)
    s = np.zeros_like(t)
    for n in range(1, 8):
        s += np.sin(2 * np.pi * freq * n * t + n) / n
        s += np.sin(2 * np.pi * freq * 1.006 * n * t) / n
    s *= 1 + 0.05 * np.sin(2 * np.pi * 5.2 * t)
    env = np.ones_like(t)
    na = int(SR * ataque)
    env[:na] = np.linspace(0, 1, na)
    ns = int(SR * solta)
    env[-ns:] = np.linspace(1, 0, ns)
    return s * env * 0.18


def baixo(freq, dur=0.6, decaimento=4.0):
    t = tempo(dur)
    tri = 2 / np.pi * np.arcsin(np.sin(2 * np.pi * freq * t))
    s = (0.8 * tri + 0.5 * np.sin(2 * np.pi * freq * t)) * np.exp(-decaimento * t)
    return s * ataque_soltura(len(t), 0.004, 0.03)


def pulso(freq, dur, largura=0.25, decaimento=9.0):
    """Onda de pulso curta (usada só como tempero)."""
    t = tempo(dur)
    fase = (freq * t) % 1.0
    s = np.where(fase < largura, 1.0, -1.0) * np.exp(-decaimento * t)
    return s * ataque_soltura(len(t), 0.002, 0.02) * 0.35


def ruido(dur, rng=None):
    rng = rng or np.random
    return rng.uniform(-1, 1, int(SR * dur))


def passa_baixa(x, janela):
    janela = max(1, int(janela))
    if janela == 1:
        return x.copy()
    return np.convolve(x, np.ones(janela) / janela, mode="same")


def passa_alta(x, janela):
    return x - passa_baixa(x, janela)


def varredura(f0, f1, dur, tipo="seno", exp=False):
    """Oscilador com frequência variando de ``f0`` a ``f1``."""
    n = int(SR * dur)
    if exp:
        f = np.geomspace(f0, f1, n)
    else:
        f = np.linspace(f0, f1, n)
    fase = np.cumsum(f) / SR
    if tipo == "seno":
        return np.sin(2 * np.pi * fase)
    if tipo == "triangulo":
        return 2 / np.pi * np.arcsin(np.sin(2 * np.pi * fase))
    if tipo == "pulso":
        return np.where((fase % 1.0) < 0.25, 1.0, -1.0)
    return np.where((fase % 1.0) < 0.5, 1.0, -1.0)


def decaimento(n, taxa):
    return np.exp(-taxa * np.arange(n) / SR)


def whoosh(dur, de, para, vol=1.0):
    """Ruído filtrado cuja 'cor' varia (de ``de`` a ``para`` em amostras de janela do filtro)."""
    x = ruido(dur)
    janelas = [1, 2, 4, 8, 16, 32, 64]
    versoes = [passa_baixa(x, j) * (1 + 0.6 * np.log2(j)) for j in janelas]
    n = len(x)
    pos = np.linspace(np.log2(de), np.log2(para), n)
    saida = np.zeros(n)
    peso_total = np.zeros(n)
    for j, v in zip(janelas, versoes):
        p = np.exp(-((pos - np.log2(j)) ** 2) / 1.0)
        saida += p * v
        peso_total += p
    return saida / np.maximum(peso_total, 1e-6) * vol


def mixar(*partes, extra=0.0):
    """Soma ``(vetor, instante_em_segundos[, volume])`` em um único vetor."""
    fim = 0
    for p in partes:
        fim = max(fim, int(p[1] * SR) + len(p[0]))
    saida = np.zeros(fim + int(extra * SR))
    for p in partes:
        vol = p[2] if len(p) > 2 else 1.0
        i = int(p[1] * SR)
        saida[i:i + len(p[0])] += p[0] * vol
    return saida


def eco_linear(x, atrasos):
    """Eco simples não circular: ``atrasos`` = [(segundos, ganho)]."""
    maior = max(int(a * SR) for a, _ in atrasos)
    saida = np.concatenate([x, np.zeros(maior)])
    for a, g in atrasos:
        i = int(a * SR)
        saida[i:i + len(x)] += x * g
    return saida


def normalizar(x, pico):
    m = np.max(np.abs(x))
    return x / m * pico if m > 0 else x


def gravar(pasta, nome, x):
    x = np.nan_to_num(x)
    salvar_wav(pasta / f"{nome}.wav", x.tolist())


# ====================================================================== efeitos
def sfx_pulo():
    s = varredura(320, 780, 0.15, exp=True) * decaimento(int(SR * 0.15), 8) * ataque_soltura(int(SR * 0.15), 0.003, 0.03)
    return mixar((s, 0, 0.7), (sino(1568, 0.3), 0.03, 0.35))


def sfx_moeda():
    return mixar((sino(nota_hz(88), 0.5), 0.0, 0.8), (sino(nota_hz(95), 0.7), 0.07, 1.0))


def sfx_dano():
    n = int(SR * 0.35)
    queda = varredura(520, 110, 0.35, "triangulo") * decaimento(n, 5)
    r = passa_baixa(ruido(0.2), 6) * decaimento(int(SR * 0.2), 14)
    return mixar((queda, 0, 0.8), (r, 0, 0.9))


def sfx_derrota():
    notas = [69, 66, 62, 57]
    partes = [(sino(nota_hz(n), 1.2), i * 0.28, 0.9) for i, n in enumerate(notas)]
    partes.append((pad(nota_hz(45), 1.4, 0.2, 0.7), 0.0, 0.8))
    return mixar(*partes)


def sfx_selecao():
    return sino(1318, 0.22) * 0.9


def sfx_confirmacao():
    return mixar((sino(nota_hz(84), 0.4), 0.0), (sino(nota_hz(91), 0.6), 0.09))


def sfx_mensagem_erro():
    b = varredura(170, 150, 0.12, "triangulo") * ataque_soltura(int(SR * 0.12), 0.005, 0.03)
    return mixar((b, 0.0), (b, 0.16, 0.9))


def sfx_bloco_bater():
    n = int(SR * 0.14)
    t = varredura(170, 70, 0.14) * decaimento(n, 22)
    tic = passa_alta(ruido(0.03), 8) * decaimento(int(SR * 0.03), 80)
    return mixar((t, 0, 1.0), (tic, 0, 0.5), (sino(1760, 0.2), 0.0, 0.15))


def sfx_bloco_quebrar():
    rng = np.random.RandomState(7)
    cr = passa_alta(ruido(0.35, rng), 5) * decaimento(int(SR * 0.35), 12)
    partes = [(cr, 0, 0.8)]
    for i in range(9):
        f = rng.choice([1760, 2093, 2349, 2637, 3136, 3520])
        partes.append((sino(f, 0.3), rng.uniform(0, 0.28), rng.uniform(0.15, 0.35)))
    return mixar(*partes)


def sfx_checkpoint():
    notas = [76, 83, 88]
    partes = [(celesta(nota_hz(n), 0.7), i * 0.1) for i, n in enumerate(notas)]
    partes.append((sino(nota_hz(100), 0.9), 0.3, 0.3))
    return mixar(*partes)


def sfx_esmagar():
    n = int(SR * 0.14)
    s = varredura(420, 90, 0.14, "triangulo") * decaimento(n, 14)
    tic = passa_baixa(ruido(0.05), 3) * decaimento(int(SR * 0.05), 40)
    return mixar((s, 0, 1.0), (tic, 0, 0.6))


def sfx_estrela():
    notas = [72, 76, 79, 84, 88, 91, 96]
    partes = [(celesta(nota_hz(n), 0.5), i * 0.07) for i, n in enumerate(notas)]
    partes.append((sino(nota_hz(103), 0.9), 0.5, 0.5))
    return mixar(*partes)


def sfx_item_surge():
    n = int(SR * 0.4)
    s = varredura(300, 1000, 0.4, exp=True) * ataque_soltura(n, 0.02, 0.1)
    return mixar((s, 0, 0.6), (sino(1760, 0.5), 0.3, 0.4))


def sfx_vida_extra():
    notas = [72, 76, 79, 84]
    partes = [(sino(nota_hz(n), 0.8), i * 0.12) for i, n in enumerate(notas)]
    partes.append((pad(nota_hz(60), 0.6, 0.05, 0.3), 0.0, 0.3))
    return mixar(*partes)


def sfx_mastro():
    n = int(SR * 0.9)
    gl = varredura(440, 1760, 0.9, exp=True) * ataque_soltura(n, 0.05, 0.4) * 0.5
    return mixar((gl, 0, 0.7), (sino(nota_hz(96), 1.4), 0.7, 0.7), (sino(nota_hz(103), 1.4), 0.85, 0.5))


def sfx_projetil():
    n = int(SR * 0.22)
    s = varredura(1100, 520, 0.22, "triangulo") * decaimento(n, 6) * ataque_soltura(n, 0.003, 0.05)
    return mixar((s, 0, 0.9), (whoosh(0.22, 2, 12), 0, 0.15))


def sfx_dash():
    w = whoosh(0.24, 3, 40) * ataque_soltura(int(SR * 0.24), 0.04, 0.12)
    return mixar((w, 0, 1.0), (varredura(300, 900, 0.18) * ataque_soltura(int(SR * 0.18), 0.02, 0.1), 0, 0.12))


def sfx_ataque():
    w = whoosh(0.16, 2, 30) * ataque_soltura(int(SR * 0.16), 0.02, 0.07)
    pop = varredura(260, 110, 0.1) * decaimento(int(SR * 0.1), 30)
    return mixar((w, 0, 0.9), (pop, 0.1, 0.7))


def sfx_ataque_acerto():
    r = passa_alta(ruido(0.12), 4) * decaimento(int(SR * 0.12), 30)
    th = varredura(220, 80, 0.14) * decaimento(int(SR * 0.14), 24)
    return mixar((r, 0, 0.8), (th, 0, 0.9), (sino(2093, 0.4), 0.0, 0.3))


def sfx_fragmento():
    """Fanfarra mágica especial: arpejo pentatônico ascendente + acorde cristalino em crescendo."""
    notas = [72, 76, 79, 84, 88, 91, 96, 100]
    partes = [(celesta(nota_hz(n), 0.9), i * 0.09, 0.8) for i, n in enumerate(notas)]
    inicio = len(notas) * 0.09
    for n in (72, 79, 84, 88, 91):
        partes.append((sino(nota_hz(n + 12), 1.8), inicio, 0.35))
    partes.append((pad(nota_hz(60), 1.5, 0.35, 0.8), 0.0, 0.9))
    rng = np.random.RandomState(11)
    for i in range(10):
        partes.append((sino(rng.choice([3136, 3520, 3951, 4186]), 0.5), inicio + rng.uniform(0, 1.2), 0.15))
    return mixar(*partes)


def sfx_chave():
    notas = [67, 74, 79]
    partes = [(sino(nota_hz(n), 1.0), i * 0.28, 0.8) for i, n in enumerate(notas)]
    for n in (67, 74, 79, 83):
        partes.append((sino(nota_hz(n + 12), 1.6), 0.9, 0.4))
    partes.append((pad(nota_hz(55), 1.2, 0.3, 0.5), 0.8, 0.8))
    return mixar(*partes)


def sfx_prisao_quebra():
    rng = np.random.RandomState(3)
    est = passa_alta(ruido(0.9, rng), 6) * decaimento(int(SR * 0.9), 4)
    thud = varredura(150, 50, 0.4) * decaimento(int(SR * 0.4), 9)
    partes = [(est, 0, 0.8), (thud, 0, 0.9)]
    for i in range(22):
        f = rng.choice([1760, 2093, 2637, 3136, 3520, 4186])
        partes.append((sino(f, 0.35), rng.uniform(0.02, 0.9), rng.uniform(0.1, 0.3)))
    return mixar(*partes)


def sfx_portal():
    n = int(SR * 1.3)
    t = tempo(1.3)
    zumbido = (np.sin(2 * np.pi * 110 * t) + 0.5 * np.sin(2 * np.pi * 165.5 * t)) * (1 + 0.4 * np.sin(2 * np.pi * 9 * t))
    zumbido *= ataque_soltura(n, 0.5, 0.5)
    sub = varredura(300, 1400, 1.3, exp=True) * ataque_soltura(n, 0.6, 0.4) * 0.35
    return mixar((zumbido, 0, 0.45), (sub, 0, 0.6), (sino(nota_hz(91), 1.2), 0.3, 0.4))


def sfx_golem_dano():
    n = int(SR * 0.3)
    g = varredura(95, 70, 0.3, "serra") * decaimento(n, 8)
    g = passa_baixa(g, 10)
    r = passa_alta(ruido(0.1), 6) * decaimento(int(SR * 0.1), 40)
    return mixar((g, 0, 1.0), (r, 0, 0.5), (sino(1320, 0.3), 0.0, 0.2))


def sfx_golem_passo():
    n = int(SR * 0.28)
    t = varredura(75, 38, 0.28) * decaimento(n, 12)
    r = passa_baixa(ruido(0.12), 12) * decaimento(int(SR * 0.12), 25)
    return mixar((t, 0, 1.0), (r, 0, 0.6))


def sfx_pinguim_grito():
    n = int(SR * 0.28)
    vib = 1 + 0.05 * np.sin(2 * np.pi * 28 * tempo(0.28))
    f = np.linspace(780, 520, n) * vib
    s = np.where(((np.cumsum(f) / SR) % 1.0) < 0.3, 1.0, -1.0)
    s = passa_baixa(s, 3) * ataque_soltura(n, 0.01, 0.1) * decaimento(n, 3)
    return mixar((s, 0, 0.8), (s, 0.15, 0.5))


def sfx_morcego():
    partes = []
    for i in range(3):
        n = int(SR * 0.07)
        c = varredura(2600, 3600, 0.07) * ataque_soltura(n, 0.005, 0.02)
        partes.append((c, i * 0.1, 0.8))
    return mixar(*partes)


def sfx_segredo():
    notas = [64, 67, 70, 76, 75, 70]
    partes = [(sino(nota_hz(n), 1.6), i * 0.3, 0.8) for i, n in enumerate(notas)]
    partes.append((pad(nota_hz(52), 2.0, 0.6, 0.9), 0.2, 0.7))
    x = mixar(*partes)
    return eco_linear(x, [(0.25, 0.4), (0.5, 0.25), (0.75, 0.12)])


def sfx_congelar():
    rng = np.random.RandomState(5)
    partes = [(passa_alta(ruido(0.5, rng), 3) * decaimento(int(SR * 0.5), 6), 0, 0.35)]
    for i, f in enumerate([4186, 3520, 3136, 2637, 2349, 1976, 1568]):
        partes.append((sino(f, 0.4), i * 0.05, 0.4))
    return mixar(*partes)


def sfx_vitoria():
    notas = [(72, 0.0), (76, 0.15), (79, 0.3), (84, 0.45), (79, 0.7), (84, 0.85)]
    partes = [(sino(nota_hz(n), 1.2), t) for n, t in notas]
    partes += [(pad(nota_hz(60), 1.0, 0.1, 0.5), 0.45, 0.8)]
    return mixar(*partes)


EFEITOS = {
    "pulo": (sfx_pulo, 1.0), "moeda": (sfx_moeda, 1.0), "dano": (sfx_dano, 1.0), "derrota": (sfx_derrota, 1.0),
    "selecao": (sfx_selecao, 0.7), "confirmacao": (sfx_confirmacao, 0.9), "mensagem_erro": (sfx_mensagem_erro, 0.9),
    "bloco_bater": (sfx_bloco_bater, 1.0), "bloco_quebrar": (sfx_bloco_quebrar, 1.0),
    "checkpoint": (sfx_checkpoint, 1.0), "esmagar": (sfx_esmagar, 1.0), "estrela": (sfx_estrela, 1.0),
    "item_surge": (sfx_item_surge, 0.9), "vida_extra": (sfx_vida_extra, 1.0),
    "projetil": (sfx_projetil, 0.85), "dash": (sfx_dash, 0.95), "ataque": (sfx_ataque, 0.95),
    "ataque_acerto": (sfx_ataque_acerto, 1.0), "fragmento": (sfx_fragmento, 1.0), "chave": (sfx_chave, 1.0),
    "prisao_quebra": (sfx_prisao_quebra, 1.0), "portal": (sfx_portal, 1.0), "golem_dano": (sfx_golem_dano, 1.0),
    "golem_passo": (sfx_golem_passo, 1.0), "pinguim_grito": (sfx_pinguim_grito, 0.9),
    "morcego": (sfx_morcego, 0.8), "segredo": (sfx_segredo, 1.0), "congelar": (sfx_congelar, 0.9),
    "vitoria": (sfx_vitoria, 1.0),
}


def gerar_efeitos():
    np.random.seed(2024)
    for nome, (funcao, ganho) in EFEITOS.items():
        x = normalizar(funcao(), PICO_EFEITO * ganho)
        gravar(PASTA_EFEITOS, nome, x)
    print(f"efeitos: {len(EFEITOS)} arquivos")


# ====================================================================== músicas
def acorde(raiz, qualidade="M", extra=()):
    """Notas MIDI de um acorde (tríade + extensões em semitons relativos à raiz)."""
    terca = 4 if qualidade == "M" else 3
    quinta = 7 if qualidade != "d" else 6
    return [raiz, raiz + terca, raiz + quinta] + [raiz + e for e in extra]


def colocar(buf, t, som, vol=1.0):
    i = int(t * SR)
    fim = min(len(buf), i + len(som))
    if i < fim:
        buf[i:fim] += som[:fim - i] * vol


def melodia_frase(rng, acordes, escala, faixa, ritmos, passo_leap=0.12):
    """Gera 4 compassos de melodia: [(compasso, passo_8avo, midi, duracao_em_8avos)]."""
    lo, hi = faixa
    pool = [m for m in range(lo, hi + 1) if m % 12 in escala]
    notas = []
    anterior = pool[len(pool) // 2]
    for c in range(4):
        raiz, qual = acordes[c][0], acordes[c][1]
        pcs = {n % 12 for n in acorde(raiz, qual)}
        mascara = list(ritmos[rng.randint(len(ritmos))])
        if c == 3 and rng.rand() < 0.7:
            mascara = [1, 0, 0, 0, 0, 0, 0, 0] if rng.rand() < 0.5 else mascara
        passos = [i for i, m in enumerate(mascara) if m]
        if not passos:
            passos = [0]
        for k, p in enumerate(passos):
            if k == 0 or p == 0:
                cand = [m for m in pool if m % 12 in pcs]
                cand.sort(key=lambda m: abs(m - anterior))
                escolha = cand[min(len(cand) - 1, rng.randint(0, 2))]
            else:
                idx = pool.index(anterior) if anterior in pool else len(pool) // 2
                salto = rng.choice([-2, -1, -1, 1, 1, 2])
                if rng.rand() < passo_leap:
                    salto = rng.choice([-3, 3, 4])
                idx = int(np.clip(idx + salto, 0, len(pool) - 1))
                escolha = pool[idx]
            prox = passos[k + 1] if k + 1 < len(passos) else 8
            notas.append((c, p, escolha, prox - p))
            anterior = escolha
    return notas


def renderizar_musica(nome, bpm, acordes, ciclos, cfg, semente):
    rng = np.random.RandomState(semente)
    batida = 60.0 / bpm
    oitavo = batida / 2
    compasso = batida * 4
    compassos = 4 * ciclos
    total = compassos * compasso
    n = int(total * SR)
    folga = int(4 * SR)
    buf = np.zeros(n + folga)

    frases = [melodia_frase(rng, acordes, cfg["escala"], cfg["faixa"], cfg["ritmos"], cfg.get("saltos", 0.12))
              for _ in range(2)]

    for c in range(compassos):
        ciclo, k = divmod(c, 4)
        raiz, qual = acordes[k][0], acordes[k][1]
        extra = acordes[k][2] if len(acordes[k]) > 2 else ()
        tons = acorde(raiz, qual, extra)
        t0 = c * compasso

        # pad sustentado
        if cfg.get("pad", 0) > 0:
            for m in tons:
                colocar(buf, t0, pad(nota_hz(m + cfg.get("oitava_pad", 0)), compasso, cfg.get("ataque_pad", 0.5),
                                     0.6), cfg["pad"])
        if cfg.get("cordas", 0) > 0:
            for m in tons[:3]:
                colocar(buf, t0, cordas(nota_hz(m), compasso), cfg["cordas"])

        # baixo
        for passo, intervalo, dur, vol in cfg["baixo"]:
            colocar(buf, t0 + passo * oitavo, baixo(nota_hz(raiz - 24 + intervalo), dur), vol * cfg.get("vol_baixo", 1))

        # arpejo
        if cfg.get("arpejo"):
            ordem = tons + [tons[0] + 12, tons[1] + 12, tons[2] + 12]
            for i, idx in enumerate(cfg["arpejo"]):
                if idx is None:
                    continue
                voz = cfg["voz_arpejo"]
                colocar(buf, t0 + i * oitavo, voz(nota_hz(ordem[idx % len(ordem)] + cfg.get("oitava_arpejo", 12))),
                        cfg["vol_arpejo"])

        # melodia (A/B alternando; último ciclo repete A)
        frase = frases[ciclo % 2] if ciclo < ciclos - 1 else frases[0]
        if ciclo >= cfg.get("entrada_melodia", 0):
            for (cc, passo, midi_n, dur8) in frase:
                if cc == k:
                    voz = cfg["voz_melodia"]
                    colocar(buf, t0 + passo * oitavo, voz(nota_hz(midi_n), min(2.2, 0.4 + dur8 * oitavo * 1.5)),
                            cfg["vol_melodia"])

        # cintilâncias aleatórias
        if cfg.get("brilho_prob", 0) > 0:
            for i in range(8):
                if rng.rand() < cfg["brilho_prob"]:
                    m = tons[rng.randint(len(tons))] + 24 + 12 * rng.randint(0, 2)
                    colocar(buf, t0 + i * oitavo, sino(nota_hz(m), 1.4), cfg.get("vol_brilho", 0.12))

        # percussão
        perc = cfg.get("perc")
        if perc == "chimbal":
            for i in range(8):
                h = passa_alta(ruido(0.05, rng), 3) * decaimento(int(SR * 0.05), 70)
                colocar(buf, t0 + i * oitavo, h, 0.10 if i % 2 else 0.17)
        elif perc == "timpano":
            for passo, vol in ((0, 1.0), (4, 0.8), (6, 0.5)):
                x = mixar((varredura(95, 45, 0.45) * decaimento(int(SR * 0.45), 6), 0),
                          (passa_baixa(ruido(0.15, rng), 10) * decaimento(int(SR * 0.15), 25), 0, 0.8))
                colocar(buf, t0 + passo * oitavo, x, 0.55 * vol)
            for i in range(8):
                h = passa_alta(ruido(0.04, rng), 3) * decaimento(int(SR * 0.04), 90)
                colocar(buf, t0 + i * oitavo, h, 0.06)
        elif perc == "tique":
            for i in (2, 6):
                h = passa_alta(ruido(0.03, rng), 4) * decaimento(int(SR * 0.03), 90)
                colocar(buf, t0 + i * oitavo, h, 0.08)

    # dobra a sobra do final sobre o início (loop sem emenda audível)
    buf[:folga] += buf[n:]
    buf = buf[:n]

    # eco circular
    saida = buf.copy()
    for atraso_batidas, ganho in cfg.get("eco", []):
        saida += np.roll(buf, int(atraso_batidas * batida * SR)) * ganho
    if cfg.get("reverb", 0) > 0:
        r = cfg["reverb"]
        for d, g in ((0.037, 0.45), (0.061, 0.38), (0.089, 0.3), (0.127, 0.22)):
            saida += np.roll(buf, int(d * SR)) * g * r
    return normalizar(saida, PICO_MUSICA)


# --- escalas (classes de altura)
PENTA_MAIOR_D = {2, 4, 6, 9, 11}               # ré maior pentatônica
MAIOR_C = {0, 2, 4, 5, 7, 9, 11}
PENTA_MAIOR_C = {0, 2, 4, 7, 9}
MENOR_NAT_A = {9, 11, 0, 2, 4, 5, 7}
MENOR_HARM_D = {2, 4, 5, 7, 9, 10, 1}


def musica_menu():
    acordes = [(62, "M", (11,)), (59, "m", (10,)), (55, "M", (14,)), (57, "M", (7,))]   # D, Bm, G, A
    cfg = dict(
        escala=PENTA_MAIOR_D | {1}, faixa=(74, 90),
        ritmos=[[1, 0, 0, 1, 0, 1, 0, 0], [1, 0, 1, 0, 0, 1, 0, 0], [1, 0, 0, 0, 1, 0, 1, 0], [1, 0, 1, 0, 1, 0, 0, 0]],
        pad=0.5, ataque_pad=0.8, oitava_pad=0,
        baixo=[(0, 0, 1.6, 0.6), (4, 7, 1.0, 0.4)],
        arpejo=[0, 1, 2, 4, 2, 1, 2, 1], voz_arpejo=celesta, vol_arpejo=0.32, oitava_arpejo=12,
        voz_melodia=lambda f, d: sino(f, d), vol_melodia=0.55, entrada_melodia=1,
        brilho_prob=0.18, vol_brilho=0.14,
        eco=[(0.75, 0.30), (1.5, 0.18)], reverb=0.6,
    )
    return renderizar_musica("menu", 84, acordes, 4, cfg, 101)


def musica_geleira():
    acordes = [(60, "M", (14,)), (55, "M", (14,)), (57, "m", (10,)), (53, "M", (11,))]   # C, G, Am, F
    cfg = dict(
        escala=PENTA_MAIOR_C | {5}, faixa=(72, 91),
        ritmos=[[1, 0, 1, 1, 0, 1, 1, 0], [1, 0, 0, 1, 0, 1, 0, 1], [1, 1, 0, 1, 0, 1, 0, 0], [1, 0, 1, 0, 1, 1, 0, 1]],
        saltos=0.18,
        pad=0.28, ataque_pad=0.15,
        baixo=[(0, 0, 0.5, 0.9), (2, 7, 0.4, 0.6), (3, 12, 0.3, 0.5), (4, 0, 0.5, 0.9), (6, 7, 0.4, 0.6),
               (7, 12, 0.3, 0.5)],
        arpejo=[0, 2, 1, 2, 0, 2, 1, 2], voz_arpejo=harpa, vol_arpejo=0.30, oitava_arpejo=12,
        voz_melodia=lambda f, d: mixar((sino(f, min(d, 1.4)), 0), (pulso(f, 0.18), 0, 0.6)), vol_melodia=0.5,
        brilho_prob=0.10, vol_brilho=0.10, perc="chimbal",
        eco=[(0.5, 0.22), (1.0, 0.12)], reverb=0.3,
    )
    return renderizar_musica("geleira", 128, acordes, 6, cfg, 202)


def musica_cavernas():
    acordes = [(57, "m", (14,)), (53, "M", (11,)), (55, "M", (9,)), (52, "m", (10,))]   # Am, F, G, Em
    cfg = dict(
        escala=MENOR_NAT_A, faixa=(69, 88),
        ritmos=[[1, 0, 0, 0, 0, 0, 1, 0], [0, 0, 1, 0, 0, 0, 0, 0], [1, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0]],
        saltos=0.2,
        pad=0.6, ataque_pad=1.0, oitava_pad=-12,
        baixo=[(0, 0, 2.5, 0.7)],
        arpejo=[0, None, 2, None, 1, None, 2, None], voz_arpejo=lambda f: harpa(f, 1.4), vol_arpejo=0.20,
        oitava_arpejo=12,
        voz_melodia=lambda f, d: sino(f, 2.0), vol_melodia=0.5, entrada_melodia=0,
        brilho_prob=0.30, vol_brilho=0.12, perc="tique",
        eco=[(1.0, 0.45), (2.0, 0.32), (3.0, 0.2)], reverb=1.0,
    )
    return renderizar_musica("cavernas", 66, acordes, 3, cfg, 303)


def musica_castelo():
    acordes = [(62, "m", ()), (58, "M", (14,)), (60, "M", (14,)), (57, "M", (10,))]   # Dm, Bb, C, A7
    cfg = dict(
        escala=MENOR_HARM_D, faixa=(69, 86),
        ritmos=[[1, 0, 1, 1, 0, 0, 1, 0], [1, 1, 0, 1, 0, 1, 0, 0], [1, 0, 0, 1, 1, 0, 1, 1], [1, 0, 1, 0, 0, 1, 1, 0]],
        saltos=0.25,
        cordas=0.55, pad=0.18, ataque_pad=0.3, oitava_pad=-12,
        baixo=[(0, 0, 0.5, 1.0), (1, 0, 0.3, 0.6), (2, 0, 0.5, 0.9), (3, 0, 0.3, 0.6), (4, 0, 0.5, 1.0),
               (5, 0, 0.3, 0.6), (6, 7, 0.5, 0.9), (7, 0, 0.3, 0.6)], vol_baixo=0.8,
        arpejo=[2, 1, 0, 1, 2, 1, 0, 1], voz_arpejo=harpa, vol_arpejo=0.22, oitava_arpejo=12,
        voz_melodia=lambda f, d: mixar((cordas(f, min(d, 0.6), 0.04, 0.12), 0, 1.4), (sino(f, 0.9), 0, 0.5)),
        vol_melodia=0.55,
        entrada_melodia=1,
        brilho_prob=0.06, vol_brilho=0.1, perc="timpano",
        eco=[(0.5, 0.25), (1.0, 0.15)], reverb=0.7,
    )
    return renderizar_musica("castelo", 138, acordes, 7, cfg, 404)


def musica_final():
    acordes = [(60, "M", (14,)), (55, "M", (11,)), (57, "m", (14,)), (53, "M", (11,))]   # C, G, Am, F
    cfg = dict(
        escala=MAIOR_C, faixa=(72, 88),
        ritmos=[[1, 0, 0, 0, 1, 0, 1, 0], [1, 0, 1, 0, 0, 0, 1, 0], [1, 0, 0, 1, 0, 0, 1, 0], [1, 0, 0, 0, 1, 0, 0, 0]],
        saltos=0.1,
        pad=0.55, ataque_pad=1.0,
        baixo=[(0, 0, 2.2, 0.7), (4, 7, 1.5, 0.45)],
        arpejo=[0, 1, 2, 3, 2, 1, 2, 1], voz_arpejo=celesta, vol_arpejo=0.30, oitava_arpejo=12,
        voz_melodia=lambda f, d: mixar((celesta(f, min(d + 0.5, 1.8)), 0), (sino(f, 1.5), 0, 0.5)),
        vol_melodia=0.6, entrada_melodia=1,
        brilho_prob=0.2, vol_brilho=0.13,
        eco=[(1.0, 0.28), (2.0, 0.16)], reverb=0.8,
    )
    return renderizar_musica("final", 68, acordes, 4, cfg, 505)


def musica_conclusao():
    """Fanfarra curta (sem loop) de fragmento coletado: arpejos ascendentes e acorde final aberto."""
    notas = [(72, 0.0), (79, 0.14), (84, 0.28), (88, 0.42), (91, 0.56), (96, 0.70)]
    partes = [(celesta(nota_hz(n), 1.0), t, 0.8) for n, t in notas]
    partes += [(sino(nota_hz(n), 2.6), 0.95, 0.7) for n in (72, 76, 79, 84, 88)]
    partes += [(pad(nota_hz(m), 2.2, 0.25, 1.0), 0.9, 1.0) for m in (48, 60, 64, 67)]
    partes += [(baixo(nota_hz(36), 2.0, 1.5), 0.95, 1.0)]
    rng = np.random.RandomState(9)
    for i in range(14):
        partes.append((sino(rng.choice([3136, 3520, 3951, 4186]), 0.6), 0.9 + rng.uniform(0, 1.6), 0.12))
    x = mixar(*partes)
    x = eco_linear(x, [(0.3, 0.3), (0.6, 0.15)])
    fim = int(SR * 0.4)
    x[-fim:] *= np.linspace(1, 0, fim)
    return normalizar(x, PICO_MUSICA * 1.2)


MUSICAS = {
    "menu": musica_menu, "geleira": musica_geleira, "cavernas": musica_cavernas,
    "castelo": musica_castelo, "conclusao": musica_conclusao, "final": musica_final,
}


def gerar_musicas():
    for nome, funcao in MUSICAS.items():
        x = funcao()
        gravar(PASTA_MUSICAS, nome, x)
        print(f"música {nome}: {len(x) / SR:.1f} s")


def limpar_antigos():
    """Remove WAVs que não fazem parte do contrato (ex.: ``fase.wav`` do tema anterior)."""
    for pasta, validos in ((PASTA_MUSICAS, set(MUSICAS)), (PASTA_EFEITOS, set(EFEITOS))):
        for arquivo in pasta.glob("*.wav"):
            if arquivo.stem not in validos:
                arquivo.unlink()
                print("removido:", arquivo.name)


def gerar():
    gerar_efeitos()
    gerar_musicas()
    limpar_antigos()


if __name__ == "__main__":
    iniciar_pygame()
    gerar()
