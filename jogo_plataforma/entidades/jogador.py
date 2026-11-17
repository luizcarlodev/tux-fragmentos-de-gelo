"""Jogador: movimentação inspirada em plataformas clássicas, com máquina de estados."""
from enum import Enum

import pygame

from configuracoes import (
    ACELERACAO_AR, ACELERACAO_CHAO, BONUS_PULO_VELOCIDADE, DESACELERACAO_AR, DESACELERACAO_CHAO,
    DURACAO_ATORDOAMENTO, DURACAO_ESTRELA, DURACAO_INVULNERAVEL, FORCA_PULO, FREIO_AR, FREIO_CHAO,
    GRAVIDADE_QUEDA, GRAVIDADE_SUBIDA, IMPULSO_PISAO, IMPULSO_PISAO_PULANDO, KNOCKBACK_X, KNOCKBACK_Y,
    MULTIPLICADOR_CORTE_PULO, TEMPO_BUFFER_PULO, TEMPO_COYOTE, VELOCIDADE_CAMINHADA, VELOCIDADE_CORRIDA,
    VELOCIDADE_QUEDA_MAXIMA,
)
from entidades.entidade import Entidade
from sistemas.animacoes import Animador


class EstadoJogador(Enum):
    """Estados da máquina de estados do jogador."""
    PARADO = "parado"
    ANDANDO = "andando"
    CORRENDO = "correndo"
    PULANDO = "pulando"
    CAINDO = "caindo"
    DANO = "dano"
    MORRENDO = "morrendo"


# estado → nome da animação na spritesheet
ANIMACAO_DO_ESTADO = {
    EstadoJogador.PARADO: "parado",
    EstadoJogador.ANDANDO: "andando",
    EstadoJogador.CORRENDO: "correndo",
    EstadoJogador.PULANDO: "pulando",
    EstadoJogador.CAINDO: "caindo",
    EstadoJogador.DANO: "dano",
    EstadoJogador.MORRENDO: "morrendo",
}

CORES_ESTRELA = [(120, 0, 0), (120, 100, 0), (0, 120, 0), (0, 100, 120), (80, 0, 120)]


def _aproximar(valor, alvo, passo):
    """Move ``valor`` na direção de ``alvo`` em no máximo ``passo``."""
    if valor < alvo:
        return min(valor + passo, alvo)
    return max(valor - passo, alvo)


class Jogador(Entidade):
    """Personagem controlado pelo jogador."""

    def __init__(self, centro_x, y_base, recursos):
        folha = recursos.folha("personagens/jogador")
        largura, altura = folha.caixa_colisao or (34, 58)
        super().__init__(centro_x - largura / 2, y_base - altura, largura, altura)
        self.animador = Animador(folha, "parado")
        self.estado = EstadoJogador.PARADO
        self.no_chao = False
        self.plataforma = None
        self.tempo_coyote = 0.0
        self.tempo_buffer = 0.0
        self.tempo_atordoado = 0.0
        self.tempo_invulneravel = 0.0
        self.tempo_estrela = 0.0
        self.tempo_morte = 0.0
        self.pulo_por_entrada = False      # ``True`` durante um pulo iniciado pelo jogador (altura variável)
        self.bloco_cabeca = None           # bloco atingido com a cabeça neste quadro
        self.congelado = False             # usado na cena final
        self.oculto = False
        self.relogio = 0.0
        self.eventos = []                  # eventos sonoros/visuais para a cena ("pulo", "pouso")

    # ------------------------------------------------------------ comandos externos
    def pedir_pulo(self):
        """Registra o apertar do botão de pulo (buffer de pulo)."""
        self.tempo_buffer = TEMPO_BUFFER_PULO

    @property
    def invulneravel(self):
        return self.tempo_invulneravel > 0 or self.tempo_estrela > 0

    @property
    def com_estrela(self):
        return self.tempo_estrela > 0

    @property
    def vivo(self):
        return self.estado != EstadoJogador.MORRENDO

    def ativar_estrela(self):
        self.tempo_estrela = DURACAO_ESTRELA

    def quicar(self, segurando_pulo):
        """Impulso depois de pisar em um inimigo."""
        self.vy = -(IMPULSO_PISAO_PULANDO if segurando_pulo else IMPULSO_PISAO)
        self.pulo_por_entrada = bool(segurando_pulo)
        self.no_chao = False
        self.plataforma = None
        self.tempo_coyote = 0.0

    def receber_dano(self, origem_x):
        """Aplica knockback + invulnerabilidade. Retorna ``False`` se estava protegido."""
        if not self.vivo or self.invulneravel:
            return False
        direcao = -1 if origem_x > self.centro_x else 1
        self.vx = direcao * KNOCKBACK_X
        self.vy = -KNOCKBACK_Y
        self.no_chao = False
        self.plataforma = None
        self.pulo_por_entrada = False
        self.tempo_atordoado = DURACAO_ATORDOAMENTO
        self.tempo_invulneravel = DURACAO_INVULNERAVEL
        self.estado = EstadoJogador.DANO
        self.animador.tocar("dano", reiniciar=True)
        return True

    def morrer(self):
        """Inicia a animação de morte."""
        self.estado = EstadoJogador.MORRENDO
        self.tempo_morte = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.tempo_estrela = 0.0
        self.animador.tocar("morrendo", reiniciar=True)

    def reaparecer(self, centro_x, y_base, invulneravel=2.5):
        """Recoloca o jogador (após morte ou ao carregar um checkpoint)."""
        self.x = centro_x - self.largura / 2
        self.y = y_base - self.altura
        self.vx = self.vy = 0.0
        self.estado = EstadoJogador.PARADO
        self.no_chao = False
        self.plataforma = None
        self.tempo_atordoado = 0.0
        self.tempo_invulneravel = invulneravel
        self.tempo_estrela = 0.0
        self.tempo_buffer = self.tempo_coyote = 0.0
        self.pulo_por_entrada = False
        self.congelado = False
        self.oculto = False
        self.animador.tocar("parado", reiniciar=True)

    # ------------------------------------------------------------ atualização
    def atualizar(self, dt, entrada, colisoes):
        """Atualiza física, estado e animação.

        ``entrada`` é um dict com as chaves ``esquerda``, ``direita``, ``pular`` (segurado)
        e ``correr``.
        """
        self.relogio += dt
        self.bloco_cabeca = None
        if self.estado == EstadoJogador.MORRENDO:
            self._atualizar_morte(dt)
            self.animador.atualizar(dt)
            return
        if self.congelado:
            self.animador.atualizar(dt)
            return

        self.tempo_atordoado = max(0.0, self.tempo_atordoado - dt)
        self.tempo_invulneravel = max(0.0, self.tempo_invulneravel - dt)
        self.tempo_estrela = max(0.0, self.tempo_estrela - dt)
        atordoado = self.tempo_atordoado > 0

        # ----- carregado por plataforma móvel
        if self.plataforma is not None:
            self.x += self.plataforma.dx
            self.y = self.plataforma.y - self.altura

        # ----- movimento horizontal (aceleração, freio e velocidade máxima)
        direcao = 0 if atordoado else int(entrada["direita"]) - int(entrada["esquerda"])
        correndo = bool(entrada["correr"]) and not atordoado
        velocidade_maxima = VELOCIDADE_CORRIDA if correndo else VELOCIDADE_CAMINHADA
        if direcao != 0:
            self.espelhado = direcao < 0
            if self.vx * direcao < 0:                              # invertendo: freia mais forte
                aceleracao = FREIO_CHAO if self.no_chao else FREIO_AR
            elif abs(self.vx) > velocidade_maxima:                 # acima do limite: desacelera suave
                aceleracao = DESACELERACAO_CHAO if self.no_chao else DESACELERACAO_AR
            else:
                aceleracao = ACELERACAO_CHAO if self.no_chao else ACELERACAO_AR
            self.vx = _aproximar(self.vx, direcao * velocidade_maxima, aceleracao * dt)
        elif self.no_chao:
            self.vx = _aproximar(self.vx, 0.0, (800.0 if atordoado else DESACELERACAO_CHAO) * dt)
        elif not atordoado:
            self.vx = _aproximar(self.vx, 0.0, DESACELERACAO_AR * dt)

        # ----- pulo (coyote time + buffer + altura variável)
        self.tempo_coyote = TEMPO_COYOTE if self.no_chao else max(0.0, self.tempo_coyote - dt)
        if self.tempo_buffer > 0 and self.tempo_coyote > 0 and not atordoado:
            self.vy = -(FORCA_PULO + abs(self.vx) * BONUS_PULO_VELOCIDADE)
            self.no_chao = False
            self.plataforma = None
            self.tempo_coyote = 0.0
            self.tempo_buffer = 0.0
            self.pulo_por_entrada = True
            self.eventos.append("pulo")
        self.tempo_buffer = max(0.0, self.tempo_buffer - dt)

        # ----- gravidade
        if self.vy < 0:
            gravidade = GRAVIDADE_SUBIDA
            if self.pulo_por_entrada and not entrada["pular"]:
                gravidade *= MULTIPLICADOR_CORTE_PULO            # soltou o botão: pulo mais baixo
        else:
            gravidade = GRAVIDADE_QUEDA
            self.pulo_por_entrada = False
        self.vy = min(self.vy + gravidade * dt, VELOCIDADE_QUEDA_MAXIMA)

        # ----- movimento + colisões
        if colisoes.mover_horizontal(self, self.vx * dt):
            self.vx = 0.0
        estava_no_ar = not self.no_chao
        no_chao, teto, plataforma = colisoes.mover_vertical(self, self.vy * dt)
        if no_chao:
            if self.vy > 0:
                self.vy = 0.0
            if estava_no_ar:
                self.eventos.append("pouso")
        if teto is not None:
            self.vy = 0.0
            self.pulo_por_entrada = False
            self.bloco_cabeca = teto
        self.no_chao = no_chao
        self.plataforma = plataforma

        self._atualizar_estado()
        self.animador.atualizar(dt)

    def _atualizar_morte(self, dt):
        self.tempo_morte += dt
        if self.tempo_morte < 0.45:
            return                                          # pausa dramática
        if self.vy == 0.0:
            self.vy = -820.0
        self.vy += 2400.0 * dt
        self.y += self.vy * dt

    def _atualizar_estado(self):
        """Máquina de estados: decide o estado conforme a situação física."""
        if self.tempo_atordoado > 0:
            novo = EstadoJogador.DANO
        elif not self.no_chao:
            novo = EstadoJogador.PULANDO if self.vy < 0 else EstadoJogador.CAINDO
        elif abs(self.vx) > VELOCIDADE_CAMINHADA + 40:
            novo = EstadoJogador.CORRENDO
        elif abs(self.vx) > 25:
            novo = EstadoJogador.ANDANDO
        else:
            novo = EstadoJogador.PARADO
        self.estado = novo
        self.animador.tocar(ANIMACAO_DO_ESTADO[novo])
        if novo in (EstadoJogador.ANDANDO, EstadoJogador.CORRENDO):
            self.animador.velocidade = max(0.6, min(1.7, abs(self.vx) / VELOCIDADE_CAMINHADA))
        else:
            self.animador.velocidade = 1.0

    # ------------------------------------------------------------ desenho
    def desenhar(self, tela, camera):
        if self.oculto:
            return
        if self.tempo_invulneravel > 0 and self.tempo_estrela <= 0 and self.vivo:
            if int(self.relogio * 14) % 2 == 0:             # pisca durante a invulnerabilidade
                return
        imagem = self.animador.imagem(self.espelhado)
        if self.tempo_estrela > 0:
            cor = CORES_ESTRELA[int(self.relogio * 14) % len(CORES_ESTRELA)]
            imagem = imagem.copy()
            imagem.fill(cor + (0,), special_flags=pygame.BLEND_RGB_ADD)
        super().desenhar(tela, camera, imagem)
