"""Fase 2 — As Cavernas Congeladas (o mapa fica em ``fases/mapas/fase_02.json``)."""
from fases.fase import Fase

NOME_DO_MAPA = "fase_02"


def criar_fase_02(recursos, audio, pontuacao, ao_checkpoint=None, segredo_descoberto=False):
    """Cria a fase 2 já carregada do JSON."""
    return Fase(recursos, audio, pontuacao, NOME_DO_MAPA, ao_checkpoint, segredo_descoberto)
