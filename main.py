import map
import config
import pygame
from menu import Menu
from player import Player


pygame.init()

clock = pygame.time.Clock()

#constantes removidas -> config.py

tela = pygame.display.set_mode((config.LARGURA_TELA, config.ALTURA_TELA))

pygame.display.set_caption("Tux: Fragmentos de Gelo")

menu = Menu(tela)
menu.executar()

# Spawn do Tux
tux = Player(100, 300)

plataformas = map.criar_plataformas_fase1()

rodando = True

while rodando:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

    teclas = pygame.key.get_pressed()

    tux.mover_player(teclas)
    tux.pular(teclas, plataformas)
    tux.dash(teclas)
    tux.atacar(teclas)

    tela.fill((0, 0, 0))

    for plataforma in plataformas:
        plataforma.desenhar(tela)

    #Desenha o personagem
    tux.desenhar(tela)

    pygame.display.update()

    clock.tick(config.FPS)

pygame.quit()