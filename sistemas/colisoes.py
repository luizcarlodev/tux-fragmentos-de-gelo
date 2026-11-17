"""Sistema de colisões entre entidades, blocos do mapa e plataformas móveis.

As entidades usam posição em ponto flutuante (``x``, ``y``) com tamanho
(``largura``, ``altura``). O movimento é resolvido eixo por eixo, o que
evita "atravessar" blocos e dá colisões previsíveis.
"""
import math

import pygame

from configuracoes import TAMANHO_BLOCO

PEQUENO = 0.001


class SistemaDeColisoes:
    """Resolve o movimento de entidades contra o mapa de blocos e as plataformas."""

    def __init__(self, mapa, plataformas):
        self.mapa = mapa
        self.plataformas = plataformas

    # ------------------------------------------------------------ utilidades
    @staticmethod
    def verificar_colisao(retangulo_a, retangulo_b):
        """Interseção simples entre dois retângulos."""
        return retangulo_a.colliderect(retangulo_b)

    def _blocos_na_area(self, x, y, largura, altura):
        coluna_ini = int(math.floor(x / TAMANHO_BLOCO))
        coluna_fim = int(math.floor((x + largura - PEQUENO) / TAMANHO_BLOCO))
        linha_ini = int(math.floor(y / TAMANHO_BLOCO))
        linha_fim = int(math.floor((y + altura - PEQUENO) / TAMANHO_BLOCO))
        for linha in range(linha_ini, linha_fim + 1):
            for coluna in range(coluna_ini, coluna_fim + 1):
                bloco = self.mapa.obter(coluna, linha)
                if bloco is not None:
                    yield bloco

    def _solidos_na_area(self, x, y, largura, altura):
        return [b for b in self._blocos_na_area(x, y, largura, altura) if b.solido]

    def ponto_solido(self, x, y):
        """``True`` se o ponto (mundo) está dentro de um bloco sólido."""
        bloco = self.mapa.obter(int(math.floor(x / TAMANHO_BLOCO)), int(math.floor(y / TAMANHO_BLOCO)))
        return bloco is not None and bloco.solido

    # ------------------------------------------------------------ movimento
    def mover_horizontal(self, entidade, deslocamento):
        """Move em X e resolve colisões com blocos sólidos. Retorna ``True`` se bateu."""
        if deslocamento == 0:
            return False
        entidade.x += deslocamento
        bateu = False
        for bloco in self._solidos_na_area(entidade.x, entidade.y, entidade.largura, entidade.altura):
            if deslocamento > 0:
                entidade.x = bloco.x - entidade.largura
            else:
                entidade.x = bloco.x + TAMANHO_BLOCO
            bateu = True
        return bateu

    def mover_vertical(self, entidade, deslocamento, usar_plataformas=True):
        """Move em Y e resolve colisões.

        Retorna ``(no_chao, bloco_do_teto, plataforma)``.
        """
        base_antes = entidade.y + entidade.altura
        entidade.y += deslocamento
        no_chao = False
        bloco_teto = None
        plataforma = None
        candidatos = self._solidos_na_area(entidade.x, entidade.y, entidade.largura, entidade.altura)
        if candidatos:
            if deslocamento >= 0:
                entidade.y = candidatos[0].y - entidade.altura
                no_chao = True
            else:
                # escolhe o bloco com maior sobreposição horizontal (o "mais acertado")
                def sobreposicao(b):
                    return min(entidade.x + entidade.largura, b.x + TAMANHO_BLOCO) - max(entidade.x, b.x)
                bloco_teto = max(candidatos, key=sobreposicao)
                entidade.y = bloco_teto.y + TAMANHO_BLOCO
        if usar_plataformas and deslocamento >= 0 and not no_chao:
            for p in self.plataformas:
                if (entidade.x < p.x + p.largura and entidade.x + entidade.largura > p.x
                        and base_antes <= max(p.y, p.y_anterior) + 3
                        and entidade.y + entidade.altura >= p.y):
                    entidade.y = p.y - entidade.altura
                    no_chao = True
                    plataforma = p
                    break
        return no_chao, bloco_teto, plataforma

    # ------------------------------------------------------------ perigos
    def perigo_em(self, retangulo):
        """Retorna ``"morte"``, ``"dano"`` ou ``None`` conforme os blocos perigosos tocados."""
        resultado = None
        for bloco in self._blocos_na_area(retangulo.x, retangulo.y, retangulo.width, retangulo.height):
            if bloco.perigo and bloco.retangulo_perigo.colliderect(retangulo):
                if bloco.perigo == "morte":
                    return "morte"
                resultado = "dano"
        return resultado
