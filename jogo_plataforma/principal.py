"""Ponto de entrada do jogo. Execute:  python principal.py"""
import sys

import pygame

import configuracoes as cfg
from cenas.menu_principal import MenuPrincipal
from sistemas.animacoes import GerenciadorDeRecursos
from sistemas.audio import GerenciadorDeAudio
from sistemas.controles import Controles
from sistemas.gerenciador_de_cenas import GerenciadorDeCenas
from sistemas.salvamento import Salvamento


class Aplicacao:
    """Reúne os serviços compartilhados (janela, áudio, recursos, salvamento) e o laço principal.

    O jogo é sempre desenhado em uma superfície de 1280x720 que é escalada (com faixas
    pretas, se preciso) para a resolução escolhida — por isso a lógica não muda com a tela.
    """

    def __init__(self):
        try:
            pygame.mixer.pre_init(22050, -16, 1, 512)
        except pygame.error:
            pass
        pygame.init()
        try:
            pygame.mixer.init(22050, -16, 1, 512)
            pygame.mixer.set_num_channels(16)
        except pygame.error as erro:
            cfg.registrar_aviso(f"Áudio indisponível ({erro}); o jogo seguirá sem som.")
        self.configuracoes = cfg.Configuracoes.carregar()
        self.salvamento = Salvamento()
        self.controles = Controles(self.configuracoes)
        self.recursos = GerenciadorDeRecursos(cfg.PASTA_RECURSOS)
        self.audio = GerenciadorDeAudio(self.recursos, self.configuracoes)
        self.superficie = None            # criada após a janela existir (convert() exige modo de vídeo)
        self.janela = None
        self._destino = pygame.Rect(0, 0, cfg.LARGURA_BASE, cfg.ALTURA_BASE)
        self.relogio = pygame.time.Clock()
        self.executando = True
        self.aplicar_video()
        self.superficie = pygame.Surface((cfg.LARGURA_BASE, cfg.ALTURA_BASE)).convert()
        self.audio.atualizar_volumes()
        self.cenas = GerenciadorDeCenas(self)

    # ------------------------------------------------------------------ vídeo
    def aplicar_video(self):
        """(Re)cria a janela conforme resolução e modo de tela das configurações."""
        resolucao = tuple(self.configuracoes["resolucao"])
        try:
            if self.configuracoes["tela_cheia"]:
                self.janela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                self.janela = pygame.display.set_mode(resolucao)
        except pygame.error as erro:
            cfg.registrar_aviso(f"Não foi possível aplicar o modo de vídeo ({erro}); usando 1280x720.")
            self.janela = pygame.display.set_mode((cfg.LARGURA_BASE, cfg.ALTURA_BASE))
        pygame.display.set_caption(cfg.TITULO_JANELA)
        largura, altura = self.janela.get_size()
        escala = min(largura / cfg.LARGURA_BASE, altura / cfg.ALTURA_BASE)
        tamanho = (int(cfg.LARGURA_BASE * escala), int(cfg.ALTURA_BASE * escala))
        self._destino = pygame.Rect(0, 0, *tamanho)
        self._destino.center = (largura // 2, altura // 2)
        self._escala = escala
        self.janela.fill((0, 0, 0))

    def converter_posicao(self, posicao):
        """Posição na janela real → posição na superfície base 1280x720."""
        return (int((posicao[0] - self._destino.x) / self._escala),
                int((posicao[1] - self._destino.y) / self._escala))

    def _apresentar(self):
        if self._destino.size == self.superficie.get_size() and self._destino.topleft == (0, 0):
            self.janela.blit(self.superficie, (0, 0))
        else:
            pygame.transform.scale(self.superficie, self._destino.size, self.janela.subsurface(self._destino))
        pygame.display.flip()

    def alternar_tela_cheia(self):
        self.configuracoes["tela_cheia"] = not self.configuracoes["tela_cheia"]
        self.aplicar_video()
        self.configuracoes.salvar()

    # ------------------------------------------------------------------ laço principal
    def encerrar(self):
        self.executando = False

    def _traduzir_evento(self, evento):
        """Converte posições do mouse para coordenadas da tela base."""
        if evento.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            dados = dict(evento.dict)
            dados["pos"] = self.converter_posicao(evento.pos)
            return pygame.event.Event(evento.type, dados)
        return evento

    def executar(self):
        self.cenas.trocar(MenuPrincipal(self), transicao=None)
        while self.executando:
            dt = min(self.relogio.tick(cfg.FPS) / 1000.0, 0.05)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.encerrar()
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                    self.alternar_tela_cheia()
                else:
                    self.cenas.tratar_evento(self._traduzir_evento(evento))
            self.cenas.atualizar(dt)
            self.cenas.desenhar(self.superficie)
            self._apresentar()
        self.configuracoes.salvar()
        pygame.quit()


def principal():
    try:
        Aplicacao().executar()
    except KeyboardInterrupt:
        pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(principal())
