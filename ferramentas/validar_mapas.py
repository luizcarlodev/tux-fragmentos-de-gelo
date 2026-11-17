"""Validador de jogabilidade dos mapas.

Mede as trajetórias REAIS de pulo/queda do Tux (rodando o próprio motor de física em um
terreno plano), e então faz uma busca em largura sobre a grade do mapa para provar que o
Fragmento de Gelo pode ser alcançado a partir do ponto inicial.

Uso (na pasta do projeto):
    python ferramentas/validar_mapas.py                 # valida todas as fases
    python ferramentas/validar_mapas.py fase_02 fase_03

O modelo é CONSERVADOR: usa apenas pulos com a tecla segurada, andando ou correndo
(sem dash, sem ataque, sem controle fino no ar). Plataformas móveis contam como superfícies
de pouso em várias posições do seu trajeto (otimista quanto ao tempo, por isso as fases
usam ilhas fixas de apoio perto delas).
"""
import hashlib
import json
import os
import sys
from collections import deque
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from legendas_glaciais import LEGENDA  # noqa: E402

T = 48
CACHE = Path(__file__).resolve().parent / ".trajetorias.json"
SUBPOSICOES = (0.12, 0.5, 0.88)          # onde, dentro do bloco, o Tux pode decolar


# ---------------------------------------------------------------------- medição das trajetórias
def _assinatura_da_fisica():
    dados = b""
    for caminho in ("entidades/jogador.py", "sistemas/colisoes.py", "configuracoes.py", "ferramentas/validar_mapas.py"):
        dados += (RAIZ / caminho).read_bytes()
    return hashlib.md5(dados).hexdigest()


def medir_trajetorias():
    """Devolve {"larg", "alt", "arcos": {nome: [[dx, dy_base], ...]}} (px, dy positivo = para baixo)."""
    assinatura = _assinatura_da_fisica()
    if CACHE.exists():
        try:
            dados = json.loads(CACHE.read_text())
            if dados.get("assinatura") == assinatura:
                return dados
        except ValueError:
            pass
    os.chdir(RAIZ)
    import pygame  # noqa: F401
    from entidades.blocos import Bloco
    from fases.fase import Fase
    from principal import Aplicacao
    from sistemas.pontuacao import SistemaDePontuacao

    app = Aplicacao()
    fase = Fase(app.recursos, app.audio, SistemaDePontuacao(600), "fase_01")
    mapa, jogador = fase.mapa, fase.jogador
    fase.perder_vida_fatal = lambda: None          # cair abaixo do mapa de teste não pode matar o Tux
    for c in range(mapa.colunas):
        for l in range(mapa.linhas):
            mapa.definir(c, l, None)
    for lista in (fase.inimigos, fase.moedas, fase.plataformas, fase.checkpoints):
        lista.clear()
    fase.altar = fase.portal = None
    definicao = LEGENDA["G"]

    def piso(ate):
        for c in range(mapa.colunas):
            for l in (13, 14):
                mapa.definir(c, l, Bloco(c, l, definicao) if c <= ate else None)

    def preparar(correr, direita=True, parado=False):
        piso(60)
        jogador.reaparecer(8 * T + T / 2, 13 * T, invulneravel=0.0)
        jogador.vx = jogador.vy = 0.0
        entrada = {"esquerda": False, "direita": not parado, "pular": False, "correr": correr}
        for _ in range(100 if not parado else 20):
            fase.atualizar(1 / 60, entrada)
        return entrada

    def gravar(entrada, pular, segurar=True):
        """Grava o arco depois da decolagem; o piso é removido no ar para a queda continuar livre."""
        ex = jogador.centro_x
        ey = jogador.base
        arco = []
        if pular:
            fase.pedir_pulo()
            entrada["pular"] = True
        no_ar = False
        for quadro in range(260):
            fase.atualizar(1 / 60, entrada)
            if not segurar and quadro > 4:
                entrada["pular"] = False
            if not jogador.no_chao:
                if not no_ar:
                    no_ar = True
                    piso(-1)                                   # sem chão: a queda segue livre
                arco.append([round(jogador.centro_x - ex, 1), round(jogador.base - ey, 1)])
                if jogador.base - ey > 9 * T:
                    break
        return arco

    arcos = {}
    e = preparar(False); arcos["pulo_andando"] = gravar(e, True)
    e = preparar(True); arcos["pulo_correndo"] = gravar(e, True)
    e = preparar(False, parado=True); e["direita"] = True; arcos["pulo_parado"] = gravar(e, True)
    e = preparar(False); arcos["pulinho_andando"] = gravar(e, True, segurar=False)
    e = preparar(True); arcos["pulinho_correndo"] = gravar(e, True, segurar=False)
    # queda ao sair da borda: o piso termina na coluna 40 (borda direita em x = 41 * T)
    desloc = 0.0
    for nome, correr in (("queda_correndo", True), ("queda_andando", False)):
        piso(40)
        jogador.reaparecer(30 * T + T / 2, 13 * T, invulneravel=0.0)
        jogador.vx = jogador.vy = 0.0
        parado = {"esquerda": False, "direita": False, "pular": False, "correr": False}
        for _ in range(30):
            fase.atualizar(1 / 60, parado)                     # assenta no piso
        entrada = {"esquerda": False, "direita": True, "pular": False, "correr": correr}
        for _ in range(300):
            fase.atualizar(1 / 60, entrada)
            if not jogador.no_chao:
                break
        ex, ey = jogador.centro_x, jogador.base
        desloc = ex - 41 * T
        arco = []
        for _ in range(200):
            fase.atualizar(1 / 60, entrada)
            arco.append([round(jogador.centro_x - ex, 1), round(jogador.base - ey, 1)])
            if jogador.base - ey > 9 * T:
                break
        arcos[nome] = arco
    dados = {"assinatura": assinatura, "larg": jogador.largura, "alt": jogador.altura, "desloc_borda": desloc, "arcos": arcos}
    try:
        CACHE.write_text(json.dumps(dados))
    except OSError:
        pass
    return dados


# ---------------------------------------------------------------------- análise do mapa
class Analise:
    def __init__(self, nome, trajetorias):
        self.nome = nome
        self.traj = trajetorias
        self.mapa = json.loads((RAIZ / "fases" / "mapas" / f"{nome}.json").read_text(encoding="utf-8"))
        self.legenda = self.mapa["legenda"]
        self.grade = self.mapa["grade"]
        self.linhas, self.colunas = len(self.grade), len(self.grade[0])
        self.solidos, self.perigos = set(), set()
        self.posicoes = {}
        for l, texto in enumerate(self.grade):
            for c, ch in enumerate(texto):
                d = self.legenda.get(ch, {})
                if d.get("tipo") == "bloco":
                    if d.get("solido", True):
                        self.solidos.add((c, l))
                    else:
                        self.perigos.add((c, l))
                if ch not in " ":
                    self.posicoes.setdefault(ch, []).append((c, l))
        self.plataformas = set()           # topos de plataformas móveis (apoio unilateral)
        for p in self.mapa.get("plataformas_moveis", []):
            for passo in range(-8, 9):
                f = passo / 8
                cx0, ln0, larg = p["coluna_centro"], p["linha"], p["largura_blocos"]
                if p.get("eixo", "x") == "x":
                    cx, ln = cx0 + p["amplitude"] * f, ln0
                else:
                    cx, ln = cx0, ln0 + p["amplitude"] * f
                for k in range(larg):
                    self.plataformas.add((int(round(cx - larg / 2 + k)), int(round(ln))))

    # ---- consultas
    def _suporte(self, c, l):
        return (c, l) in self.solidos or (c, l) in self.plataformas

    def em_pe(self, c, l):
        """Célula (c, l) é um ponto onde o Tux pode ficar de pé (pés na base da linha l)."""
        if not (0 <= c < self.colunas and 0 <= l < self.linhas):
            return False
        if not self._suporte(c, l + 1):
            return False
        for dl in (0, -1):
            if (c, l + dl) in self.solidos or (c, l + dl) in self.perigos:
                return False
        return True

    def _caixa_livre(self, cx, base):
        """Hitbox do Tux (com 1 px de folga em cada lado) livre de blocos sólidos e perigos?"""
        larg, alt = self.traj["larg"], self.traj["alt"]
        c0, c1 = int((cx - larg / 2 + 1) // T), int((cx + larg / 2 - 1) // T)
        l0, l1 = int((base - alt + 1) // T), int((base - 1.5) // T)
        for c in range(c0, c1 + 1):
            for l in range(l0, l1 + 1):
                if (c, l) in self.solidos or (c, l) in self.perigos:
                    return False
        return True

    def _pouso(self, cx, anterior, base):
        """Se os pés cruzaram o topo de um apoio neste quadro, devolve a célula em pé; senão None."""
        if base < anterior:
            return None
        k = -int(-(anterior - 0.5) // T)               # primeira fronteira de bloco (teto do piso) abaixo
        if k * T > base + 0.5:
            return None
        l = k - 1
        larg = self.traj["larg"]
        colunas = [c for c in range(int((cx - larg / 2 + 2) // T), int((cx + larg / 2 - 2) // T) + 1)
                   if self._suporte(c, l + 1) and self.em_pe(c, l)]
        if not colunas:
            return None
        coluna = min(colunas, key=lambda c: abs(c * T + T / 2 - cx))
        return (coluna, l)

    def simular_arco(self, cx0, base0, direcao, arco):
        """Percorre um arco medido a partir de (cx0, base0). Devolve a célula de pouso ou None."""
        anterior = base0
        for dx, dy in arco:
            cx, base = cx0 + dx * direcao, base0 + dy
            destino = self._pouso(cx, anterior, base)
            if destino is not None:
                return destino
            if not self._caixa_livre(cx, base):
                return None
            anterior = base
            if not (-2 * T <= cx <= (self.colunas + 2) * T) or base > (self.linhas + 2) * T:
                return None
        return None

    def vizinhos(self, c, l):
        saida = set()
        # caminhar por piso contínuo
        for dc in (-1, 1):
            if self.em_pe(c + dc, l):
                saida.add((c + dc, l))
        for direcao in (-1, 1):
            for sub in SUBPOSICOES:
                cx0 = c * T + sub * T
                base0 = (l + 1) * T
                for nome, arco in self.traj["arcos"].items():
                    if nome.startswith("queda"):
                        # só decola da borda: precisa de vazio de pé adiante
                        if self._suporte(c + direcao, l + 1):
                            continue
                        borda = (c + 1) * T if direcao > 0 else c * T
                        cx_ini = borda + direcao * self.traj["desloc_borda"]
                        destino = self.simular_arco(cx_ini, base0, direcao, arco)
                    else:
                        destino = self.simular_arco(cx0, base0, direcao, arco)
                    if destino and destino != (c, l):
                        saida.add(destino)
        return saida

    def alcancaveis(self, inicio):
        visitados, fila = {inicio}, deque([inicio])
        while fila:
            c, l = fila.popleft()
            for v in self.vizinhos(c, l):
                if v not in visitados:
                    visitados.add(v)
                    fila.append(v)
        return visitados


def celula_de_pe(analise, c, l):
    """Ajusta uma posição marcada na grade (base do objeto na linha l) para a célula de pé mais próxima."""
    for dl in (0, 1, -1):
        if analise.em_pe(c, l + dl):
            return (c, l + dl)
    return (c, l)


def validar(nome, trajetorias):
    a = Analise(nome, trajetorias)
    erros, avisos = [], []
    inicio = a.posicoes.get("J")
    if not inicio:
        return ["sem posição inicial 'J'"], [], {}
    for ch in set(a.posicoes) - set(a.legenda):
        erros.append(f"caractere '{ch}' sem legenda")
    for obrigatorio, descricao in (("F", "altar"), ("P", "portal")):
        if obrigatorio not in a.posicoes:
            erros.append(f"sem {descricao} '{obrigatorio}'")
    if erros:
        return erros, avisos, {}
    c, l = inicio[0]
    origem = celula_de_pe(a, c, l)
    alcance = a.alcancaveis(origem)
    cobertas = {}

    def alcanca(c, l, folga=1, abaixo=(0, 1)):
        """Há uma célula alcançável até ``folga`` colunas ao lado e com os pés entre as linhas dadas?"""
        return any((c + dc, l + dl) in alcance for dc in range(-folga, folga + 1) for dl in range(abaixo[0], abaixo[1] + 1))

    for ch, rotulo in (("F", "altar do fragmento"), ("C", "totem"), ("P", "portal")):
        for (c, l) in a.posicoes.get(ch, []):
            if not alcanca(c, l, 1, (0, 1)):
                erros.append(f"{rotulo} em ({c},{l}) INALCANÇÁVEL")
    for (c, l) in a.posicoes.get("X", []):
        if not alcanca(c - 1, l, 1, (0, 2)) and not alcanca(c + 1, l, 1, (0, 2)):
            erros.append(f"parede rachada em ({c},{l}) INALCANÇÁVEL (segredo impossível)")
    for (c, l) in a.posicoes.get("J", []):
        pass
    # cristais: contam se algum apoio alcançável está até 3 colunas ao lado e até 5 linhas abaixo
    total_cristais = len(a.posicoes.get("o", []))
    cristais_ok = sum(1 for (c, l) in a.posicoes.get("o", []) if alcanca(c, l, 3, (0, 5)))
    if total_cristais and cristais_ok < total_cristais * 0.9:
        avisos.append(f"só {cristais_ok}/{total_cristais} cristais parecem alcançáveis")
    cobertas.update(estados=len(alcance), cristais=f"{cristais_ok}/{total_cristais}",
                    largura_em_telas=round(a.colunas * T / 1280, 1), linhas=a.linhas)
    # marcos intermediários: coluna máxima alcançada
    cobertas["coluna_maxima"] = max(c for c, _ in alcance)
    return erros, avisos, cobertas


def principal(argumentos):
    nomes = argumentos or sorted(p.stem for p in (RAIZ / "fases" / "mapas").glob("fase_*.json"))
    trajetorias = medir_trajetorias()
    alcance_andando = max(x for x, _ in trajetorias["arcos"]["pulo_andando"])
    alcance_correndo = max(x for x, _ in trajetorias["arcos"]["pulo_correndo"])
    print(f"Trajetórias medidas: pulo andando {alcance_andando / T:.1f} blocos, correndo {alcance_correndo / T:.1f} blocos.")
    falhou = False
    for nome in nomes:
        erros, avisos, info = validar(nome, trajetorias)
        status = "OK" if not erros else "FALHOU"
        print(f"[{status}] {nome}: {info}")
        for texto in avisos:
            print("   aviso:", texto)
        for texto in erros:
            print("   ERRO:", texto)
        falhou = falhou or bool(erros)
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
