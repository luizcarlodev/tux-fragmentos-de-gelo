"""Sequência especial de conclusão: mastro → caminhada → encontro com a princesa → fogos."""
import random

from entidades.efeitos import CoracaoFlutuante, criar_fogos

VELOCIDADE_DESCIDA = 300.0
DURACAO_COMEMORACAO = 5.5


class SequenciaFinal:
    """Roteiro automático executado quando o jogador toca o mastro final.

    Etapas: ``descendo`` (desliza pelo mastro) → ``espera`` → ``andando``
    (caminha até a princesa) → ``encontro`` (corações e fogos) → ``concluida``.
    """

    def __init__(self, fase):
        self.fase = fase
        jogador, mastro = fase.jogador, fase.mastro
        # bônus proporcional à altura em que o jogador agarrou o mastro (100 a 1000)
        altura_relativa = max(0.0, min(1.0, (mastro.base - jogador.base) / mastro.altura))
        bonus = max(1, round(altura_relativa * 10)) * 100
        fase.pontuacao.bonus_mastro = bonus
        fase.pontuacao.adicionar_pontos(bonus)
        fase.pontuacao.contando_tempo = False
        fase._texto(mastro.centro_x + 50, jogador.y, f"+{bonus}", (255, 230, 90), 30)
        jogador.congelado = True
        jogador.vx = jogador.vy = 0.0
        jogador.tempo_estrela = 0.0
        jogador.x = mastro.x - jogador.largura + 8
        jogador.espelhado = False
        jogador.animador.tocar("pulando", reiniciar=True)
        mastro.tocado = True
        fase.audio.parar_musica()
        fase.audio.tocar_efeito("mastro")
        fase.projeteis.clear()
        self.estado = "descendo"
        self.tempo = 0.0
        self.proximo_fogo = 0.0
        self.proximo_coracao = 0.0
        self.pulos = 0
        self.musica_iniciada = False
        self.concluida = False

    @property
    def _entrada_vazia(self):
        return {"esquerda": False, "direita": False, "pular": False, "correr": False}

    def atualizar(self, dt):
        metodo = getattr(self, f"_{self.estado}", None)
        if metodo:
            metodo(dt)

    # ------------------------------------------------------------------ etapas
    def _descendo(self, dt):
        jogador, mastro = self.fase.jogador, self.fase.mastro
        passo = VELOCIDADE_DESCIDA * dt
        jogador.y = min(jogador.y + passo, mastro.base - jogador.altura)
        mastro.descer_bandeira(passo)
        jogador.animador.atualizar(dt)
        if jogador.base >= mastro.base - 0.5 and mastro.bandeira_embaixo:
            self.estado, self.tempo = "espera", 0.0

    def _espera(self, dt):
        self.tempo += dt
        if self.tempo >= 0.6:
            jogador, mastro = self.fase.jogador, self.fase.mastro
            jogador.x = mastro.x + mastro.largura + 6
            jogador.y = mastro.base - jogador.altura
            jogador.congelado = False
            jogador.espelhado = False
            self.estado = "andando"

    def _andando(self, dt):
        fase = self.fase
        jogador, princesa = fase.jogador, fase.princesa
        alvo = (princesa.centro_x - 90) if princesa else (fase.castelo.porta_x if fase.castelo else jogador.centro_x)
        chegou = jogador.centro_x >= alvo
        entrada = self._entrada_vazia
        entrada["direita"] = not chegou
        jogador.atualizar(dt, entrada, fase.colisoes)
        if chegou and abs(jogador.vx) < 15 and jogador.no_chao:
            jogador.vx = 0.0
            jogador.espelhado = False
            self.estado, self.tempo = "encontro", 0.0
            if princesa:
                princesa.comemorar()
            fase.audio.tocar_musica("conclusao", repetir=False)

    def _encontro(self, dt):
        fase = self.fase
        jogador, princesa = fase.jogador, fase.princesa
        self.tempo += dt
        entrada = self._entrada_vazia
        if self.pulos < 2 and self.tempo >= 0.3 + self.pulos * 1.3:
            jogador.pedir_pulo()
            self.pulos += 1
        entrada["pular"] = jogador.vy < 0 and self.tempo < 3.0
        jogador.atualizar(dt, entrada, fase.colisoes)
        for evento in jogador.eventos:
            pass
        jogador.eventos.clear()
        meio_x = (jogador.centro_x + (princesa.centro_x if princesa else jogador.centro_x)) / 2
        if self.tempo >= self.proximo_coracao and princesa:
            fase.efeitos.append(CoracaoFlutuante(fase.recursos.folha("objetos/coracao"),
                                                 meio_x + random.uniform(-25, 25), jogador.y - 10))
            self.proximo_coracao = self.tempo + 0.28
        if self.tempo >= self.proximo_fogo:
            x = meio_x + random.uniform(-380, 380)
            fase.efeitos.extend(criar_fogos(x, random.uniform(110, 300)))
            self.proximo_fogo = self.tempo + 0.55
        if self.tempo >= DURACAO_COMEMORACAO:
            self.estado = "concluida"
            self.concluida = True
