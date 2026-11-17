"""Menu inicial temático: castelo de gelo ao fundo, neve caindo, Tux em espera e botões."""
import math

import pygame

from cenas.cena import Cena
from configuracoes import ALTURA_BASE, CORES, LARGURA_BASE, TOTAL_DE_FASES
from fases.fase import ErroDeFase
from interface.botoes import MenuDeBotoes
from interface.textos import desenhar_texto
from sistemas.animacoes import Animador
from sistemas.neve import SistemaDeNeve

CHAO_DO_MENU = 650          # y onde Tux apoia os pés
CENTRO_COLUNA = 330         # x central do logo e dos botões


class MenuPrincipal(Cena):
    """JOGAR, CONTINUAR, SELECIONAR FASE, CONFIGURAÇÕES, COMO JOGAR, CRÉDITOS e SAIR."""

    def __init__(self, aplicacao):
        super().__init__(aplicacao)
        r = aplicacao.recursos
        self.ceu = r.fundo("cenarios/geleira/ceu.png")          # o fundo do menu é uma camada translúcida
        self.fundo = r.fundo("cenarios/menu/menu_castelo.png")
        self.neve = SistemaDeNeve(r, {"densidade": 110, "vento": -45}, semente=11)
        self.tempo = 0.0
        self.mensagem = ""
        self.tempo_mensagem = 0.0
        itens = [("JOGAR", self.jogar), ("CONTINUAR", self.continuar),
                 ("SELECIONAR FASE", self.selecionar_fase), ("CONFIGURAÇÕES", self.configuracoes),
                 ("COMO JOGAR", self.como_jogar), ("CRÉDITOS", self.creditos), ("SAIR", self.app.encerrar)]
        self.menu = MenuDeBotoes(aplicacao, itens, centro_x=CENTRO_COLUNA, y_inicial=272, espacamento=56,
                                 largura=380, altura=46)
        # personagens e objetos decorativos animados
        self.tux = Animador(r.folha("personagens/tux"), "parado")
        self.fragmento = Animador(r.folha("objetos/fragmento_de_gelo"), "fragmento_1")
        self.cristais = [(Animador(r.folha("objetos/cristal"), "girando"), x, y)
                         for x, y in ((560, 560), (845, 600), (1010, 585))]
        self.pinheiros = [(Animador(r.folha("cenarios/decoracoes/pinheiro_nevado")), x)
                          for x in (470, 1130)]
        logo = r.imagem("interface/logo.png", 1)
        largura = 470
        self.logo = pygame.transform.smoothscale(logo, (largura, int(logo.get_height() * largura / logo.get_width())))

    # ---------------------------------------------------------------- ações
    def ao_entrar(self):
        self.app.audio.tocar_musica("menu")

    def _avisar(self, texto):
        self.mensagem, self.tempo_mensagem = texto, 3.0
        self.app.audio.tocar_efeito("mensagem_erro")

    def _iniciar(self, numero_fase, continuar=False):
        """Cria a cena da fase e faz a transição em íris a partir do botão selecionado."""
        from cenas.cena_jogo import CenaJogo
        try:
            cena = CenaJogo(self.app, numero_fase, continuar=continuar)
        except ErroDeFase as erro:
            self._avisar(f"Erro ao carregar a fase: {erro}")
            return
        self.app.cenas.trocar(cena, "iris", self.menu.botoes[self.menu.selecionado].base.center)

    def jogar(self):
        """Começa pela Fase 1 (o progresso da campanha já salvo é mantido)."""
        self._iniciar(1)

    def continuar(self):
        """Retoma o último checkpoint ou, sem ele, a próxima fase ainda não concluída."""
        salvamento = self.app.salvamento
        if salvamento.tem_progresso():
            self._iniciar(salvamento.obter_progresso()["fase"], continuar=True)
            return
        if salvamento.fase_concluida(1):                     # há campanha em andamento
            for numero in range(1, TOTAL_DE_FASES + 1):
                if salvamento.fase_desbloqueada(numero) and not salvamento.fase_concluida(numero):
                    self._iniciar(numero)
                    return
        self._avisar("Nenhum jogo salvo. Alcance um checkpoint ou conclua uma fase!")

    def selecionar_fase(self):
        from cenas.selecao_de_fases import SelecaoDeFases
        self.app.cenas.empilhar(SelecaoDeFases(self.app), "fade")

    def configuracoes(self):
        from cenas.configuracoes_menu import ConfiguracoesMenu
        self.app.cenas.empilhar(ConfiguracoesMenu(self.app), "fade")

    def como_jogar(self):
        from cenas.como_jogar import ComoJogar
        self.app.cenas.empilhar(ComoJogar(self.app), "fade")

    def creditos(self):
        from cenas.creditos import Creditos
        self.app.cenas.empilhar(Creditos(self.app), "fade")

    # ---------------------------------------------------------------- ciclo
    def tratar_evento(self, evento):
        self.menu.tratar_evento(evento)

    def atualizar(self, dt):
        self.tempo += dt
        self.tempo_mensagem = max(0.0, self.tempo_mensagem - dt)
        self.neve.atualizar(dt)
        self.menu.atualizar(dt)
        self.tux.atualizar(dt)
        self.fragmento.atualizar(dt)
        for animador, _, _ in self.cristais:
            animador.atualizar(dt)
        for animador, _ in self.pinheiros:
            animador.atualizar(dt)

    def desenhar(self, tela):
        tela.blit(self.ceu, (0, 0))
        tela.blit(self.fundo, (0, 0))
        self._desenhar_brilho_das_janelas(tela)
        self._desenhar_decoracao(tela)
        self.neve.desenhar(tela)
        self._desenhar_titulo(tela)
        self.menu.desenhar(tela)
        melhor = self.app.salvamento.melhor_pontuacao
        desenhar_texto(tela, f"Melhor pontuação: {melhor}", 26, CORES["texto"], (LARGURA_BASE - 20, 24),
                       "direita", contorno=True)
        if self.tempo_mensagem > 0:
            alfa = int(255 * min(1.0, self.tempo_mensagem))
            desenhar_texto(tela, self.mensagem, 30, CORES["erro"], (LARGURA_BASE // 2, 690), contorno=True,
                           alfa=alfa)
        desenhar_texto(tela, "Setas / mouse: navegar    Enter / clique: escolher", 22, CORES["botao_borda"],
                       (LARGURA_BASE - 20, ALTURA_BASE - 14), "direita", deslocamento=0)

    def _desenhar_brilho_das_janelas(self, tela):
        """Halo pulsante sobre a porta do castelo (efeito discreto sobre o fundo estático)."""
        pulso = 0.5 + 0.5 * math.sin(self.tempo * 2.2)
        halo = pygame.Surface((160, 160), pygame.SRCALPHA)
        pygame.draw.circle(halo, (255, 214, 120, int(30 + 40 * pulso)), (80, 80), 70)
        tela.blit(halo, (930 - 80, 480 - 80))

    def _desenhar_decoracao(self, tela):
        for animador, x in self.pinheiros:
            imagem = animador.imagem()
            tela.blit(imagem, (x, CHAO_DO_MENU + 10 - imagem.get_height()))
        for i, (animador, x, y) in enumerate(self.cristais):
            imagem = animador.imagem()
            tela.blit(imagem, (x, y + math.sin(self.tempo * 2 + i) * 5))
        tux = self.tux.imagem()
        x_tux = 720
        tela.blit(tux, (x_tux - tux.get_width() // 2, CHAO_DO_MENU - tux.get_height()))
        # o fragmento flutua sobre Tux com um brilho pulsante
        flutuar = math.sin(self.tempo * 2.5) * 8
        fragmento = self.fragmento.imagem()
        cx, cy = x_tux + 8, CHAO_DO_MENU - tux.get_height() - 60 + flutuar
        brilho = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(brilho, (140, 230, 255, int(50 + 30 * math.sin(self.tempo * 3))), (60, 60), 52)
        tela.blit(brilho, (cx - 60, cy - 60))
        tela.blit(fragmento, (cx - fragmento.get_width() // 2, cy - fragmento.get_height() // 2))

    def _desenhar_titulo(self, tela):
        y = 18 + math.sin(self.tempo * 2) * 5
        tela.blit(self.logo, (CENTRO_COLUNA - self.logo.get_width() // 2, y))
        base = y + self.logo.get_height() + 10
        desenhar_texto(tela, "A ERA DOS", 34, CORES["botao_borda"], (CENTRO_COLUNA, base), deslocamento=0)
        desenhar_texto(tela, "FRAGMENTOS DE GELO", 38, CORES["botao"], (CENTRO_COLUNA, base + 36), deslocamento=0)
