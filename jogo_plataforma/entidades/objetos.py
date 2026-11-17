"""Objetos do mundo: moedas, itens, checkpoints, mastro, castelo, plataformas..."""
import math

import pygame

from configuracoes import TAMANHO_BLOCO
from entidades.entidade import Entidade
from sistemas.animacoes import Animador


class Moeda(Entidade):
    """Moeda coletável."""

    def __init__(self, centro_x, centro_y, recursos):
        folha = recursos.folha("objetos/moeda")
        super().__init__(centro_x - 16, centro_y - 24, 32, 48)
        self.animador = Animador(folha, "girando")
        self.animador.tempo = (centro_x % 7) * 0.05      # defasa as moedas para não girarem em uníssono

    def atualizar(self, dt):
        self.animador.atualizar(dt)


class ItemEmergente(Entidade):
    """Item que surge de um bloco ? e depois se move pelo cenário."""

    pasta = ""
    animacao = "parado"
    tipo = ""

    def __init__(self, bloco, recursos):
        folha = recursos.folha(self.pasta)
        largura, altura = folha.caixa_colisao or (40, 40)
        super().__init__(bloco.x + (TAMANHO_BLOCO - largura) / 2, bloco.y + TAMANHO_BLOCO - altura, largura, altura)
        self.animador = Animador(folha, self.animacao)
        self.emergindo = True
        self.y_alvo = bloco.y - altura
        self.direcao = 1

    def atualizar(self, dt, colisoes):
        self.animador.atualizar(dt)
        if self.emergindo:
            self.y -= 110.0 * dt
            if self.y <= self.y_alvo:
                self.y = self.y_alvo
                self.emergindo = False
                self.ao_terminar_de_emergir()
            return
        self.mover(dt, colisoes)
        if self.y > colisoes.mapa.altura_pixels + 200:
            self.ativo = False

    def ao_terminar_de_emergir(self):
        pass

    def mover(self, dt, colisoes):
        pass


class CogumeloVida(ItemEmergente):
    """Vida extra: anda pelo chão e inverte ao bater."""

    pasta = "objetos/cogumelo_vida"
    tipo = "cogumelo_vida"

    def ao_terminar_de_emergir(self):
        self.vx = 140.0

    def mover(self, dt, colisoes):
        self.vy = min(self.vy + 2600.0 * dt, 900.0)
        if colisoes.mover_horizontal(self, self.vx * dt):
            self.vx = -self.vx
        no_chao, _, _ = colisoes.mover_vertical(self, self.vy * dt)
        if no_chao:
            self.vy = 0.0


class Estrela(ItemEmergente):
    """Estrela de invencibilidade: quica pelo cenário."""

    pasta = "objetos/estrela"
    animacao = "brilho"
    tipo = "estrela"

    def ao_terminar_de_emergir(self):
        self.vx = 190.0
        self.vy = -500.0

    def mover(self, dt, colisoes):
        self.vy = min(self.vy + 1800.0 * dt, 900.0)
        if colisoes.mover_horizontal(self, self.vx * dt):
            self.vx = -self.vx
        no_chao, teto, _ = colisoes.mover_vertical(self, self.vy * dt)
        if no_chao:
            self.vy = -640.0
        elif teto is not None:
            self.vy = 0.0


RECOMPENSAS = {"cogumelo_vida": CogumeloVida, "estrela": Estrela}


class Checkpoint(Entidade):
    """Bandeira de checkpoint: ao ser tocada, grava o ponto de retorno."""

    def __init__(self, centro_x, y_base, recursos, indice):
        folha = recursos.folha("objetos/checkpoint")
        largura, altura = folha.caixa_colisao or (40, 96)
        super().__init__(centro_x - largura / 2, y_base - altura, largura, altura)
        self.animador = Animador(folha, "baixada")
        self.ativado = False
        self.indice = indice

    def ativar(self):
        self.ativado = True
        self.animador.tocar("levantada")

    @property
    def ponto_de_retorno(self):
        """(x do centro, y da base) usados para reposicionar o jogador."""
        return self.centro_x, self.base

    def atualizar(self, dt):
        self.animador.atualizar(dt)


class MastroFinal(Entidade):
    """Mastro da bandeira que marca o fim da fase."""

    def __init__(self, centro_x, y_base, recursos):
        self.folha_mastro = recursos.folha("objetos/mastro_final")
        largura, altura = self.folha_mastro.caixa_colisao or (12, 384)
        super().__init__(centro_x - largura / 2, y_base - altura, largura, altura)
        self.animador = Animador(self.folha_mastro, "parado")
        self.animador_bandeira = Animador(recursos.folha("objetos/bandeira_final"), "tremulando")
        self.deslocamento_bandeira = 30.0       # distância da bandeira ao topo
        self.base_y = y_base
        self.tocado = False

    def descer_bandeira(self, distancia):
        limite = self.altura - 48 - 8
        self.deslocamento_bandeira = min(limite, self.deslocamento_bandeira + distancia)

    @property
    def bandeira_embaixo(self):
        return self.deslocamento_bandeira >= self.altura - 48 - 8

    def atualizar(self, dt):
        self.animador_bandeira.atualizar(dt)

    def desenhar(self, tela, camera):
        super().desenhar(tela, camera)
        bandeira = self.animador_bandeira.imagem()
        sx, sy = camera.mundo_para_tela(self.centro_x - bandeira.get_width() + 6, self.y + self.deslocamento_bandeira)
        tela.blit(bandeira, (round(sx), round(sy)))


class Castelo(Entidade):
    """Castelo decorativo no fim da fase."""

    def __init__(self, x_esquerda, y_base, recursos):
        folha = recursos.folha("objetos/castelo")
        largura, altura = folha.tamanho_quadro
        super().__init__(x_esquerda, y_base - altura, largura, altura)
        self.animador = Animador(folha, "parado")

    @property
    def porta_x(self):
        return self.x + self.largura / 2


class Princesa(Entidade):
    """Princesa que espera o jogador no final."""

    def __init__(self, centro_x, y_base, recursos):
        folha = recursos.folha("personagens/princesa")
        largura, altura = folha.caixa_colisao or (34, 58)
        super().__init__(centro_x - largura / 2, y_base - altura, largura, altura)
        self.animador = Animador(folha, "parada")
        self.espelhado = True                    # olha para a esquerda, esperando o herói

    def comemorar(self):
        self.animador.tocar("feliz")

    def atualizar(self, dt):
        self.animador.atualizar(dt)


class PlataformaMovel(Entidade):
    """Plataforma que oscila (horizontal ou vertical); só é sólida por cima."""

    def __init__(self, dados, recursos):
        folha = recursos.folha("objetos/plataforma_movel")
        largura, altura = folha.caixa_colisao or (144, 24)
        largura = int(dados.get("largura_blocos", 3) * TAMANHO_BLOCO)
        self.eixo = dados.get("eixo", "x")
        self.amplitude = float(dados.get("amplitude", 2)) * TAMANHO_BLOCO
        self.periodo = max(0.5, float(dados.get("periodo", 4.0)))
        self.fase = float(dados.get("fase", 0.0))
        self.centro_x0 = float(dados["coluna_centro"]) * TAMANHO_BLOCO
        self.y0 = float(dados["linha"]) * TAMANHO_BLOCO
        super().__init__(self.centro_x0 - largura / 2, self.y0, largura, altura)
        self.animador = Animador(folha, "parada")
        self.imagem_larga = pygame.transform.scale(self.animador.imagem(), (largura, altura))
        self.tempo = 0.0
        self.x_anterior, self.y_anterior = self.x, self.y
        self.dx = self.dy = 0.0
        self._posicionar()
        self.x_anterior, self.y_anterior = self.x, self.y

    def _posicionar(self):
        desvio = self.amplitude * math.sin(2 * math.pi * self.tempo / self.periodo + self.fase)
        if self.eixo == "x":
            self.x = self.centro_x0 - self.largura / 2 + desvio
        else:
            self.y = self.y0 + desvio

    def atualizar(self, dt):
        self.x_anterior, self.y_anterior = self.x, self.y
        self.tempo += dt
        self._posicionar()
        self.dx = self.x - self.x_anterior
        self.dy = self.y - self.y_anterior

    def desenhar(self, tela, camera):
        sx, sy = camera.mundo_para_tela(self.x, self.y)
        tela.blit(self.imagem_larga, (round(sx), round(sy)))


class Projetil(Entidade):
    """Projétil lançado por inimigos voadores; machuca o jogador."""

    def __init__(self, centro_x, centro_y, recursos, vx=0.0):
        folha = recursos.folha("objetos/projetil")
        largura, altura = folha.caixa_colisao or (20, 20)
        super().__init__(centro_x - largura / 2, centro_y - altura / 2, largura, altura)
        self.animador = Animador(folha, "girando")
        self.vx = vx
        self.vy = 120.0

    def atualizar(self, dt, colisoes):
        self.animador.atualizar(dt)
        self.vy = min(self.vy + 900.0 * dt, 700.0)
        self.x += self.vx * dt
        self.y += self.vy * dt
        if colisoes.ponto_solido(self.centro_x, self.y + self.altura) or self.y > colisoes.mapa.altura_pixels + 50:
            self.ativo = False


class Decoracao:
    """Elemento decorativo do cenário (sem colisão)."""

    def __init__(self, dados, recursos):
        folha = recursos.folha("cenarios/decoracoes/" + dados["imagem"])
        self.animador = Animador(folha)
        imagem = self.animador.imagem()
        self.x = dados["coluna"] * TAMANHO_BLOCO
        self.y = dados["linha_base"] * TAMANHO_BLOCO - imagem.get_height()
        self.largura = imagem.get_width()

    def atualizar(self, dt):
        self.animador.atualizar(dt)

    def desenhar(self, tela, camera):
        sx, sy = camera.mundo_para_tela(self.x, self.y)
        tela.blit(self.animador.imagem(), (round(sx), round(sy)))
