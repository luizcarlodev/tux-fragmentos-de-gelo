import pygame
import sys


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

        self.tela.fill((20, 40, 90))

        titulo = self.fonte_titulo.render(
            "Tux: Fragmentos de Gelo",
            True,
            (255, 255, 255)
        )

        self.tela.blit(titulo, (160, 120))

        for i, opcao in enumerate(self.opcoes):

            cor = (255, 255, 255)

            if i == self.selecionado:
                cor = (0, 255, 255)

            texto = self.fonte_menu.render(
                opcao,
                True,
                cor
            )

            self.tela.blit(
                texto,
                (340, 250 + i * 60)
            )

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