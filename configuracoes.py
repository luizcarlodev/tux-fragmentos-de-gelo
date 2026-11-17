"""Constantes globais do jogo e gerenciamento das configurações do usuário."""
import copy
import json
import os
import sys
from pathlib import Path

import pygame

# ----------------------------------------------------------------- caminhos
RAIZ = Path(__file__).resolve().parent
PASTA_RECURSOS = RAIZ / "recursos"
PASTA_DADOS = RAIZ / "dados"
ARQUIVO_CONFIGURACOES = PASTA_DADOS / "configuracoes.json"
ARQUIVO_SALVAMENTO = PASTA_DADOS / "salvamento.json"

# ----------------------------------------------------------------- tela
TITULO_JANELA = "Tux: A Era dos Fragmentos de Gelo"
NOME_DO_JOGO = "TUX: A ERA DOS FRAGMENTOS DE GELO"
LARGURA_BASE = 1280
ALTURA_BASE = 720
FPS = 60
TAMANHO_BLOCO = 48
RESOLUCOES_DISPONIVEIS = [(960, 540), (1280, 720), (1600, 900), (1920, 1080)]

# ----------------------------------------------------------------- cores
CORES = {
    "branco": (255, 255, 255),
    "preto": (0, 0, 0),
    "texto": (240, 250, 255),
    "texto_suave": (176, 208, 236),
    "destaque": (255, 208, 96),          # dourado: pequenos detalhes quentes
    "titulo": (120, 226, 255),           # ciano glacial
    "botao": (28, 64, 120),
    "botao_borda": (14, 30, 72),
    "botao_selecionado": (60, 150, 220),
    "botao_desabilitado": (58, 66, 96),
    "painel": (10, 18, 46),
    "erro": (255, 130, 130),
    "sucesso": (150, 255, 210),
    "gelo": (170, 230, 255),
    "roxo_gelo": (170, 150, 246),
}

# ----------------------------------------------------------------- física do jogador (px e segundos)
GRAVIDADE_SUBIDA = 2200.0
GRAVIDADE_QUEDA = 3000.0
MULTIPLICADOR_CORTE_PULO = 3.0      # gravidade extra ao soltar o botão (altura variável)
VELOCIDADE_QUEDA_MAXIMA = 1100.0
VELOCIDADE_CAMINHADA = 300.0
VELOCIDADE_CORRIDA = 480.0
ACELERACAO_CHAO = 1800.0
DESACELERACAO_CHAO = 2200.0
FREIO_CHAO = 3800.0                 # ao inverter a direção
ACELERACAO_AR = 1300.0
DESACELERACAO_AR = 500.0
FREIO_AR = 2200.0
FORCA_PULO = 1000.0
BONUS_PULO_VELOCIDADE = 0.08        # pulo um pouco mais alto correndo
TEMPO_COYOTE = 0.10                 # tolerância para pular logo após sair da borda
TEMPO_BUFFER_PULO = 0.12            # tolerância para apertar o pulo um pouco antes de pousar
IMPULSO_PISAO = 650.0
IMPULSO_PISAO_PULANDO = 950.0
DURACAO_ATORDOAMENTO = 0.40
DURACAO_INVULNERAVEL = 2.0
KNOCKBACK_X = 380.0
KNOCKBACK_Y = 480.0
DURACAO_ESTRELA = 8.0               # duração do Cristal Mágico (invencibilidade)

# ----------------------------------------------------------------- habilidades do Tux (novas; não alteram a física base)
DURACAO_ATAQUE = 0.28               # 4 quadros de 0,07 s
ATAQUE_INICIO_ATIVO = 0.07          # o golpe só acerta entre estes dois instantes
ATAQUE_FIM_ATIVO = 0.21
ATAQUE_ALCANCE = 62                 # px à frente do Tux
ATAQUE_ALTURA = 56
RECARGA_ATAQUE = 0.18
VELOCIDADE_DASH = 760.0
DURACAO_DASH = 0.20
RECARGA_DASH = 0.65

# ----------------------------------------------------------------- partida
VIDAS_INICIAIS = 3
TEMPO_LIMITE_PADRAO = 600
PONTOS_INIMIGO = 100
PONTOS_MOEDA = 10
PONTOS_CONCLUSAO = 500
PONTOS_POR_SEGUNDO = 10
PONTOS_VIDA_EXTRA = 1000
PONTOS_FRAGMENTO = 1000
TOTAL_DE_FASES = 3
PONTOS_SEGREDO = 2000

# ----------------------------------------------------------------- controles
ACOES_CONTROLE = ["esquerda", "direita", "pular", "correr", "atacar", "dash", "pausar"]
NOMES_ACOES = {
    "esquerda": "Andar p/ esquerda",
    "direita": "Andar p/ direita",
    "pular": "Pular",
    "correr": "Correr",
    "atacar": "Atacar",
    "dash": "Dash",
    "pausar": "Pausar",
}

CONFIGURACOES_PADRAO = {
    "volume_geral": 0.8,
    "volume_musica": 0.7,
    "volume_efeitos": 0.8,
    "resolucao": [1280, 720],
    "tela_cheia": False,
    "controles": {
        "esquerda": ["a", "left"],
        "direita": ["d", "right"],
        "pular": ["space", "up"],
        "correr": ["left shift", "right shift"],
        "atacar": ["j", "z"],
        "dash": ["k", "x"],
        "pausar": ["escape", "p"],
    },
}


def registrar_aviso(mensagem):
    """Mostra um aviso no console (sem interromper o jogo)."""
    print(f"[AVISO] {mensagem}", file=sys.stderr)


def _limitar(valor, minimo, maximo, padrao):
    try:
        return max(minimo, min(maximo, float(valor)))
    except (TypeError, ValueError):
        return padrao


class Configuracoes:
    """Configurações do usuário, persistidas em ``dados/configuracoes.json``."""

    def __init__(self, caminho=ARQUIVO_CONFIGURACOES):
        self.caminho = Path(caminho)
        self.dados = copy.deepcopy(CONFIGURACOES_PADRAO)

    # ------------------------------------------------------------ acesso
    def __getitem__(self, chave):
        return self.dados[chave]

    def __setitem__(self, chave, valor):
        self.dados[chave] = valor

    @property
    def controles(self):
        return self.dados["controles"]

    # ------------------------------------------------------------ persistência
    @classmethod
    def carregar(cls, caminho=ARQUIVO_CONFIGURACOES):
        """Carrega as configurações; arquivo ausente ou corrompido → valores padrão."""
        configuracoes = cls(caminho)
        try:
            with open(configuracoes.caminho, "r", encoding="utf-8") as arquivo:
                bruto = json.load(arquivo)
            if not isinstance(bruto, dict):
                raise ValueError("o conteúdo deveria ser um objeto JSON")
            configuracoes._aplicar(bruto)
        except FileNotFoundError:
            pass  # primeira execução: usa os padrões
        except (OSError, ValueError, json.JSONDecodeError) as erro:
            registrar_aviso(f"Configurações inválidas ({erro}); usando valores padrão.")
        return configuracoes

    def _aplicar(self, bruto):
        padrao = CONFIGURACOES_PADRAO
        for chave in ("volume_geral", "volume_musica", "volume_efeitos"):
            self.dados[chave] = _limitar(bruto.get(chave), 0.0, 1.0, padrao[chave])
        self.dados["tela_cheia"] = bool(bruto.get("tela_cheia", False))
        resolucao = bruto.get("resolucao")
        if (isinstance(resolucao, (list, tuple)) and len(resolucao) == 2
                and all(isinstance(v, int) for v in resolucao) and tuple(resolucao) in RESOLUCOES_DISPONIVEIS):
            self.dados["resolucao"] = list(resolucao)
        controles = bruto.get("controles")
        if isinstance(controles, dict):
            for acao in ACOES_CONTROLE:
                teclas = controles.get(acao)
                if isinstance(teclas, list):
                    validas = [t for t in teclas if isinstance(t, str) and self._tecla_valida(t)]
                    if validas:
                        self.dados["controles"][acao] = validas[:2]

    @staticmethod
    def _tecla_valida(nome):
        try:
            pygame.key.key_code(nome)
            return True
        except (ValueError, pygame.error):
            return False

    def salvar(self):
        """Grava as configurações de forma atômica (arquivo temporário + substituição)."""
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            temporario = self.caminho.with_suffix(".tmp")
            with open(temporario, "w", encoding="utf-8") as arquivo:
                json.dump(self.dados, arquivo, ensure_ascii=False, indent=2)
            os.replace(temporario, self.caminho)
        except OSError as erro:
            registrar_aviso(f"Não foi possível salvar as configurações: {erro}")

    def restaurar_controles_padrao(self):
        self.dados["controles"] = copy.deepcopy(CONFIGURACOES_PADRAO["controles"])
