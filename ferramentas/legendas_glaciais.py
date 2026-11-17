"""Legenda de caracteres e temas de fundo compartilhados pelos geradores de mapas das 3 fases.

Os caracteres são os mesmos do jogo original (a grade da fase 1 não muda); só o
significado visual muda. Caracteres novos (cavernas/castelo) usam letras que não existiam.
"""


def _bloco(sprite, descricao, **extra):
    return {"tipo": "bloco", "sprite": sprite, "descricao": descricao, **extra}


LEGENDA = {
    " ": {"descricao": "vazio"},
    # ---- terreno (fase 1 e 3)
    "G": _bloco("neve", "chão coberto de neve"),
    "T": _bloco("solo_congelado", "solo congelado"),
    "B": _bloco("bloco_gelo", "bloco de gelo (quebra com cabeçada ou ataque)", quebravel=True),
    "?": _bloco("cristal", "bloco de cristal com cristais", recompensa="moeda", sprite_usado="cristal_usado"),
    "M": _bloco("cristal", "bloco de cristal com coração de gelo (vida extra)", recompensa="coracao_gelo"),
    "*": _bloco("cristal", "bloco de cristal com Cristal Mágico (invencibilidade)", recompensa="cristal_magico"),
    "S": _bloco("bloco_pedra", "bloco de pedra congelada (degraus, ilhas)"),
    "a": _bloco("pilar_topo_esq", "pilar de gelo: topo esquerdo"),
    "b": _bloco("pilar_topo_dir", "pilar de gelo: topo direito"),
    "c": _bloco("pilar_corpo_esq", "pilar de gelo: corpo esquerdo"),
    "d": _bloco("pilar_corpo_dir", "pilar de gelo: corpo direito"),
    "K": _bloco("tijolo_castelo", "tijolo do castelo"),
    "k": _bloco("chao_castelo", "chão do castelo (topo)"),
    "q": _bloco("topo_castelo", "topo de muralha do castelo"),
    "E": _bloco("espinhos_gelo", "espinhos de gelo (dano)", solido=False, perigo="dano"),
    "V": _bloco("agua_gelida", "água gélida (mata)", solido=False, perigo="morte"),
    # ---- cavernas
    "N": _bloco("neve_caverna", "chão de caverna com neve"),
    "R": _bloco("pedra_caverna", "pedra de caverna"),
    "L": _bloco("cristal_luminoso", "cristal luminoso (sólido, decorativo)"),
    "W": _bloco("estalactite", "estalactite afiada no teto (dano)", solido=False, perigo="dano", perigo_zona="topo"),
    "g": _bloco("gelo_profundo", "gelo profundo"),
    "p": _bloco("ponte_gelo", "ponte de gelo"),
    "X": _bloco("parede_rachada", "parede rachada (SEGREDO: quebra com 3 ataques)", fragil=True, resistencia=3,
                revela="porta_secreta"),
    # ---- objetos e personagens
    "o": {"tipo": "cristal", "descricao": "cristal coletável"},
    "1": {"tipo": "inimigo", "inimigo": "criatura_de_neve", "descricao": "Criatura de Neve (anda de um lado a outro)"},
    "2": {"tipo": "inimigo", "inimigo": "morcego_glacial", "descricao": "Morcego Glacial (voa e solta estilhaços)"},
    "3": {"tipo": "inimigo", "inimigo": "pinguim_selvagem", "descricao": "Pinguim Selvagem (persegue; 2 golpes)"},
    "4": {"tipo": "inimigo", "inimigo": "golem_de_gelo", "descricao": "Golem de Gelo (lento; 3 golpes)"},
    "5": {"tipo": "inimigo", "inimigo": "morcego_glacial", "opcoes": {"mergulha": True},
          "descricao": "Morcego Glacial que mergulha sobre o Tux"},
    "C": {"tipo": "totem", "descricao": "totem glacial (checkpoint)"},
    "J": {"tipo": "inicio", "descricao": "posição inicial do Tux"},
    "F": {"tipo": "altar", "descricao": "altar do Fragmento de Gelo (base)"},
    "P": {"tipo": "portal", "descricao": "portal de saída da fase"},
    "H": {"tipo": "castelo", "descricao": "Castelo (canto inferior esquerdo)"},
    "Q": {"tipo": "porta_secreta", "descricao": "portal secreto (aparece quando a parede rachada cai)"},
    "Z": {"tipo": "princesa", "descricao": "Princesa do Gelo aprisionada (salão final)"},
    "O": {"tipo": "lembranca", "descricao": "lembrança dourada (câmara secreta)"},
}


def camadas(regiao, **extra):
    """Camadas de parallax de uma região (arquivos em ``recursos/cenarios``)."""
    return REGIOES[regiao]


REGIOES = {
    "geleira": {"musica": "geleira", "neve": {"densidade": 70, "vento": -35}, "camadas": [
        {"imagem": "cenarios/geleira/ceu.png", "fator": 0.0},
        {"imagem": "cenarios/geleira/nuvens.png", "fator": 0.10, "deriva": 12},
        {"imagem": "cenarios/geleira/montanhas_longe.png", "fator": 0.25},
        {"imagem": "cenarios/geleira/montanhas_perto.png", "fator": 0.50}]},
    "tempestade": {"musica": "castelo", "neve": {"densidade": 190, "vento": -150}, "camadas": [
        {"imagem": "cenarios/castelo/ceu.png", "fator": 0.0},
        {"imagem": "cenarios/castelo/nuvens.png", "fator": 0.08, "deriva": 14},
        {"imagem": "cenarios/castelo/montanhas_longe.png", "fator": 0.20},
        {"imagem": "cenarios/castelo/castelo_distante.png", "fator": 0.30},
        {"imagem": "cenarios/castelo/pinheiros_tempestade.png", "fator": 0.55}]},
    "tempestade_perto": {"musica": "castelo", "neve": {"densidade": 240, "vento": -190}, "camadas": [
        {"imagem": "cenarios/castelo/ceu.png", "fator": 0.0},
        {"imagem": "cenarios/castelo/nuvens.png", "fator": 0.08, "deriva": 16},
        {"imagem": "cenarios/castelo/montanhas_longe.png", "fator": 0.20},
        {"imagem": "cenarios/castelo/castelo_proximo.png", "fator": 0.35},
        {"imagem": "cenarios/castelo/pinheiros_tempestade.png", "fator": 0.55}]},
    "salao": {"musica": "final", "neve": {"densidade": 0}, "camadas": [
        {"imagem": "cenarios/salao/fundo.png", "fator": 0.10},
        {"imagem": "cenarios/salao/pilares.png", "fator": 0.38}]},
    "camara": {"musica": "cavernas", "neve": {"densidade": 0}, "camadas": [
        {"imagem": "cenarios/camara/fundo.png", "fator": 0.08},
        {"imagem": "cenarios/camara/cristais.png", "fator": 0.35}]},
    "epilogo": {"musica": "final", "neve": {"densidade": 55, "vento": -22}, "camadas": [
        {"imagem": "cenarios/epilogo/ceu.png", "fator": 0.0},
        {"imagem": "cenarios/geleira/montanhas_longe.png", "fator": 0.25},
        {"imagem": "cenarios/geleira/montanhas_perto.png", "fator": 0.50}]},
    "cavernas": {"musica": "cavernas", "neve": {"densidade": 14, "vento": -6}, "camadas": [
        {"imagem": "cenarios/cavernas/ceu.png", "fator": 0.0},
        {"imagem": "cenarios/cavernas/paredes_longe.png", "fator": 0.22},
        {"imagem": "cenarios/cavernas/cristais_perto.png", "fator": 0.5},
        {"imagem": "cenarios/cavernas/estalactites.png", "fator": 0.62}]},
}
