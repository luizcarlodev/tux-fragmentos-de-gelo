"""Mapeamento de teclas configurável (ações → teclas)."""
import pygame

from configuracoes import ACOES_CONTROLE


class Controles:
    """Traduz as teclas escolhidas nas configurações em ações do jogo."""

    def __init__(self, configuracoes):
        self.configuracoes = configuracoes
        self._codigos = {}
        self.recarregar()

    def recarregar(self):
        """Reconstrói a tabela de teclas a partir das configurações."""
        self._codigos = {}
        for acao in ACOES_CONTROLE:
            codigos = []
            for nome in self.configuracoes.controles.get(acao, []):
                try:
                    codigos.append(pygame.key.key_code(nome))
                except (ValueError, pygame.error):
                    continue
            self._codigos[acao] = codigos

    def pressionada(self, acao):
        """``True`` enquanto alguma tecla da ação estiver segurada."""
        teclas = pygame.key.get_pressed()
        return any(teclas[codigo] for codigo in self._codigos.get(acao, []))

    def acao_do_evento(self, evento):
        """Ação disparada por um evento KEYDOWN (ou ``None``)."""
        if evento.type != pygame.KEYDOWN:
            return None
        for acao, codigos in self._codigos.items():
            if evento.key in codigos:
                return acao
        return None

    def nome_tecla(self, acao, indice=0):
        """Nome legível da tecla de uma ação, em maiúsculas."""
        nomes = self.configuracoes.controles.get(acao, [])
        if indice < len(nomes):
            return nomes[indice].upper()
        return "-"

    def definir_tecla(self, acao, codigo):
        """Define a tecla principal de ``acao``; troca com a ação que a usava, se houver."""
        nome_novo = pygame.key.name(codigo)
        controles = self.configuracoes.controles
        antiga = controles[acao][0] if controles[acao] else None
        for outra, teclas in controles.items():
            if outra != acao and teclas and teclas[0] == nome_novo:
                teclas[0] = antiga if antiga else nome_novo
        controles[acao] = [nome_novo] + [t for t in controles[acao][1:] if t != nome_novo]
        self.recarregar()
