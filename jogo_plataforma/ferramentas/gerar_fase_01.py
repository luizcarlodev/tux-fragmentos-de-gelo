"""Gerador do mapa da Fase 01 (fases/mapas/fase_01.json).

O mapa é uma grade ASCII (15 linhas x 312 colunas, blocos de 48 px).
Você pode editar o JSON gerado diretamente (a legenda explica cada caractere)
ou alterar este script e executá-lo novamente:

    python ferramentas/gerar_fase_01.py

Convenções:
  * linhas 13 e 14 = chão (o topo do chão fica na linha 13);
  * personagens e objetos são marcados na linha onde a BASE deles encosta
    (ex.: um inimigo em pé no chão é marcado na linha 12);
  * plataformas móveis, decorações e temas ficam em listas separadas.
"""
import json
from pathlib import Path

COLUNAS, LINHAS = 312, 15
TOPO_CHAO = 13
INICIO_CASTELO = 262

grade = [[" "] * COLUNAS for _ in range(LINHAS)]
plataformas = []
decoracoes = []


def p(c, l, ch):
    """Coloca um caractere na grade (ignora posições fora do mapa)."""
    if 0 <= c < COLUNAS and 0 <= l < LINHAS:
        grade[l][c] = ch


def chao(c0, c1, topo="G", corpo="T"):
    for c in range(c0, c1 + 1):
        p(c, TOPO_CHAO, topo)
        p(c, TOPO_CHAO + 1, corpo)


def buraco(c0, c1):
    for c in range(c0, c1 + 1):
        p(c, 13, " ")
        p(c, 14, " ")


def lava(c0, c1):
    for c in range(c0, c1 + 1):
        p(c, 13, "V")
        p(c, 14, "V")


def texto(c, l, s):
    for i, ch in enumerate(s):
        if ch != " ":
            p(c + i, l, ch)


def tubo(c, altura):
    topo = TOPO_CHAO - altura
    p(c, topo, "a"); p(c + 1, topo, "b")
    for l in range(topo + 1, TOPO_CHAO):
        p(c, l, "c"); p(c + 1, l, "d")


def escada(c0, n, sentido=1, ch="S"):
    for i in range(n):
        c = c0 + i * sentido
        for h in range(i + 1):
            p(c, TOPO_CHAO - 1 - h, ch)


def moedas(c0, c1, l, passo=1):
    for c in range(c0, c1 + 1, passo):
        p(c, l, "o")


def arco(c, l, n=5):
    """Arco de moedas centrado em c (n ímpar)."""
    meio = n // 2
    for i in range(n):
        p(c - meio + i, l - (1 if 0 < i < n - 1 else 0), "o")


def plataforma_movel(centro, linha, eixo, amplitude, periodo, fase=0.0, largura=3):
    plataformas.append({"coluna_centro": centro, "linha": linha, "largura_blocos": largura,
                        "eixo": eixo, "amplitude": amplitude, "periodo": periodo, "fase": fase})


def deco(imagem, c, linha_base=TOPO_CHAO):
    decoracoes.append({"imagem": imagem, "coluna": c, "linha_base": linha_base})


# ======================================================================
# CHÃO BASE
# ======================================================================
chao(0, INICIO_CASTELO - 1)
chao(INICIO_CASTELO, COLUNAS - 1, "K", "K")

# ======================================================================
# ZONA A (0-56) — INÍCIO: área segura e tutorial das mecânicas
# ======================================================================
p(3, 12, "J")                                    # posição inicial do jogador
deco("placa", 6, 13); deco("arbusto", 9); deco("arvore", 14); deco("arbusto", 22)
deco("arvore", 25); deco("arbusto", 36); deco("arvore", 52)
moedas(11, 13, 10)                               # ensina a coletar moedas pulando
texto(17, 9, "?B?B?")                            # primeiros blocos interativos
p(27, 12, "1")                                   # primeiro inimigo, sozinho
moedas(29, 32, 11)
p(33, 12, "1")
tubo(37, 2); tubo(43, 3); tubo(49, 4)            # tubos de alturas crescentes
moedas(37, 38, 8); moedas(43, 44, 7); moedas(49, 50, 6)
p(40, 12, "1")
buraco(57, 59)                                   # primeiro buraco (3 blocos)
arco(58, 9, 5)

# ======================================================================
# ZONA B (60-127) — DESENVOLVIMENTO 1
# ======================================================================
deco("arbusto", 62)
escada(67, 4)                                    # sobe (alturas 1..4)
escada(77, 4, -1)                                # desce (alturas 4..1), vale entre 71 e 73
moedas(67, 70, 7)
p(72, 12, "1")                                   # inimigo preso no vale
texto(82, 10, "B?B")                             # plataforma baixa
texto(85, 9, "B?B?B")                            # plataforma média
moedas(84, 88, 7)
p(92, 12, "1"); p(96, 12, "1")
tubo(100, 2)
p(104, 5, "2")                                   # primeiro inimigo voador
moedas(104, 106, 11)
buraco(108, 111)                                 # buraco de 4 blocos
arco(110, 8, 5)
deco("arbusto", 114); deco("arvore", 117)
buraco(120, 127)                                 # buraco largo: plataforma móvel
plataforma_movel(124.0, 13, "x", 2.5, 5.0)
moedas(121, 127, 10, 2)

# ======================================================================
# ZONA C (128-195) — DESENVOLVIMENTO 2: perseguidor, espinhos,
# checkpoint e caminhos alternativos (alto = moedas e 1UP / baixo = inimigos)
# ======================================================================
deco("arvore", 130)
p(134, 12, "3")                                  # primeiro perseguidor
texto(137, 9, "?B?")
p(142, 12, "1")
texto(145, 12, "EEE")                            # espinhos no chão
moedas(145, 147, 10)
p(151, 11, "C")                                  # CHECKPOINT 1 (meio da fase)
deco("arbusto", 153)
# caminho alto (opcional)
texto(156, 10, "SSS"); texto(161, 8, "SSS"); texto(166, 9, "SS"); texto(170, 7, "SSS")
moedas(156, 158, 8); moedas(161, 163, 6); moedas(166, 167, 7); moedas(170, 172, 5)
texto(162, 5, "M")                               # bloco com 1UP
# caminho baixo
p(159, 12, "1"); p(165, 12, "3"); p(168, 5, "2")
texto(176, 12, "EE")
p(181, 12, "1")
moedas(183, 186, 11)
tubo(188, 3)
p(192, 12, "3")

# ======================================================================
# PARKOUR (196-224) — grande abismo com pedras e plataforma vertical
# ======================================================================
buraco(196, 224)
texto(198, 12, "SS"); moedas(198, 199, 10)
texto(203, 11, "SS"); moedas(203, 204, 9)
texto(208, 10, "S"); arco(208, 8, 3)
texto(212, 11, "SS"); moedas(212, 213, 9)
plataforma_movel(217.5, 10, "y", 1.5, 4.0)
moedas(217, 218, 6)
texto(221, 10, "SS"); moedas(221, 222, 8)
p(206, 6, "2")                                   # voador atira sobre o parkour

# ======================================================================
# ZONA D (225-261) — DIFICULDADE ALTA: buracos, espinhos e inimigos
# ======================================================================
deco("arbusto", 226)
texto(228, 9, "*")                               # bloco da estrela
p(231, 12, "3")
p(234, 11, "C")                                  # CHECKPOINT 2
p(236, 12, "1")
texto(239, 12, "EE")
moedas(238, 241, 10)
buraco(243, 246)                                 # buraco de 4
arco(244, 9, 5)
buraco(250, 254)                                 # buraco de 5 com pedra no meio
texto(252, 12, "S"); moedas(251, 253, 10)
p(248, 6, "2")
p(258, 12, "1")
moedas(255, 260, 11)

# ======================================================================
# ZONA E (262-311) — FINAL: castelo, lava, escadaria, mastro e princesa
# ======================================================================
texto(264, 9, "*")                               # estrela antes do desafio final
p(266, 12, "3")
for c in (263, 267):
    deco("tocha", c)
deco("estandarte", 265, 10)
lava(268, 286)
plataforma_movel(271.5, 13, "x", 2.0, 4.5)
texto(274, 12, "SS")
moedas(272, 275, 9)
plataforma_movel(279.5, 11, "y", 1.5, 4.0)
moedas(279, 280, 6)
texto(283, 11, "S"); texto(285, 12, "S")
moedas(283, 285, 8, 2)
p(273, 6, "2"); p(282, 5, "2")
for c in (289, 296):
    deco("tocha", c)
escada(291, 4)                                   # escadaria até o mastro
moedas(291, 294, 6)
p(297, 12, "F")                                  # mastro final (base)
p(303, 12, "P")                                  # princesa
p(306, 12, "H")                                  # castelo (canto esquerdo)
deco("estandarte", 300, 10)

# ======================================================================
# EXPORTAÇÃO
# ======================================================================
legenda = {
    " ": {"descricao": "vazio"},
    "G": {"tipo": "bloco", "sprite": "grama", "descricao": "chão com grama"},
    "T": {"tipo": "bloco", "sprite": "terra", "descricao": "terra"},
    "B": {"tipo": "bloco", "sprite": "tijolo", "quebravel": True, "descricao": "bloco quebrável"},
    "?": {"tipo": "bloco", "sprite": "interrogacao", "recompensa": "moeda", "descricao": "bloco ? com moedas"},
    "M": {"tipo": "bloco", "sprite": "interrogacao", "recompensa": "cogumelo_vida", "descricao": "bloco ? com vida extra"},
    "*": {"tipo": "bloco", "sprite": "interrogacao", "recompensa": "estrela", "descricao": "bloco ? com estrela de invencibilidade"},
    "S": {"tipo": "bloco", "sprite": "bloco_solido", "descricao": "bloco sólido (degraus, pedras)"},
    "a": {"tipo": "bloco", "sprite": "tubo_topo_esq", "descricao": "tubo: topo esquerdo"},
    "b": {"tipo": "bloco", "sprite": "tubo_topo_dir", "descricao": "tubo: topo direito"},
    "c": {"tipo": "bloco", "sprite": "tubo_corpo_esq", "descricao": "tubo: corpo esquerdo"},
    "d": {"tipo": "bloco", "sprite": "tubo_corpo_dir", "descricao": "tubo: corpo direito"},
    "K": {"tipo": "bloco", "sprite": "castelo_tijolo", "descricao": "tijolo do castelo"},
    "E": {"tipo": "bloco", "sprite": "espinhos", "solido": False, "perigo": "dano", "descricao": "espinhos (dano)"},
    "V": {"tipo": "bloco", "sprite": "lava", "solido": False, "perigo": "morte", "descricao": "lava (mata)"},
    "o": {"tipo": "moeda", "descricao": "moeda"},
    "1": {"tipo": "inimigo", "inimigo": "cogumelo", "descricao": "inimigo terrestre simples"},
    "2": {"tipo": "inimigo", "inimigo": "voador", "descricao": "inimigo voador que atira"},
    "3": {"tipo": "inimigo", "inimigo": "perseguidor", "descricao": "inimigo perseguidor (2 pisões)"},
    "C": {"tipo": "checkpoint", "descricao": "checkpoint"},
    "J": {"tipo": "inicio", "descricao": "posição inicial do jogador"},
    "F": {"tipo": "mastro", "descricao": "mastro final (base)"},
    "P": {"tipo": "princesa", "descricao": "princesa"},
    "H": {"tipo": "castelo", "descricao": "castelo (canto inferior esquerdo)"},
}

temas = {
    "campo": {"musica": "fase", "camadas": [
        {"imagem": "cenarios/campo/ceu.png", "fator": 0.0},
        {"imagem": "cenarios/campo/nuvens.png", "fator": 0.10, "deriva": 12},
        {"imagem": "cenarios/campo/colinas_longe.png", "fator": 0.25},
        {"imagem": "cenarios/campo/colinas_perto.png", "fator": 0.50}]},
    "castelo": {"musica": "castelo", "camadas": [
        {"imagem": "cenarios/castelo/ceu.png", "fator": 0.0},
        {"imagem": "cenarios/castelo/nuvens.png", "fator": 0.08, "deriva": 8},
        {"imagem": "cenarios/castelo/muralha_longe.png", "fator": 0.25},
        {"imagem": "cenarios/castelo/pilares.png", "fator": 0.50}]},
}

mapa = {
    "nome": "Fase 1 - Rumo ao Castelo",
    "tamanho_bloco": 48,
    "colunas": COLUNAS,
    "linhas": LINHAS,
    "tempo_limite": 600,
    "tileset": "blocos/tileset",
    "legenda": legenda,
    "grade": ["".join(l) for l in grade],
    "plataformas_moveis": plataformas,
    "decoracoes": decoracoes,
    "temas": temas,
    "zonas": [{"coluna_inicio": 0, "tema": "campo"},
              {"coluna_inicio": INICIO_CASTELO, "tema": "castelo"}],
}

destino = Path(__file__).resolve().parent.parent / "fases" / "mapas" / "fase_01.json"
destino.parent.mkdir(parents=True, exist_ok=True)
# grava a grade em uma linha por string para facilitar a edição manual
texto_json = json.dumps(mapa, ensure_ascii=False, indent=1)
destino.write_text(texto_json, encoding="utf-8")

# relatório rápido
contagem = {}
for linha in grade:
    for ch in linha:
        contagem[ch] = contagem.get(ch, 0) + 1
print("Mapa gerado:", destino)
print("Largura:", COLUNAS * 48, "px =", round(COLUNAS * 48 / 1280, 2), "telas")
print("Moedas:", contagem.get("o", 0), "| Inimigos:",
      sum(contagem.get(c, 0) for c in "123"), "| Checkpoints:", contagem.get("C", 0))
