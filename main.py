import map
import config
import utils
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

camera_x = 0

projeteis = []
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

    camera_x = tux.x - config.LARGURA_TELA // 2
    camera_x = utils.limitar(camera_x, 0, config.LARGURA_MUNDO - config.LARGURA_TELA)

    novo_projetil = tux.atacar(teclas)
    if novo_projetil:
        projeteis.append(novo_projetil)

    for projetil in projeteis[:]:
        projetil.atualizar()
        if projetil.fora_da_tela():
            projeteis.remove(projetil)

    tela.fill(config.COR_FUNDO)

    for plataforma in plataformas:
        plataforma.desenhar(tela, camera_x)

    for projetil in projeteis:
        projetil.desenhar(tela, camera_x)

    #Desenha o personagem
    tux.desenhar(tela, camera_x)

    pygame.display.update()

    clock.tick(config.FPS)

pygame.quit()