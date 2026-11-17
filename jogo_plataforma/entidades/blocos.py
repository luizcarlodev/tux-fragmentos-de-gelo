"""Blocos do cenário (chão, tijolos, interrogação, tubos...) e o mapa de blocos."""
import pygame

from configuracoes import TAMANHO_BLOCO
from sistemas.animacoes import Animador


class Tileset:
    """Conjunto de imagens de blocos; as animações avançam com um relógio global."""

    def __init__(self, folha):
        self.folha = folha
        self.tempo = 0.0

    def atualizar(self, dt):
        self.tempo += dt

    def imagem(self, nome):
        animacao = self.folha.obter(nome)
        indice = int(self.tempo / animacao.duracao_quadro) % len(animacao.quadros) \
            if animacao.repetir else 0
        return animacao.quadros[indice]


class Bloco:
    """Um bloco da grade do mapa."""

    def __init__(self, coluna, linha, definicao):
        self.coluna = coluna
        self.linha = linha
        self.x = coluna * TAMANHO_BLOCO
        self.y = linha * TAMANHO_BLOCO
        self.sprite = definicao["sprite"]
        self.solido = definicao.get("solido", True)
        self.perigo = definicao.get("perigo")            # None | "dano" | "morte"
        self.quebravel = definicao.get("quebravel", False)
        self.recompensa = definicao.get("recompensa")    # None | "moeda" | "cogumelo_vida" | "estrela"
        self.usado = False
        # impacto visual quando atingido por baixo
        self.deslocamento = 0.0
        self._velocidade_impacto = 0.0
        # caixa de perigo (espinhos: só a metade de baixo; lava: o bloco todo)
        if self.perigo == "dano":
            self.retangulo_perigo = pygame.Rect(self.x + 6, self.y + TAMANHO_BLOCO // 2, TAMANHO_BLOCO - 12,
                                                TAMANHO_BLOCO // 2)
        else:
            self.retangulo_perigo = pygame.Rect(self.x + 2, self.y + 8, TAMANHO_BLOCO - 4, TAMANHO_BLOCO - 8)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, TAMANHO_BLOCO, TAMANHO_BLOCO)

    def iniciar_impacto(self):
        self._velocidade_impacto = -260.0

    @property
    def animando(self):
        return self.deslocamento != 0.0 or self._velocidade_impacto != 0.0

    def atualizar(self, dt):
        if self.animando:
            self._velocidade_impacto += 1800.0 * dt
            self.deslocamento += self._velocidade_impacto * dt
            if self.deslocamento >= 0.0:
                self.deslocamento = 0.0
                self._velocidade_impacto = 0.0


class MapaDeBlocos:
    """Grade de blocos da fase (linhas x colunas)."""

    def __init__(self, colunas, linhas, tileset):
        self.colunas = colunas
        self.linhas = linhas
        self.tileset = tileset
        self.grade = [[None] * colunas for _ in range(linhas)]
        self._animando = []

    @property
    def largura_pixels(self):
        return self.colunas * TAMANHO_BLOCO

    @property
    def altura_pixels(self):
        return self.linhas * TAMANHO_BLOCO

    def obter(self, coluna, linha):
        if 0 <= linha < self.linhas and 0 <= coluna < self.colunas:
            return self.grade[linha][coluna]
        return None

    def definir(self, coluna, linha, bloco):
        self.grade[linha][coluna] = bloco

    def remover(self, coluna, linha):
        if 0 <= linha < self.linhas and 0 <= coluna < self.colunas:
            self.grade[linha][coluna] = None

    def impactar(self, bloco):
        """Anima o bloco (sobe e desce) e o registra para atualização."""
        bloco.iniciar_impacto()
        if bloco not in self._animando:
            self._animando.append(bloco)

    def atualizar(self, dt):
        self.tileset.atualizar(dt)
        for bloco in self._animando:
            bloco.atualizar(dt)
        self._animando = [b for b in self._animando if b.animando]

    def desenhar(self, tela, camera):
        coluna_ini = max(0, int(camera.x // TAMANHO_BLOCO))
        coluna_fim = min(self.colunas - 1, int((camera.x + camera.largura_tela) // TAMANHO_BLOCO))
        deslocamento_x, deslocamento_y = camera.deslocamento_tremor
        for linha in range(self.linhas):
            for coluna in range(coluna_ini, coluna_fim + 1):
                bloco = self.grade[linha][coluna]
                if bloco is None:
                    continue
                sprite = self.tileset.imagem(bloco.sprite)
                tela.blit(sprite, (round(bloco.x - camera.x + deslocamento_x),
                                   round(bloco.y - camera.y + bloco.deslocamento + deslocamento_y)))
