import os
import re
import pygame

_cache_frames = {}


def _carregar_imagem(caminho):
    if caminho not in _cache_frames:
        _cache_frames[caminho] = pygame.image.load(caminho).convert_alpha()
    return _cache_frames[caminho]


class Animacao:
    """Carrega os PNGs '<prefixo>_1.png', '<prefixo>_2.png'... de uma pasta e
    troca de frame a cada `ticks_por_frame` atualizações. Sem arquivos,
    `frame_atual()` retorna None."""

    def __init__(self, pasta, prefixo, ticks_por_frame=8, loop=True, escala=1.0):
        self.ticks_por_frame = ticks_por_frame
        self.loop = loop
        self._tick = 0
        self._indice = 0
        self.terminou = False
        self.frames = self._carregar_frames(pasta, prefixo, escala)

    def _carregar_frames(self, pasta, prefixo, escala):
        if not os.path.isdir(pasta):
            return []

        padrao = re.compile(rf"^{re.escape(prefixo)}_(\d+)\.png$", re.IGNORECASE)
        candidatos = []
        for nome_arquivo in os.listdir(pasta):
            m = padrao.match(nome_arquivo)
            if m:
                candidatos.append((int(m.group(1)), nome_arquivo))

        candidatos.sort()
        frames = [_carregar_imagem(os.path.join(pasta, nome)) for _, nome in candidatos]

        if escala != 1.0:
            frames = [
                pygame.transform.scale(
                    f, (max(1, round(f.get_width() * escala)), max(1, round(f.get_height() * escala)))
                )
                for f in frames
            ]
        return frames

    def reiniciar(self):
        self._tick = 0
        self._indice = 0
        self.terminou = False

    def atualizar(self):
        if not self.frames or self.terminou:
            return

        self._tick += 1
        if self._tick < self.ticks_por_frame:
            return

        self._tick = 0
        self._indice += 1
        if self._indice >= len(self.frames):
            if self.loop:
                self._indice = 0
            else:
                self._indice = len(self.frames) - 1
                self.terminou = True

    def frame_atual(self):
        if not self.frames:
            return None
        return self.frames[self._indice]
