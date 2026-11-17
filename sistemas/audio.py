"""Gerenciador de áudio: músicas e efeitos sonoros com controle de volume."""
import pygame

from configuracoes import PASTA_RECURSOS, registrar_aviso

EXTENSOES = (".ogg", ".wav", ".mp3")


class GerenciadorDeAudio:
    """Toca músicas (``recursos/sons/musicas``) e efeitos (``recursos/sons/efeitos``).

    Se um arquivo não existir ou o dispositivo de áudio estiver indisponível,
    o jogo continua normalmente em silêncio.
    """

    def __init__(self, recursos, configuracoes):
        self.recursos = recursos
        self.configuracoes = configuracoes
        self.disponivel = pygame.mixer.get_init() is not None
        self.musica_atual = None
        self._avisos = set()

    # --------------------------------------------------------------- volumes
    @property
    def volume_musica(self):
        return self.configuracoes["volume_geral"] * self.configuracoes["volume_musica"]

    @property
    def volume_efeitos(self):
        return self.configuracoes["volume_geral"] * self.configuracoes["volume_efeitos"]

    def atualizar_volumes(self):
        """Reaplica os volumes (chamar após alterar as configurações)."""
        if self.disponivel:
            pygame.mixer.music.set_volume(self.volume_musica)

    # --------------------------------------------------------------- música
    def _caminho_musica(self, nome):
        pasta = PASTA_RECURSOS / "sons" / "musicas"
        for extensao in EXTENSOES:
            caminho = pasta / f"{nome}{extensao}"
            if caminho.exists():
                return caminho
        return None

    def tocar_musica(self, nome, repetir=True, fade_ms=0):
        """Toca a música ``nome`` (sem reiniciar se já estiver tocando)."""
        if not self.disponivel:
            return
        if nome == self.musica_atual and pygame.mixer.music.get_busy():
            return
        caminho = self._caminho_musica(nome)
        if caminho is None:
            if nome not in self._avisos:
                registrar_aviso(f"Música '{nome}' não encontrada em recursos/sons/musicas.")
                self._avisos.add(nome)
            self.musica_atual = None
            pygame.mixer.music.stop()
            return
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(str(caminho))
            pygame.mixer.music.set_volume(self.volume_musica)
            pygame.mixer.music.play(-1 if repetir else 0, fade_ms=fade_ms)
            self.musica_atual = nome
        except pygame.error as erro:
            registrar_aviso(f"Não foi possível tocar a música '{nome}': {erro}")
            self.musica_atual = None

    def parar_musica(self, fade_ms=0):
        if not self.disponivel:
            return
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
        self.musica_atual = None

    def pausar_musica(self):
        if self.disponivel:
            pygame.mixer.music.pause()

    def retomar_musica(self):
        if self.disponivel:
            pygame.mixer.music.unpause()

    # --------------------------------------------------------------- efeitos
    def tocar_efeito(self, nome, volume=1.0):
        """Toca o efeito ``recursos/sons/efeitos/<nome>.(ogg|wav|mp3)``."""
        if not self.disponivel:
            return
        for extensao in EXTENSOES:
            som = self.recursos.som(f"sons/efeitos/{nome}{extensao}")
            if som is not None:
                som.set_volume(max(0.0, min(1.0, self.volume_efeitos * volume)))
                som.play()
                return
        if nome not in self._avisos:
            registrar_aviso(f"Efeito sonoro '{nome}' não encontrado em recursos/sons/efeitos.")
            self._avisos.add(nome)
