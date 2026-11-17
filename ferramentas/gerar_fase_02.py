"""Gerador do mapa da Fase 02 — As Cavernas Congeladas (fases/mapas/fase_02.json).

    python ferramentas/gerar_fase_02.py

Mapa ALTO (22 linhas = 1056 px): a câmera também acompanha na vertical. Piso principal com
superfície na linha 19 (o Tux fica em pé na linha 18).

Estrutura (colunas):
  A   0- 44  entrada: tutorial das criaturas e do ataque
  B  45-100  primeiro lago congelado: piso de gelo com buracos de água gélida
  C 101-138  abismo com plataformas suspensas e plataformas móveis  (totem 1 na ilha central)
  D 139-190  torre de plataformas: CAMINHO ALTO (parkour + golem + SEGREDO) ou CAMINHO BAIXO (espinhos)
  E 191-245  segundo lago, golem e plataformas móveis (totem 2)
  F 246-287  câmara final: parkour ascendente até o altar do Fragmento de Gelo 2 e o portal
"""
from construtor_de_mapas import ConstrutorDeMapa

COLUNAS, LINHAS = 288, 22
PISO = 19            # linha da superfície do piso
EM_PE = PISO - 1     # linha onde ficam os pés de quem está no piso

m = ConstrutorDeMapa(COLUNAS, LINHAS)
m.zona(0, "cavernas")

# ================================================================ A — ENTRADA (0-44)
m.chao(0, 44, PISO, "N", "R")
m.p(3, EM_PE, "J")
m.deco("placa_gelo", 6, PISO)
m.deco("estalagmite", 9, PISO); m.deco("cristal_luminoso", 13, PISO); m.deco("cristal_grande", 21, PISO)
m.deco("estalagmite", 30, PISO); m.deco("cristal_luminoso", 41, PISO)
m.cristais(11, 13, 15)
m.texto(17, 15, "?B?B?")                       # primeiros blocos de cristal
m.p(26, EM_PE, "1")
m.cristais(28, 31, 16)
m.p(35, EM_PE, "1")
m.p(40, 12, "2")                               # primeiro morcego, bem alto
m.dialogo(4, "As Cavernas Congeladas...\nO segundo fragmento deve estar aqui no fundo.", 4.2)

# ================================================================ B — LAGO CONGELADO 1 (45-100)
m.chao(45, 100, PISO, "g", "g")
m.agua(58, 61, PISO)                            # 4 de largura
m.agua(73, 77, PISO)                            # 5 de largura
m.agua(87, 92, PISO)                            # 6 de largura (corrida) ...
m.ilha(89, 17, 2)                               # ... ou apoio intermediário
m.p(50, EM_PE, "1")
m.arco(59, 15, 5)
m.p(66, EM_PE, "3")                             # pinguim selvagem entre os buracos
m.arco(75, 14, 5)
m.texto(82, 15, "B*B")
m.p(81, 11, "2")
m.arco(90, 13, 5)
m.p(97, EM_PE, "1")
for c in (48, 64, 84, 96):
    m.deco("cristal_luminoso", c, PISO)
m.deco("estalagmite", 70, PISO); m.deco("cristal_grande", 54, PISO)

# ================================================================ C — ABISMO SUSPENSO (101-138)
m.buraco(101, 138, PISO)
m.ilha(104, 17, 3)
m.ilha(111, 15, 2)
m.plataforma_movel(118.5, 16, "x", 2.2, 5.0)
m.ilha(124, 14, 5)
m.p(126, 13, "C")                               # totem 1 (ilha central)
m.plataforma_movel(133.5, 15, "y", 1.5, 4.0)
m.ilha(136, 17, 3)
m.cristais(105, 106, 15); m.cristais(111, 112, 13)
m.arco(118, 12, 5); m.cristais(125, 128, 12); m.arco(133, 11, 5)
m.p(109, 10, "2"); m.p(121, 9, "2"); m.p(131, 8, "5")
m.deco("tocha_gelo", 125, 14); m.deco("tocha_gelo", 128, 14)
m.deco("estalactite_frente", 108, 3, frente=True); m.deco("estalactite_frente", 122, 3, frente=True)

# ================================================================ D — TORRE E CAMINHOS (139-190)
m.chao(139, 190, PISO, "N", "R")
# ---- caminho ALTO: torre em zigue-zague, depois plataforma do golem e o segredo
m.ilha(145, 16, 3)
m.ilha(151, 13, 3)
m.ilha(145, 10, 3)
m.ilha(151, 7, 3)
m.ilha(157, 5, 4)                              # topo da torre
m.ilha(164, 6, 11)                             # plataforma longa (golem)
m.p(170, 4, "4")
m.ilha(176, 6, 6)                              # trecho final do caminho alto
m.cristais(146, 146, 14); m.cristais(152, 152, 11); m.cristais(146, 146, 8); m.cristais(152, 153, 5)
m.cristais(158, 160, 3); m.arco(167, 3, 5); m.cristais(177, 181, 4)
m.p(161, 10, "5")
# rocha pendurada com a câmara secreta (parede rachada nas colunas 182, linhas 4-5)
m.retangulo(182, 0, 191, 2, "R")               # teto da formação
m.retangulo(190, 0, 191, 9, "R")               # parede do fundo
m.retangulo(182, 6, 191, 9, "R")               # piso/base da formação
m.retangulo(182, 3, 182, 3, "R")
m.p(182, 4, "X"); m.p(182, 5, "X")             # parede rachada: 3 ataques
m.p(186, 5, "Q")                               # portal secreto (aparece quando a parede cai)
m.deco("estatua_pinguim", 179, 6)              # pista discreta
m.deco("cristal_luminoso", 174, 6)
# ---- descida do caminho alto
m.ilha(177, 10, 3); m.ilha(180, 14, 3); m.ilha(185, 17, 3)
# ---- caminho BAIXO: piso com espinhos e inimigos
m.p(143, EM_PE, "1"); m.p(155, EM_PE, "3")
m.texto(160, EM_PE, "EEE"); m.p(167, EM_PE, "1")
m.texto(172, EM_PE, "EE"); m.p(179, EM_PE, "3")
m.texto(156, 14, "?M?")                          # bloco de vida extra (caminho baixo)
m.cristais(141, 150, 17, 3); m.cristais(161, 165, 15); m.cristais(173, 178, 16)
m.deco("cristal_grande", 148, PISO); m.deco("estalagmite", 163, PISO); m.deco("cristal_luminoso", 170, PISO)

# ================================================================ E — LAGO 2 E GOLEM (191-245)
m.chao(191, 245, PISO, "g", "g")
m.p(193, EM_PE, "C")                           # totem 2
m.agua(198, 203, PISO)
m.plataforma_movel(200.5, 17, "x", 1.6, 4.5, largura=2)
m.agua(212, 216, PISO)
m.agua(236, 241, PISO)
m.ilha(238, 17, 2)
m.p(207, EM_PE, "3")
m.p(223, EM_PE, "4")                           # golem em ilha larga (217-235)
m.p(229, 12, "2"); m.p(209, 10, "5")
m.texto(219, 15, "B?B")
m.cristais(197, 204, 15); m.arco(214, 14, 5); m.cristais(218, 222, 17); m.cristais(224, 232, 17, 2)
m.arco(238, 14, 5); m.p(244, EM_PE, "1")
for c in (195, 207, 220, 232):
    m.deco("cristal_luminoso", c, PISO)
m.deco("tocha_gelo", 217, PISO); m.deco("tocha_gelo", 235, PISO)
m.dialogo(196, "Cuidado com os lagos... a água é gélida demais!", 3.4)

# ================================================================ F — CÂMARA FINAL (246-287)
m.chao(246, 258, PISO, "N", "R")
m.escada(250, PISO, 3)                         # degraus até a altura 3
m.buraco(259, 287, PISO)
m.ilha(262, 15, 3); m.ilha(268, 13, 3); m.ilha(274, 11, 3)
m.plataforma_movel(266, 17, "x", 1.5, 4.0, largura=2)
m.ilha(279, 10, 9)                             # plataforma do altar
m.p(282, 9, "F"); m.p(286, 9, "P")
m.cristais(262, 264, 12); m.cristais(268, 270, 10); m.cristais(274, 276, 8)
m.p(265, 8, "2"); m.p(271, 6, "5")
m.p(256, EM_PE, "1")
m.deco("tocha_gelo", 280, 10); m.deco("tocha_gelo", 287, 10)
m.deco("cristal_grande", 283, 10); m.deco("estandarte_gelo", 278, 10)
m.dialogo(247, "O fragmento brilha lá em cima...", 3.4)

m.salvar("fase_02", "As Cavernas Congeladas", ["cavernas"], {"fragmento": 2}, tempo_limite=720)
