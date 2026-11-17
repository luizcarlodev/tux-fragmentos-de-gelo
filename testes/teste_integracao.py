"""Teste de integração sem janela (SDL 'dummy') de "Tux: A Era dos Fragmentos de Gelo".

Percorre menu, seleção de fases, as três fases, fragmentos, desbloqueios, pausa, checkpoint,
segredo (Easter Egg), game over, final da campanha e a robustez do salvamento.

Execute a partir da pasta do projeto:   python testes/teste_integracao.py
Usa uma pasta temporária para os dados: o seu salvamento real nunca é alterado.
"""
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pygame  # noqa: E402

from cenas.camara_secreta import CamaraSecreta  # noqa: E402
from cenas.cena_final import CenaFinal  # noqa: E402
from cenas.cena_jogo import CenaJogo  # noqa: E402
from cenas.menu_pausa import MenuPausa  # noqa: E402
from cenas.menu_principal import MenuPrincipal  # noqa: E402
from cenas.selecao_de_fases import SelecaoDeFases  # noqa: E402
from cenas.tela_game_over import TelaGameOver  # noqa: E402
from cenas.tela_vitoria import TelaVitoria  # noqa: E402
from principal import Aplicacao  # noqa: E402
from sistemas.salvamento import Salvamento  # noqa: E402

# Hash (MD5) da grade da Fase 1 ORIGINAL (a geometria jamais pode mudar).
HASH_GRADE_FASE_1 = "8a8bb2ecb9e632a1d1053c7d3bd9e0fc"
SEM_ENTRADA = {"esquerda": False, "direita": False, "pular": False, "correr": False}
falhas = 0


def verificar(condicao, mensagem):
    """Imprime OK/FALHA e conta as falhas."""
    global falhas
    print(("  OK    " if condicao else "  FALHA ") + mensagem)
    if not condicao:
        falhas += 1


def rodar(app, quadros, parar_quando=None):
    """Executa até ``quadros`` ciclos (dt = 1/60 s); ``parar_quando`` encerra antes se retornar verdadeiro."""
    for _ in range(quadros):
        app.cenas.atualizar(1 / 60)
        app.cenas.desenhar(app.superficie)
        if parar_quando and parar_quando():
            return True
    return False


def tecla(app, chave):
    """Simula o pressionar de uma tecla."""
    app.cenas.tratar_evento(pygame.event.Event(pygame.KEYDOWN, key=chave, mod=0, unicode="", scancode=0))


def cena(app):
    return app.cenas.cena_atual


def entrada(cena_jogo, **teclas):
    """Substitui a leitura do teclado por uma entrada fixa."""
    dados = dict(SEM_ENTRADA, **teclas)
    cena_jogo._entrada = lambda: dict(dados)


def iniciar_fase(app, numero):
    """Abre a fase pelo caminho real (seleção de fases) e devolve a CenaJogo."""
    rodar(app, 300, lambda: not app.cenas.em_transicao)      # espera transições em andamento terminarem
    app.cenas.trocar(MenuPrincipal(app), transicao=None)
    rodar(app, 5)
    cena(app).selecionar_fase()
    rodar(app, 40)
    selecao = cena(app)
    selecao.selecionada = numero - 1
    selecao.jogar_fase(numero - 1)
    rodar(app, 120)
    return cena(app)


def teleportar_para_altar(cena_jogo, recuo=150):
    """Coloca o Tux no chão diante do altar do fragmento (a fase 3 tem o altar numa torre alta)."""
    fase = cena_jogo.fase
    altar = fase.altar
    fase.jogador.reaparecer(altar.centro_x - recuo, altar.base, invulneravel=5.0)
    fase.camera.centralizar_em(altar.centro_x - recuo, altar.base - 100)


def completar_fase(app, cena_jogo, esperada):
    """Anda até o altar pulando degraus, deixa a sequência do fragmento rodar e confere a cena seguinte."""
    # na fase 3 o altar fica no topo de uma torre: o Tux começa já sobre a plataforma do altar
    teleportar_para_altar(cena_jogo, recuo=40 if cena_jogo.numero_fase == 3 else 150)
    fase = cena_jogo.fase
    for quadro in range(60 * 45):
        entrada(cena_jogo, direita=True, pular=(quadro // 20) % 2 == 0)
        if quadro % 40 == 0 and fase.final is None:
            fase.pedir_pulo()
        rodar(app, 1)
        if isinstance(cena(app), esperada):
            return True
    return False


def principal():
    pasta = Path(tempfile.mkdtemp(prefix="tux_teste_"))
    app = Aplicacao()
    app.salvamento = Salvamento(pasta / "salvamento.json")
    app.cenas.trocar(MenuPrincipal(app), transicao=None)
    rodar(app, 30)

    # ------------------------------------------------------------------ menu e telas
    print("Menu principal e telas secundárias")
    menu = cena(app)
    verificar(isinstance(menu, MenuPrincipal), "menu principal abre")
    rotulos = [b.texto for b in menu.menu.botoes] if hasattr(menu.menu.botoes[0], "texto") else []
    for esperado in ("JOGAR", "CONTINUAR", "SELECIONAR FASE", "CONFIGURAÇÕES", "COMO JOGAR", "CRÉDITOS", "SAIR"):
        verificar(esperado in rotulos, f"botão '{esperado}' existe")
    for nome in ("configuracoes", "como_jogar", "creditos", "selecionar_fase"):
        getattr(menu, nome)()
        rodar(app, 40)
        verificar(cena(app) is not menu, f"'{nome}' abre outra cena")
        tecla(app, pygame.K_ESCAPE)
        rodar(app, 40)
        verificar(cena(app) is menu, f"'{nome}' volta ao menu com ESC")
    menu.continuar()
    rodar(app, 10)
    verificar(cena(app) is menu and menu.mensagem, "CONTINUAR sem jogo salvo mostra aviso e permanece no menu")

    # ------------------------------------------------------------------ seleção de fases
    print("Seleção de fases e bloqueios")
    menu.selecionar_fase()
    rodar(app, 40)
    selecao = cena(app)
    verificar(isinstance(selecao, SelecaoDeFases), "tela de seleção de fases abre")
    for numero in (2, 3):
        selecao.jogar_fase(numero - 1)
        rodar(app, 20)
        verificar(cena(app) is selecao, f"fase {numero} bloqueada não abre")
    verificar(not app.salvamento.fase_desbloqueada(2) and not app.salvamento.fase_desbloqueada(3),
              "salvamento: só a fase 1 liberada no início")

    # ------------------------------------------------------------------ fase 1
    print("Fase 1 — A Geleira Perdida")
    cena_jogo = iniciar_fase(app, 1)
    verificar(isinstance(cena_jogo, CenaJogo), "fase 1 inicia pela seleção")
    fase = cena_jogo.fase
    grade = json.load(open(RAIZ / "fases/mapas/fase_01.json", encoding="utf-8"))["grade"]
    verificar(hashlib.md5("".join(grade).encode()).hexdigest() == HASH_GRADE_FASE_1,
              "geometria da fase 1 idêntica à original (hash da grade)")
    verificar(8 <= fase.mapa.largura_pixels / 1280 <= 12, f"largura: {fase.mapa.largura_pixels / 1280:.1f} telas")
    tipos = {type(e).__name__ for e in fase.inimigos}
    verificar(len(tipos) >= 3, f"{len(fase.inimigos)} inimigos de {len(tipos)} tipos: {sorted(tipos)}")
    verificar(len(fase.moedas) == 100, f"{len(fase.moedas)} cristais")
    verificar(len(fase.checkpoints) >= 1, f"{len(fase.checkpoints)} totem(ns) de checkpoint")
    verificar(fase.altar is not None and fase.portal is not None, "altar do fragmento e portal existem")

    # robô: corre e pula, usa ataque e dash
    x0 = fase.jogador.x
    dados = {"direita": True, "correr": True}
    entrada(cena_jogo, **dados)
    for i in range(600):
        entrada(cena_jogo, direita=True, correr=True, pular=(i // 25) % 2 == 0)
        if i % 25 == 0:
            fase.pedir_pulo()
        if i % 90 == 10:
            fase.pedir_ataque()
        if i % 140 == 30:
            fase.pedir_dash()
        rodar(app, 1)
    verificar(fase.jogador.x > x0 + 100 or not fase.jogador.vivo, "Tux se movimenta (andar, pular, atacar, dash)")

    # pausa
    tecla(app, pygame.K_ESCAPE)
    rodar(app, 20)
    pausa = cena(app)
    verificar(isinstance(pausa, MenuPausa), "ESC abre o menu de pausa")
    tempo, px = cena_jogo.pontuacao.tempo_restante, fase.jogador.x
    rodar(app, 60)
    verificar(cena_jogo.pontuacao.tempo_restante == tempo and fase.jogador.x == px, "pausa congela tempo e física")
    tecla(app, pygame.K_ESCAPE)
    rodar(app, 30)
    verificar(cena(app) is cena_jogo, "ESC retoma a partida")

    # checkpoint e CONTINUAR
    print("Checkpoint e CONTINUAR")
    entrada(cena_jogo)
    totem = fase.checkpoints[0]
    fase.jogador.reaparecer(totem.centro_x, totem.base, invulneravel=3.0)
    rodar(app, 30)
    verificar(fase.checkpoint_atual == 0 and app.salvamento.tem_progresso(), "totem ativado e progresso salvo")
    app.cenas.trocar(MenuPrincipal(app), transicao=None)
    rodar(app, 5)
    cena(app).continuar()
    rodar(app, 120)
    retomada = cena(app)
    verificar(isinstance(retomada, CenaJogo) and retomada.fase.checkpoint_atual == 0,
              "CONTINUAR retoma a partir do checkpoint")

    # fim da fase 1
    print("Conclusão da fase 1")
    verificar(completar_fase(app, retomada, TelaVitoria), "alcançar o fragmento → portal → tela de vitória")
    verificar(app.salvamento.fase_concluida(1) and 1 in app.salvamento.fragmentos_coletados,
              "fase 1 concluída e fragmento 1 registrado")
    verificar(app.salvamento.fase_desbloqueada(2) and not app.salvamento.fase_desbloqueada(3),
              "concluir a fase 1 libera só a fase 2")
    rodar(app, 300)

    # ------------------------------------------------------------------ fase 2 e segredo
    print("Fase 2 — As Cavernas Congeladas")
    cena_jogo = iniciar_fase(app, 2)
    fase = cena_jogo.fase
    verificar(cena_jogo.numero_fase == 2 and fase.altar.numero == 2, "fase 2 carrega com o fragmento 2")
    tipos = {type(e).__name__ for e in fase.inimigos}
    verificar(len(tipos) >= 4, f"fase 2: {len(fase.inimigos)} inimigos de {len(tipos)} tipos (inclui golem)")

    print("Easter Egg (Câmara da Lembrança)")
    verificar(not app.salvamento.segredo_descoberto, "segredo ainda não descoberto")
    blocos = [b for linha in fase.mapa.grade for b in linha if b is not None and b.revela == "porta_secreta"]
    verificar(len(blocos) >= 1 and fase.porta_secreta is not None, "parede rachada e porta secreta existem")
    verificar(not fase.porta_secreta.aberto, "a porta secreta não está visível/aberta no início")
    alvo = blocos[-1]                                   # o Tux fica ao lado da parede, de frente para ela
    fase.jogador.reaparecer((alvo.coluna - 1) * 48 + 24, (alvo.linha + 1) * 48, invulneravel=9.0)
    entrada(cena_jogo)
    rodar(app, 30)
    fase.jogador.espelhado = False
    ataques = 0
    while not fase.porta_secreta.aberto and ataques < 6:
        fase.pedir_ataque()
        ataques += 1
        rodar(app, 40)
    verificar(fase.porta_secreta.aberto and ataques == 3, f"3 ataques derrubam a parede rachada e revelam a porta (usou {ataques})")
    porta = fase.porta_secreta
    fase.jogador.reaparecer(porta.centro_x, porta.base, invulneravel=3.0)
    entrada(cena_jogo)
    camara = None
    rodar(app, 120, lambda: isinstance(cena(app), CamaraSecreta))
    camara = cena(app)
    verificar(isinstance(camara, CamaraSecreta), "tocar a porta abre a câmara secreta")
    if isinstance(camara, CamaraSecreta):
        rodar(app, 90)
        orbe = camara.fase.lembranca
        camara.fase.jogador.reaparecer(orbe.centro_x, orbe.base + 4, invulneravel=2.0)
        rodar(app, 5, lambda: camara.estado == "lembranca")
        verificar(camara.estado == "lembranca", "tocar o orbe inicia a lembrança")
        tecla(app, pygame.K_SPACE) if camara.tempo_lembranca > 1.5 else None
        rodar(app, 60 * 20, lambda: camara.estado == "fim")
        verificar(camara.estado == "fim" and app.salvamento.segredo_descoberto, "recompensa dada e segredo salvo")
        verificar(cena_jogo.pontuacao.segredo_encontrado, "pontos do segredo contabilizados")
        tecla(app, pygame.K_RETURN)
        tecla(app, pygame.K_ESCAPE)
        rodar(app, 120, lambda: cena(app) is cena_jogo)
        verificar(cena(app) is cena_jogo, "câmara devolve o Tux à fase 2")
        verificar(cena_jogo.fase.jogador.rastro_dourado, "recompensa: rastro dourado ativo")
    entrada(cena_jogo)
    cena_jogo.fase.evento_segredo = False

    print("Conclusão da fase 2")
    verificar(completar_fase(app, cena_jogo, TelaVitoria), "fase 2 termina na tela de vitória")
    verificar(app.salvamento.fase_concluida(2) and app.salvamento.fase_desbloqueada(3), "fase 3 liberada")
    verificar(app.salvamento.fragmentos_coletados == [1, 2], "fragmentos registrados: 1 e 2")

    # ------------------------------------------------------------------ morte e game over
    print("Dano, morte e Game Over (fase 3)")
    cena_jogo = iniciar_fase(app, 3)
    fase = cena_jogo.fase
    tipos = {type(e).__name__ for e in fase.inimigos}
    verificar(cena_jogo.numero_fase == 3 and fase.altar.numero == 3, "fase 3 carrega com o fragmento 3")
    jogador = fase.jogador
    jogador.tempo_invulneravel = 0.0
    vidas_antes = cena_jogo.pontuacao.vidas
    antes = len(fase.efeitos)
    verificar(fase._machucar(jogador.centro_x - 20), "tocar num inimigo/perigo causa dano")
    verificar(cena_jogo.pontuacao.vidas == vidas_antes - 1 and jogador.tempo_invulneravel > 0,
              "dano: perde 1 vida e ganha invulnerabilidade temporária")
    verificar(any(type(e).__name__ == "EfeitoAnimado" for e in fase.efeitos[antes:]), "efeito de congelamento exibido")
    rodar(app, 90)
    cena_jogo.pontuacao.vidas = vidas_antes
    vidas = cena_jogo.pontuacao.vidas
    fase.perder_vida_fatal()
    rodar(app, 240, lambda: cena_jogo.pontuacao.vidas < vidas and not fase.jogador_morto)
    verificar(cena_jogo.pontuacao.vidas == vidas - 1 and not fase.jogador_morto, "perder uma vida renasce no início/checkpoint")
    cena_jogo.pontuacao.vidas = 1
    fase.perder_vida_fatal()
    verificar(rodar(app, 600, lambda: isinstance(cena(app), TelaGameOver)), "sem vidas → GAME OVER")

    # ------------------------------------------------------------------ final da campanha
    print("Final da campanha")
    cena_jogo = iniciar_fase(app, 3)
    verificar(completar_fase(app, cena_jogo, CenaFinal), "fase 3 → chave mágica → cena do castelo")
    final = cena(app)
    verificar(app.salvamento.tem_todos_os_fragmentos, "os três fragmentos foram registrados")
    if isinstance(final, CenaFinal):
        estados = set()
        for _ in range(60 * 120):
            rodar(app, 1)
            estados.add(final.estado)
            if isinstance(cena(app), TelaVitoria):
                break
            if final.estado == "epilogo":
                tecla(app, pygame.K_RETURN)
        verificar({"chave", "libertacao", "reencontro"} <= estados,
                  f"sequência: chave → prisão de gelo se desfaz → reencontro ({sorted(estados)})")
        verificar(isinstance(cena(app), TelaVitoria), "epílogo termina na tela de conclusão da campanha")
    verificar(app.salvamento.campanha_concluida, "campanha marcada como concluída")
    rodar(app, 200)

    # ------------------------------------------------------------------ salvamento
    print("Salvamento: persistência, migração e arquivos corrompidos")
    app.salvamento.salvar()
    recarregado = Salvamento(pasta / "salvamento.json")
    verificar(recarregado.fragmentos_coletados == [1, 2, 3] and recarregado.fase_concluida(3)
              and recarregado.segredo_descoberto and recarregado.melhor_pontuacao > 0,
              "tudo persiste: fases, fragmentos, segredo e recorde")
    antigo = pasta / "antigo.json"
    antigo.write_text(json.dumps({"versao": 1, "melhor_pontuacao": 1234, "progresso": None}), encoding="utf-8")
    migrado = Salvamento(antigo)
    verificar(migrado.melhor_pontuacao == 1234 and migrado.fase_desbloqueada(1),
              "salvamento da versão antiga é aproveitado (recorde mantido)")
    ruim = pasta / "ruim.json"
    for conteudo in ("{lixo", "[1, 2]", json.dumps({"fases_concluidas": "x", "fragmentos": [99, -1, "a"],
                                                    "melhor_pontuacao": -5})):
        ruim.write_text(conteudo, encoding="utf-8")
        s = Salvamento(ruim)
        verificar(s.fase_desbloqueada(1) and s.melhor_pontuacao >= 0 and s.fragmentos_coletados == [],
                  f"conteúdo inválido não impede o jogo ({conteudo[:18]!r})")

    app.encerrar_sem_sair() if hasattr(app, "encerrar_sem_sair") else None
    pygame.quit()
    print(f"\nFALHAS: {falhas}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(principal())
