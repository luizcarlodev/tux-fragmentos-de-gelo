import pygame
import config
from entidade import Entidade
from animacao import Animacao
import sprites

_PASTA_PROJETEIS = "assets/projeteis"
_PASTA_OBJETOS = "assets/objetos"

# Escala dos PNGs (canvas 64x64) para o tamanho em tela
_ESCALA_PROJETIL = 0.42

_animacoes_gelo_tux = None
_animacoes_pedra_golem = None
_sprite_cristal = None
_frames_aviso_nuvem = None


def _obter_frames_gelo_tux():
    global _animacoes_gelo_tux
    if _animacoes_gelo_tux is None:
        _animacoes_gelo_tux = Animacao(_PASTA_PROJETEIS, "gelo_tux", ticks_por_frame=6, escala=_ESCALA_PROJETIL)
    return _animacoes_gelo_tux


def _obter_frames_pedra_golem():
    global _animacoes_pedra_golem
    if _animacoes_pedra_golem is None:
        _animacoes_pedra_golem = Animacao(_PASTA_PROJETEIS, "pedra_golem", ticks_por_frame=6, escala=_ESCALA_PROJETIL)
    return _animacoes_pedra_golem


class Projetil(Entidade):
    """Projétil horizontal. origem: 'tux' ou 'golem' (muda o sprite)."""

    def __init__(self, x, y, direcao, origem="tux"):
        super().__init__(x, y, config.PROJETIL_LARGURA, config.PROJETIL_ALTURA, vida=0)
        self.direcao = direcao
        self.origem = origem
        self._animacao = _obter_frames_gelo_tux() if origem == "tux" else _obter_frames_pedra_golem()

    def atualizar(self):
        self.mover(self.direcao * config.PROJETIL_VELOCIDADE, 0)
        self._animacao.atualizar()

    def fora_da_tela(self, camera_x=0):
        margem = 64
        return self.x < camera_x - margem or self.x > camera_x + config.LARGURA_TELA + margem

    def desenhar(self, tela, camera_x=0):
        frame = self._animacao.frame_atual()
        if frame is None:
            super().desenhar(tela, config.COR_PROJETIL, camera_x)
            return

        if self.direcao == -1:
            frame = pygame.transform.flip(frame, True, False)

        cx = self.rect.x - camera_x + self.rect.width / 2
        cy = self.rect.y + self.rect.height / 2
        tela.blit(frame, (cx - frame.get_width() / 2, cy - frame.get_height() / 2))


class CristalGelo(Entidade):
    """Cristal da chuva: cai reto até atingir o chão."""

    def __init__(self, x, y):
        super().__init__(x, y, config.PROJETIL_LARGURA, config.PROJETIL_LARGURA, vida=0)

    def atualizar(self):
        self.mover(0, config.GOLEM_CHUVA_VELOCIDADE_QUEDA)

    def atingiu_chao(self):
        return self.y + self.altura >= config.CHAO_Y

    def desenhar(self, tela, camera_x=0):
        global _sprite_cristal
        if _sprite_cristal is None:
            _sprite_cristal = sprites.carregar(f"{_PASTA_OBJETOS}/cristal_chuva.png", config.PROJETIL_LARGURA * 2)

        if _sprite_cristal is None:
            super().desenhar(tela, config.COR_PROJETIL, camera_x)
            return

        cx = self.rect.x - camera_x + self.rect.width / 2
        cy = self.rect.y + self.rect.height / 2
        tela.blit(_sprite_cristal, (cx - _sprite_cristal.get_width() / 2, cy - _sprite_cristal.get_height() / 2))


class AvisoQueda(Entidade):
    """Nuvem que cresce no topo da tela antes do cristal cair."""

    def __init__(self, x):
        super().__init__(x, 0, config.PROJETIL_LARGURA, 2, vida=0)
        self._timer = config.GOLEM_CHUVA_TELEGRAPH_DURACAO
        self._duracao_total = config.GOLEM_CHUVA_TELEGRAPH_DURACAO

    def atualizar(self):
        self._timer -= 1
        progresso = 1 - max(self._timer, 0) / self._duracao_total
        self.altura = max(2, int(config.GOLEM_CHUVA_ALTURA_NUVEM_MAX * progresso))
        self.rect.height = self.altura

    def pronto(self):
        return self._timer <= 0

    def desenhar(self, tela, camera_x=0):
        global _frames_aviso_nuvem
        if _frames_aviso_nuvem is None:
            altura_alvo = round(config.GOLEM_CHUVA_ALTURA_NUVEM_MAX * 1.3)
            # 159 = altura útil (sem transparência) do maior frame da nuvem
            _frames_aviso_nuvem = Animacao(
                _PASTA_OBJETOS, "aviso_nuvem", ticks_por_frame=999, loop=False, escala=altura_alvo / 159
            ).frames

        if not _frames_aviso_nuvem:
            super().desenhar(tela, config.COR_TELEGRAPH_CHUVA, camera_x)
            return

        progresso = 1 - max(self._timer, 0) / self._duracao_total
        indice = min(len(_frames_aviso_nuvem) - 1, int(progresso * len(_frames_aviso_nuvem)))
        frame = _frames_aviso_nuvem[indice]

        cx = self.rect.x - camera_x + self.rect.width / 2
        tela.blit(frame, (cx - frame.get_width() / 2, 0))
