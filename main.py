import pygame
from menu import Menu


pygame.init()

LARGURA = 800
ALTURA = 600

tela = pygame.display.set_mode(
    (LARGURA, ALTURA)
)

pygame.display.set_caption(
    "Tux: Fragmentos de Gelo"
)

menu = Menu(tela)
menu.executar()


rodando = True

while rodando:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

    tela.fill((0, 0, 0))

    pygame.display.update()

pygame.quit()