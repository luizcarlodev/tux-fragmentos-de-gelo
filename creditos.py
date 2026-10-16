import pygame
import audio


class TelaCreditos:

    def __init__(self, tela):
        self.tela = tela

        self.fonte_titulo = pygame.font.SysFont(
            "Arial", 48, bold=True
        )

        self.fonte_creditos = pygame.font.SysFont(
            "Arial", 32
        )

        self.fonte_instrucao = pygame.font.SysFont(
            "Arial", 22
        )

    def desenhar(self):
        largura = self.tela.get_width()
        altura = self.tela.get_height()

        self.tela.fill((20, 40, 90))

        titulo = self.fonte_titulo.render(
            "Créditos", True, (255, 255, 255)
        )

        creditos = self.fonte_creditos.render(
            "Desenvolvido por Júlio e Luiz",
            True, (0, 255, 255)
        )

        instrucao = self.fonte_instrucao.render(
            "Pressione ESC ou ENTER para voltar",
            True, (220, 220, 220)
        )

        self.tela.blit(
            titulo,
            titulo.get_rect(
                center=(largura // 2, altura // 3)
            )
        )

        self.tela.blit(
            creditos,
            creditos.get_rect(
                center=(largura // 2, altura // 2)
            )
        )

        self.tela.blit(
            instrucao,
            instrucao.get_rect(
                center=(largura // 2, altura * 3 // 4)
            )
        )

    def executar(self):
        while True:
            for evento in pygame.event.get():

                if audio.tratar_tecla(evento):
                    continue

                if evento.type == pygame.QUIT:
                    return

                if evento.type == pygame.KEYDOWN:
                    if evento.key in (
                        pygame.K_ESCAPE,
                        pygame.K_RETURN
                    ):
                        return

            self.desenhar()
            pygame.display.flip()