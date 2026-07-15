import pygame
import sys
import config


class Menu:

    def __init__(self, tela):
        self.tela = tela

        self.fonte_titulo = pygame.font.SysFont(
            "Arial",
            50
        )

        self.fonte_menu = pygame.font.SysFont(
            "Arial",
            35
        )

        self.opcoes = [
            "Jogar",
            "Créditos",
            "Sair"
        ]

        self.selecionado = 0

    def desenhar(self):

        largura_tela = self.tela.get_width()
        altura_tela = self.tela.get_height()

        self.tela.fill((20, 40, 90))

        titulo = self.fonte_titulo.render(
            "Tux: Fragmentos de Gelo",
            True,
            (255, 255, 255)
        )

        rect_titulo = titulo.get_rect(center=(largura_tela / 2, altura_tela * 0.25))
        self.tela.blit(titulo, rect_titulo)

        for i, opcao in enumerate(self.opcoes):

            cor = (255, 255, 255)

            if i == self.selecionado:
                cor = (0, 255, 255)

            texto = self.fonte_menu.render(
                opcao,
                True,
                cor
            )

            rect_texto = texto.get_rect(center=(largura_tela / 2, altura_tela * 0.5 + i * 60))
            self.tela.blit(texto, rect_texto)

    def executar(self):

        while True:

            for evento in pygame.event.get():

                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if evento.type == pygame.KEYDOWN:

                    if evento.key == pygame.K_UP:
                        self.selecionado -= 1

                    if evento.key == pygame.K_DOWN:
                        self.selecionado += 1

                    self.selecionado %= len(
                        self.opcoes
                    )

                    if evento.key == pygame.K_RETURN:

                        opcao = self.opcoes[
                            self.selecionado
                        ]

                        if opcao == "Jogar":
                            return

                        elif opcao == "Créditos":
                            print(
                                "Projeto criado por Luiz"
                            )

                        elif opcao == "Sair":
                            pygame.quit()
                            sys.exit()

            self.desenhar()

            pygame.display.update()