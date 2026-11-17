"""Sistema de spritesheets e animações.

Cada recurso animado vive em uma pasta com um PNG e um ``configuracao.json``:

    {
      "arquivo": "personagem.png",
      "largura_quadro": 16, "altura_quadro": 22,   # tamanho de UM quadro no PNG
      "escala": 3,                                  # ampliação aplicada ao carregar
      "margem": 0, "espacamento": 0,                # opcionais
      "caixa_colisao": [34, 58],                    # opcional (largura, altura) em pixels finais
      "animacoes": {
        "andando": {"linha": 1, "quadro_inicial": 0, "quadros": 4,
                    "duracao_quadro": 0.12, "repetir": true}
      }
    }

Trocar a arte do jogo = trocar o PNG (e, se mudar o tamanho/quantidade de
quadros, ajustar o JSON). Nenhuma linha de código precisa mudar.
"""
import json
from pathlib import Path

import pygame

from configuracoes import registrar_aviso


class Animacao:
    """Sequência de quadros com duração e modo de repetição."""

    def __init__(self, nome, quadros, duracao_quadro=0.1, repetir=True):
        self.nome = nome
        self.quadros = quadros
        self.quadros_espelhados = [pygame.transform.flip(q, True, False) for q in quadros]
        self.duracao_quadro = max(0.01, float(duracao_quadro))
        self.repetir = repetir

    def __len__(self):
        return len(self.quadros)


class FolhaDeSprites:
    """Conjunto de animações recortadas de uma spritesheet."""

    def __init__(self, nome, animacoes, caixa_colisao=None, tamanho_quadro=(48, 48)):
        self.nome = nome
        self.animacoes = animacoes
        self.caixa_colisao = tuple(caixa_colisao) if caixa_colisao else None
        self.tamanho_quadro = tamanho_quadro
        self._padrao = next(iter(animacoes.values())) if animacoes else None

    def obter(self, nome):
        """Retorna a animação pedida (ou a primeira, se o nome não existir)."""
        animacao = self.animacoes.get(nome)
        if animacao is None:
            registrar_aviso(f"Animação '{nome}' não existe em '{self.nome}'.")
            animacao = self._padrao
            self.animacoes[nome] = animacao  # evita repetir o aviso
        return animacao

    def tem(self, nome):
        return nome in self.animacoes

    @classmethod
    def carregar(cls, pasta):
        """Carrega a folha a partir de ``pasta/configuracao.json``."""
        pasta = Path(pasta)
        with open(pasta / "configuracao.json", "r", encoding="utf-8") as arquivo:
            cfg = json.load(arquivo)
        imagem = pygame.image.load(str(pasta / cfg["arquivo"])).convert_alpha()
        lw, lh = int(cfg["largura_quadro"]), int(cfg["altura_quadro"])
        escala = float(cfg.get("escala", 1))
        margem = int(cfg.get("margem", 0))
        espaco = int(cfg.get("espacamento", 0))
        tamanho_final = (max(1, round(lw * escala)), max(1, round(lh * escala)))
        animacoes = {}
        for nome, dados in cfg["animacoes"].items():
            quadros = []
            linha = int(dados["linha"])
            inicial = int(dados.get("quadro_inicial", 0))
            for i in range(int(dados["quadros"])):
                x = margem + (inicial + i) * (lw + espaco)
                y = margem + linha * (lh + espaco)
                recorte = pygame.Surface((lw, lh), pygame.SRCALPHA)
                recorte.blit(imagem, (0, 0), pygame.Rect(x, y, lw, lh))
                if tamanho_final != (lw, lh):
                    recorte = pygame.transform.scale(recorte, tamanho_final)
                quadros.append(recorte)
            animacoes[nome] = Animacao(nome, quadros, dados.get("duracao_quadro", 0.1),
                                       dados.get("repetir", True))
        return cls(pasta.name, animacoes, cfg.get("caixa_colisao"), tamanho_final)

    @classmethod
    def provisoria(cls, nome, tamanho=(48, 48)):
        """Folha de emergência (xadrez magenta) usada quando o recurso não carrega."""
        quadro = pygame.Surface(tamanho, pygame.SRCALPHA)
        metade = max(1, tamanho[0] // 2), max(1, tamanho[1] // 2)
        quadro.fill((255, 0, 255))
        pygame.draw.rect(quadro, (0, 0, 0), (0, 0, metade[0], metade[1]))
        pygame.draw.rect(quadro, (0, 0, 0), (metade[0], metade[1], metade[0], metade[1]))
        animacao = Animacao("padrao", [quadro], 1.0, True)
        return cls(nome, {"padrao": animacao}, None, tamanho)


class Animador:
    """Controla o tempo e o quadro atual de uma animação de uma folha."""

    def __init__(self, folha, animacao_inicial=None):
        self.folha = folha
        self.animacao = None
        self.nome_atual = None
        self.tempo = 0.0
        self.indice = 0
        self.velocidade = 1.0
        self.finalizada = False
        if animacao_inicial:
            self.tocar(animacao_inicial)
        elif folha.animacoes:
            self.tocar(next(iter(folha.animacoes)))

    def tocar(self, nome, reiniciar=False):
        """Troca de animação (não reinicia se já for a atual, a menos que pedido)."""
        if nome == self.nome_atual and not reiniciar:
            return
        self.nome_atual = nome
        self.animacao = self.folha.obter(nome)
        self.tempo = 0.0
        self.indice = 0
        self.finalizada = False

    def atualizar(self, dt):
        if self.animacao is None or self.finalizada:
            return
        self.tempo += dt * self.velocidade
        total = len(self.animacao)
        passos = int(self.tempo / self.animacao.duracao_quadro)
        if self.animacao.repetir:
            self.indice = passos % total
        elif passos >= total:
            self.indice = total - 1
            self.finalizada = True
        else:
            self.indice = passos

    def imagem(self, espelhado=False):
        quadros = self.animacao.quadros_espelhados if espelhado else self.animacao.quadros
        return quadros[min(self.indice, len(quadros) - 1)]


class GerenciadorDeRecursos:
    """Carrega e guarda em cache imagens, folhas de sprites e sons."""

    def __init__(self, pasta_raiz):
        self.pasta_raiz = Path(pasta_raiz)
        self._folhas = {}
        self._imagens = {}
        self._sons = {}

    def folha(self, caminho_relativo):
        """Folha de sprites da pasta ``recursos/<caminho_relativo>``."""
        if caminho_relativo not in self._folhas:
            try:
                self._folhas[caminho_relativo] = FolhaDeSprites.carregar(self.pasta_raiz / caminho_relativo)
            except (OSError, ValueError, KeyError, pygame.error, json.JSONDecodeError) as erro:
                registrar_aviso(f"Falha ao carregar a folha '{caminho_relativo}': {erro}")
                self._folhas[caminho_relativo] = FolhaDeSprites.provisoria(caminho_relativo)
        return self._folhas[caminho_relativo]

    def imagem(self, caminho_relativo, escala=1.0):
        """Imagem PNG avulsa (ex.: ícones da interface)."""
        chave = (caminho_relativo, escala)
        if chave not in self._imagens:
            try:
                img = pygame.image.load(str(self.pasta_raiz / caminho_relativo)).convert_alpha()
                if escala != 1.0:
                    img = pygame.transform.scale(img, (round(img.get_width() * escala),
                                                       round(img.get_height() * escala)))
            except (OSError, pygame.error) as erro:
                registrar_aviso(f"Falha ao carregar a imagem '{caminho_relativo}': {erro}")
                img = FolhaDeSprites.provisoria(caminho_relativo, (32, 32)).obter("padrao").quadros[0]
            self._imagens[chave] = img
        return self._imagens[chave]

    def fundo(self, caminho_relativo):
        """Imagem de cenário (PNG grande); usa ``convert_alpha`` para preservar transparência."""
        return self.imagem(caminho_relativo)

    def som(self, caminho_relativo):
        """Efeito sonoro; retorna ``None`` se o arquivo não existir ou o áudio estiver indisponível."""
        if caminho_relativo not in self._sons:
            som = None
            if pygame.mixer.get_init():
                caminho = self.pasta_raiz / caminho_relativo
                if caminho.exists():
                    try:
                        som = pygame.mixer.Sound(str(caminho))
                    except pygame.error as erro:
                        registrar_aviso(f"Falha ao carregar o som '{caminho_relativo}': {erro}")
            self._sons[caminho_relativo] = som
        return self._sons[caminho_relativo]
