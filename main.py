import pygame

import config
import audio
from menu import Menu
from game import Jogo


def main():
    audio.preparar()
    pygame.init()
    audio.inicializar()

    tela = pygame.display.set_mode((config.LARGURA_TELA, config.ALTURA_TELA))
    pygame.display.set_caption(config.TITULO_JANELA)

    menu = Menu(tela)
    mostrar_menu = True
    jogo = None

    while True:
        if mostrar_menu:
            audio.mudar_musica("normal")
            audio.continuar_musica()
            menu.executar()
            jogo = None

        if jogo is None:
            jogo = Jogo(tela)

        resultado = jogo.executar()

        if resultado == "sair":
            break

        if resultado == "menu_pausa":
            mostrar_menu = True
            continue

        # aqui o resultado é 'vitoria' ou 'derrota'
        escolha = jogo.ui.tela_fim_de_jogo(vitoria=(resultado == "vitoria"))
        mostrar_menu = (escolha == "menu")
        jogo = None   # 'reiniciar' cria um Jogo novo sem passar pelo menu

    pygame.quit()


if __name__ == "__main__":
    main()
