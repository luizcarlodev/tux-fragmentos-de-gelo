import config
from entidade import Entidade
from enemy import MiniGolem, Golem
import tileset
import sprites

TILE = config.TILE


class Plataforma(Entidade):
    """tipo: 'chao' (altura CHAO_ALTURA) ou 'plataforma' (altura TILE)."""

    def __init__(self, x, y, largura, altura, tipo="plataforma"):
        super().__init__(x, y, largura, altura, vida=0)
        self.tipo = tipo
        self.cor = config.COR_CHAO if tipo == "chao" else config.COR_PLATAFORMA

    def desenhar(self, tela, camera_x=0):
        tileset.desenhar_bloco(
            tela, self.tipo, self.x, self.y, self.largura, self.altura, camera_x, self.cor
        )


class Porta(Entidade):
    """Fica trancada (parede sólida) até o Tux reunir todos os fragmentos."""

    _PASTA = "assets/objetos"
    _ALTURA_SPRITE = 55   # um pouco maior que o hitbox (48px)

    def __init__(self, x, y):
        super().__init__(x, y, TILE * 2, TILE * 3, vida=0)

    def desenhar(self, tela, camera_x=0, destrancada=False):
        nome = "porta_destrancada" if destrancada else "porta_trancada"
        sprite = sprites.carregar(f"{self._PASTA}/{nome}.png", self._ALTURA_SPRITE)

        if sprite is None:
            cor = config.COR_CHAVE if destrancada else config.COR_PORTA
            super().desenhar(tela, cor, camera_x)
            return

        centro_x = self.rect.x - camera_x + self.rect.width / 2
        base_y = self.rect.y + self.rect.height
        tela.blit(sprite, (centro_x - sprite.get_width() / 2, base_y - sprite.get_height()))


# Cada trecho do mapa, em ordem:
#   largura : largura em tiles
#   altura  : altura acima do chão em tiles (0 = chão)
#   gap     : distância do trecho anterior em tiles
#   inimigo : True se nasce um MiniGolem no trecho
DEFINICAO_MAPA = [
    # spawn
    {"largura": 10, "altura": 0, "gap": 0, "inimigo": False},

    # chão (tutorial de pulo)
    {"largura": 6, "altura": 0, "gap": 3, "inimigo": False},
    {"largura": 6, "altura": 0, "gap": 3, "inimigo": False},
    {"largura": 6, "altura": 0, "gap": 3, "inimigo": False},

    # plataformas baixa -> alta
    {"largura": 4, "altura": 2, "gap": 4, "inimigo": False},
    {"largura": 4, "altura": 4, "gap": 3, "inimigo": False},

    # chão + 1º mini golem
    {"largura": 8, "altura": 0, "gap": 3, "inimigo": True},

    # plataformas alta -> baixa (a subida é em etapas de 2 tiles por causa do alcance do pulo)
    {"largura": 3, "altura": 2, "gap": 4, "inimigo": False},
    {"largura": 4, "altura": 4, "gap": 3, "inimigo": False},
    {"largura": 4, "altura": 2, "gap": 4, "inimigo": False},

    # chão
    {"largura": 6, "altura": 0, "gap": 3, "inimigo": False},

    # plataforma
    {"largura": 4, "altura": 3, "gap": 4, "inimigo": False},

    # plataforma maior + 2º mini golem
    {"largura": 6, "altura": 3, "gap": 5, "inimigo": True},

    # plataforma baixa
    {"largura": 4, "altura": 1, "gap": 4, "inimigo": False},

    # chão
    {"largura": 6, "altura": 0, "gap": 3, "inimigo": False},
    {"largura": 6, "altura": 0, "gap": 3, "inimigo": False},

    # chão maior + 3º mini golem
    {"largura": 7, "altura": 0, "gap": 4, "inimigo": True},

    # chão
    {"largura": 6, "altura": 0, "gap": 3, "inimigo": False},
    {"largura": 6, "altura": 0, "gap": 3, "inimigo": False},

    # plataformas baixa -> alta
    {"largura": 4, "altura": 2, "gap": 5, "inimigo": False},
    {"largura": 4, "altura": 4, "gap": 5, "inimigo": False},

    # plataforma grande + 4º mini golem
    {"largura": 6, "altura": 4, "gap": 6, "inimigo": True},

    # plataformas alta -> baixa
    {"largura": 4, "altura": 3, "gap": 5, "inimigo": False},
    {"largura": 4, "altura": 1, "gap": 5, "inimigo": False},

    # chão
    {"largura": 6, "altura": 0, "gap": 3, "inimigo": False},
    {"largura": 6, "altura": 0, "gap": 3, "inimigo": False},

    # plataforma
    {"largura": 4, "altura": 3, "gap": 5, "inimigo": False},

    # chão
    {"largura": 6, "altura": 0, "gap": 3, "inimigo": False},

    # plataforma alta
    {"largura": 4, "altura": 4, "gap": 5, "inimigo": False},

    # plataforma grande + 5º mini golem
    {"largura": 5, "altura": 4, "gap": 7, "inimigo": True},

    # plataforma baixa
    {"largura": 4, "altura": 2, "gap": 5, "inimigo": False},

    # chão maior + 6º mini golem (último antes da escadinha)
    {"largura": 8, "altura": 0, "gap": 5, "inimigo": True},
]

# Escadinha de precisão
QTD_DEGRAUS_ESCADINHA = 10
LARGURA_DEGRAU = 2            # tiles
GAP_ENTRE_DEGRAUS = 7         # tiles
ALTURA_INICIAL_ESCADINHA = 3  # tiles acima do chão; sobe 1 tile por degrau

# Penhasco antes da arena do boss
GAP_PENHASCO_ARENA = 8        # tiles


def _gerar_trechos_principais():
    plataformas = []
    mini_golens = []
    x_atual = 0

    for trecho in DEFINICAO_MAPA:
        x_atual += trecho["gap"] * TILE

        largura_px = trecho["largura"] * TILE
        y_px = config.CHAO_Y - trecho["altura"] * TILE
        eh_chao = trecho["altura"] == 0
        altura_bloco = config.CHAO_ALTURA if eh_chao else TILE

        plataformas.append(Plataforma(x_atual, y_px, largura_px, altura_bloco, "chao" if eh_chao else "plataforma"))

        if trecho["inimigo"]:
            margem = TILE
            mini_golens.append(MiniGolem(
                x_atual + margem,
                y_px - config.MINI_GOLEM_ALTURA,
                limite_esq=x_atual + margem,
                limite_dir=x_atual + largura_px - config.MINI_GOLEM_LARGURA - margem,
            ))

        x_atual += largura_px

    return plataformas, mini_golens, x_atual


def _gerar_escadinha(x_inicial):
    plataformas = []
    x_atual = x_inicial

    for i in range(QTD_DEGRAUS_ESCADINHA):
        x_atual += GAP_ENTRE_DEGRAUS * TILE
        y_px = config.CHAO_Y - (ALTURA_INICIAL_ESCADINHA + i) * TILE
        plataformas.append(Plataforma(x_atual, y_px, LARGURA_DEGRAU * TILE, TILE))
        x_atual += LARGURA_DEGRAU * TILE

    return plataformas, x_atual


def _gerar_arena_boss(x_inicial):
    x_arena = x_inicial + GAP_PENHASCO_ARENA * TILE
    largura_px = config.GOLEM_ARENA_LARGURA

    chao_arena = Plataforma(x_arena, config.CHAO_Y, largura_px, config.CHAO_ALTURA, "chao")

    golem = Golem(
        x_arena + largura_px - config.GOLEM_LARGURA - TILE * 3,
        config.CHAO_Y - config.GOLEM_ALTURA,
        arena_inicio=x_arena,
        arena_fim=x_arena + largura_px,
    )

    # a porta fica atrás do golem, no fim da arena
    porta = Porta(x_arena + largura_px - TILE * 2, config.CHAO_Y - TILE * 3)

    return chao_arena, golem, porta, x_arena + largura_px


def criar_mapa_fase1():
    plataformas, mini_golens, x_fim_principal = _gerar_trechos_principais()
    ultima_plataforma_principal = plataformas[-1]

    plataformas_escadinha, x_fim_escadinha = _gerar_escadinha(x_fim_principal)
    plataformas.extend(plataformas_escadinha)

    chao_arena, golem, porta, x_fim_mapa = _gerar_arena_boss(x_fim_escadinha)
    plataformas.append(chao_arena)

    # checkpoint: 3 tiles antes da borda da última plataforma, antes da escadinha
    x_checkpoint = ultima_plataforma_principal.x + ultima_plataforma_principal.largura - TILE * 3
    y_checkpoint = ultima_plataforma_principal.y - config.PLAYER_ALTURA

    return {
        "plataformas": plataformas,
        "mini_golens": mini_golens,
        "golem": golem,
        "porta": porta,
        "largura_mundo": x_fim_mapa + TILE * 5,
        "x_spawn": TILE * 2,
        "y_spawn": config.CHAO_Y - config.PLAYER_ALTURA,
        "x_checkpoint": x_checkpoint,
        "y_checkpoint": y_checkpoint,
    }
