"""Tela HOW TO PLAY: controles atuais, objetivo e dicas (lê as teclas configuradas)."""
import pygame

from cenas.cena import Cena
from configuracoes import ACOES_CONTROLE, ALTURA_BASE, CORES, LARGURA_BASE, NOMES_ACOES
from interface.efeitos_de_tela import gradiente_vertical
from interface.textos import desenhar_texto
from sistemas.animacoes import Animador

DICAS = [
    ("moeda", "girando", "Colete moedas: 10 pontos cada (100 moedas = vida extra)."),
    ("inimigos/cogumelo", "andando", "Pule EM CIMA dos inimigos para derrotá-los (100 pontos)."),
    ("inimigos/perseguidor", "furioso", "O perseguidor aguenta DOIS pisões. Pise, afaste-se e pise de novo!"),
    ("inimigos/voador", "voando", "Voadores soltam projéteis quando você passa embaixo deles."),
    ("estrela", "brilho", "Bata nos blocos ? por baixo: moedas, vida extra e estrela de invencibilidade."),
    ("checkpoint", "levantada", "Toque nos checkpoints: o progresso é salvo e você volta de lá."),
    ("mastro_final", "tremulando", "Alcance o mastro, depois o castelo, e salve a princesa!"),
]


class ComoJogar(Cena):
    """Mostra controles e dicas de jogo."""

    def __init__(self, aplicacao):
        super().__init__(aplicacao)
        self.fundo = gradiente_vertical((40, 90, 170), (12, 16, 50))
        pastas = {"moeda": "objetos/moeda", "estrela": "objetos/estrela", "checkpoint": "objetos/checkpoint",
                  "mastro_final": "objetos/bandeira_final"}
        self.icones = []
        for nome, animacao, _ in DICAS:
            pasta = pastas.get(nome, nome)
            self.icones.append(Animador(aplicacao.recursos.folha(pasta), animacao))

    def voltar(self):
        self.app.audio.tocar_efeito("selecao")
        self.app.cenas.desempilhar("fade")

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE,
                                                             pygame.K_BACKSPACE):
            self.voltar()
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self.voltar()

    def atualizar(self, dt):
        for icone in self.icones:
            icone.atualizar(dt)

    def desenhar(self, tela):
        tela.blit(self.fundo, (0, 0))
        desenhar_texto(tela, "HOW TO PLAY", 72, CORES["destaque"], (LARGURA_BASE // 2, 60), contorno=True)
        painel = pygame.Surface((420, 440), pygame.SRCALPHA)
        pygame.draw.rect(painel, (8, 12, 40, 190), painel.get_rect(), border_radius=18)
        tela.blit(painel, (50, 130))
        desenhar_texto(tela, "CONTROLES", 36, CORES["destaque"], (260, 165))
        for i, acao in enumerate(ACOES_CONTROLE):
            y = 225 + i * 62
            desenhar_texto(tela, NOMES_ACOES[acao], 26, CORES["texto_suave"], (75, y), "esquerda", deslocamento=1)
            tecla = self.app.controles.nome_tecla(acao)
            desenhar_texto(tela, tecla, 28, CORES["texto"], (450, y), "direita", deslocamento=1)
        desenhar_texto(tela, "Segure o botão de pulo para pular mais alto.", 20, CORES["texto_suave"],
                       (260, 545), deslocamento=1)
        for i, (_, _, texto) in enumerate(DICAS):
            y = 150 + i * 64
            imagem = self.icones[i].imagem()
            escala = min(1.0, 52 / max(imagem.get_width(), imagem.get_height()))
            if escala < 1.0:
                imagem = pygame.transform.scale(imagem, (int(imagem.get_width() * escala),
                                                         int(imagem.get_height() * escala)))
            tela.blit(imagem, imagem.get_rect(center=(530, y + 20)))
            desenhar_texto(tela, texto, 24, CORES["texto"], (575, y + 20), "esquerda", deslocamento=1)
        desenhar_texto(tela, "Enter / ESC / clique para voltar", 26, CORES["texto_suave"],
                       (LARGURA_BASE // 2, ALTURA_BASE - 40))
