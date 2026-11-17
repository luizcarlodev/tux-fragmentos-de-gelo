"""Seleção de fases: ilustração de cada região, nome, estado de desbloqueio, fragmento e conclusão."""
import math

import pygame

from cenas.cena import Cena
from configuracoes import ALTURA_BASE, CORES, LARGURA_BASE, TOTAL_DE_FASES
from fases.fase import ErroDeFase
from fases.gerenciador_de_fases import INFORMACOES
from interface.efeitos_de_tela import escurecer
from interface.textos import desenhar_texto, tamanho_para_caber
from sistemas.neve import SistemaDeNeve

LARGURA_CARTAO = 360
ALTURA_CARTAO = 470
ESPACO = 40
TOPO = 150


class SelecaoDeFases(Cena):
    """Três cartões lado a lado. Fases bloqueadas aparecem escurecidas com um cadeado."""

    def __init__(self, aplicacao):
        super().__init__(aplicacao)
        r = aplicacao.recursos
        self.ceu = r.fundo("cenarios/geleira/ceu.png")
        self.fundo = r.fundo("cenarios/menu/menu_castelo.png")
        self.neve = SistemaDeNeve(r, {"densidade": 70, "vento": -30}, semente=3)
        self.selecionada = 0
        self.tempo = 0.0
        self.mensagem = ""
        self.tempo_mensagem = 0.0
        self.imagens = {}
        for numero, info in INFORMACOES.items():
            imagem = r.imagem(info["imagem"], 1)
            imagem = pygame.transform.smoothscale(imagem, (LARGURA_CARTAO - 24, int((LARGURA_CARTAO - 24) * 9 / 16)))
            self.imagens[numero] = (imagem, pygame.transform.grayscale(imagem))
        self.icone_cadeado = r.imagem("interface/icone_cadeado.png", 5)
        self.icone_check = r.imagem("interface/icone_check.png", 3)
        self.icones_fragmento = [r.imagem(f"interface/icone_fragmento_{n}.png", 3) for n in range(1, TOTAL_DE_FASES + 1)]
        self.icone_vazio = r.imagem("interface/icone_fragmento_vazio.png", 3)
        self.retangulos = []
        inicio = (LARGURA_BASE - (TOTAL_DE_FASES * LARGURA_CARTAO + (TOTAL_DE_FASES - 1) * ESPACO)) // 2
        for i in range(TOTAL_DE_FASES):
            self.retangulos.append(pygame.Rect(inicio + i * (LARGURA_CARTAO + ESPACO), TOPO, LARGURA_CARTAO,
                                               ALTURA_CARTAO))
        # abre já selecionando a primeira fase ainda não concluída (ou a última liberada)
        salvamento = aplicacao.salvamento
        for numero in range(1, TOTAL_DE_FASES + 1):
            if salvamento.fase_desbloqueada(numero) and not salvamento.fase_concluida(numero):
                self.selecionada = numero - 1
                break

    # ---------------------------------------------------------------- ações
    def ao_entrar(self):
        if pygame.mixer.get_init() and not pygame.mixer.music.get_busy():
            self.app.audio.tocar_musica("menu")

    def _avisar(self, texto):
        self.mensagem, self.tempo_mensagem = texto, 2.6
        self.app.audio.tocar_efeito("mensagem_erro")

    def mover(self, delta):
        antiga = self.selecionada
        self.selecionada = (self.selecionada + delta) % TOTAL_DE_FASES
        if self.selecionada != antiga:
            self.app.audio.tocar_efeito("selecao")

    def jogar_fase(self, indice):
        numero = indice + 1
        if not self.app.salvamento.fase_desbloqueada(numero):
            self._avisar("Conclua a fase anterior para liberar esta região.")
            return
        from cenas.cena_jogo import CenaJogo
        self.app.audio.tocar_efeito("confirmacao")
        try:
            cena = CenaJogo(self.app, numero)
        except ErroDeFase as erro:
            self._avisar(f"Erro ao carregar a fase: {erro}")
            return
        self.app.cenas.trocar(cena, "iris", self.retangulos[indice].center)

    def voltar(self):
        if len(self.app.cenas.pilha) > 1:
            self.app.cenas.desempilhar("fade")
        else:
            from cenas.menu_principal import MenuPrincipal
            self.app.cenas.trocar(MenuPrincipal(self.app), "fade")

    # ---------------------------------------------------------------- ciclo
    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_LEFT, pygame.K_a):
                self.mover(-1)
            elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                self.mover(1)
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.jogar_fase(self.selecionada)
            elif evento.key == pygame.K_ESCAPE:
                self.voltar()
        elif evento.type == pygame.MOUSEMOTION:
            for i, retangulo in enumerate(self.retangulos):
                if retangulo.collidepoint(evento.pos) and i != self.selecionada:
                    self.selecionada = i
                    self.app.audio.tocar_efeito("selecao")
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for i, retangulo in enumerate(self.retangulos):
                if retangulo.collidepoint(evento.pos):
                    self.selecionada = i
                    self.jogar_fase(i)

    def atualizar(self, dt):
        self.tempo += dt
        self.tempo_mensagem = max(0.0, self.tempo_mensagem - dt)
        self.neve.atualizar(dt)

    # ---------------------------------------------------------------- desenho
    def desenhar(self, tela):
        tela.blit(self.ceu, (0, 0))
        tela.blit(self.fundo, (0, 0))
        escurecer(tela, 150)
        self.neve.desenhar(tela)
        salvamento = self.app.salvamento
        desenhar_texto(tela, "SELECIONAR FASE", 66, CORES["titulo"], (LARGURA_BASE // 2, 62), contorno=True)
        total = len(salvamento.fragmentos_coletados)
        desenhar_texto(tela, f"Fragmentos de Gelo: {total}/{TOTAL_DE_FASES}", 28, CORES["destaque"],
                       (LARGURA_BASE // 2, 112), contorno=True)
        for i in range(TOTAL_DE_FASES):
            self._desenhar_cartao(tela, i, i == self.selecionada)
        if self.tempo_mensagem > 0:
            alfa = int(255 * min(1.0, self.tempo_mensagem))
            desenhar_texto(tela, self.mensagem, 30, CORES["erro"], (LARGURA_BASE // 2, 656), contorno=True, alfa=alfa)
        else:
            desenhar_texto(tela, "Esq/Dir: escolher    Enter: jogar    ESC: voltar", 24, CORES["texto_suave"],
                           (LARGURA_BASE // 2, 676))

    def _desenhar_cartao(self, tela, indice, selecionado):
        numero = indice + 1
        salvamento = self.app.salvamento
        liberada = salvamento.fase_desbloqueada(numero)
        concluida = salvamento.fase_concluida(numero)
        info = INFORMACOES[numero]
        retangulo = self.retangulos[indice].copy()
        if selecionado:
            retangulo.y -= 12 + int(math.sin(self.tempo * 4) * 3)
        sombra = retangulo.move(0, 8)
        pygame.draw.rect(tela, (4, 8, 30), sombra, border_radius=18)
        cor_fundo = (22, 46, 104) if liberada else (30, 34, 56)
        pygame.draw.rect(tela, cor_fundo, retangulo, border_radius=18)
        borda = CORES["destaque"] if selecionado else ((150, 220, 255) if liberada else (80, 90, 120))
        pygame.draw.rect(tela, borda, retangulo, width=4 if selecionado else 3, border_radius=18)
        # ilustração da região
        imagem_cor, imagem_cinza = self.imagens[numero]
        tela.blit(imagem_cor if liberada else imagem_cinza, (retangulo.x + 12, retangulo.y + 14))
        altura_imagem = imagem_cor.get_height()
        if not liberada:
            veu = pygame.Surface((imagem_cor.get_width(), altura_imagem), pygame.SRCALPHA)
            veu.fill((8, 12, 34, 175))
            tela.blit(veu, (retangulo.x + 12, retangulo.y + 14))
            tela.blit(self.icone_cadeado, self.icone_cadeado.get_rect(
                center=(retangulo.centerx, retangulo.y + 14 + altura_imagem // 2)))
        y = retangulo.y + altura_imagem + 38
        desenhar_texto(tela, f"FASE {numero}", 26, CORES["destaque"] if liberada else CORES["botao_desabilitado"],
                       (retangulo.centerx, y))
        nome = info["nome"].upper()
        tamanho = tamanho_para_caber(nome, 30, LARGURA_CARTAO - 30)
        desenhar_texto(tela, nome, tamanho, CORES["texto"] if liberada else CORES["texto_suave"],
                       (retangulo.centerx, y + 36), contorno=False)
        descricao = info["descricao"] if liberada else "Região bloqueada"
        desenhar_texto(tela, descricao, tamanho_para_caber(descricao, 20, LARGURA_CARTAO - 30),
                       CORES["texto_suave"], (retangulo.centerx, y + 72), deslocamento=1)
        # fragmento e conclusão
        tem_fragmento = numero in salvamento.fragmentos_coletados
        icone = self.icones_fragmento[indice] if tem_fragmento else self.icone_vazio
        tela.blit(icone, icone.get_rect(center=(retangulo.x + 60, retangulo.bottom - 52)))
        if concluida:
            tela.blit(self.icone_check, self.icone_check.get_rect(center=(retangulo.x + 120, retangulo.bottom - 52)))
            desenhar_texto(tela, "CONCLUÍDA", 22, CORES["sucesso"], (retangulo.x + 148, retangulo.bottom - 52),
                           "esquerda", deslocamento=1)
            melhor = salvamento.melhor_da_fase(numero)
            desenhar_texto(tela, f"Melhor: {melhor}", 20, CORES["texto_suave"],
                           (retangulo.right - 20, retangulo.bottom - 22), "direita", deslocamento=1)
        elif liberada:
            desenhar_texto(tela, "DISPONÍVEL", 22, CORES["titulo"], (retangulo.x + 110, retangulo.bottom - 52),
                           "esquerda", deslocamento=1)
