"""Final da campanha: o Salão do Inverno Eterno, o resgate da Princesa do Gelo e o epílogo.

Roteiro (tudo automático; ENTER/ESC pula):

1. ``entrada``    — fade in no salão do castelo;
2. ``andando``    — o Tux caminha até a princesa, presa em um bloco de gelo;
3. ``fala``       — o Tux anuncia que reuniu os três fragmentos;
4. ``chave``      — os fragmentos giram e formam a Chave Mágica, que voa até a prisão;
5. ``rachando``   — a prisão de gelo racha;
6. ``libertacao`` — a prisão se estilhaça e a princesa é libertada;
7. ``reencontro`` — o Tux vai até ela; abraço, corações e fogos;
8. ``epilogo``    — amanhecer sobre o Reino Glacial, legendas de encerramento e "FIM".
"""
import math

import pygame

from cenas.cena import Cena
from configuracoes import ALTURA_BASE, CORES, LARGURA_BASE, NOME_DO_JOGO, TAMANHO_BLOCO
from entidades.efeitos import CoracaoFlutuante, criar_explosao_gelo, criar_fogos
from entidades.objetos import ChaveMagica
from fases.fase import Fase
from interface.efeitos_de_tela import Confetes
from interface.textos import desenhar_texto
from sistemas.animacoes import Animador
from sistemas.cenario import Cenario
from sistemas.neve import SistemaDeNeve
from sistemas.pontuacao import SistemaDePontuacao

ENTRADA_VAZIA = {"esquerda": False, "direita": False, "pular": False, "correr": False}
COR_TUX = (120, 226, 255)
COR_PRINCESA = (255, 170, 210)
LEGENDAS_EPILOGO = [
    (1.5, 6.0, "O Inverno Eterno chegou ao fim."),
    (7.0, 12.5, "Os Fragmentos de Gelo se transformaram em luz,\ne o Reino Glacial voltou a brilhar."),
    (13.5, 19.0, "Tux e a Princesa do Gelo nunca mais se separaram."),
]
INICIO_DO_FIM = 20.0


class CenaFinal(Cena):
    """Cena cinematográfica exibida ao concluir a fase 3."""

    def __init__(self, aplicacao, numero_fase, resultado, novo_recorde=False):
        super().__init__(aplicacao)
        self.numero_fase = numero_fase
        self.resultado = resultado
        self.novo_recorde = novo_recorde
        r = aplicacao.recursos
        self.fase = Fase(r, aplicacao.audio, SistemaDePontuacao(999), "salao_final")
        self.jogador, self.princesa, self.prisao = self.fase.jogador, self.fase.princesa, self.fase.prisao
        self.estado = "entrada"
        self.t = 0.0                       # tempo dentro do estado
        self.tempo_total = 0.0
        self.fade = 1.0                    # 1 = tela preta
        self.legenda = None                # (quem, texto, cor)
        self.fragmentos = []
        self.chave = None
        self.centro_chave = (0.0, 0.0)
        self.proximo_efeito = 0.0
        self.folha_coracao = r.folha("objetos/coracao")
        self.tem_segredo = aplicacao.salvamento.segredo_descoberto
        # epílogo
        self.cenario = Cenario(r, self.fase.temas, "epilogo")
        self.neve = SistemaDeNeve(r, self.fase.temas["epilogo"].get("neve"), semente=21)
        self.tux = Animador(r.folha("personagens/tux"), "andando")
        self.princesa_epilogo = Animador(r.folha("personagens/princesa"), "feliz")
        self.tileset = r.folha(self.fase.dados.get("tileset", "blocos/tileset"))
        self.confetes = Confetes(70)
        self.camera_epilogo = 0.0
        self.t_epilogo = 0.0

    # ------------------------------------------------------------------ ciclo de vida
    def ao_entrar(self):
        self.app.audio.tocar_musica("castelo")

    # ------------------------------------------------------------------ controle de estados
    def _ir_para(self, estado):
        self.estado, self.t = estado, 0.0

    def tratar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key not in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE, pygame.K_SPACE):
            return
        if self.estado == "epilogo":
            if self.t_epilogo >= INICIO_DO_FIM:
                self._ir_para_vitoria()
            elif self.t_epilogo > 2.0:
                self.t_epilogo = INICIO_DO_FIM
        elif self.estado not in ("transicao",) and self.tempo_total > 2.0:
            self._ir_para("transicao")

    def _ir_para_vitoria(self):
        from cenas.tela_vitoria import TelaVitoria
        self.app.cenas.trocar(TelaVitoria(self.app, self.numero_fase, self.resultado, self.novo_recorde,
                                          campanha=True), "fade")

    # ------------------------------------------------------------------ atualização
    def atualizar(self, dt):
        self.tempo_total += dt
        self.t += dt
        if self.estado == "epilogo":
            self._atualizar_epilogo(dt)
            return
        entrada = ENTRADA_VAZIA
        if self.estado == "andando":
            entrada = self._entrada_andando(self.princesa.centro_x - 150)
        elif self.estado == "reencontro" and self.t < 3.0:
            entrada = self._entrada_andando(self.princesa.centro_x - 62)
        self.fase.atualizar(dt, entrada)
        metodo = getattr(self, f"_estado_{self.estado}", None)
        if metodo:
            metodo(dt)

    def _entrada_andando(self, alvo_x):
        distancia = alvo_x - self.jogador.centro_x
        return {"esquerda": distancia < -6, "direita": distancia > 6, "pular": False, "correr": False}

    # -------- 1. entrada
    def _estado_entrada(self, dt):
        self.fade = max(0.0, 1.0 - self.t / 1.6)
        if self.t > 2.2:
            self._ir_para("andando")

    # -------- 2. andando
    def _estado_andando(self, dt):
        if abs(self.princesa.centro_x - 150 - self.jogador.centro_x) <= 8 or self.t > 14.0:
            self.jogador.vx = 0.0
            self.jogador.espelhado = False
            self._ir_para("fala")
            self.legenda = ("TUX", "Princesa! Eu reuni os três Fragmentos de Gelo!", COR_TUX)

    # -------- 3. fala
    def _estado_fala(self, dt):
        if self.t > 3.2:
            self.legenda = ("TUX", "Com a Chave Mágica, eu vou libertar você!", COR_TUX)
            self.fase.audio.tocar_efeito("chave")
            self.centro_chave = (self.jogador.centro_x + 40, self.jogador.y - 90)
            folha = self.fase.recursos.folha("objetos/fragmento_de_gelo")
            self.fragmentos = [[n * 2.094, 120.0, Animador(folha, f"fragmento_{n}")] for n in (1, 2, 3)]
            self._ir_para("chave")

    # -------- 4. chave
    def _estado_chave(self, dt):
        fase, t = self.fase, self.t
        orbita = min(1.0, t / 2.0)
        for item in self.fragmentos:
            item[0] += dt * (2.0 + 7.0 * orbita)
            item[1] = 120.0 * (1.0 - orbita * orbita)
            item[2].atualizar(dt)
        if self.chave is None and t >= 2.0:
            self.fragmentos = []
            self.chave = ChaveMagica(*self.centro_chave, fase.recursos)
            self.chave.escala = 0.5
            fase.flash = 1.0
            fase.camera.tremer(7.0, 0.5)
            fase.audio.tocar_efeito("chave")
            fase.efeitos.extend(criar_fogos(*self.centro_chave, quantidade=28))
        if self.chave is not None:
            self.chave.atualizar(dt)
            self.chave.escala = 0.5 + 1.0 * min(1.0, (t - 2.0) / 0.5)
            if t >= 3.4:                                   # voa até a prisão
                f = min(1.0, (t - 3.4) / 1.3)
                f = f * f * (3 - 2 * f)
                alvo = (self.princesa.centro_x, self.princesa.centro_y)
                origem = self.centro_chave
                self.chave.centro = (origem[0] + (alvo[0] - origem[0]) * f, origem[1] + (alvo[1] - origem[1]) * f)
                if int(t * 40) % 2 == 0:
                    fase.efeitos.extend(criar_explosao_gelo(*self.chave.centro, 2, [(255, 235, 160), (255, 255, 255)]))
                if t >= 4.7:
                    self.chave = None
                    self.prisao.rachar()
                    fase.flash = 0.8
                    fase.camera.tremer(5.0, 0.4)
                    fase.audio.tocar_efeito("congelar")
                    self._ir_para("rachando")

    # -------- 5. rachando
    def _estado_rachando(self, dt):
        fase = self.fase
        if self.t >= self.proximo_efeito:
            self.proximo_efeito = self.t + 0.14
            fase.efeitos.extend(criar_explosao_gelo(self.princesa.centro_x + (self.t * 90) % 40 - 20,
                                                    self.princesa.centro_y, 3))
        fase.camera.tremer(2.5, 0.1)
        if self.t >= 1.8:
            self.prisao.estilhacar()
            fase.flash = 1.0
            fase.camera.tremer(9.0, 0.6)
            fase.audio.tocar_efeito("prisao_quebra")
            fase.audio.tocar_musica("conclusao", repetir=False)
            fase.efeitos.extend(criar_explosao_gelo(self.princesa.centro_x, self.princesa.centro_y, 46,
                                                    [(210, 246, 255), (255, 255, 255), (170, 150, 246), (255, 214, 96)]))
            fase.efeitos.extend(criar_fogos(self.princesa.centro_x, self.princesa.y - 40, (255, 214, 96), 30))
            self.princesa.tocar("livre")
            self.legenda = None
            self._ir_para("libertacao")

    # -------- 6. libertação
    def _estado_libertacao(self, dt):
        if self.t > 1.0 and self.legenda is None:
            self.princesa.tocar("feliz")
            self.legenda = ("PRINCESA", "Tux...! Eu sabia que você me encontraria.", COR_PRINCESA)
        if self.t > 4.2:
            self.legenda = None
            self._ir_para("reencontro")

    # -------- 7. reencontro
    def _estado_reencontro(self, dt):
        fase = self.fase
        if self.t < 3.0:
            if abs(self.princesa.centro_x - 62 - self.jogador.centro_x) <= 10:
                self.t = max(self.t, 3.0)
            return
        if self.legenda is None:
            self.jogador.vx = 0.0
            self.jogador.espelhado = False
            self.jogador.comemorar()
            self.princesa.tocar("abracando")
            fase.audio.tocar_efeito("vitoria")
            fase.flash = 0.5
            fase.efeitos.extend(criar_fogos(self.princesa.centro_x, self.princesa.y - 70, None, 34))
            if self.tem_segredo:
                self.legenda = ("PRINCESA", "Você se lembrou da nossa promessa...", COR_PRINCESA)
            else:
                self.legenda = ("TUX", "Eu jamais deixaria de procurar você.", COR_TUX)
        if self.t >= self.proximo_efeito:
            self.proximo_efeito = self.t + 0.5
            fase.efeitos.append(CoracaoFlutuante(self.folha_coracao, (self.jogador.centro_x + self.princesa.centro_x) / 2,
                                                 self.princesa.y - 20))
        if 6.2 < self.t < 6.3:
            self.legenda = ("TUX", "Eu prometi que encontraria você.", COR_TUX)
        if self.t > 9.5:
            self._ir_para("transicao")

    # -------- transição para o epílogo
    def _estado_transicao(self, dt):
        self.fade = min(1.0, self.t / 1.2)
        if self.fade >= 1.0:
            self.legenda = None
            self.estado, self.t = "epilogo", 0.0
            self.t_epilogo = 0.0
            self.app.salvamento.registrar_campanha_concluida()
            self.app.audio.tocar_musica("final")

    # -------- 8. epílogo
    def _atualizar_epilogo(self, dt):
        self.t_epilogo += dt
        self.fade = max(0.0, 1.0 - self.t_epilogo / 1.6)
        self.camera_epilogo += 26 * dt if self.t_epilogo < INICIO_DO_FIM else 8 * dt
        self.cenario.atualizar(dt)
        self.neve.atualizar(dt)
        self.tux.atualizar(dt)
        self.princesa_epilogo.atualizar(dt)
        self.confetes.atualizar(dt)
        parar = self.t_epilogo >= INICIO_DO_FIM - 0.5
        self.tux.tocar("parado" if parar else "andando")

    # ------------------------------------------------------------------ desenho
    def desenhar(self, tela):
        if self.estado == "epilogo":
            self._desenhar_epilogo(tela)
        else:
            self._desenhar_salao(tela)
        if self.fade > 0:
            veu = pygame.Surface((LARGURA_BASE, ALTURA_BASE))
            veu.set_alpha(int(255 * min(1.0, self.fade)))
            tela.blit(veu, (0, 0))

    def _desenhar_salao(self, tela):
        self.fase.desenhar(tela)
        camera = self.fase.camera
        if self.chave is not None:
            self.chave.desenhar(tela, camera)
        for angulo, raio, animador in self.fragmentos:
            imagem = animador.imagem()
            cx, cy = self.centro_chave
            sx, sy = camera.mundo_para_tela(cx + math.cos(angulo) * raio, cy + math.sin(angulo) * raio * 0.6)
            tela.blit(imagem, imagem.get_rect(center=(round(sx), round(sy))))
        self._desenhar_faixas(tela)
        if self.legenda is not None:
            self._desenhar_legenda(tela)
        if self.tempo_total > 2.0 and self.estado != "transicao" and int(self.tempo_total * 2) % 2 == 0:
            desenhar_texto(tela, "ENTER: pular", 20, CORES["texto_suave"], (LARGURA_BASE - 24, ALTURA_BASE - 20),
                           "direita")

    def _desenhar_faixas(self, tela):
        """Faixas pretas de cinema (cima e baixo) durante a cena."""
        altura = 56
        pygame.draw.rect(tela, (4, 6, 22), (0, 0, LARGURA_BASE, altura))
        pygame.draw.rect(tela, (4, 6, 22), (0, ALTURA_BASE - altura, LARGURA_BASE, altura))

    def _desenhar_legenda(self, tela):
        quem, texto, cor = self.legenda
        caixa = pygame.Surface((1040, 96), pygame.SRCALPHA)
        pygame.draw.rect(caixa, (10, 18, 56, 225), caixa.get_rect(), border_radius=16)
        pygame.draw.rect(caixa, cor + (255,), caixa.get_rect(), width=3, border_radius=16)
        tela.blit(caixa, ((LARGURA_BASE - 1040) // 2, ALTURA_BASE - 170))
        desenhar_texto(tela, quem, 24, cor, ((LARGURA_BASE - 1040) // 2 + 26, ALTURA_BASE - 150), "topo_esquerda")
        desenhar_texto(tela, texto, 32, CORES["texto"], (LARGURA_BASE // 2, ALTURA_BASE - 100))

    def _desenhar_epilogo(self, tela):
        self.cenario.desenhar(tela, self.camera_epilogo)
        brilho = pygame.Surface((LARGURA_BASE, ALTURA_BASE), pygame.SRCALPHA)
        brilho.fill((255, 200, 140, 38))                      # luz quente do amanhecer
        tela.blit(brilho, (0, 0))
        self._desenhar_chao(tela)
        base = ALTURA_BASE - 96
        tux = self.tux.imagem(False)
        princesa = self.princesa_epilogo.imagem(False)
        tela.blit(tux, (560 - tux.get_width() // 2, base - tux.get_height()))
        tela.blit(princesa, (650 - princesa.get_width() // 2, base - princesa.get_height()))
        self.neve.desenhar(tela)
        t = self.t_epilogo
        for inicio, fim, texto in LEGENDAS_EPILOGO:
            if inicio <= t <= fim:
                alfa = int(255 * max(0.0, min(1.0, (t - inicio) / 0.8, (fim - t) / 0.8)))
                for i, linha in enumerate(texto.split("\n")):
                    desenhar_texto(tela, linha, 38, CORES["branco"], (LARGURA_BASE // 2, 150 + i * 46),
                                   contorno=True, alfa=alfa)
        if t >= INICIO_DO_FIM:
            f = min(1.0, (t - INICIO_DO_FIM) / 1.5)
            self.confetes.desenhar(tela)
            desenhar_texto(tela, "FIM", int(120 * f) + 1, CORES["destaque"], (LARGURA_BASE // 2, 190), contorno=True)
            desenhar_texto(tela, NOME_DO_JOGO, 34, CORES["titulo"], (LARGURA_BASE // 2, 280), contorno=True,
                           alfa=int(255 * f))
            if t > INICIO_DO_FIM + 2.0 and int(self.tempo_total * 2) % 2 == 0:
                desenhar_texto(tela, "Pressione ENTER", 28, CORES["texto"], (LARGURA_BASE // 2, 360), contorno=True)
        elif t > 2.0:
            desenhar_texto(tela, "ENTER: pular", 20, CORES["texto_suave"], (LARGURA_BASE - 24, ALTURA_BASE - 20),
                           "direita")

    def _desenhar_chao(self, tela):
        neve, solo = self.tileset.obter("neve").quadros[0], self.tileset.obter("solo_congelado").quadros[0]
        deslocamento = -int(self.camera_epilogo % TAMANHO_BLOCO)
        y = ALTURA_BASE - 96
        for x in range(deslocamento, LARGURA_BASE + TAMANHO_BLOCO, TAMANHO_BLOCO):
            tela.blit(neve, (x, y))
            tela.blit(solo, (x, y + TAMANHO_BLOCO))
