"""Tela de conclusão da fase: pontuação final e estatísticas da partida."""
import math

import pygame

from cenas.cena import Cena
from configuracoes import CORES, LARGURA_BASE
from interface.botoes import MenuDeBotoes
from interface.efeitos_de_tela import Confetes, gradiente_vertical
from interface.hud import formatar_tempo
from interface.textos import desenhar_texto


class TelaVitoria(Cena):
    """Revela, linha por linha, o cálculo da pontuação final."""

    INTERVALO = 0.55

    def __init__(self, aplicacao, resultado, novo_recorde=False):
        super().__init__(aplicacao)
        self.resultado = resultado
        self.novo_recorde = novo_recorde
        self.fundo = gradiente_vertical((255, 170, 90), (70, 40, 120))
        self.confetes = Confetes()
        self.tempo = 0.0
        self.linhas = [
            ("Pontos coletados", str(resultado["pontos_coletados"])),
            ("Bônus de conclusão", f"+{resultado['bonus_conclusao']}"),
            (f"Bônus de tempo ({resultado['tempo_restante']}s)", f"+{resultado['bonus_tempo']}"),
            ("Moedas", str(resultado["moedas"])),
            ("Inimigos derrotados", str(resultado["inimigos"])),
            ("Tempo de jogo", formatar_tempo(resultado["tempo_gasto"])),
            ("Vidas perdidas", str(resultado["mortes"])),
        ]
        self.menu = MenuDeBotoes(aplicacao, [("PLAY AGAIN", self.jogar_de_novo), ("MAIN MENU", self.ir_ao_menu)],
                                 centro_x=640, y_inicial=610, espacamento=0, largura=300, altura=54)
        self.menu.botoes[0].base.center = (440, 640)
        self.menu.botoes[1].base.center = (840, 640)
        self.musica_checada = False

    def jogar_de_novo(self):
        from cenas.cena_jogo import CenaJogo
        self.app.cenas.trocar(CenaJogo(self.app), "fade")

    def ir_ao_menu(self):
        from cenas.menu_principal import MenuPrincipal
        self.app.cenas.trocar(MenuPrincipal(self.app), "fade")

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_LEFT, pygame.K_a):
            self.menu.selecionar(self.menu.selecionado - 1)
        elif evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RIGHT, pygame.K_d):
            self.menu.selecionar(self.menu.selecionado + 1)
        else:
            self.menu.tratar_evento(evento)

    def atualizar(self, dt):
        self.tempo += dt
        self.confetes.atualizar(dt)
        self.menu.atualizar(dt)
        if not self.musica_checada and self.tempo > 0.2:
            self.musica_checada = True
            if pygame.mixer.get_init() and not pygame.mixer.music.get_busy():
                self.app.audio.tocar_musica("menu")

    def desenhar(self, tela):
        tela.blit(self.fundo, (0, 0))
        self.confetes.desenhar(tela)
        escala = 1.0 + 0.04 * math.sin(self.tempo * 3)
        desenhar_texto(tela, "FASE CONCLUÍDA!", int(80 * escala), CORES["branco"], (LARGURA_BASE // 2, 70),
                       contorno=True)
        desenhar_texto(tela, "A princesa está a salvo!", 32, CORES["destaque"], (LARGURA_BASE // 2, 130))
        painel = pygame.Surface((640, 400), pygame.SRCALPHA)
        pygame.draw.rect(painel, (10, 12, 40, 200), painel.get_rect(), border_radius=20)
        pygame.draw.rect(painel, (255, 255, 255, 200), painel.get_rect(), width=3, border_radius=20)
        tela.blit(painel, painel.get_rect(center=(LARGURA_BASE // 2, 360)))
        for i, (rotulo, valor) in enumerate(self.linhas):
            if self.tempo < 0.5 + i * self.INTERVALO:
                break
            y = 190 + i * 38
            desenhar_texto(tela, rotulo, 28, CORES["texto_suave"], (340, y), "esquerda", deslocamento=1)
            desenhar_texto(tela, valor, 30, CORES["texto"], (940, y), "direita", deslocamento=1)
        revelar_total = 0.5 + len(self.linhas) * self.INTERVALO
        if self.tempo >= revelar_total:
            cresc = min(1.0, (self.tempo - revelar_total) * 3)
            pygame.draw.line(tela, CORES["branco"], (340, 468), (940, 468), 2)
            desenhar_texto(tela, "TOTAL", int(40 * cresc) + 1, CORES["destaque"], (340, 505), "esquerda")
            desenhar_texto(tela, str(self.resultado["total"]), int(52 * cresc) + 1, CORES["destaque"],
                           (940, 505), "direita")
            if self.novo_recorde:
                if int(self.tempo * 3) % 2 == 0:
                    desenhar_texto(tela, "NOVO RECORDE!", 34, CORES["sucesso"], (LARGURA_BASE // 2, 560))
            else:
                desenhar_texto(tela, f"Melhor: {self.app.salvamento.melhor_pontuacao}", 26,
                               CORES["texto_suave"], (LARGURA_BASE // 2, 560))
            self.menu.desenhar(tela)
