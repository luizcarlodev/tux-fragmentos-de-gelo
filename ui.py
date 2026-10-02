import os
import pygame
import config
import sprites

_PASTA_UI = "assets/ui"
_ALTURA_ICONE = 24

_BARRA_LARGURA = 400
_BARRA_ALTURA = 18
_MOLDURA_MARGEM = 20


class UI:
    """Tudo que é desenhado por cima do jogo: HUD, fade do void, pausa e fim de jogo."""

    def __init__(self, tela):
        self.tela = tela
        self.fonte_hud = pygame.font.SysFont("Arial", 24)
        self.fonte_titulo = pygame.font.SysFont("Arial", 48)
        self.fonte_menu = pygame.font.SysFont("Arial", 32)

        self._fade_surface = pygame.Surface((config.LARGURA_TELA, config.ALTURA_TELA))
        self._fade_surface.fill(config.COR_VOID_FADE)

        self._moldura = None
        self._moldura_carregada = False

    def desenhar_hud(self, tux, fragmentos_coletados, fragmentos_totais):
        cheia = sprites.carregar(f"{_PASTA_UI}/vida_cheia.png", _ALTURA_ICONE)
        vazia = sprites.carregar(f"{_PASTA_UI}/vida_vazia.png", _ALTURA_ICONE)

        for i in range(config.PLAYER_VIDA_INICIAL):
            icone = cheia if i < tux.vida else vazia
            x, y = 16 + i * 28, 16
            if icone is None:
                cor = (220, 30, 30) if i < tux.vida else (90, 90, 90)
                pygame.draw.rect(self.tela, cor, (x, y, 20, 20))
            else:
                self.tela.blit(icone, (x, y))

        fragmento = sprites.carregar(f"{_PASTA_UI}/fragmento.png", _ALTURA_ICONE)
        x_texto = 16
        if fragmento is not None:
            self.tela.blit(fragmento, (16, 46))
            x_texto = 16 + fragmento.get_width() + 6

        texto = f"{fragmentos_coletados}/{fragmentos_totais}"
        if fragmento is None:
            texto = f"Fragmentos: {texto}"
        self.tela.blit(self.fonte_hud.render(texto, True, (255, 255, 255)), (x_texto, 48))

    def desenhar_barra_vida_golem(self, golem):
        x = (config.LARGURA_TELA - _BARRA_LARGURA) / 2
        y = 18

        proporcao = max(0, golem.vida / golem.vida_maxima)

        pygame.draw.rect(self.tela, (50, 50, 60), (x, y, _BARRA_LARGURA, _BARRA_ALTURA))
        pygame.draw.rect(self.tela, (210, 45, 45), (x, y, _BARRA_LARGURA * proporcao, _BARRA_ALTURA))

        moldura = self._obter_moldura()
        if moldura is None:
            pygame.draw.rect(self.tela, (255, 255, 255), (x, y, _BARRA_LARGURA, _BARRA_ALTURA), 2)
        else:
            self.tela.blit(moldura, (x - _MOLDURA_MARGEM, y - _MOLDURA_MARGEM))

        texto = self.fonte_hud.render("Golem", True, (255, 255, 255))
        self.tela.blit(texto, texto.get_rect(center=(config.LARGURA_TELA / 2, y - 14)))

    def _obter_moldura(self):
        """Moldura esticada para a barra + margem (carregada uma vez)."""
        if self._moldura_carregada:
            return self._moldura

        self._moldura_carregada = True
        caminho = f"{_PASTA_UI}/moldura_barra.png"
        if os.path.isfile(caminho):
            bruta = pygame.image.load(caminho).convert_alpha()
            bruta = bruta.subsurface(bruta.get_bounding_rect())
            tamanho = (_BARRA_LARGURA + _MOLDURA_MARGEM * 2, _BARRA_ALTURA + _MOLDURA_MARGEM * 2)
            self._moldura = pygame.transform.smoothscale(bruta, tamanho)

        return self._moldura

    def desenhar_fade_void(self, timer_restante):
        """Tela escura logo após cair, clareando até o timer chegar a 0."""
        alpha = int(255 * timer_restante / config.VOID_FADE_ENTRADA_DURACAO)
        self._fade_surface.set_alpha(alpha)
        self.tela.blit(self._fade_surface, (0, 0))

    def menu_pausa(self, titulo="PAUSADO", texto_opcao_principal="Continuar"):
        """Menu sobre o último frame do jogo. Retorna 'continuar', 'menu' ou 'sair'."""
        opcoes = [texto_opcao_principal, "Menu Inicial", "Sair do Jogo"]
        valores = ["continuar", "menu", "sair"]
        selecionado = 0

        overlay = pygame.Surface((config.LARGURA_TELA, config.ALTURA_TELA))
        overlay.fill((10, 10, 20))
        overlay.set_alpha(90)

        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        return "continuar"

                    if evento.key in (pygame.K_UP, pygame.K_DOWN):
                        passo = 1 if evento.key == pygame.K_DOWN else -1
                        selecionado = (selecionado + passo) % len(opcoes)

                    if evento.key == pygame.K_RETURN:
                        return valores[selecionado]

            self.tela.blit(overlay, (0, 0))
            self._desenhar_opcoes(titulo, (255, 255, 255), opcoes, selecionado, 0.3, 0.5)
            pygame.display.update()

    def tela_fim_de_jogo(self, vitoria):
        """Retorna 'reiniciar' ou 'menu'."""
        opcoes = ["Tentar Novamente", "Menu Inicial"]
        selecionado = 0

        titulo = "Você Venceu!" if vitoria else "Game Over"
        cor_titulo = (120, 220, 255) if vitoria else (220, 60, 60)

        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_UP, pygame.K_DOWN):
                        selecionado = 1 - selecionado

                    if evento.key == pygame.K_RETURN:
                        return "reiniciar" if selecionado == 0 else "menu"

            self.tela.fill((20, 20, 30))
            self._desenhar_opcoes(titulo, cor_titulo, opcoes, selecionado, 0.35, 0.55)
            pygame.display.update()

    def _desenhar_opcoes(self, titulo, cor_titulo, opcoes, selecionado, y_titulo, y_opcoes):
        texto_titulo = self.fonte_titulo.render(titulo, True, cor_titulo)
        self.tela.blit(
            texto_titulo,
            texto_titulo.get_rect(center=(config.LARGURA_TELA / 2, config.ALTURA_TELA * y_titulo)),
        )

        for i, opcao in enumerate(opcoes):
            cor = (0, 255, 255) if i == selecionado else (255, 255, 255)
            texto_opcao = self.fonte_menu.render(opcao, True, cor)
            self.tela.blit(
                texto_opcao,
                texto_opcao.get_rect(center=(config.LARGURA_TELA / 2, config.ALTURA_TELA * y_opcoes + i * 50)),
            )
