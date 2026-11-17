"""Câmara da Lembrança — o Easter Egg do jogo.

Como chegar (NÃO é anunciado em nenhum menu): na fase 2, uma parede rachada escondida na rocha
suspensa do caminho alto. Ela quebra com 3 golpes de ataque e revela um portal secreto.
Dentro da câmara o Tux encontra um orbe dourado: a lembrança de quando a Princesa do Gelo
ensinou um pinguinzinho a deslizar no lago congelado.

Recompensa (só na primeira vez): +2000 pontos e um rastro de faíscas douradas permanente
quando o Tux corre. Nada aqui é necessário para concluir a campanha.
"""
import pygame

from cenas.cena import Cena
from configuracoes import ALTURA_BASE, CORES, LARGURA_BASE, PONTOS_SEGREDO
from entidades.efeitos import CoracaoFlutuante, Fagulha, criar_explosao_gelo, criar_fogos
from fases.fase import Fase
from interface.efeitos_de_tela import escurecer, gradiente_vertical
from interface.textos import desenhar_texto
from sistemas.animacoes import Animador
from sistemas.neve import SistemaDeNeve

PAINEL = pygame.Rect(190, 100, 900, 440)
CHAO_LAGO = 330                      # y do lago, em coordenadas do painel
LEGENDAS = [
    (0.0, "Há muito tempo, antes do Inverno Eterno..."),
    (3.8, "...uma pequena princesa ensinou um pinguinzinho\na deslizar sobre o lago congelado."),
    (8.6, "\"Prometa que vai me encontrar,\nnão importa onde eu esteja.\""),
    (13.2, "Tux prometeu."),
]
DURACAO_LEMBRANCA = 17.0


class _CameraFixa:
    """Câmera 'nula' para reutilizar efeitos (corações, faíscas) em coordenadas do painel."""

    @staticmethod
    def mundo_para_tela(x, y):
        return x, y


class CamaraSecreta(Cena):
    """Pequena sala jogável; tocar o orbe dourado exibe a lembrança. O portal leva de volta à fase."""

    def __init__(self, aplicacao, cena_jogo):
        super().__init__(aplicacao)
        self.cena_jogo = cena_jogo
        r = aplicacao.recursos
        self.primeira_vez = not aplicacao.salvamento.segredo_descoberto
        self.fase = Fase(r, aplicacao.audio, cena_jogo.pontuacao, "camara_secreta",
                         segredo_descoberto=aplicacao.salvamento.segredo_descoberto)
        self.estado = "explorar"                 # explorar | lembranca | fim
        self.tempo = 0.0
        self.tempo_lembranca = 0.0
        self.proximo_coracao = 0.0
        self.efeitos_painel = []
        self.camera_fixa = _CameraFixa()
        self.mensagem_final = ""
        self._recompensa_dada = False
        self.fundo_lembranca = self._criar_fundo()
        self.neve_lembranca = SistemaDeNeve(r, {"densidade": 80, "vento": -25}, semente=11)
        self.tux_filhote = Animador(r.folha("personagens/tux_filhote"), "andando")
        self.princesa = Animador(r.folha("personagens/princesa"), "feliz")
        self.folha_coracao = r.folha("objetos/coracao")

    # ------------------------------------------------------------------ ciclo de vida
    def ao_entrar(self):
        if self.fase.portal is not None:
            self.fase.portal.abrir()                  # a saída fica aberta desde o início
        musica = self.fase.musica_atual_do_tema()
        if musica:
            self.app.audio.tocar_musica(musica)

    def ao_sair(self):
        self.cena_jogo.retornar_da_camara()

    def _criar_fundo(self):
        fundo = gradiente_vertical((255, 196, 160), (255, 238, 206), PAINEL.width, CHAO_LAGO)
        painel = pygame.Surface(PAINEL.size)
        painel.blit(fundo, (0, 0))
        pygame.draw.rect(painel, (170, 224, 248), (0, CHAO_LAGO, PAINEL.width, PAINEL.height - CHAO_LAGO))
        pygame.draw.rect(painel, (214, 244, 255), (0, CHAO_LAGO, PAINEL.width, 6))
        for i in range(14):                                # reflexos no gelo
            x = 40 + i * 62
            pygame.draw.line(painel, (232, 250, 255), (x, CHAO_LAGO + 40 + (i % 3) * 22),
                             (x + 28, CHAO_LAGO + 40 + (i % 3) * 22), 2)
        # montanhas distantes
        for x, h in ((60, 120), (240, 170), (430, 110), (620, 190), (800, 130)):
            pygame.draw.polygon(painel, (190, 206, 240), [(x - 130, CHAO_LAGO), (x, CHAO_LAGO - h), (x + 130, CHAO_LAGO)])
            pygame.draw.polygon(painel, (250, 252, 255), [(x - 30, CHAO_LAGO - h * 0.78), (x, CHAO_LAGO - h),
                                                          (x + 30, CHAO_LAGO - h * 0.78)])
        return painel

    # ------------------------------------------------------------------ entrada
    def _entrada(self):
        c = self.app.controles
        return {"esquerda": c.pressionada("esquerda"), "direita": c.pressionada("direita"),
                "pular": c.pressionada("pular"), "correr": c.pressionada("correr")}

    def tratar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if self.estado == "lembranca":
            if self.tempo_lembranca > 1.5:                # qualquer tecla pula a lembrança
                self._terminar_lembranca()
            return
        acao = self.app.controles.acao_do_evento(evento)
        if self.estado == "fim" and evento.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
            self.estado = "explorar"
            self.fase.jogador.congelado = False
            return
        if acao == "pular":
            self.fase.pedir_pulo()
        elif acao == "atacar":
            self.fase.pedir_ataque()
        elif acao == "dash":
            self.fase.pedir_dash()
        elif acao == "pausar" or evento.key == pygame.K_ESCAPE:
            self._sair()

    # ------------------------------------------------------------------ lógica
    def atualizar(self, dt):
        self.tempo += dt
        if self.estado == "lembranca":
            self._atualizar_lembranca(dt)
            self.fase.atualizar(dt, {"esquerda": False, "direita": False, "pular": False, "correr": False})
            return
        entrada = self._entrada() if self.estado == "explorar" else {"esquerda": False, "direita": False,
                                                                     "pular": False, "correr": False}
        self.fase.atualizar(dt, entrada)
        if self.fase.jogador.y > self.fase.mapa.altura_pixels:       # segurança: nunca fica preso/caindo
            self.fase.jogador.reaparecer(*self.fase.ponto_inicial)
        if self.estado == "explorar":
            self._verificar_orbe()
            self._verificar_saida()

    def _verificar_orbe(self):
        orbe, jogador = self.fase.lembranca, self.fase.jogador
        if orbe is not None and jogador.rect.colliderect(orbe.rect.inflate(30, 30)):
            self.estado = "lembranca"
            self.tempo_lembranca = 0.0
            jogador.congelado = True
            jogador.vx = 0.0
            self.fase.flash = 0.8
            self.fase.audio.tocar_efeito("segredo")
            self.fase.efeitos.extend(criar_fogos(orbe.centro_x, orbe.centro_y, (255, 214, 96), 30))
            self.fase.lembranca = None
            self.app.audio.parar_musica()
            self.app.audio.tocar_musica("final", repetir=False)

    def _verificar_saida(self):
        portal, jogador = self.fase.portal, self.fase.jogador
        if (portal is not None and portal.animador.nome_atual == "aberto"
                and jogador.rect.colliderect(portal.rect.inflate(-50, -10)) and self.tempo > 1.0):
            self._sair()

    def _sair(self):
        if self.estado != "lembranca" and not self.app.cenas.em_transicao:
            self.app.cenas.desempilhar("fade")

    # ------------------------------------------------------------------ lembrança
    def _posicoes(self, t):
        """Posições (x do Tux filhote, x da princesa) no painel em função do tempo."""
        if t < 4.0:
            f = t / 4.0
            return 80 + 290 * f, 820 - 330 * f
        if t < 9.0:
            return 370.0, 490.0
        desliza = min(t - 9.0, 5.0) * 52
        return 370.0 + desliza, 490.0 + desliza

    def _atualizar_lembranca(self, dt):
        self.tempo_lembranca += dt
        t = self.tempo_lembranca
        self.neve_lembranca.atualizar(dt)
        self.tux_filhote.atualizar(dt)
        self.princesa.atualizar(dt)
        parado = 4.0 <= t < 9.0
        self.tux_filhote.tocar("parado" if parado else "andando")
        if t >= 9.5 and t >= self.proximo_coracao:
            self.proximo_coracao = t + 0.55
            x_tux, x_princesa = self._posicoes(t)
            self.efeitos_painel.append(CoracaoFlutuante(self.folha_coracao, (x_tux + x_princesa) / 2 + 30,
                                                        CHAO_LAGO - 90))
        for efeito in self.efeitos_painel:
            efeito.atualizar(dt)
        self.efeitos_painel = [e for e in self.efeitos_painel if e.ativo]
        if t >= DURACAO_LEMBRANCA:
            self._terminar_lembranca()

    def _terminar_lembranca(self):
        self.estado = "fim"
        self._dar_recompensa()
        self.app.audio.tocar_musica(self.fase.musica_atual_do_tema() or "cavernas")

    def _dar_recompensa(self):
        if self._recompensa_dada:
            return
        self._recompensa_dada = True
        if self.primeira_vez:
            pontuacao = self.cena_jogo.pontuacao
            pontuacao.adicionar_pontos(PONTOS_SEGREDO)
            pontuacao.segredo_encontrado = True
            self.app.salvamento.registrar_segredo()
            self.cena_jogo.fase.segredo_descoberto = True
            self.cena_jogo.fase.jogador.rastro_dourado = True
            self.fase.jogador.rastro_dourado = True
            self.mensagem_final = f"LEMBRANÇA RECUPERADA!  +{PONTOS_SEGREDO}"
        else:
            self.mensagem_final = "Uma lembrança que o Tux jamais esquecerá."

    # ------------------------------------------------------------------ desenho
    def desenhar(self, tela):
        self.fase.desenhar(tela)
        if self.estado in ("lembranca", "fim"):
            self._desenhar_lembranca(tela)

    def _desenhar_lembranca(self, tela):
        t = min(self.tempo_lembranca, DURACAO_LEMBRANCA)
        aparecer = min(1.0, self.tempo_lembranca / 1.2)
        escurecer(tela, int(215 * aparecer))
        if self.estado == "fim":
            desenhar_texto(tela, self.mensagem_final, 44, CORES["destaque"], (LARGURA_BASE // 2, 250), contorno=True)
            if self.primeira_vez:
                desenhar_texto(tela, "Faíscas douradas passam a seguir os passos do Tux.", 28, CORES["texto"],
                               (LARGURA_BASE // 2, 320))
            if int(self.tempo * 2) % 2 == 0:
                desenhar_texto(tela, "Pressione ENTER", 26, CORES["texto_suave"], (LARGURA_BASE // 2, 470))
            return
        painel = self.fundo_lembranca.copy()
        self.neve_lembranca.desenhar(painel)
        x_tux, x_princesa = self._posicoes(t)
        base = CHAO_LAGO + 56
        filhote = pygame.transform.scale(self.tux_filhote.imagem(False), (84, 84))
        painel.blit(filhote, (x_tux - 42, base - 84))
        princesa_img = self.princesa.imagem(t < 4.0)          # vem da direita olhando para a esquerda
        princesa_img = pygame.transform.scale(princesa_img, (round(princesa_img.get_width() * 1.15),
                                                             round(princesa_img.get_height() * 1.15)))
        painel.blit(princesa_img, (x_princesa - princesa_img.get_width() // 2, base - princesa_img.get_height()))
        for efeito in self.efeitos_painel:
            efeito.desenhar(painel, self.camera_fixa)
        legenda = ""
        for inicio, texto in LEGENDAS:
            if t >= inicio:
                legenda = texto
        for i, linha in enumerate(legenda.split("\n")):
            desenhar_texto(painel, linha, 30, (40, 36, 90), (PAINEL.width // 2, 402 + i * 30 - 12), contorno=False,
                           sombra=(255, 255, 255), deslocamento=1)
        painel.set_alpha(int(255 * aparecer))
        tela.blit(painel, PAINEL.topleft)
        pygame.draw.rect(tela, (255, 214, 96), PAINEL, width=4, border_radius=2)
        pygame.draw.rect(tela, (255, 244, 200), PAINEL.inflate(10, 10), width=2)
        if self.tempo_lembranca > 1.5:
            desenhar_texto(tela, "qualquer tecla para continuar", 20, CORES["texto_suave"],
                           (LARGURA_BASE // 2, ALTURA_BASE - 26))
