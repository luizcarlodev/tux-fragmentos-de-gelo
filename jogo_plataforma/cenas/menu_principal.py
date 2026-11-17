"""Menu inicial: fundo animado com parallax, personagem em espera e botões."""
import math

from cenas.cena import Cena
from configuracoes import ALTURA_BASE, CORES, LARGURA_BASE, TAMANHO_BLOCO
from fases.fase import ErroDeFase
from interface.botoes import MenuDeBotoes
from interface.textos import desenhar_texto
from sistemas.animacoes import Animador
from sistemas.cenario import Cenario

TEMAS_DO_MENU = {"campo": {"musica": "menu", "camadas": [
    {"imagem": "cenarios/campo/ceu.png", "fator": 0.0},
    {"imagem": "cenarios/campo/nuvens.png", "fator": 0.1, "deriva": 22},
    {"imagem": "cenarios/campo/colinas_longe.png", "fator": 0.25},
    {"imagem": "cenarios/campo/colinas_perto.png", "fator": 0.5}]}}


class MenuPrincipal(Cena):
    """PLAY, CONTINUE, SETTINGS, HOW TO PLAY, CREDITS e EXIT."""

    def __init__(self, aplicacao):
        super().__init__(aplicacao)
        r = aplicacao.recursos
        self.cenario = Cenario(r, TEMAS_DO_MENU, "campo")
        self.tempo = 0.0
        self.camera_x = 0.0
        self.mensagem = ""
        self.tempo_mensagem = 0.0
        itens = [("PLAY", self.jogar), ("CONTINUE", self.continuar), ("SETTINGS", self.configuracoes),
                 ("HOW TO PLAY", self.como_jogar), ("CREDITS", self.creditos), ("EXIT", self.app.encerrar)]
        self.menu = MenuDeBotoes(aplicacao, itens, centro_x=330, y_inicial=290, espacamento=68, largura=380)
        self.heroi = Animador(r.folha("personagens/jogador"), "parado")
        self.princesa = Animador(r.folha("personagens/princesa"), "parada")
        self.moeda = Animador(r.folha("objetos/moeda"), "girando")
        self.bloco = r.folha("blocos/tileset")
        self.tileset_tempo = 0.0
        self.decoracoes = [(Animador(r.folha(f"cenarios/decoracoes/{nome}")), x)
                           for nome, x in (("arvore", 800), ("arbusto", 1010), ("arvore", 1130), ("arbusto", 650))]

    # ---------------------------------------------------------------- ações
    def ao_entrar(self):
        self.app.audio.tocar_musica("menu")

    def _iniciar(self, continuar):
        from cenas.cena_jogo import CenaJogo
        try:
            cena = CenaJogo(self.app, continuar=continuar)
        except ErroDeFase as erro:
            self._avisar(f"Erro ao carregar a fase: {erro}")
            return
        self.app.cenas.trocar(cena, "iris", self.menu.botoes[self.menu.selecionado].base.center)

    def jogar(self):
        self._iniciar(False)

    def continuar(self):
        if self.app.salvamento.tem_progresso():
            self._iniciar(True)
        else:
            self._avisar("Nenhum jogo salvo. Alcance um checkpoint para salvar!")

    def _avisar(self, texto):
        self.mensagem, self.tempo_mensagem = texto, 3.0
        self.app.audio.tocar_efeito("mensagem_erro")

    def configuracoes(self):
        from cenas.configuracoes_menu import ConfiguracoesMenu
        self.app.cenas.empilhar(ConfiguracoesMenu(self.app), "fade")

    def como_jogar(self):
        from cenas.como_jogar import ComoJogar
        self.app.cenas.empilhar(ComoJogar(self.app), "fade")

    def creditos(self):
        from cenas.creditos import Creditos
        self.app.cenas.empilhar(Creditos(self.app), "fade")

    # ---------------------------------------------------------------- ciclo
    def tratar_evento(self, evento):
        self.menu.tratar_evento(evento)

    def atualizar(self, dt):
        self.tempo += dt
        self.camera_x += 60 * dt
        self.tempo_mensagem = max(0.0, self.tempo_mensagem - dt)
        self.cenario.atualizar(dt)
        self.menu.atualizar(dt)
        for animador in (self.heroi, self.princesa, self.moeda):
            animador.atualizar(dt)
        for animador, _ in self.decoracoes:
            animador.atualizar(dt)

    def desenhar(self, tela):
        self.cenario.desenhar(tela, self.camera_x)
        self._desenhar_chao(tela)
        for animador, x in self.decoracoes:
            imagem = animador.imagem()
            tela.blit(imagem, (x, ALTURA_BASE - 96 - imagem.get_height()))
        self._desenhar_personagens(tela)
        self._desenhar_titulo(tela)
        self.menu.desenhar(tela)
        melhor = self.app.salvamento.melhor_pontuacao
        desenhar_texto(tela, f"Melhor pontuação: {melhor}", 26, CORES["texto"], (LARGURA_BASE - 20, 24),
                       "direita", contorno=True)
        if self.tempo_mensagem > 0:
            alfa = int(255 * min(1.0, self.tempo_mensagem))
            desenhar_texto(tela, self.mensagem, 30, CORES["erro"], (LARGURA_BASE // 2, 668), contorno=True,
                           alfa=alfa)
        desenhar_texto(tela, "Setas / mouse: navegar    Enter / clique: escolher", 22, CORES["texto"],
                       (LARGURA_BASE - 20, ALTURA_BASE - 20), "direita", deslocamento=1)

    def _desenhar_chao(self, tela):
        grama, terra = self.bloco.obter("grama").quadros[0], self.bloco.obter("terra").quadros[0]
        deslocamento = -int(self.camera_x % TAMANHO_BLOCO)
        y = ALTURA_BASE - 96
        for x in range(deslocamento, LARGURA_BASE + TAMANHO_BLOCO, TAMANHO_BLOCO):
            tela.blit(grama, (x, y))
            tela.blit(terra, (x, y + TAMANHO_BLOCO))

    def _desenhar_personagens(self, tela):
        base = ALTURA_BASE - 96
        heroi = self.heroi.imagem()
        tela.blit(heroi, (760 - heroi.get_width() // 2, base - heroi.get_height()))
        princesa = self.princesa.imagem(True)
        tela.blit(princesa, (900 - princesa.get_width() // 2, base - princesa.get_height()))
        # blocos "?" flutuando e moeda girando
        flutuar = math.sin(self.tempo * 2.5) * 6
        interrogacao = self.bloco.obter("interrogacao")
        indice = int(self.tempo / interrogacao.duracao_quadro) % len(interrogacao.quadros)
        for i in range(3):
            tela.blit(interrogacao.quadros[indice], (1030 + i * TAMANHO_BLOCO, base - 250 + flutuar))
        moeda = self.moeda.imagem()
        tela.blit(moeda, (1030 + TAMANHO_BLOCO - 0, base - 330 + flutuar * 1.5))

    def _desenhar_titulo(self, tela):
        y = 120 + math.sin(self.tempo * 2) * 8
        desenhar_texto(tela, "SUPER", 84, CORES["destaque"], (330, y - 32), contorno=True)
        desenhar_texto(tela, "AVENTURA", 110, CORES["titulo"], (330, y + 54), contorno=True)
