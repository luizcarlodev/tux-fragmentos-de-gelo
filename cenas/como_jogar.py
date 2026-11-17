"""Tela COMO JOGAR: controles atuais, objetivo e dicas (lê as teclas configuradas)."""
import pygame

from cenas.cena import Cena
from configuracoes import ACOES_CONTROLE, ALTURA_BASE, CORES, LARGURA_BASE, NOMES_ACOES
from interface.efeitos_de_tela import gradiente_vertical
from interface.textos import desenhar_texto
from sistemas.animacoes import Animador

DICAS = [
    ("objetos/cristal", "girando", "Colete cristais: 10 pontos cada (100 cristais = vida extra)."),
    ("inimigos/criatura_de_neve", "andando", "Pise nas criaturas ou ataque para derrotá-las (100 pontos)."),
    ("inimigos/pinguim_selvagem", "furioso", "O Pinguim Selvagem persegue você e aguenta dois golpes."),
    ("inimigos/morcego_glacial", "voando", "Morcegos Glaciais soltam estilhaços quando você passa embaixo."),
    ("inimigos/golem_de_gelo", "andando", "O Golem de Gelo é lento e resistente: exige três golpes."),
    ("personagens/tux", "atacando", "O ataque quebra blocos de gelo; o dash atropela criaturas e cruza vãos."),
    ("objetos/cristal_magico", "brilho", "Blocos de cristal escondem cristais, corações de gelo e poderes."),
    ("objetos/totem", "levantada", "Acenda os totens: o progresso é salvo (CONTINUAR volta de lá)."),
    ("objetos/fragmento_de_gelo", "fragmento_1", "Alcance o Fragmento de Gelo ao fim de cada região e salve a Princesa!"),
]


class ComoJogar(Cena):
    """Mostra controles e dicas de jogo."""

    def __init__(self, aplicacao):
        super().__init__(aplicacao)
        self.fundo = gradiente_vertical((24, 52, 130), (8, 12, 44))
        self.icones = [Animador(aplicacao.recursos.folha(pasta), animacao) for pasta, animacao, _ in DICAS]

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
        desenhar_texto(tela, "COMO JOGAR", 72, CORES["destaque"], (LARGURA_BASE // 2, 60), contorno=True)
        painel = pygame.Surface((420, 540), pygame.SRCALPHA)
        pygame.draw.rect(painel, (8, 12, 40, 190), painel.get_rect(), border_radius=18)
        tela.blit(painel, (50, 130))
        desenhar_texto(tela, "CONTROLES", 36, CORES["destaque"], (260, 165))
        for i, acao in enumerate(ACOES_CONTROLE):
            y = 212 + i * 54
            desenhar_texto(tela, NOMES_ACOES[acao], 26, CORES["texto_suave"], (75, y), "esquerda", deslocamento=1)
            tecla = self.app.controles.nome_tecla(acao)
            desenhar_texto(tela, tecla, 28, CORES["texto"], (450, y), "direita", deslocamento=1)
        desenhar_texto(tela, "Segure o pulo para saltar mais alto.", 20, CORES["texto_suave"],
                       (260, 622), deslocamento=1)
        for i, (_, _, texto) in enumerate(DICAS):
            y = 132 + i * 56
            imagem = self.icones[i].imagem()
            escala = min(1.0, 52 / max(imagem.get_width(), imagem.get_height()))
            if escala < 1.0:
                imagem = pygame.transform.scale(imagem, (int(imagem.get_width() * escala),
                                                         int(imagem.get_height() * escala)))
            tela.blit(imagem, imagem.get_rect(center=(530, y + 20)))
            desenhar_texto(tela, texto, 23, CORES["texto"], (575, y + 20), "esquerda", deslocamento=1)
        desenhar_texto(tela, "Enter / ESC / clique para voltar", 26, CORES["texto_suave"],
                       (LARGURA_BASE // 2, ALTURA_BASE - 40))
