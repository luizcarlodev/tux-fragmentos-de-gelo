"""Definição da fase 1 (o mapa fica em ``fases/mapas/fase_01.json``)."""
from fases.fase import Fase

NOME_DO_MAPA = "fase_01"


def criar_fase_01(recursos, audio, pontuacao, ao_checkpoint=None):
    """Cria a fase 1 já carregada do JSON."""
    return Fase(recursos, audio, pontuacao, NOME_DO_MAPA, ao_checkpoint)
