"""Pilha de cenas com transições visuais (fade e íris)."""
import pygame

from configuracoes import ALTURA_BASE, LARGURA_BASE


class GerenciadorDeCenas:
    """Gerencia a pilha de cenas ativas.

    * ``trocar``     — substitui TODA a pilha por uma nova cena;
    * ``empilhar``   — coloca uma cena por cima (ex.: menu de pausa);
    * ``desempilhar``— remove a cena do topo (volta à anterior);
    * ``executar_com_transicao`` — executa uma função no meio de uma transição.
    """

    DURACAO = 0.32

    def __init__(self, aplicacao):
        self.aplicacao = aplicacao
        self.pilha = []
        self._acao = None
        self._fase = None          # None | "saindo" | "entrando"
        self._tempo = 0.0
        self._tipo = "fade"
        self._centro = (LARGURA_BASE // 2, ALTURA_BASE // 2)
        self._cobertura = pygame.Surface((LARGURA_BASE, ALTURA_BASE))
        self._cobertura.set_colorkey((255, 0, 255))

    # ------------------------------------------------------------ acesso
    @property
    def cena_atual(self):
        return self.pilha[-1] if self.pilha else None

    @property
    def em_transicao(self):
        return self._fase is not None

    # ------------------------------------------------------------ operações
    def trocar(self, cena, transicao="fade", centro=None):
        def acao():
            for antiga in reversed(self.pilha):
                antiga.ao_sair()
            self.pilha = [cena]
            cena.ao_entrar()
        self._agendar(acao, transicao, centro)

    def empilhar(self, cena, transicao=None):
        def acao():
            if self.pilha:
                self.pilha[-1].ao_pausar()
            self.pilha.append(cena)
            cena.ao_entrar()
        self._agendar(acao, transicao)

    def desempilhar(self, transicao=None):
        def acao():
            if self.pilha:
                topo = self.pilha.pop()
                topo.ao_sair()
            if self.pilha:
                self.pilha[-1].ao_retomar()
        self._agendar(acao, transicao)

    def executar_com_transicao(self, funcao, transicao="fade", centro=None):
        self._agendar(funcao, transicao, centro)

    def _agendar(self, acao, transicao, centro=None):
        if self._fase is not None:
            return  # ignora pedidos durante uma transição em andamento
        if transicao is None or not self.pilha:
            acao()
            return
        self._acao = acao
        self._tipo = transicao
        self._centro = centro or (LARGURA_BASE // 2, ALTURA_BASE // 2)
        self._fase = "saindo"
        self._tempo = 0.0

    # ------------------------------------------------------------ ciclo
    def tratar_evento(self, evento):
        if self._fase is None and self.cena_atual:
            self.cena_atual.tratar_evento(evento)

    def atualizar(self, dt):
        if self.cena_atual:
            self.cena_atual.atualizar(dt)
        if self._fase is None:
            return
        self._tempo += dt
        if self._tempo >= self.DURACAO:
            if self._fase == "saindo":
                acao, self._acao = self._acao, None
                if acao:
                    acao()
                self._fase = "entrando"
                self._tempo = 0.0
            else:
                self._fase = None

    def desenhar(self, tela):
        # desenha a partir da última cena opaca até o topo
        inicio = 0
        for i in range(len(self.pilha) - 1, -1, -1):
            if not self.pilha[i].transparente:
                inicio = i
                break
        for cena in self.pilha[inicio:]:
            cena.desenhar(tela)
        if self._fase is not None:
            progresso = min(1.0, self._tempo / self.DURACAO)
            cobertura = progresso if self._fase == "saindo" else 1.0 - progresso
            self._desenhar_cobertura(tela, cobertura)

    def _desenhar_cobertura(self, tela, cobertura):
        """``cobertura`` 0 = nada, 1 = tela totalmente coberta."""
        if cobertura <= 0:
            return
        if self._tipo == "iris":
            self._cobertura.fill((0, 0, 0))
            raio_maximo = int((LARGURA_BASE ** 2 + ALTURA_BASE ** 2) ** 0.5)
            raio = int(raio_maximo * (1.0 - cobertura))
            if raio > 0:
                pygame.draw.circle(self._cobertura, (255, 0, 255), self._centro, raio)
            tela.blit(self._cobertura, (0, 0))
        else:
            self._cobertura.fill((0, 0, 0))
            self._cobertura.set_alpha(int(255 * cobertura))
            tela.blit(self._cobertura, (0, 0))
            self._cobertura.set_alpha(255)
