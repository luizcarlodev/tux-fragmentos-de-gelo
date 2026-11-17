"""Registro das fases da campanha. Para adicionar uma fase: crie o JSON do mapa, um módulo
``fase_NN.py`` com ``criar_fase_NN`` e registre-a em ``FASES`` (e ajuste ``TOTAL_DE_FASES``)."""
from fases.fase_01 import criar_fase_01
from fases.fase_02 import criar_fase_02
from fases.fase_03 import criar_fase_03

# informações usadas pela seleção de fases e pelo menu
INFORMACOES = {
    1: {"nome": "A Geleira Perdida", "imagem": "interface/regiao_geleira.png",
        "descricao": "Montanhas nevadas, pinheiros e cristais."},
    2: {"nome": "As Cavernas Congeladas", "imagem": "interface/regiao_cavernas.png",
        "descricao": "Cristais luminosos e lagos subterrâneos."},
    3: {"nome": "O Castelo do Inverno Eterno", "imagem": "interface/regiao_castelo.png",
        "descricao": "Tempestade, pontes de gelo e o castelo."},
}


class GerenciadorDeFases:
    """Cria fases pelo número (1 a 3)."""

    FASES = {1: criar_fase_01, 2: criar_fase_02, 3: criar_fase_03}

    @classmethod
    def criar(cls, numero, recursos, audio, pontuacao, ao_checkpoint=None, segredo_descoberto=False):
        if numero not in cls.FASES:
            raise ValueError(f"A fase {numero} não existe. Disponíveis: {sorted(cls.FASES)}")
        return cls.FASES[numero](recursos, audio, pontuacao, ao_checkpoint, segredo_descoberto)
