"""Construtor de mapas: ferramentas comuns aos geradores das fases (grade ASCII + listas extras).

Convenções (as mesmas da fase original):
  * cada caractere da grade é um bloco de 48 px; a legenda está em ``legendas_glaciais.py``;
  * personagens/objetos são marcados na linha onde a BASE deles encosta (um inimigo em pé
    sobre o piso cujo topo é a linha 19 é marcado na linha 18);
  * plataformas móveis, decorações, diálogos e temas ficam em listas separadas.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from legendas_glaciais import LEGENDA, REGIOES  # noqa: E402

PASTA_MAPAS = Path(__file__).resolve().parent.parent / "fases" / "mapas"


class ConstrutorDeMapa:
    def __init__(self, colunas, linhas):
        self.colunas, self.linhas = colunas, linhas
        self.grade = [[" "] * colunas for _ in range(linhas)]
        self.plataformas = []
        self.decoracoes = []
        self.dialogos = []
        self.zonas = []

    # ---------------------------------------------------------------- blocos
    def p(self, c, l, ch):
        if 0 <= c < self.colunas and 0 <= l < self.linhas:
            self.grade[l][c] = ch

    def ler(self, c, l):
        if 0 <= c < self.colunas and 0 <= l < self.linhas:
            return self.grade[l][c]
        return " "

    def retangulo(self, c0, l0, c1, l1, ch):
        for l in range(l0, l1 + 1):
            for c in range(c0, c1 + 1):
                self.p(c, l, ch)

    def chao(self, c0, c1, topo, topo_ch="G", corpo_ch="T", fundo=None):
        """Piso com superfície na linha ``topo`` e corpo até o fim do mapa (ou ``fundo``)."""
        fundo = self.linhas - 1 if fundo is None else fundo
        for c in range(c0, c1 + 1):
            self.p(c, topo, topo_ch)
            for l in range(topo + 1, fundo + 1):
                self.p(c, l, corpo_ch)

    def buraco(self, c0, c1, topo, fundo=None):
        """Apaga o piso (queda mortal) entre as colunas."""
        fundo = self.linhas - 1 if fundo is None else fundo
        self.retangulo(c0, topo, c1, fundo, " ")

    def agua(self, c0, c1, topo, fundo=None):
        """Água gélida (mata ao tocar)."""
        fundo = self.linhas - 1 if fundo is None else fundo
        self.retangulo(c0, topo, c1, fundo, "V")

    def texto(self, c, l, linha):
        for i, ch in enumerate(linha):
            if ch != " ":
                self.p(c + i, l, ch)

    def pilar(self, c, topo, base):
        """Pilar de gelo de 2 colunas entre a linha ``topo`` e a linha ``base`` (inclusive)."""
        self.p(c, topo, "a"); self.p(c + 1, topo, "b")
        for l in range(topo + 1, base + 1):
            self.p(c, l, "c"); self.p(c + 1, l, "d")

    def escada(self, c0, base, n, sentido=1, ch="S"):
        """Degraus de altura 1..n; ``base`` é a linha do piso onde a escada se apoia."""
        for i in range(n):
            c = c0 + i * sentido
            for h in range(i + 1):
                self.p(c, base - 1 - h, ch)

    def ilha(self, c, l, largura, ch="p"):
        for i in range(largura):
            self.p(c + i, l, ch)

    # ---------------------------------------------------------------- itens
    def cristais(self, c0, c1, l, passo=1):
        for c in range(c0, c1 + 1, passo):
            self.p(c, l, "o")

    def arco(self, c, l, n=5):
        meio = n // 2
        for i in range(n):
            self.p(c - meio + i, l - (1 if 0 < i < n - 1 else 0), "o")

    def plataforma_movel(self, centro, linha, eixo, amplitude, periodo, fase=0.0, largura=3):
        self.plataformas.append({"coluna_centro": centro, "linha": linha, "largura_blocos": largura,
                                 "eixo": eixo, "amplitude": amplitude, "periodo": periodo, "fase": fase})

    def deco(self, imagem, c, linha_base, frente=False):
        dados = {"imagem": imagem, "coluna": c, "linha_base": linha_base}
        if frente:
            dados["frente"] = True
        self.decoracoes.append(dados)

    def dialogo(self, coluna, texto, duracao=3.6):
        self.dialogos.append({"coluna": coluna, "texto": texto, "duracao": duracao})

    def zona(self, coluna_inicio, tema):
        self.zonas.append({"coluna_inicio": coluna_inicio, "tema": tema})

    # ---------------------------------------------------------------- exportação
    def contagem(self):
        total = {}
        for linha in self.grade:
            for ch in linha:
                total[ch] = total.get(ch, 0) + 1
        return total

    def salvar(self, nome_arquivo, nome, regioes, extras=None, tempo_limite=600):
        """Grava ``fases/mapas/<nome_arquivo>.json``. ``regioes``: nomes de REGIOES usados em ``zonas``."""
        mapa = {
            "nome": nome, "tamanho_bloco": 48, "colunas": self.colunas, "linhas": self.linhas,
            "tempo_limite": tempo_limite, "tileset": "blocos/tileset",
            "legenda": LEGENDA,
            "grade": ["".join(l) for l in self.grade],
            "plataformas_moveis": self.plataformas, "decoracoes": self.decoracoes,
            "temas": {r: REGIOES[r] for r in regioes},
            "zonas": self.zonas, "dialogos": sorted(self.dialogos, key=lambda d: d["coluna"]),
        }
        mapa.update(extras or {})
        PASTA_MAPAS.mkdir(parents=True, exist_ok=True)
        destino = PASTA_MAPAS / f"{nome_arquivo}.json"
        destino.write_text(json.dumps(mapa, ensure_ascii=False, indent=1), encoding="utf-8")
        c = self.contagem()
        print(f"{destino.name}: {self.colunas}x{self.linhas} = {self.colunas * 48 / 1280:.1f} telas | "
              f"cristais {c.get('o', 0)} | inimigos {sum(c.get(x, 0) for x in '12345')} | totens {c.get('C', 0)}")
        return destino
