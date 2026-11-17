"""Gera os dois mapas pequenos que não fazem parte da campanha linear:

* ``camara_secreta.json`` — a Câmara da Lembrança (Easter Egg, achada na fase 2);
* ``salao_final.json``    — o salão do castelo onde a princesa está aprisionada (final do jogo).

Uso (na pasta do projeto):  python ferramentas/gerar_mapas_especiais.py
"""
from construtor_de_mapas import ConstrutorDeMapa

# ================================================================ CÂMARA DA LEMBRANÇA (40 x 15)
m = ConstrutorDeMapa(40, 15)
PISO = 13
m.retangulo(0, 0, 39, 1, "R")                    # teto
m.retangulo(0, 0, 1, 14, "R"); m.retangulo(38, 0, 39, 14, "R")      # paredes
m.chao(2, 37, PISO, "N", "R")
m.p(6, PISO - 1, "J")                            # entrada (o Tux reaparece junto ao portal)
m.p(3, PISO - 1, "P")                            # portal de volta à caverna (aberto pela cena)
m.escada(15, PISO, 4)                            # degraus até o altar da lembrança
m.ilha(19, PISO - 4, 15, "g")                    # patamar elevado
m.retangulo(35, 2, 37, PISO - 1, "R")            # parede do fundo
m.p(27, PISO - 5, "O")                           # a lembrança dourada flutua sobre o patamar
m.arco(10, 10, 5); m.cristais(21, 25, PISO - 6); m.cristais(29, 33, PISO - 6)
m.deco("tocha_gelo", 12, PISO); m.deco("tocha_gelo", 35, PISO - 4)
m.deco("cristal_grande", 8, PISO); m.deco("cristal_luminoso", 24, PISO - 4); m.deco("cristal_luminoso", 31, PISO - 4)
m.deco("estatua_pinguim", 34, PISO - 4); m.deco("estalagmite", 13, PISO); m.deco("estandarte_gelo", 19, PISO - 4)
m.dialogo(6, "Uma câmara escondida...\nQuem a teria construído?", 3.4)
m.dialogo(22, "Esse brilho dourado... me é familiar.", 3.2)
m.zona(0, "camara")
m.salvar("camara_secreta", "Câmara da Lembrança", ["camara"], {"fragmento": 0}, tempo_limite=900)

# ================================================================ SALÃO FINAL (38 x 15)
m = ConstrutorDeMapa(38, 15)
PISO = 12
m.retangulo(0, 0, 37, 1, "K")                    # teto
m.retangulo(0, 0, 0, 14, "K"); m.retangulo(37, 0, 37, 14, "K")
m.chao(1, 36, PISO, "k", "K")
m.p(3, PISO - 1, "J")
m.p(31, PISO - 1, "Z")                           # a princesa, presa no gelo
for c in (6, 12, 18, 24):
    m.deco("pilar_castelo", c, PISO)
for c in (9, 15, 21, 27):
    m.deco("tocha_gelo", c, PISO)
m.deco("estandarte_gelo", 4, PISO); m.deco("estandarte_gelo", 29, PISO); m.deco("estandarte_gelo", 34, PISO)
m.deco("cristal_grande", 26, PISO); m.deco("cristal_grande", 36, PISO)
m.deco("estatua_pinguim", 11, PISO); m.deco("estatua_pinguim", 20, PISO)
m.zona(0, "salao")
m.salvar("salao_final", "O Salão do Inverno Eterno", ["salao", "epilogo"], {"fragmento": 0}, tempo_limite=900)
