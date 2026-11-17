"""Tela de configurações: volumes, vídeo e remapeamento de controles (tudo persistido em JSON)."""
import pygame

from cenas.cena import Cena
from configuracoes import (
    ACOES_CONTROLE, ALTURA_BASE, CORES, LARGURA_BASE, NOMES_ACOES, RESOLUCOES_DISPONIVEIS,
)
from interface.efeitos_de_tela import gradiente_vertical
from interface.textos import desenhar_texto

X_ROTULO, X_VALOR, LARGURA_LINHA, ALTURA_LINHA = 250, 1030, 780, 56
BARRA = pygame.Rect(0, 0, 280, 16)


class ConfiguracoesMenu(Cena):
    """Linhas navegáveis por teclado (cima/baixo escolhe, esquerda/direita ajusta, Enter ativa) ou mouse."""

    def __init__(self, aplicacao):
        super().__init__(aplicacao)
        self.cfg = aplicacao.configuracoes
        self.fundo = gradiente_vertical((28, 48, 120), (10, 12, 40))
        self.modo = "principal"
        self.selecionado = 0
        self.capturando = None            # ação cuja tecla está sendo redefinida
        self.tempo = 0.0
        self.linhas = []
        self._montar()

    # ---------------------------------------------------------------- montagem das linhas
    def _montar(self):
        self.linhas = self._linhas_principais() if self.modo == "principal" else self._linhas_controles()
        self.selecionado = min(self.selecionado, len(self.linhas) - 1)

    def _linhas_principais(self):
        linhas = []
        for chave, rotulo in (("volume_geral", "Volume geral"), ("volume_musica", "Volume da música"),
                              ("volume_efeitos", "Volume dos efeitos")):
            linhas.append({"rotulo": rotulo, "tipo": "slider", "chave": chave})
        linhas.append({"rotulo": "Resolução (janela)", "tipo": "opcao",
                       "valor": lambda: "x".join(map(str, self.cfg["resolucao"])),
                       "ajustar": self._mudar_resolucao})
        linhas.append({"rotulo": "Modo de tela", "tipo": "opcao",
                       "valor": lambda: "TELA CHEIA" if self.cfg["tela_cheia"] else "JANELA",
                       "ajustar": self._alternar_tela_cheia})
        linhas.append({"rotulo": "Controles", "tipo": "acao", "valor": lambda: "ABRIR >",
                       "ativar": self._abrir_controles})
        linhas.append({"rotulo": "VOLTAR", "tipo": "acao", "valor": lambda: "", "ativar": self.voltar})
        return linhas

    def _linhas_controles(self):
        linhas = []
        for acao in ACOES_CONTROLE:
            linhas.append({"rotulo": NOMES_ACOES[acao], "tipo": "tecla", "acao": acao})
        linhas.append({"rotulo": "Restaurar controles padrão", "tipo": "acao", "valor": lambda: "",
                       "ativar": self._restaurar_controles})
        linhas.append({"rotulo": "VOLTAR", "tipo": "acao", "valor": lambda: "", "ativar": self._fechar_controles})
        return linhas

    # ---------------------------------------------------------------- ações
    def _salvar(self):
        self.cfg.salvar()

    def _ajustar_volume(self, chave, delta, som=True):
        self.cfg[chave] = round(max(0.0, min(1.0, self.cfg[chave] + delta)), 2)
        self.app.audio.atualizar_volumes()
        if som:
            self.app.audio.tocar_efeito("selecao")

    def _mudar_resolucao(self, sentido):
        if self.cfg["tela_cheia"]:
            self.app.audio.tocar_efeito("mensagem_erro")
            return
        atual = tuple(self.cfg["resolucao"])
        indice = RESOLUCOES_DISPONIVEIS.index(atual) if atual in RESOLUCOES_DISPONIVEIS else 1
        self.cfg["resolucao"] = list(RESOLUCOES_DISPONIVEIS[(indice + sentido) % len(RESOLUCOES_DISPONIVEIS)])
        self.app.aplicar_video()
        self._salvar()

    def _alternar_tela_cheia(self, sentido=1):
        self.cfg["tela_cheia"] = not self.cfg["tela_cheia"]
        self.app.aplicar_video()
        self._salvar()

    def _abrir_controles(self):
        self.modo, self.selecionado = "controles", 0
        self._montar()

    def _fechar_controles(self):
        self.modo, self.selecionado = "principal", 5
        self._montar()

    def _restaurar_controles(self):
        self.cfg.restaurar_controles_padrao()
        self.app.controles.recarregar()
        self._salvar()

    def voltar(self):
        if self.modo == "controles":
            self._fechar_controles()
        else:
            self._salvar()
            self.app.cenas.desempilhar("fade")

    def ao_sair(self):
        self._salvar()

    # ---------------------------------------------------------------- entrada
    def _retangulo_linha(self, indice):
        retangulo = pygame.Rect(0, 0, LARGURA_LINHA, ALTURA_LINHA)
        retangulo.midtop = (LARGURA_BASE // 2, 150 + indice * (ALTURA_LINHA + 12))
        return retangulo

    def _barra_da_linha(self, indice):
        barra = BARRA.copy()
        barra.midright = (self._retangulo_linha(indice).right - 90, self._retangulo_linha(indice).centery)
        return barra

    def _definir_slider_pelo_mouse(self, indice, x):
        barra = self._barra_da_linha(indice)
        chave = self.linhas[indice]["chave"]
        self.cfg[chave] = round(max(0.0, min(1.0, (x - barra.left) / barra.width)), 2)
        self.app.audio.atualizar_volumes()

    def tratar_evento(self, evento):
        if self.capturando:
            self._capturar_tecla(evento)
            return
        if evento.type == pygame.KEYDOWN:
            self._tecla(evento.key)
        elif evento.type == pygame.MOUSEMOTION:
            for i in range(len(self.linhas)):
                if self._retangulo_linha(i).collidepoint(evento.pos):
                    if i != self.selecionado:
                        self.selecionado = i
                        self.app.audio.tocar_efeito("selecao")
                    break
            linha = self.linhas[self.selecionado]
            if evento.buttons[0] and linha["tipo"] == "slider":
                self._definir_slider_pelo_mouse(self.selecionado, evento.pos[0])
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for i in range(len(self.linhas)):
                if self._retangulo_linha(i).collidepoint(evento.pos):
                    self.selecionado = i
                    if self.linhas[i]["tipo"] == "slider":
                        self._definir_slider_pelo_mouse(i, evento.pos[0])
                        self.app.audio.tocar_efeito("selecao")
                    else:
                        self._ativar()
                    break
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self._salvar()

    def _tecla(self, tecla):
        linha = self.linhas[self.selecionado]
        if tecla in (pygame.K_UP, pygame.K_w):
            self.selecionado = (self.selecionado - 1) % len(self.linhas)
            self.app.audio.tocar_efeito("selecao")
        elif tecla in (pygame.K_DOWN, pygame.K_s):
            self.selecionado = (self.selecionado + 1) % len(self.linhas)
            self.app.audio.tocar_efeito("selecao")
        elif tecla in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
            sentido = -1 if tecla in (pygame.K_LEFT, pygame.K_a) else 1
            if linha["tipo"] == "slider":
                self._ajustar_volume(linha["chave"], 0.05 * sentido)
                self._salvar()
            elif linha["tipo"] == "opcao":
                linha["ajustar"](sentido)
        elif tecla in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self._ativar()
        elif tecla == pygame.K_ESCAPE:
            self.voltar()

    def _ativar(self):
        linha = self.linhas[self.selecionado]
        self.app.audio.tocar_efeito("confirmacao")
        if linha["tipo"] == "acao":
            linha["ativar"]()
        elif linha["tipo"] == "opcao":
            linha["ajustar"](1)
        elif linha["tipo"] == "tecla":
            self.capturando = linha["acao"]

    def _capturar_tecla(self, evento):
        """Espera a próxima tecla para a ação escolhida (ESC cancela)."""
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key != pygame.K_ESCAPE:
            self.app.controles.definir_tecla(self.capturando, evento.key)
            self._salvar()
            self.app.audio.tocar_efeito("confirmacao")
        self.capturando = None

    # ---------------------------------------------------------------- desenho
    def atualizar(self, dt):
        self.tempo += dt

    def desenhar(self, tela):
        tela.blit(self.fundo, (0, 0))
        titulo = "CONTROLES" if self.modo == "controles" else "SETTINGS"
        desenhar_texto(tela, titulo, 76, CORES["destaque"], (LARGURA_BASE // 2, 80), contorno=True)
        for i, linha in enumerate(self.linhas):
            self._desenhar_linha(tela, i, linha)
        dica = ("Pressione a nova tecla (ESC cancela)" if self.capturando else
                "Cima/Baixo: escolher   Esq/Dir: ajustar   Enter: ativar   ESC: voltar")
        desenhar_texto(tela, dica, 26, CORES["texto_suave"], (LARGURA_BASE // 2, ALTURA_BASE - 40))

    def _desenhar_linha(self, tela, indice, linha):
        retangulo = self._retangulo_linha(indice)
        selecionada = indice == self.selecionado
        cor = CORES["botao_selecionado"] if selecionada else CORES["painel"]
        pygame.draw.rect(tela, cor, retangulo, border_radius=12)
        pygame.draw.rect(tela, CORES["destaque"] if selecionada else CORES["botao_borda"], retangulo, 3,
                         border_radius=12)
        cor_texto = CORES["destaque"] if selecionada else CORES["texto"]
        desenhar_texto(tela, linha["rotulo"], 32, cor_texto, (retangulo.left + 24, retangulo.centery), "esquerda")
        tipo = linha["tipo"]
        if tipo == "slider":
            self._desenhar_slider(tela, indice, linha)
        elif tipo == "tecla":
            capturando = self.capturando == linha["acao"]
            texto = "..." if capturando else self.app.controles.nome_tecla(linha["acao"])
            alt = self.app.controles.nome_tecla(linha["acao"], 1)
            if not capturando and alt != "-":
                texto += f"  /  {alt}"
            cor_valor = CORES["sucesso"] if capturando else CORES["texto"]
            desenhar_texto(tela, texto, 30, cor_valor, (retangulo.right - 24, retangulo.centery), "direita")
        elif linha.get("valor"):
            valor = linha["valor"]()
            desenhar_texto(tela, valor, 30, CORES["texto"], (retangulo.right - 24, retangulo.centery), "direita")

    def _desenhar_slider(self, tela, indice, linha):
        barra = self._barra_da_linha(indice)
        valor = self.cfg[linha["chave"]]
        pygame.draw.rect(tela, (10, 14, 40), barra, border_radius=8)
        preenchida = barra.copy()
        preenchida.width = max(8, int(barra.width * valor))
        pygame.draw.rect(tela, CORES["destaque"], preenchida, border_radius=8)
        pygame.draw.circle(tela, CORES["branco"], (barra.left + int(barra.width * valor), barra.centery), 12)
        desenhar_texto(tela, f"{int(round(valor * 100))}%", 28, CORES["texto"],
                       (self._retangulo_linha(indice).right - 24, barra.centery), "direita")
