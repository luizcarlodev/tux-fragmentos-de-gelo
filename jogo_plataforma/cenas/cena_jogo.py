"""Cena principal: a partida em andamento (fase, HUD, pausa, morte e conclusão)."""
import math

import pygame

from cenas.cena import Cena
from configuracoes import CORES, LARGURA_BASE, TEMPO_LIMITE_PADRAO
from fases.gerenciador_de_fases import GerenciadorDeFases
from interface.hud import Hud
from interface.textos import desenhar_texto
from sistemas.pontuacao import SistemaDePontuacao

PASSO_MAXIMO = 1.0 / 50.0       # a física é dividida em passos pequenos (evita atravessar blocos)
TEMPO_DA_MORTE = 2.4
TEMPO_MINIMO_APOS_MORTE = 100.0


class CenaJogo(Cena):
    """Executa a partida. ``continuar=True`` retoma o último checkpoint salvo."""

    def __init__(self, aplicacao, continuar=False):
        super().__init__(aplicacao)
        self.pontuacao = SistemaDePontuacao(TEMPO_LIMITE_PADRAO)
        self.fase = GerenciadorDeFases.criar(1, aplicacao.recursos, aplicacao.audio, self.pontuacao,
                                             ao_checkpoint=self._salvar_checkpoint)
        tempo = float(self.fase.dados.get("tempo_limite", TEMPO_LIMITE_PADRAO))
        self.pontuacao.tempo_limite = self.pontuacao.tempo_restante = tempo
        self.hud = Hud(aplicacao.recursos)
        self.tempo_total = 0.0
        self.tempo_morte = 0.0
        self._saindo = False
        if continuar:
            progresso = aplicacao.salvamento.obter_progresso()
            if progresso and self.fase.restaurar_checkpoint(progresso["checkpoint"]):
                self.pontuacao.importar_progresso(progresso)

    # ------------------------------------------------------------------ ciclo de vida
    def ao_entrar(self):
        self.app.audio.tocar_musica(self.fase.musica_atual_do_tema() or "fase")

    def ao_pausar(self):
        self.app.audio.pausar_musica()

    def ao_retomar(self):
        self.app.audio.retomar_musica()

    # ------------------------------------------------------------------ entrada
    def _entrada(self):
        c = self.app.controles
        return {"esquerda": c.pressionada("esquerda"), "direita": c.pressionada("direita"),
                "pular": c.pressionada("pular"), "correr": c.pressionada("correr")}

    def tratar_evento(self, evento):
        if evento.type == pygame.WINDOWFOCUSLOST and not self._saindo:
            self.pausar()
            return
        acao = self.app.controles.acao_do_evento(evento)
        if acao == "pular":
            self.fase.pedir_pulo()
        elif acao == "pausar" and not self._saindo and self.fase.final is None:
            self.pausar()

    def pausar(self):
        from cenas.menu_pausa import MenuPausa
        if self.app.cenas.cena_atual is self:
            self.app.cenas.empilhar(MenuPausa(self.app, self))

    # ------------------------------------------------------------------ atualização
    def atualizar(self, dt):
        self.tempo_total += dt
        self.hud.atualizar(dt)
        entrada = self._entrada()
        passos = max(1, math.ceil(dt / PASSO_MAXIMO))
        for _ in range(passos):
            self._passo(dt / passos, entrada)
        if self._saindo:
            return
        if self.fase.jogador_morto:
            self.tempo_morte += dt
            if self.tempo_morte >= TEMPO_DA_MORTE:
                self._apos_morte()
        elif self.fase.concluida:
            self._concluir()

    def _passo(self, dt, entrada):
        fase = self.fase
        fase.atualizar(dt, entrada)
        if fase.final is None and fase.jogador.vivo:
            self.pontuacao.atualizar_tempo(dt)
            if self.pontuacao.tempo_esgotado:
                fase.perder_vida_fatal()

    # ------------------------------------------------------------------ eventos de partida
    def _salvar_checkpoint(self, indice):
        self.app.salvamento.salvar_progresso(self.pontuacao.exportar_progresso(indice))

    def _apos_morte(self):
        self._saindo = True
        if self.pontuacao.vidas > 0:
            self.app.cenas.executar_com_transicao(self._renascer, "fade")
        else:
            from cenas.tela_game_over import TelaGameOver
            self.app.salvamento.limpar_progresso()
            novo_recorde = self.app.salvamento.registrar_pontuacao(self.pontuacao.pontos)
            self.app.cenas.trocar(TelaGameOver(self.app, self.pontuacao.pontos, novo_recorde), "fade")

    def _renascer(self):
        self.fase.renascer()
        self.pontuacao.tempo_restante = max(self.pontuacao.tempo_restante, TEMPO_MINIMO_APOS_MORTE)
        self.tempo_morte = 0.0
        self._saindo = False
        self.app.audio.tocar_musica(self.fase.musica_atual_do_tema() or "fase")

    def _concluir(self):
        from cenas.tela_vitoria import TelaVitoria
        self._saindo = True
        resultado = self.pontuacao.calcular_final()
        novo_recorde = self.app.salvamento.registrar_pontuacao(resultado["total"])
        self.app.salvamento.limpar_progresso()
        jogador = self.fase.jogador
        centro = self.fase.camera.mundo_para_tela(jogador.centro_x, jogador.centro_y)
        self.app.cenas.trocar(TelaVitoria(self.app, resultado, novo_recorde), "iris",
                              (int(centro[0]), int(centro[1])))

    # ------------------------------------------------------------------ desenho
    def desenhar(self, tela):
        self.fase.desenhar(tela)
        self.hud.desenhar(tela, self.pontuacao, self.fase, self.app.salvamento.melhor_pontuacao)
        if self.tempo_total < 3.5:
            alfa = int(255 * min(1.0, (3.5 - self.tempo_total) / 0.8))
            desenhar_texto(tela, self.fase.nome.upper(), 54, CORES["texto"], (LARGURA_BASE // 2, 190),
                           contorno=True, alfa=alfa)
