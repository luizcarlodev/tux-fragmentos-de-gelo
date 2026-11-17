"""Fundo com parallax em várias camadas, com troca suave de tema."""
import pygame

from configuracoes import ALTURA_BASE, LARGURA_BASE


class Cenario:
    """Desenha as camadas de fundo (cada uma rola numa fração da velocidade da câmera).

    ``temas`` tem o formato do JSON da fase::

        {"campo": {"musica": "fase", "camadas": [{"imagem": "...", "fator": 0.25, "deriva": 10}]}}
    """

    def __init__(self, recursos, temas, tema_inicial):
        self.recursos = recursos
        self.temas = temas
        self.tema_atual = tema_inicial
        self.tema_anterior = None
        self.progresso_troca = 1.0
        self.tempo = 0.0
        self._temporaria = pygame.Surface((LARGURA_BASE, ALTURA_BASE))

    def definir_tema(self, nome, instantaneo=False):
        if nome == self.tema_atual or nome not in self.temas:
            return False
        self.tema_anterior = self.tema_atual
        self.tema_atual = nome
        self.progresso_troca = 1.0 if instantaneo else 0.0
        return True

    def atualizar(self, dt):
        self.tempo += dt
        if self.progresso_troca < 1.0:
            self.progresso_troca = min(1.0, self.progresso_troca + dt / 1.2)

    def _desenhar_tema(self, tela, nome, camera_x):
        for camada in self.temas[nome]["camadas"]:
            imagem = self.recursos.fundo(camada["imagem"])
            largura = max(1, imagem.get_width())      # largura 0 (arte inválida) causaria laço infinito
            fator = camada.get("fator", 0.0)
            deslocamento = camera_x * fator + self.tempo * camada.get("deriva", 0.0)
            if fator == 0.0 and not camada.get("deriva"):
                tela.blit(imagem, (0, 0))
                continue
            inicio = -(deslocamento % largura)
            x = inicio
            while x < LARGURA_BASE:
                tela.blit(imagem, (round(x), 0))
                x += largura

    def desenhar(self, tela, camera_x):
        if self.progresso_troca >= 1.0 or self.tema_anterior is None:
            self._desenhar_tema(tela, self.tema_atual, camera_x)
            return
        self._desenhar_tema(tela, self.tema_anterior, camera_x)
        self._desenhar_tema(self._temporaria, self.tema_atual, camera_x)
        self._temporaria.set_alpha(int(255 * self.progresso_troca))
        tela.blit(self._temporaria, (0, 0))
