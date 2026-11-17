"""Tela de GAME OVER (acabaram as vidas)."""
from cenas.cena import Cena
from configuracoes import CORES, LARGURA_BASE
from interface.botoes import MenuDeBotoes
from interface.efeitos_de_tela import gradiente_vertical
from interface.textos import desenhar_texto


class TelaGameOver(Cena):
    """Mostra a pontuação e permite reiniciar a fase ou voltar ao menu."""

    def __init__(self, aplicacao, pontos, novo_recorde=False):
        super().__init__(aplicacao)
        self.pontos = pontos
        self.novo_recorde = novo_recorde
        self.fundo = gradiente_vertical((60, 8, 16), (8, 4, 20))
        self.tempo = 0.0
        self.menu = MenuDeBotoes(aplicacao, [("RETRY", self.tentar_de_novo), ("MAIN MENU", self.ir_ao_menu)],
                                 y_inicial=470, espacamento=80)

    def tentar_de_novo(self):
        from cenas.cena_jogo import CenaJogo
        self.app.cenas.trocar(CenaJogo(self.app), "fade")

    def ir_ao_menu(self):
        from cenas.menu_principal import MenuPrincipal
        self.app.cenas.trocar(MenuPrincipal(self.app), "fade")

    def tratar_evento(self, evento):
        self.menu.tratar_evento(evento)

    def atualizar(self, dt):
        self.tempo += dt
        self.menu.atualizar(dt)

    def desenhar(self, tela):
        tela.blit(self.fundo, (0, 0))
        y = 150 + int(__import__("math").sin(self.tempo * 2) * 6)
        desenhar_texto(tela, "GAME OVER", 120, CORES["titulo"], (LARGURA_BASE // 2, y), contorno=True)
        desenhar_texto(tela, f"Pontuação: {self.pontos}", 42, CORES["texto"], (LARGURA_BASE // 2, 270))
        melhor = self.app.salvamento.melhor_pontuacao
        texto = "NOVO RECORDE!" if self.novo_recorde else f"Melhor pontuação: {melhor}"
        cor = CORES["destaque"] if self.novo_recorde else CORES["texto_suave"]
        desenhar_texto(tela, texto, 34, cor, (LARGURA_BASE // 2, 330))
        desenhar_texto(tela, "Suas vidas acabaram... mas toda aventura merece outra chance!", 26,
                       CORES["texto_suave"], (LARGURA_BASE // 2, 395))
        self.menu.desenhar(tela)
