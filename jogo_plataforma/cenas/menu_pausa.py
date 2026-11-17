"""Menu de pausa: aparece por cima da partida (que fica completamente parada)."""
import pygame

from cenas.cena import Cena
from configuracoes import CORES, LARGURA_BASE
from interface.botoes import MenuDeBotoes
from interface.efeitos_de_tela import escurecer
from interface.textos import desenhar_texto


class MenuPausa(Cena):
    """RESUME, RESTART LEVEL, SETTINGS, MAIN MENU e EXIT GAME."""

    transparente = True

    def __init__(self, aplicacao, cena_jogo):
        super().__init__(aplicacao)
        self.cena_jogo = cena_jogo
        itens = [("RESUME", self.continuar), ("RESTART LEVEL", self.reiniciar),
                 ("SETTINGS", self.abrir_configuracoes), ("MAIN MENU", self.ir_ao_menu),
                 ("EXIT GAME", self.app.encerrar)]
        self.menu = MenuDeBotoes(aplicacao, itens, y_inicial=250, espacamento=76)
        self.tempo = 0.0

    def ao_entrar(self):
        self.app.audio.tocar_efeito("selecao")

    # ---------------------------------------------------------------- ações
    def continuar(self):
        self.app.cenas.desempilhar()

    def reiniciar(self):
        from cenas.cena_jogo import CenaJogo
        self.app.cenas.trocar(CenaJogo(self.app), "fade")

    def abrir_configuracoes(self):
        from cenas.configuracoes_menu import ConfiguracoesMenu
        self.app.cenas.empilhar(ConfiguracoesMenu(self.app), "fade")

    def ir_ao_menu(self):
        from cenas.menu_principal import MenuPrincipal
        self.app.cenas.trocar(MenuPrincipal(self.app), "fade")

    # ---------------------------------------------------------------- ciclo
    def tratar_evento(self, evento):
        if self.app.controles.acao_do_evento(evento) == "pausar":
            self.continuar()
            return
        self.menu.tratar_evento(evento)

    def atualizar(self, dt):
        self.tempo += dt
        self.menu.atualizar(dt)

    def desenhar(self, tela):
        escurecer(tela, 160)
        desenhar_texto(tela, "PAUSED", 84, CORES["destaque"], (LARGURA_BASE // 2, 150), contorno=True)
        self.menu.desenhar(tela)
        pausar = self.app.controles.nome_tecla("pausar")
        desenhar_texto(tela, f"{pausar} para continuar", 24, CORES["texto_suave"], (LARGURA_BASE // 2, 660))
