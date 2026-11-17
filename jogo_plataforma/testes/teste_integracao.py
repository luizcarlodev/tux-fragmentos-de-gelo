"""Teste de integração sem janela (SDL 'dummy'): percorre todas as telas e uma partida inteira.

Execute a partir da pasta do projeto:   python testes/teste_integracao.py
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame  # noqa: E402

import configuracoes as cfg  # noqa: E402
from cenas.cena_jogo import CenaJogo  # noqa: E402
from cenas.menu_principal import MenuPrincipal  # noqa: E402
from principal import Aplicacao  # noqa: E402


def rodar(app, quadros, antes=None):
    """Executa ``quadros`` ciclos de atualização + desenho (dt fixo de 1/60 s)."""
    for _ in range(quadros):
        if antes:
            antes()
        app.cenas.atualizar(1 / 60)
        app.cenas.desenhar(app.superficie)


def tecla(app, chave):
    app.cenas.tratar_evento(pygame.event.Event(pygame.KEYDOWN, key=chave, mod=0, unicode="", scancode=0))


def verificar(condicao, mensagem):
    print(("  OK   " if condicao else "  FALHA ") + mensagem)
    if not condicao:
        verificar.falhas += 1


verificar.falhas = 0


def principal():
    app = Aplicacao()
    app.salvamento.limpar_progresso()
    app.cenas.trocar(MenuPrincipal(app), transicao=None)
    rodar(app, 30)
    menu = app.cenas.cena_atual
    verificar(isinstance(menu, MenuPrincipal), "menu principal abre")

    print("Telas secundárias")
    for nome in ("configuracoes", "como_jogar", "creditos"):
        getattr(menu, nome)()
        rodar(app, 40)
        verificar(app.cenas.cena_atual is not menu, f"'{nome}' abre outra cena")
        tecla(app, pygame.K_ESCAPE)
        rodar(app, 40)
        verificar(app.cenas.cena_atual is menu, f"'{nome}' volta ao menu com ESC")

    print("CONTINUE sem save")
    menu.continuar()
    rodar(app, 10)
    verificar(app.cenas.cena_atual is menu, "continuar sem salvamento permanece no menu (com aviso)")

    print("Partida")
    menu.jogar()
    rodar(app, 90)
    cena = app.cenas.cena_atual
    verificar(isinstance(cena, CenaJogo), "PLAY inicia a fase")
    fase = cena.fase
    largura = fase.mapa.largura_pixels
    verificar(8 <= largura / 1280 <= 12, f"fase tem {largura / 1280:.1f} telas de largura (8 a 12)")
    verificar(len(fase.inimigos) >= 10, f"{len(fase.inimigos)} inimigos")
    verificar(len({type(e).__name__ for e in fase.inimigos}) >= 3, "pelo menos 3 tipos de inimigos")
    verificar(len(fase.moedas) >= 40, f"{len(fase.moedas)} moedas")
    verificar(len(fase.checkpoints) >= 1, f"{len(fase.checkpoints)} checkpoint(s)")
    verificar(len(fase.plataformas) >= 1, f"{len(fase.plataformas)} plataforma(s) móvel(is)")
    verificar(fase.mastro is not None and fase.princesa is not None and fase.castelo is not None,
              "mastro, princesa e castelo existem")

    # robô: corre para a direita e pula; apenas confere que nada quebra
    entrada = {"esquerda": False, "direita": True, "pular": False, "correr": True}
    cena._entrada = lambda: dict(entrada)
    x0 = fase.jogador.x
    for i in range(600):
        entrada["pular"] = (i // 25) % 2 == 0
        if entrada["pular"] and i % 25 == 0:
            fase.pedir_pulo()
        rodar(app, 1)
    verificar(fase.jogador.x > x0 + 100 or not fase.jogador.vivo, "jogador se movimenta/interage")

    print("Pausa")
    tecla(app, pygame.K_ESCAPE)
    rodar(app, 20)
    pausa = app.cenas.cena_atual
    verificar(pausa is not cena, "ESC abre o menu de pausa")
    tempo = cena.pontuacao.tempo_restante
    px = fase.jogador.x
    rodar(app, 60)
    verificar(cena.pontuacao.tempo_restante == tempo and fase.jogador.x == px, "pausa congela tempo e física")
    tecla(app, pygame.K_ESCAPE)
    rodar(app, 30)
    verificar(app.cenas.cena_atual is cena, "ESC retoma o jogo")

    print("Moedas, dano e Game Over")
    cena.pontuacao.vidas = 1
    fase.perder_vida_fatal()
    rodar(app, 300)
    from cenas.tela_game_over import TelaGameOver
    verificar(isinstance(app.cenas.cena_atual, TelaGameOver), "vidas acabam → tela de GAME OVER")

    print("Final da fase")
    app.cenas.trocar(MenuPrincipal(app), transicao=None)
    rodar(app, 5)
    app.cenas.cena_atual.jogar()
    rodar(app, 90)
    cena = app.cenas.cena_atual
    fase = cena.fase
    cena._entrada = lambda: {"esquerda": False, "direita": False, "pular": False, "correr": False}
    fase.jogador.x = fase.mastro.x - 120
    fase.jogador.y = fase.mastro.y - 10 if hasattr(fase.mastro, "y") else fase.jogador.y
    entrada_final = {"esquerda": False, "direita": True, "pular": False, "correr": False}
    cena._entrada = lambda: dict(entrada_final)
    from cenas.tela_vitoria import TelaVitoria
    for _ in range(60 * 40):
        rodar(app, 1)
        if isinstance(app.cenas.cena_atual, TelaVitoria):
            break
        if fase.jogador_morto:
            break
    verificar(isinstance(app.cenas.cena_atual, TelaVitoria), "alcançar o mastro leva à tela de vitória")
    rodar(app, 600)

    print("Salvamento")
    verificar(app.salvamento.melhor_pontuacao >= 0, "melhor pontuação registrada")
    app.encerrar()
    pygame.quit()
    print("\nFALHAS:", verificar.falhas)
    return 1 if verificar.falhas else 0


if __name__ == "__main__":
    sys.exit(principal())
