"""Botões de menu com navegação por teclado e mouse, efeito de hover e animação de seleção."""
import math

import pygame

from configuracoes import CORES
from interface.textos import desenhar_texto


class Botao:
    """Um botão retangular com texto e ação."""

    def __init__(self, texto, centro, acao, largura=400, altura=58):
        self.texto = texto
        self.acao = acao
        self.base = pygame.Rect(0, 0, largura, altura)
        self.base.center = centro
        self.escala = 1.0

    @property
    def retangulo(self):
        crescimento = int((self.escala - 1.0) * self.base.width)
        return self.base.inflate(crescimento, int(crescimento * 0.25))


class MenuDeBotoes:
    """Lista vertical de botões. Cuida de seleção, hover, cliques e sons."""

    def __init__(self, aplicacao, itens, centro_x=640, y_inicial=300, espacamento=72, largura=400, altura=58):
        self.app = aplicacao
        self.botoes = [Botao(texto, (centro_x, y_inicial + i * espacamento), acao, largura, altura)
                       for i, (texto, acao) in enumerate(itens)]
        self.selecionado = 0
        self.tempo = 0.0
        self.seta = aplicacao.recursos.imagem("interface/seta.png", 2)

    # ------------------------------------------------------------ interação
    def selecionar(self, indice, som=True):
        indice %= len(self.botoes)
        if indice != self.selecionado:
            self.selecionado = indice
            if som:
                self.app.audio.tocar_efeito("selecao")

    def ativar(self):
        botao = self.botoes[self.selecionado]
        self.app.audio.tocar_efeito("confirmacao")
        botao.acao()

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_UP, pygame.K_w):
                self.selecionar(self.selecionado - 1)
            elif evento.key in (pygame.K_DOWN, pygame.K_s):
                self.selecionar(self.selecionado + 1)
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.ativar()
        elif evento.type == pygame.MOUSEMOTION:
            for i, botao in enumerate(self.botoes):
                if botao.base.collidepoint(evento.pos):
                    self.selecionar(i)
                    break
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for i, botao in enumerate(self.botoes):
                if botao.base.collidepoint(evento.pos):
                    self.selecionado = i
                    self.ativar()
                    break

    # ------------------------------------------------------------ ciclo
    def atualizar(self, dt):
        self.tempo += dt
        for i, botao in enumerate(self.botoes):
            alvo = 1.08 if i == self.selecionado else 1.0
            botao.escala += (alvo - botao.escala) * min(1.0, dt * 14)

    def desenhar(self, tela):
        for i, botao in enumerate(self.botoes):
            self._desenhar_botao(tela, botao, i == self.selecionado)

    def _desenhar_botao(self, tela, botao, selecionado):
        retangulo = botao.retangulo
        sombra = retangulo.move(0, 5)
        pygame.draw.rect(tela, CORES["botao_borda"], sombra, border_radius=14)
        cor = CORES["botao_selecionado"] if selecionado else CORES["botao"]
        pygame.draw.rect(tela, cor, retangulo, border_radius=14)
        brilho = retangulo.inflate(-10, -retangulo.height // 2)
        brilho.top = retangulo.top + 4
        pygame.draw.rect(tela, tuple(min(255, c + 28) for c in cor), brilho, border_radius=10)
        borda = CORES["destaque"] if selecionado else CORES["botao_borda"]
        pygame.draw.rect(tela, borda, retangulo, width=3, border_radius=14)
        cor_texto = CORES["destaque"] if selecionado else CORES["texto"]
        desenhar_texto(tela, botao.texto, 36, cor_texto, retangulo.center)
        if selecionado:
            balanco = math.sin(self.tempo * 8) * 5
            tela.blit(self.seta, self.seta.get_rect(midright=(retangulo.left - 10 + balanco, retangulo.centery)))
