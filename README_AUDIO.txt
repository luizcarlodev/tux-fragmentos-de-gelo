(**README PROVISORIO**)

EXECUTAR NO WINDOWS / VS CODE
-----------------------------
Na pasta que contém main.py:
    python -m pip install -r requirements.txt
    python main.py

Se o projeto estiver usando o ambiente virtual .venv:
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe main.py

ÁUDIO — TUX: FRAGMENTOS DE GELO
================================

arquivos de áudio dentro de assets/:
- assets/music/snow_theme.ogg: trilha de exploração em loop.
- assets/music/boss_theme.ogg: trilha exclusiva da luta contra o boss.
- assets/music/boss_climax.ogg: variação mais intensa quando o boss entra na fase final.
- assets/sounds/: efeitos de pulo, ataque, dano, inimigos, coleta e menus.

CONTROLES
---------
F1: ligar/desligar a música.
F2: ligar/desligar os efeitos sonoros.

EVENTOS COM ÁUDIO
-----------------
- Pulo do Tux
- Ataque do Tux
- Tux sofre dano ou cai no vazio
- Ataque pesado do golem, aviso da chuva de cristais e impacto dos projéteis do boss
- Inimigos atingidos ou derrotados
- Coleta de fragmento
- Navegação e confirmação em menus
- Música em loop, pausada durante o menu de pausa

LICENÇAS E CRÉDITOS
-------------------
A trilha "Snow Theme" foi criada por Cleyton Kauffman e está identificada como
Creative Commons Zero (CC0).
Fonte: https://opengameart.org/content/snow-theme
Crédito: Cleyton Kauffman.

Pacotes Públicos utilizados:
- Sound Effects for Platformer:
  https://opengameart.org/content/sound-effects-for-platformer
- Soundpack 04:
  https://opengameart.org/content/soundpack-04

Os arquivos de áudio usados foram incluídos no projeto para evitar downloads
adicionais durante a execução. Consulte as páginas de origem para ver os detalhes
de licença e atribuição de cada pacote.

ÁUDIO DO BOSS
-------------
Ao entrar na arena, a música de exploração muda automaticamente para a trilha de boss.
Quando o golem chega à fase final (30% de vida ou menos), a trilha muda para uma
variação mais intensa. Ao derrotá-lo, a música normal volta.

Os efeitos de ataque, impacto e chuva de cristais foram selecionados do pacote
Sound Pack for Platformer que acompanha o projeto. As duas trilhas de boss são
loops chiptune originais incluídos no projeto, portanto não há download extra.
Fonte pública de efeitos: https://opengameart.org/content/sound-effects-for-platformer