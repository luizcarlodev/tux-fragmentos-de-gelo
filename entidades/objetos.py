"""Objetos do mundo glacial: cristais, itens, totens, altar com Fragmento de Gelo, portal,
castelo, princesa, plataformas de gelo, projéteis e decorações."""
import math

import pygame

from configuracoes import TAMANHO_BLOCO
from entidades.entidade import Entidade
from sistemas.animacoes import Animador


class Cristal(Entidade):
    """Cristal de gelo coletável (a "moeda" do jogo)."""

    def __init__(self, centro_x, centro_y, recursos):
        folha = recursos.folha("objetos/cristal")
        super().__init__(centro_x - 16, centro_y - 24, 32, 48)
        self.animador = Animador(folha, "girando")
        self.animador.tempo = (centro_x % 7) * 0.05      # defasa os cristais para não girarem em uníssono

    def atualizar(self, dt):
        self.animador.atualizar(dt)


class ItemEmergente(Entidade):
    """Item que surge de um bloco de cristal e depois se move pelo cenário."""

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


class CoracaoDeGelo(ItemEmergente):
    """Coração congelado: vida extra. Desliza pelo chão e inverte ao bater."""

    pasta = "objetos/coracao_gelo"
    tipo = "coracao_gelo"

    def ao_terminar_de_emergir(self):
        self.vx = 140.0

    def mover(self, dt, colisoes):
        self.vy = min(self.vy + 2600.0 * dt, 900.0)
        if colisoes.mover_horizontal(self, self.vx * dt):
            self.vx = -self.vx
        no_chao, _, _ = colisoes.mover_vertical(self, self.vy * dt)
        if no_chao:
            self.vy = 0.0


class CristalMagico(ItemEmergente):
    """Cristal Mágico: invencibilidade temporária. Quica pelo cenário."""

    pasta = "objetos/cristal_magico"
    animacao = "brilho"
    tipo = "cristal_magico"

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


RECOMPENSAS = {"coracao_gelo": CoracaoDeGelo, "cristal_magico": CristalMagico}


class Totem(Entidade):
    """Totem glacial (checkpoint): ao ser tocado, acende e grava o ponto de retorno."""

    def __init__(self, centro_x, y_base, recursos, indice):
        folha = recursos.folha("objetos/totem")
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


class AltarDoFragmento(Entidade):
    """Altar que guarda um Fragmento de Gelo (1, 2 ou 3), o objetivo de cada fase."""

    def __init__(self, centro_x, y_base, recursos, numero):
        folha = recursos.folha("objetos/altar")
        largura, altura = folha.tamanho_quadro
        super().__init__(centro_x - largura / 2, y_base - altura, largura, altura)
        self.animador = Animador(folha, "parado")
        self.numero = numero
        self.fragmento = Animador(recursos.folha("objetos/fragmento_de_gelo"), f"fragmento_{numero}")
        self.coletado = False
        self.tempo = 0.0
        self.elevacao = 0.0          # usado pela sequência de coleta (o fragmento sobe)
        self.escala_brilho = 1.0

    @property
    def centro_do_fragmento(self):
        flutuacao = math.sin(self.tempo * 2.6) * 6
        return self.centro_x, self.y - 14 - self.elevacao + flutuacao

    @property
    def rect_coleta(self):
        cx, cy = self.centro_do_fragmento
        return pygame.Rect(round(cx - 40), round(cy - 40), 80, 130)

    def ativar(self):
        self.animador.tocar("ativo")

    def atualizar(self, dt):
        self.tempo += dt
        self.animador.atualizar(dt)
        self.fragmento.atualizar(dt)

    def desenhar(self, tela, camera, imagem=None):
        super().desenhar(tela, camera)
        if self.coletado and self.elevacao <= 0:
            return
        quadro = self.fragmento.imagem()
        if self.escala_brilho != 1.0:
            quadro = pygame.transform.scale(quadro, (round(quadro.get_width() * self.escala_brilho),
                                                     round(quadro.get_height() * self.escala_brilho)))
        cx, cy = self.centro_do_fragmento
        sx, sy = camera.mundo_para_tela(cx, cy)
        # halo discreto atrás do fragmento
        halo = pygame.Surface((110, 110), pygame.SRCALPHA)
        pulsar = 0.6 + 0.4 * math.sin(self.tempo * 4)
        pygame.draw.circle(halo, (170, 230, 255, int(60 * pulsar)), (55, 55), 54)
        pygame.draw.circle(halo, (220, 250, 255, int(70 * pulsar)), (55, 55), 32)
        tela.blit(halo, halo.get_rect(center=(round(sx), round(sy))))
        tela.blit(quadro, quadro.get_rect(center=(round(sx), round(sy))))


class Portal(Entidade):
    """Portal de gelo: abre depois da coleta do fragmento e leva à conclusão da fase."""

    def __init__(self, centro_x, y_base, recursos):
        folha = recursos.folha("objetos/portal")
        largura, altura = folha.tamanho_quadro
        super().__init__(centro_x - largura / 2, y_base - altura, largura, altura)
        self.animador = Animador(folha, "fechado")
        self.aberto = False

    def abrir(self):
        self.aberto = True
        self.animador.tocar("abrindo", reiniciar=True)

    @property
    def x_entrada(self):
        return self.centro_x

    def atualizar(self, dt):
        self.animador.atualizar(dt)
        if self.aberto and self.animador.nome_atual == "abrindo" and self.animador.finalizada:
            self.animador.tocar("aberto")


class CasteloDeGelo(Entidade):
    """Castelo do Inverno Eterno: aparece ao fundo no fim das fases (decorativo)."""

    def __init__(self, x_esquerda, y_base, recursos):
        folha = recursos.folha("objetos/castelo_gelo")
        largura, altura = folha.tamanho_quadro
        super().__init__(x_esquerda, y_base - altura, largura, altura)
        self.animador = Animador(folha, "parado")

    @property
    def porta_x(self):
        return self.x + self.largura / 2


class Princesa(Entidade):
    """Princesa do Gelo (aprisionada no castelo; aparece no salão final)."""

    def __init__(self, centro_x, y_base, recursos):
        folha = recursos.folha("personagens/princesa")
        largura, altura = folha.caixa_colisao or (34, 58)
        super().__init__(centro_x - largura / 2, y_base - altura, largura, altura)
        self.animador = Animador(folha, "presa")
        self.espelhado = True                    # olha para a esquerda, esperando o herói

    def tocar(self, nome):
        self.animador.tocar(nome)

    def atualizar(self, dt):
        self.animador.atualizar(dt)


class PrisaoDeGelo(Entidade):
    """Bloco de gelo translúcido desenhado SOBRE a princesa; racha e se estilhaça no final."""

    def __init__(self, alvo, recursos):
        folha = recursos.folha("objetos/prisao_de_gelo")
        largura, altura = folha.tamanho_quadro
        super().__init__(alvo.centro_x - largura / 2, alvo.base - altura + 4, largura, altura)
        self.animador = Animador(folha, "intacta")
        self.visivel = True

    def rachar(self):
        self.animador.tocar("rachando", reiniciar=True)

    def estilhacar(self):
        self.animador.tocar("estilhacando", reiniciar=True)

    @property
    def terminou(self):
        return self.animador.nome_atual == "estilhacando" and self.animador.finalizada

    def atualizar(self, dt):
        self.animador.atualizar(dt)

    def desenhar(self, tela, camera, imagem=None):
        if self.visivel and not self.terminou:
            super().desenhar(tela, camera)


class ChaveMagica(Entidade):
    """Chave formada pelos três Fragmentos de Gelo (sequência final da fase 3)."""

    def __init__(self, centro_x, centro_y, recursos):
        super().__init__(centro_x - 24, centro_y - 24, 48, 48)
        self.animador = Animador(recursos.folha("objetos/chave_magica"), "brilho")
        self.escala = 1.0
        self.centro = (centro_x, centro_y)

    def atualizar(self, dt):
        self.animador.atualizar(dt)

    def desenhar(self, tela, camera, imagem=None):
        quadro = self.animador.imagem()
        if self.escala != 1.0:
            quadro = pygame.transform.scale(quadro, (round(quadro.get_width() * self.escala),
                                                     round(quadro.get_height() * self.escala)))
        sx, sy = camera.mundo_para_tela(*self.centro)
        halo = pygame.Surface((150, 150), pygame.SRCALPHA)
        pygame.draw.circle(halo, (255, 230, 150, 60), (75, 75), 72)
        pygame.draw.circle(halo, (255, 250, 220, 80), (75, 75), 40)
        tela.blit(halo, halo.get_rect(center=(round(sx), round(sy))))
        tela.blit(quadro, quadro.get_rect(center=(round(sx), round(sy))))


class Lembranca(Entidade):
    """Orbe dourado da câmara secreta (lembrança da princesa)."""

    def __init__(self, centro_x, centro_y, recursos):
        folha = recursos.folha("objetos/lembranca")
        largura, altura = folha.caixa_colisao or (40, 40)
        super().__init__(centro_x - largura / 2, centro_y - altura / 2, largura, altura)
        self.animador = Animador(folha, "brilhando")
        self.tempo = 0.0
        self.y_base = self.y

    def atualizar(self, dt):
        self.tempo += dt
        self.y = self.y_base + math.sin(self.tempo * 2.2) * 7
        self.animador.atualizar(dt)


class PlataformaMovel(Entidade):
    """Plataforma de gelo que oscila (horizontal ou vertical); só é sólida por cima."""

    def __init__(self, dados, recursos):
        folha = recursos.folha("objetos/plataforma_gelo")
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

    def desenhar(self, tela, camera, imagem=None):
        sx, sy = camera.mundo_para_tela(self.x, self.y)
        tela.blit(self.imagem_larga, (round(sx), round(sy)))


class Projetil(Entidade):
    """Estilhaço de gelo lançado por inimigos voadores; machuca o jogador."""

    def __init__(self, centro_x, centro_y, recursos, vx=0.0):
        folha = recursos.folha("objetos/projetil_gelo")
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
    """Elemento decorativo do cenário (sem colisão). ``frente`` = desenhado na frente do jogador."""

    def __init__(self, dados, recursos):
        folha = recursos.folha("cenarios/decoracoes/" + dados["imagem"])
        self.animador = Animador(folha)
        imagem = self.animador.imagem()
        self.x = dados["coluna"] * TAMANHO_BLOCO
        self.y = dados["linha_base"] * TAMANHO_BLOCO - imagem.get_height()
        self.largura = imagem.get_width()
        self.frente = bool(dados.get("frente", False))

    def atualizar(self, dt):
        self.animador.atualizar(dt)

    def desenhar(self, tela, camera):
        sx, sy = camera.mundo_para_tela(self.x, self.y)
        tela.blit(self.animador.imagem(), (round(sx), round(sy)))
