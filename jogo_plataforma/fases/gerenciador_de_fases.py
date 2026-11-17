"""Registro das fases disponíveis. Para adicionar uma fase: crie o JSON, um módulo
``fase_NN.py`` com uma função ``criar_fase_NN`` e registre-a em ``FASES``."""
from fases.fase_01 import criar_fase_01


class GerenciadorDeFases:
    """Cria fases pelo número (hoje existe apenas a fase 1)."""

    FASES = {1: criar_fase_01}

    @classmethod
    def criar(cls, numero, recursos, audio, pontuacao, ao_checkpoint=None):
        if numero not in cls.FASES:
            raise ValueError(f"A fase {numero} não existe. Disponíveis: {sorted(cls.FASES)}")
        return cls.FASES[numero](recursos, audio, pontuacao, ao_checkpoint)
