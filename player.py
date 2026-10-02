import utils
import config
import pygame
from entidade import Entidade
from projetil import Projetil
from animacao import Animacao

_PASTA_SPRITES_TUX = "assets/tux"

# Frames de jogo por quadro (menor = animação mais rápida)
_TICKS_POR_FRAME = {
    "idle": 14,
    "andar": 6,
    "pulo": 10,
    "ataque": 5,
}

_DURACAO_ANIMACAO_ATAQUE = 18   # frames

# Escala dos PNGs (128x256) para o tamanho em tela (2x o hitbox)
_ESCALA_SPRITE_TUX = 0.25


class Player(Entidade):

    def __init__(self, x, y, limite_direita):
        super().__init__(x, y, config.PLAYER_LARGURA, config.PLAYER_ALTURA, config.PLAYER_VIDA_INICIAL)

        self.limite_direita = limite_direita
        self.velocidade = config.PLAYER_VELOCIDADE

        self.velocidade_y = 0
        self.gravidade = config.PLAYER_GRAVIDADE
        self.pulando = False

        self.direcao = 1
        self.ataque_cooldown = 0

        self.animacoes = {
            nome: Animacao(_PASTA_SPRITES_TUX, nome, ticks_por_frame=ticks, escala=_ESCALA_SPRITE_TUX)
            for nome, ticks in _TICKS_POR_FRAME.items()
        }
        self.animacao_estado = "idle"
        self.animacao_ataque_timer = 0
        self._movendo_horizontal = False

        self.invencivel_timer = 0

        # última plataforma pisada, usada para voltar quando cai no void
        self.ultima_borda_segura = (x, y)
        self._ultima_plataforma_bounds = None   # (x, largura, y)

    @property
    def esta_morto(self):
        return self.vida <= 0

    def mover_player(self, teclas):
        self._movendo_horizontal = False

        if teclas[pygame.K_a]:
            self.direcao = -1
            self.mover(-self.velocidade, 0)
            self._movendo_horizontal = True

        if teclas[pygame.K_d]:
            self.direcao = 1
            self.mover(self.velocidade, 0)
            self._movendo_horizontal = True

        if self.x < config.LIMITE_ESQUERDA:
            self.x = config.LIMITE_ESQUERDA
            self.rect.x = self.x

        if self.x > self.limite_direita:
            self.x = self.limite_direita
            self.rect.x = self.x

    def pular(self, teclas, plataformas):
        if teclas[pygame.K_SPACE] and not self.pulando:
            self.velocidade_y = config.PLAYER_FORCA_PULO
            self.pulando = True

        self.velocidade_y += self.gravidade
        self.y += self.velocidade_y
        self.rect.y = self.y

        self.pulando = True

        # só colide com plataformas quando está caindo
        if self.velocidade_y >= 0:
            for plataforma in plataformas:
                if utils.checar_colisao(self.rect, plataforma.rect):
                    self.y = plataforma.y - self.altura
                    self.rect.y = self.y
                    self.velocidade_y = 0
                    self.pulando = False

                    self.ultima_borda_segura = (self.x, self.y)
                    self._ultima_plataforma_bounds = (plataforma.x, plataforma.largura, plataforma.y)

    def atacar(self, teclas):
        if self.ataque_cooldown > 0:
            self.ataque_cooldown -= 1

        if teclas[config.TECLA_ATAQUE] and self.ataque_cooldown <= 0:
            self.ataque_cooldown = config.ATAQUE_COOLDOWN
            self.animacao_ataque_timer = _DURACAO_ANIMACAO_ATAQUE
            return Projetil(self.x + self.largura / 2, self.y + self.altura / 2, self.direcao, origem="tux")

        return None

    def sofrer_dano(self, origem_x, forca_knockback=None):
        """Retorna True se o dano foi aplicado, False se o Tux estava invencível."""
        if self.invencivel_timer > 0:
            return False

        self.receber_dano(config.PLAYER_DANO_INIMIGO)

        forca = forca_knockback if forca_knockback is not None else config.PLAYER_KNOCKBACK_FORCA
        direcao_knockback = 1 if self.x > origem_x else -1   # empurra para longe da origem
        self.mover(direcao_knockback * forca, 0)

        self.invencivel_timer = config.PLAYER_INVENCIBILIDADE_DURACAO
        return True

    def cair_no_void(self):
        """Perde 1 vida e volta para a última plataforma pisada, longe da borda."""
        if self.invencivel_timer > 0:
            return

        self._vida -= config.VOID_DANO_VIDA

        if self._ultima_plataforma_bounds:
            plat_x, plat_largura, plat_y = self._ultima_plataforma_bounds
            margem = config.TILE

            min_x = plat_x + margem
            max_x = plat_x + plat_largura - self.largura - margem

            if max_x < min_x:
                novo_x = plat_x + (plat_largura - self.largura) / 2
            else:
                novo_x = min(max(self.x, min_x), max_x)

            self.x = novo_x
            self.y = plat_y - self.altura
        else:
            self.x, self.y = self.ultima_borda_segura

        self.rect.x = self.x
        self.rect.y = self.y
        self.velocidade_y = 0
        self.pulando = False

        self.invencivel_timer = config.PLAYER_INVENCIBILIDADE_DURACAO

    def atualizar_timers(self):
        if self.invencivel_timer > 0:
            self.invencivel_timer -= 1

        if self.animacao_ataque_timer > 0:
            self.animacao_ataque_timer -= 1

        self._atualizar_estado_animacao()
        self.animacoes[self.animacao_estado].atualizar()

    def _atualizar_estado_animacao(self):
        """Prioridade: ataque > pulo > andar > idle."""
        novo_estado = "idle"
        if self.animacao_ataque_timer > 0:
            novo_estado = "ataque"
        elif self.pulando:
            novo_estado = "pulo"
        elif self._movendo_horizontal:
            novo_estado = "andar"

        if novo_estado != self.animacao_estado:
            self.animacao_estado = novo_estado
            self.animacoes[novo_estado].reiniciar()

    def desenhar(self, tela, camera_x=0):
        if self.invencivel_timer > 0 and self.invencivel_timer % 10 < 5:
            return

        frame = self.animacoes[self.animacao_estado].frame_atual()
        if frame is None:
            super().desenhar(tela, config.COR_TUX, camera_x)
            return

        if self.direcao == -1:
            frame = pygame.transform.flip(frame, True, False)

        # sprite maior que o hitbox: centraliza e alinha pela base
        pos_x = self.rect.x - camera_x - (frame.get_width() - self.rect.width) // 2
        pos_y = self.rect.y - (frame.get_height() - self.rect.height)
        tela.blit(frame, (pos_x, pos_y))
