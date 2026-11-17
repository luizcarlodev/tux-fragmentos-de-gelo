"""Classe-base de todas as cenas (menus, jogo, telas finais)."""


class Cena:
    """Uma tela do jogo. O ``GerenciadorDeCenas`` chama estes métodos."""

    transparente = False      # True: a cena de baixo continua sendo desenhada (ex.: pausa)

    def __init__(self, aplicacao):
        self.app = aplicacao

    def ao_entrar(self):
        """Chamado quando a cena passa a ser a do topo da pilha."""

    def ao_sair(self):
        """Chamado quando a cena é removida da pilha."""

    def ao_pausar(self):
        """Chamado quando outra cena é empilhada por cima."""

    def ao_retomar(self):
        """Chamado quando a cena volta a ser a do topo."""

    def tratar_evento(self, evento):
        pass

    def atualizar(self, dt):
        pass

    def desenhar(self, tela):
        pass
