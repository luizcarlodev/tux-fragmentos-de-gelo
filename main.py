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
projeteis_inimigos = []
plataformas = map.criar_plataformas_fase1()
chefe1 = map.criar_chefe1()
chefe2 = map.criar_chefe2()
barreira_atual = config.CHEFE1_BARREIRA

rodando = True

while rodando:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

    teclas = pygame.key.get_pressed()

    tux.mover_player(teclas)
    tux.pular(teclas, plataformas)
    tux.dash(teclas)

    if tux.x > barreira_atual:
        tux.x = barreira_atual
        tux.rect.x = tux.x

    camera_x = tux.x - config.LARGURA_TELA // 2
    camera_x = utils.limitar(camera_x, 0, config.LARGURA_MUNDO - config.LARGURA_TELA)

    novo_projetil = tux.atacar(teclas)
    if novo_projetil:
        projeteis.append(novo_projetil)

    tela.fill(config.COR_FUNDO)

    for plataforma in plataformas:
        plataforma.desenhar(tela, camera_x)

    #projeteis
    for projetil in projeteis[:]:
        projetil.atualizar()

        atingiu = False
        if chefe1.vida > 0 and utils.checar_colisao(projetil.rect, chefe1.rect):
            chefe1.receber_dano(config.PROJETIL_DANO)
            atingiu = True
        elif chefe2.vida > 0 and utils.checar_colisao(projetil.rect, chefe2.rect):
            chefe2.receber_dano(config.PROJETIL_DANO)
            atingiu = True

        if atingiu or projetil.fora_da_tela():
            projeteis.remove(projetil)

    #chefe1
    if chefe1.vida > 0:
        chefe1.comportamento(tux.x)

        novo_projetil_inimigo = chefe1.atacar(tux.x)
        if novo_projetil_inimigo:
            projeteis_inimigos.append(novo_projetil_inimigo)

        if utils.checar_colisao(tux.rect, chefe1.rect):
            tux.sofrer_dano(chefe1.x)
    #chefe2
    elif chefe2.vida > 0:
        barreira_atual = config.CHEFE2_BARREIRA

        chefe2.comportamento(tux.x)

        if utils.checar_colisao(tux.rect, chefe2.rect):
            tux.sofrer_dano(chefe2.x)
    else:
        barreira_atual = config.LIMITE_DIREITA

    for projetil in projeteis_inimigos[:]:
        projetil.atualizar()

        if utils.checar_colisao(projetil.rect, tux.rect):
            tux.sofrer_dano(projetil.x)
            projeteis_inimigos.remove(projetil)
        elif projetil.fora_da_tela():
            projeteis_inimigos.remove(projetil)

    if tux.invencivel_timer > 0:
        tux.invencivel_timer -= 1

    #Desenha o personagem
    tux.desenhar(tela, camera_x)

    for projetil in projeteis:
        projetil.desenhar(tela, camera_x)

    for projetil in projeteis_inimigos:
        projetil.desenhar(tela, camera_x)

    if chefe1.vida > 0:
        chefe1.desenhar(tela, camera_x)

    if chefe2.vida > 0:
        chefe2.desenhar(tela, camera_x)


    pygame.display.update()

    clock.tick(config.FPS)

pygame.quit()