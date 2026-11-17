"""Fase 3 — O Castelo do Inverno Eterno (o mapa fica em ``fases/mapas/fase_03.json``)."""
from fases.fase import Fase

NOME_DO_MAPA = "fase_03"


def criar_fase_03(recursos, audio, pontuacao, ao_checkpoint=None, segredo_descoberto=False):
    """Cria a fase 3 já carregada do JSON."""
    return Fase(recursos, audio, pontuacao, NOME_DO_MAPA, ao_checkpoint, segredo_descoberto)
