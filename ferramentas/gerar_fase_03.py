"""Gerador do mapa da Fase 03 — O Castelo do Inverno Eterno (fases/mapas/fase_03.json).

    python ferramentas/gerar_fase_03.py

A fase mais difícil. Mapa com 18 linhas (864 px); piso inicial com superfície na linha 15.

  A   0- 40  sopé da montanha: reaquecimento (pinguins selvagens)
  B  41- 90  pontes de gelo sobre abismos, plataformas móveis e espinhos
  C  91-140  escalada em terraços; golem no primeiro terraço (totem 1)
  D 141-190  CUME: parkour sobre ilhas de pedra e plataformas móveis, morcegos mergulhadores
  E 191-245  vale congelado: pilares, espinhos, lagos e dois golems (totem 2)
  F 246-319  muralha do castelo: fosso móvel, ameias, pátio (totem 3), torres, altar e portão
"""
from construtor_de_mapas import ConstrutorDeMapa

COLUNAS, LINHAS = 320, 18
PISO = 15
EM_PE = PISO - 1

m = ConstrutorDeMapa(COLUNAS, LINHAS)
m.zona(0, "tempestade")
m.zona(246, "tempestade_perto")

# ================================================================ A — SOPÉ (0-40)
m.chao(0, 40, PISO, "G", "T")
m.p(3, EM_PE, "J")
m.deco("placa_gelo", 6, PISO)
for c in (9, 19, 31):
    m.deco("pinheiro_tempestade", c, PISO)
m.deco("pedra_gelada", 13, PISO); m.deco("boneco_de_neve", 27, PISO)
m.cristais(11, 13, 11)
m.texto(25, 10, "B?M?B")
m.p(22, EM_PE, "3"); m.p(30, EM_PE, "1"); m.p(37, EM_PE, "3")
m.cristais(32, 36, 12)
m.dialogo(4, "O Castelo do Inverno Eterno...\nO último fragmento deve estar lá dentro!", 4.4)

# ================================================================ B — PONTES DE GELO (41-90)
m.buraco(41, 90, PISO)
m.ilha(41, PISO, 4)                             # 41-44
m.ilha(48, PISO, 3)                             # 48-50
m.plataforma_movel(55, PISO, "x", 1.6, 4.0)      # cobre a lacuna 51-58
m.ilha(59, PISO, 5)                             # 59-63
m.p(61, EM_PE, "E")                             # espinho no meio da ponte
m.ilha(66, 13, 2)                               # apoio opcional na lacuna larga 64-69
m.ilha(70, PISO, 4)                             # 70-73
m.ilha(77, 13, 3)                               # 77-79
m.ilha(83, 11, 3)                               # 83-85
m.ilha(88, PISO, 3)                             # 88-90
m.arco(46, 11, 5); m.arco(54, 11, 5); m.arco(66, 8, 5); m.arco(75, 9, 5); m.arco(81, 7, 5)
m.p(47, 8, "2"); m.p(56, 6, "5"); m.p(67, 9, "2"); m.p(82, 7, "5")
for c in (43, 61, 72):
    m.deco("tocha_gelo", c, PISO)
m.dialogo(42, "Pontes de gelo... melhor não olhar para baixo.", 3.2)

# ================================================================ C — ESCALADA (91-140)
m.chao(91, 99, PISO, "G", "T")
m.escada(100, PISO, 3)                          # degraus até a altura 3 (topo na linha 12)
m.chao(103, 125, 12, "G", "T")                  # terraço 1
m.p(108, 11, "C")                               # totem 1
m.p(114, 11, "1"); m.p(121, 11, "4")            # golem guarda o fim do terraço
m.texto(117, 7, "B*B")
m.escada(126, 12, 3)                            # degraus até o topo na linha 9
m.chao(129, 140, 9, "G", "T")                   # terraço 2
m.p(134, 8, "3"); m.p(138, 8, "1")
m.texto(132, 8, "EE")
m.cristais(93, 98, 12); m.cristais(104, 112, 9); m.cristais(122, 125, 8); m.cristais(130, 131, 6)
m.p(111, 6, "2"); m.p(128, 4, "5")
for c in (95, 105, 130):
    m.deco("pinheiro_tempestade", c, PISO if c < 100 else (12 if c < 126 else 9))
m.deco("estandarte_gelo", 106, 12); m.deco("pilar_castelo", 124, 12)
m.dialogo(102, "A montanha é íngreme... e o vento só piora.", 3.2)

# ================================================================ D — CUME (141-190)
m.buraco(141, 190, 9)
m.ilha(144, 9, 2, "S")                          # 144-145
m.ilha(149, 7, 2, "S")                          # 149-150
m.plataforma_movel(155.5, 7, "x", 1.8, 4.5)      # lacuna 151-159
m.ilha(160, 6, 2, "S")                          # 160-161
m.ilha(165, 8, 3, "S")                          # 165-167
m.ilha(172, 5, 2, "S")                          # 172-173
m.ilha(178, 4, 2, "S")                          # 178-179
m.plataforma_movel(184.5, 6, "y", 2.0, 4.0)      # sobe e desce entre 180-188
m.ilha(188, 9, 3, "S")                          # 188-190
m.cristais(144, 145, 6); m.arco(147, 4, 5); m.arco(155, 3, 5); m.cristais(165, 167, 5)
m.arco(170, 2, 5); m.arco(176, 1, 5); m.cristais(188, 190, 6)
m.p(147, 2, "2"); m.p(158, 2, "5"); m.p(169, 2, "2"); m.p(182, 1, "5")
m.p(166, 7, "E")
for c in (145, 166, 179):
    m.deco("cristal_grande", c, {145: 9, 166: 8, 179: 4}[c])
m.dialogo(143, "O cume! Um passo em falso e... bem, melhor não errar.", 3.6)

# ================================================================ E — VALE CONGELADO (191-245)
m.chao(191, 245, 13, "G", "T")
m.p(193, 12, "C")                               # totem 2
m.agua(205, 210, 13)
m.plataforma_movel(207.5, 12, "x", 1.4, 4.0)
m.pilar(216, 10, 12)                            # obstáculo alto (3 blocos)
m.texto(212, 12, "EE")
m.pilar(224, 10, 12)
m.texto(228, 12, "EEE")
m.pilar(236, 10, 12)
m.p(199, 12, "3"); m.p(219, 12, "4"); m.p(226, 12, "3"); m.p(232, 12, "3"); m.p(241, 12, "4")
m.p(214, 6, "2"); m.p(230, 5, "5")
m.texto(209, 8, "B?B"); m.texto(233, 8, "?M?")
m.cristais(194, 203, 10, 3); m.arco(207, 9, 5); m.arco(220, 7, 5); m.cristais(238, 243, 10)
for c in (197, 214, 222, 232, 240):
    m.deco("pinheiro_tempestade", c, 13)
m.deco("estatua_pinguim", 202, 13); m.deco("pilar_castelo", 244, 13)
m.dialogo(196, "O castelo está tão perto... posso sentir o gelo dele.", 3.6)

# ================================================================ F — MURALHA DO CASTELO (246-319)
m.chao(246, 319, 13, "k", "K")
m.agua(256, 266, 13)                            # fosso
m.plataforma_movel(258.5, 12, "x", 1.0, 3.6, fase=0.0)
m.plataforma_movel(263.5, 12, "x", 1.0, 3.6, fase=3.14)
m.escada(268, 13, 4, 1, "K")                    # degraus de tijolo (até a linha 9)
m.retangulo(272, 9, 277, 9, "q")                # ameia
m.retangulo(272, 10, 277, 12, "K")
m.escada(281, 13, 4, -1, "K")                   # descida
m.p(274, 8, "3"); m.p(276, 8, "1")
m.p(284, 12, "C")                               # totem 3 no pátio
m.texto(288, 12, "EE")
m.p(291, 12, "3"); m.p(294, 12, "4")
# torres de parkour até a plataforma do altar
m.retangulo(297, 10, 299, 12, "K"); m.retangulo(297, 9, 299, 9, "q")
m.retangulo(303, 8, 305, 12, "K"); m.retangulo(303, 7, 305, 7, "q")
m.plataforma_movel(301, 9, "y", 1.5, 3.4, largura=2)
m.retangulo(308, 6, 313, 12, "K"); m.retangulo(308, 5, 313, 5, "q")   # plataforma do altar (linha 5)
m.p(310, 4, "F")                                # altar do 3º fragmento
m.p(318, 12, "P")                               # portão do castelo (portal)
m.p(315, 12, "H")                               # castelo ao fundo, colado ao portão
m.cristais(257, 265, 9, 2); m.cristais(269, 272, 5); m.cristais(278, 280, 6)
m.cristais(298, 298, 6); m.cristais(304, 304, 4)
m.p(262, 6, "5"); m.p(285, 7, "2"); m.p(296, 5, "5"); m.p(302, 3, "2")
for c in (250, 270, 292, 307):
    m.deco("tocha_gelo", c, 13)
m.deco("estandarte_gelo", 281, 9); m.deco("estandarte_gelo", 296, 12)
m.deco("pilar_castelo", 248, 13); m.deco("pilar_castelo", 286, 13)
m.dialogo(247, "O fosso... e as muralhas. É agora!", 3.2)
m.dialogo(300, "O terceiro fragmento!\nCom ele, a chave estará completa.", 4.0)

m.salvar("fase_03", "O Castelo do Inverno Eterno", ["tempestade", "tempestade_perto"],
         {"fragmento": 3, "final": "chave"}, tempo_limite=780)
