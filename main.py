import pygame
from menu import Menu
from player import Player


pygame.init()

clock = pygame.time.Clock()
FPS = 60

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

# Spawn do Tux
tux = Player(
    100,
    300
)

rodando = True

while rodando:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

    teclas = pygame.key.get_pressed()

    tux.mover_player(teclas)
    tux.pular(teclas)

    tela.fill((0, 0, 0))

    #Desenha o personagem
    tux.desenhar(tela)

    pygame.display.update()

    clock.tick(FPS)

pygame.quit()