"""Inimigos do jogo: três tipos com comportamentos distintos."""
import math

import pygame

from configuracoes import PONTOS_INIMIGO
from entidades.entidade import Entidade
from sistemas.animacoes import Animador

GRAVIDADE_INIMIGO = 2400.0


class Inimigo(Entidade):
    """Base dos inimigos: estados "vivo", "esmagado" e "arremessado"."""

    nome = "base"
    pasta = ""
    animacao_inicial = "andando"
    velocidade = 60.0
    pontos = PONTOS_INIMIGO

    def __init__(self, centro_x, y_base, recursos):
        folha = recursos.folha(self.pasta)
        largura, altura = folha.caixa_colisao or (40, 40)
        super().__init__(centro_x - largura / 2, y_base - altura, largura, altura)
        self.animador = Animador(folha, self.animacao_inicial)
        self.estado = "vivo"
        self.tempo_estado = 0.0
        self.direcao = -1
        self.no_chao = False
        self.x_origem = centro_x
        self.pedido_tiro = False

    # ------------------------------------------------------------ propriedades
    @property
    def perigoso(self):
        """``True`` se tocar nele machuca o jogador."""
        return self.estado == "vivo"

    @property
    def pisavel(self):
        return self.estado == "vivo"

    # ------------------------------------------------------------ ciclo
    def atualizar(self, dt, colisoes, jogador):
        self.animador.atualizar(dt)
        if self.estado == "vivo":
            self.comportamento(dt, colisoes, jogador)
        elif self.estado == "esmagado":
            self.tempo_estado += dt
            if self.tempo_estado > 0.45:
                self.ativo = False
        else:  # arremessado: cai girando para fora da tela
            self.vy += GRAVIDADE_INIMIGO * dt
            self.x += self.vx * dt
            self.y += self.vy * dt
            if self.y > colisoes.mapa.altura_pixels + 200:
                self.ativo = False
        if self.estado == "vivo" and self.y > colisoes.mapa.altura_pixels + 200:
            self.ativo = False                              # caiu em um buraco

    def comportamento(self, dt, colisoes, jogador):
        """Sobrescrito por cada tipo de inimigo."""

    # ------------------------------------------------------------ combate
    def ser_pisado(self):
        """O jogador pulou em cima. Retorna ``"morto"`` ou ``"ferido"``."""
        self._esmagar()
        return "morto"

    def _esmagar(self):
        self.estado = "esmagado"
        self.tempo_estado = 0.0
        self.vx = 0.0
        self.animador.tocar("esmagado", reiniciar=True)

    def ser_derrotado(self, origem_x=None):
        """Derrota o inimigo arremessando-o (estrela, bloco por baixo...)."""
        if self.estado == "arremessado":
            return
        self.estado = "arremessado"
        sentido = 1 if origem_x is None or origem_x < self.centro_x else -1
        self.vx = sentido * 160.0
        self.vy = -520.0

    # ------------------------------------------------------------ movimento
    def _borda_a_frente(self, colisoes):
        x_frente = self.x + self.largura + 3 if self.direcao > 0 else self.x - 3
        return not colisoes.ponto_solido(x_frente, self.y + self.altura + 4)

    def mover_no_chao(self, dt, colisoes, velocidade, modo_borda="virar"):
        """Anda pelo chão. ``modo_borda``: ``"virar"``, ``"parar"`` ou ``"cair"``."""
        self.espelhado = self.direcao < 0
        passo = self.direcao * velocidade * dt
        if self.no_chao and velocidade > 0 and modo_borda != "cair" and self._borda_a_frente(colisoes):
            if modo_borda == "virar":
                self.direcao = -self.direcao
            passo = 0.0
        if colisoes.mover_horizontal(self, passo):
            if modo_borda != "parar":
                self.direcao = -self.direcao
        self.vy = min(self.vy + GRAVIDADE_INIMIGO * dt, 900.0)
        no_chao, _, _ = colisoes.mover_vertical(self, self.vy * dt, usar_plataformas=False)
        if no_chao:
            self.vy = 0.0
        self.no_chao = no_chao


class Cogumelo(Inimigo):
    """Inimigo terrestre simples: anda de um lado para o outro e vira na borda."""

    nome = "cogumelo"
    pasta = "inimigos/cogumelo"
    velocidade = 70.0

    def comportamento(self, dt, colisoes, jogador):
        self.mover_no_chao(dt, colisoes, self.velocidade, "virar")


class Voador(Inimigo):
    """Inimigo aéreo: patrulha uma região e solta projéteis quando o jogador passa embaixo."""

    nome = "voador"
    pasta = "inimigos/voador"
    animacao_inicial = "voando"

    def __init__(self, centro_x, y_base, recursos):
        super().__init__(centro_x, y_base, recursos)
        self.y0 = self.y - self.altura * 0.0
        self.raio_x = 170.0
        self.velocidade_angular = 0.9
        self.tempo = (centro_x % 13) * 0.3
        self.tempo_tiro = 1.6

    def comportamento(self, dt, colisoes, jogador):
        self.tempo += dt
        novo_x = self.x_origem - self.largura / 2 + self.raio_x * math.sin(self.tempo * self.velocidade_angular)
        self.espelhado = (novo_x - self.x) < 0
        self.x = novo_x
        self.y = self.y0 + 34.0 * math.sin(self.tempo * 2.4)
        self.tempo_tiro -= dt
        if (self.tempo_tiro <= 0 and abs(jogador.centro_x - self.centro_x) < 330
                and jogador.centro_y > self.centro_y and jogador.vivo):
            self.pedido_tiro = True
            self.tempo_tiro = 2.8


class Perseguidor(Inimigo):
    """Inimigo agressivo: persegue o jogador e aguenta DOIS pisões.

    Estratégia: o primeiro pisão o atordoa e o deixa furioso (mais rápido);
    o segundo o derrota. A estrela também o derrota de uma vez.
    """

    nome = "perseguidor"
    pasta = "inimigos/perseguidor"
    velocidade = 60.0

    def __init__(self, centro_x, y_base, recursos):
        super().__init__(centro_x, y_base, recursos)
        self.vida = 2
        self.furioso = False
        self.tempo_atordoado = 0.0
        self.alcance = 440.0

    @property
    def perigoso(self):
        return self.estado == "vivo" and self.tempo_atordoado <= 0

    def ser_pisado(self):
        self.vida -= 1
        if self.vida <= 0:
            self._esmagar()
            return "morto"
        self.tempo_atordoado = 0.8
        self.animador.tocar("atordoado", reiniciar=True)
        return "ferido"

    def comportamento(self, dt, colisoes, jogador):
        if self.tempo_atordoado > 0:
            self.tempo_atordoado -= dt
            self.mover_no_chao(dt, colisoes, 0.0, "parar")
            if self.tempo_atordoado <= 0:
                self.furioso = True
            return
        self.animador.tocar("furioso" if self.furioso else "andando")
        distancia = jogador.centro_x - self.centro_x
        if abs(distancia) < self.alcance and abs(jogador.centro_y - self.centro_y) < 170 and jogador.vivo:
            self.direcao = 1 if distancia > 0 else -1
            velocidade = 250.0 if self.furioso else 150.0
            self.mover_no_chao(dt, colisoes, velocidade if abs(distancia) > 6 else 0.0, "parar")
        else:
            # patrulha perto do ponto de origem
            if self.centro_x > self.x_origem + 144:
                self.direcao = -1
            elif self.centro_x < self.x_origem - 144:
                self.direcao = 1
            self.mover_no_chao(dt, colisoes, self.velocidade * (1.6 if self.furioso else 1.0), "virar")


TIPOS_DE_INIMIGO = {
    "cogumelo": Cogumelo,
    "voador": Voador,
    "perseguidor": Perseguidor,
}


def criar_inimigo(tipo, centro_x, y_base, recursos):
    """Cria um inimigo pelo nome usado na legenda do mapa."""
    classe = TIPOS_DE_INIMIGO.get(tipo)
    if classe is None:
        raise ValueError(f"Tipo de inimigo desconhecido: '{tipo}'. Disponíveis: {', '.join(TIPOS_DE_INIMIGO)}")
    return classe(centro_x, y_base, recursos)
