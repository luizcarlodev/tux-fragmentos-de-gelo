"""Cena principal: a partida em andamento (fase, HUD, pausa, morte, segredo e conclusão)."""
import math

import pygame

from cenas.cena import Cena
from configuracoes import CORES, LARGURA_BASE, PONTOS_SEGREDO, TEMPO_LIMITE_PADRAO, TOTAL_DE_FASES
from fases.gerenciador_de_fases import INFORMACOES, GerenciadorDeFases
from interface.hud import Hud
from interface.textos import desenhar_texto
from sistemas.pontuacao import SistemaDePontuacao

PASSO_MAXIMO = 1.0 / 50.0       # a física é dividida em passos pequenos (evita atravessar blocos)
TEMPO_DA_MORTE = 2.4
TEMPO_MINIMO_APOS_MORTE = 100.0


class CenaJogo(Cena):
    """Executa uma fase da campanha.

    ``numero_fase``: 1 a 3. ``continuar=True`` retoma o último checkpoint salvo (se for desta fase).
    """

    def __init__(self, aplicacao, numero_fase=1, continuar=False):
        super().__init__(aplicacao)
        self.numero_fase = numero_fase
        self.pontuacao = SistemaDePontuacao(TEMPO_LIMITE_PADRAO)
        self.fase = GerenciadorDeFases.criar(
            numero_fase, aplicacao.recursos, aplicacao.audio, self.pontuacao,
            ao_checkpoint=self._salvar_checkpoint, segredo_descoberto=aplicacao.salvamento.segredo_descoberto)
        tempo = float(self.fase.dados.get("tempo_limite", TEMPO_LIMITE_PADRAO))
        self.pontuacao.tempo_limite = self.pontuacao.tempo_restante = tempo
        self.hud = Hud(aplicacao.recursos)
        self.tempo_total = 0.0
        self.tempo_morte = 0.0
        self._saindo = False
        self._retorno_do_segredo = False
        if continuar:
            progresso = aplicacao.salvamento.obter_progresso()
            if progresso and progresso["fase"] == numero_fase and self.fase.restaurar_checkpoint(progresso["checkpoint"]):
                self.pontuacao.importar_progresso(progresso)

    # ------------------------------------------------------------------ ciclo de vida
    def _tocar_musica_da_fase(self):
        self.app.audio.tocar_musica(self.fase.musica_atual_do_tema() or "geleira")

    def ao_entrar(self):
        self._tocar_musica_da_fase()

    def ao_pausar(self):
        self.app.audio.pausar_musica()

    def ao_retomar(self):
        if self._retorno_do_segredo:          # voltou da câmara secreta: reinicia a música da fase
            self._retorno_do_segredo = False
            self._tocar_musica_da_fase()
        else:
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
        elif acao == "atacar":
            self.fase.pedir_ataque()
        elif acao == "dash":
            self.fase.pedir_dash()
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
        if self.fase.evento_segredo:
            self._abrir_camara_secreta()
        elif self.fase.jogador_morto:
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
        progresso = self.pontuacao.exportar_progresso(indice)
        progresso["fase"] = self.numero_fase
        self.app.salvamento.salvar_progresso(progresso)

    def _abrir_camara_secreta(self):
        """O Tux atravessou o portal secreto: empilha a Câmara da Lembrança (Easter Egg)."""
        from cenas.camara_secreta import CamaraSecreta
        self._saindo = True
        self._retorno_do_segredo = True
        self.app.cenas.empilhar(CamaraSecreta(self.app, self), "fade")

    def retornar_da_camara(self):
        """Chamado pela câmara secreta ao terminar (o jogo da fase continua de onde parou)."""
        self._saindo = False
        self.fase.retornar_do_segredo()

    def _apos_morte(self):
        self._saindo = True
        if self.pontuacao.vidas > 0:
            self.app.cenas.executar_com_transicao(self._renascer, "fade")
        else:
            from cenas.tela_game_over import TelaGameOver
            self.app.salvamento.limpar_progresso()
            novo_recorde = self.app.salvamento.registrar_pontuacao(self.pontuacao.pontos)
            self.app.cenas.trocar(TelaGameOver(self.app, self.numero_fase, self.pontuacao.pontos, novo_recorde),
                                  "fade")

    def _renascer(self):
        self.fase.renascer()
        self.pontuacao.tempo_restante = max(self.pontuacao.tempo_restante, TEMPO_MINIMO_APOS_MORTE)
        self.tempo_morte = 0.0
        self._saindo = False
        self._tocar_musica_da_fase()

    def _concluir(self):
        """O Tux entrou no portal: registra a fase e segue para a vitória (ou para o final da campanha)."""
        from cenas.cena_final import CenaFinal
        from cenas.tela_vitoria import TelaVitoria
        self._saindo = True
        salvamento = self.app.salvamento
        resultado = self.pontuacao.calcular_final()
        novo_recorde = salvamento.registrar_conclusao(self.numero_fase, resultado["total"])
        salvamento.limpar_progresso()
        jogador = self.fase.jogador
        centro = self.fase.camera.mundo_para_tela(jogador.centro_x, jogador.centro_y)
        if self.numero_fase >= TOTAL_DE_FASES:
            proxima = CenaFinal(self.app, self.numero_fase, resultado, novo_recorde)
        else:
            proxima = TelaVitoria(self.app, self.numero_fase, resultado, novo_recorde)
        self.app.cenas.trocar(proxima, "iris", (int(centro[0]), int(centro[1])))

    # ------------------------------------------------------------------ desenho
    def desenhar(self, tela):
        self.fase.desenhar(tela)
        self.hud.desenhar(tela, self.pontuacao, self.fase, self.app.salvamento.melhor_pontuacao,
                          self.app.salvamento.fragmentos_coletados)
        if self.tempo_total < 3.8:
            alfa = int(255 * min(1.0, (3.8 - self.tempo_total) / 0.8))
            info = INFORMACOES.get(self.numero_fase, {})
            desenhar_texto(tela, f"FASE {self.numero_fase}", 30, CORES["destaque"], (LARGURA_BASE // 2, 150),
                           contorno=True, alfa=alfa)
            desenhar_texto(tela, info.get("nome", self.fase.nome).upper(), 54, CORES["texto"],
                           (LARGURA_BASE // 2, 200), contorno=True, alfa=alfa)
