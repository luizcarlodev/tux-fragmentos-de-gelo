"""Salva capturas de tela de pontos de um mapa (sem abrir janela), para conferir o visual.

    python ferramentas/capturar_fase.py fase_02 150:17 200:18 --saida /tmp/capturas

Cada ponto é ``coluna:linha_dos_pes``. Gera ``<mapa>_<coluna>.png`` na pasta de saída.
"""
import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

import pygame  # noqa: E402

from fases.fase import Fase  # noqa: E402
from principal import Aplicacao  # noqa: E402
from sistemas.pontuacao import SistemaDePontuacao  # noqa: E402
from interface.hud import Hud  # noqa: E402

T = 48


def principal():
    analisador = argparse.ArgumentParser()
    analisador.add_argument("mapa")
    analisador.add_argument("pontos", nargs="+")
    analisador.add_argument("--saida", default=str(RAIZ / "capturas"))
    args = analisador.parse_args()
    Path(args.saida).mkdir(parents=True, exist_ok=True)
    app = Aplicacao()
    pontuacao = SistemaDePontuacao(600)
    fase = Fase(app.recursos, app.audio, pontuacao, args.mapa)
    hud = Hud(app.recursos)
    for ponto in args.pontos:
        coluna, linha = (int(v) for v in ponto.split(":"))
        jogador = fase.jogador
        jogador.x, jogador.y = coluna * T, (linha + 1) * T - jogador.altura
        jogador.vx = jogador.vy = 0.0
        fase.camera.centralizar_em(jogador.centro_x, jogador.base)
        for _ in range(30):
            fase.atualizar(1 / 60, {"esquerda": False, "direita": False, "pular": False, "correr": False})
            jogador.y = (linha + 1) * T - jogador.altura
            jogador.vy = 0.0
        fase.camera.centralizar_em(jogador.centro_x, jogador.base)
        fase.cenario.atualizar(0.0)
        fase.desenhar(app.superficie)
        hud.desenhar(app.superficie, pontuacao, fase)
        destino = Path(args.saida) / f"{args.mapa}_{coluna}.png"
        pygame.image.save(app.superficie, str(destino))
        print(destino)


if __name__ == "__main__":
    principal()
