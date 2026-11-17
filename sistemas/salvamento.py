"""Sistema de salvamento em JSON: campanha (fases, fragmentos, segredo) e progresso da partida.

Formato (versão 2)::

    {"versao": 2, "melhor_pontuacao": 0,
     "fases_concluidas": [1], "fases_desbloqueadas": [1, 2], "fragmentos": [1],
     "melhores_por_fase": {"1": 3200}, "segredo_descoberto": false, "campanha_concluida": false,
     "progresso": {"fase": 2, "checkpoint": 0, "pontos": 0, ...} | null}

Salvamentos da versão 1 (sem campanha) são migrados automaticamente: o recorde e o
checkpoint da fase 1 são preservados. Arquivos ausentes ou corrompidos nunca impedem o
jogo de iniciar: o arquivo ruim é renomeado (``.corrompido``) e um salvamento limpo é usado.
"""
import json
import os
from pathlib import Path

from configuracoes import ARQUIVO_SALVAMENTO, TOTAL_DE_FASES, registrar_aviso

VERSAO_ATUAL = 2
CAMPOS_PROGRESSO = {
    "checkpoint": int, "pontos": int, "moedas": int, "vidas": int,
    "inimigos_derrotados": int, "tempo_restante": float,
}


def _inteiro_valido(valor, minimo=0):
    return isinstance(valor, int) and not isinstance(valor, bool) and valor >= minimo


class Salvamento:
    """Guarda recorde, fases concluídas/desbloqueadas, fragmentos, segredo e o último checkpoint."""

    def __init__(self, caminho=ARQUIVO_SALVAMENTO):
        self.caminho = Path(caminho)
        self.dados = self._padrao()
        self.carregar()

    @staticmethod
    def _padrao():
        return {"versao": VERSAO_ATUAL, "melhor_pontuacao": 0, "fases_concluidas": [],
                "fases_desbloqueadas": [1], "fragmentos": [], "melhores_por_fase": {},
                "segredo_descoberto": False, "campanha_concluida": False, "progresso": None}

    # ------------------------------------------------------------ leitura/gravação
    def carregar(self):
        self.dados = self._padrao()
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                bruto = json.load(arquivo)
            if not isinstance(bruto, dict):
                raise ValueError("conteúdo inesperado")
            self._importar(bruto)
        except FileNotFoundError:
            pass
        except (OSError, ValueError, json.JSONDecodeError) as erro:
            registrar_aviso(f"Salvamento inválido ({erro}); iniciando um novo.")
            try:
                os.replace(self.caminho, self.caminho.with_suffix(".corrompido"))
            except OSError:
                pass
            self.dados = self._padrao()

    def _importar(self, bruto):
        """Valida campo a campo (aceita a versão 1 e a versão 2); campos inválidos viram o padrão."""
        dados = self.dados
        if _inteiro_valido(bruto.get("melhor_pontuacao")):
            dados["melhor_pontuacao"] = bruto["melhor_pontuacao"]
        concluidas = bruto.get("fases_concluidas", [])
        if isinstance(concluidas, list):
            dados["fases_concluidas"] = sorted({n for n in concluidas if _inteiro_valido(n, 1) and n <= TOTAL_DE_FASES})
        fragmentos = bruto.get("fragmentos", [])
        if isinstance(fragmentos, list):
            dados["fragmentos"] = sorted({n for n in fragmentos if _inteiro_valido(n, 1) and n <= TOTAL_DE_FASES})
        melhores = bruto.get("melhores_por_fase", {})
        if isinstance(melhores, dict):
            for chave, valor in melhores.items():
                if str(chave).isdigit() and 1 <= int(chave) <= TOTAL_DE_FASES and _inteiro_valido(valor):
                    dados["melhores_por_fase"][str(int(chave))] = valor
        dados["segredo_descoberto"] = bruto.get("segredo_descoberto") is True
        dados["campanha_concluida"] = bruto.get("campanha_concluida") is True
        self._recalcular_desbloqueios()
        dados["progresso"] = self._validar_progresso(bruto.get("progresso"))
        if dados["progresso"] and not self.fase_desbloqueada(dados["progresso"]["fase"]):
            dados["progresso"] = None

    def _recalcular_desbloqueios(self):
        """A fase 1 está sempre liberada; concluir a fase N libera a N+1."""
        liberadas = {1}
        for n in self.dados["fases_concluidas"]:
            liberadas.add(n)
            if n + 1 <= TOTAL_DE_FASES:
                liberadas.add(n + 1)
        self.dados["fases_desbloqueadas"] = sorted(liberadas)

    def salvar(self):
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            temporario = self.caminho.with_suffix(".tmp")
            with open(temporario, "w", encoding="utf-8") as arquivo:
                json.dump(self.dados, arquivo, ensure_ascii=False, indent=2)
            os.replace(temporario, self.caminho)
        except OSError as erro:
            registrar_aviso(f"Não foi possível gravar o salvamento: {erro}")

    # ------------------------------------------------------------ progresso da partida (checkpoint)
    @staticmethod
    def _validar_progresso(bruto):
        """Retorna o progresso validado ou ``None`` se estiver incompleto/inconsistente."""
        if not isinstance(bruto, dict):
            return None
        limpo = {}
        for campo, tipo in CAMPOS_PROGRESSO.items():
            valor = bruto.get(campo)
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                return None
            limpo[campo] = tipo(valor)
        fase = bruto.get("fase", 1)                         # salvamentos antigos não tinham "fase"
        if isinstance(fase, bool) or not isinstance(fase, int) or not 1 <= fase <= TOTAL_DE_FASES:
            return None
        limpo["fase"] = fase
        if not (0 <= limpo["checkpoint"] < 100 and limpo["pontos"] >= 0 and limpo["moedas"] >= 0
                and 1 <= limpo["vidas"] <= 99 and limpo["inimigos_derrotados"] >= 0
                and 0 < limpo["tempo_restante"] <= 9999):
            return None
        return limpo

    def tem_progresso(self):
        return self.dados["progresso"] is not None

    def obter_progresso(self):
        return dict(self.dados["progresso"]) if self.dados["progresso"] else None

    def salvar_progresso(self, progresso):
        validado = self._validar_progresso(progresso)
        if validado is None:
            registrar_aviso("Progresso inválido; não foi salvo.")
            return
        self.dados["progresso"] = validado
        self.salvar()

    def limpar_progresso(self):
        self.dados["progresso"] = None
        self.salvar()

    # ------------------------------------------------------------ campanha
    def fase_concluida(self, numero):
        return numero in self.dados["fases_concluidas"]

    def fase_desbloqueada(self, numero):
        return numero in self.dados["fases_desbloqueadas"]

    @property
    def fragmentos_coletados(self):
        return list(self.dados["fragmentos"])

    @property
    def tem_todos_os_fragmentos(self):
        return len(self.dados["fragmentos"]) >= TOTAL_DE_FASES

    def melhor_da_fase(self, numero):
        return self.dados["melhores_por_fase"].get(str(numero), 0)

    def registrar_conclusao(self, numero, pontos):
        """Marca a fase como concluída, guarda o fragmento e libera a próxima. Retorna ``True`` se bateu recorde."""
        dados = self.dados
        if numero not in dados["fases_concluidas"]:
            dados["fases_concluidas"] = sorted(dados["fases_concluidas"] + [numero])
        if numero not in dados["fragmentos"]:
            dados["fragmentos"] = sorted(dados["fragmentos"] + [numero])
        if pontos > self.melhor_da_fase(numero):
            dados["melhores_por_fase"][str(numero)] = int(pontos)
        self._recalcular_desbloqueios()
        recorde = pontos > dados["melhor_pontuacao"]
        if recorde:
            dados["melhor_pontuacao"] = int(pontos)
        self.salvar()
        return recorde

    @property
    def pontuacao_da_campanha(self):
        """Soma dos melhores resultados de cada fase."""
        return sum(self.dados["melhores_por_fase"].values())

    # ------------------------------------------------------------ segredo e final
    @property
    def segredo_descoberto(self):
        return self.dados["segredo_descoberto"]

    def registrar_segredo(self):
        if not self.dados["segredo_descoberto"]:
            self.dados["segredo_descoberto"] = True
            self.salvar()

    @property
    def campanha_concluida(self):
        return self.dados["campanha_concluida"]

    def registrar_campanha_concluida(self):
        self.dados["campanha_concluida"] = True
        self.salvar()

    # ------------------------------------------------------------ pontuação
    @property
    def melhor_pontuacao(self):
        return self.dados["melhor_pontuacao"]

    def registrar_pontuacao(self, pontos):
        """Atualiza o recorde; retorna ``True`` se a pontuação for um novo recorde."""
        if pontos > self.dados["melhor_pontuacao"]:
            self.dados["melhor_pontuacao"] = int(pontos)
            self.salvar()
            return True
        return False

    def reiniciar_campanha(self):
        """Apaga o progresso da campanha (mantém o recorde e o segredo)."""
        melhor, segredo = self.dados["melhor_pontuacao"], self.dados["segredo_descoberto"]
        self.dados = self._padrao()
        self.dados["melhor_pontuacao"], self.dados["segredo_descoberto"] = melhor, segredo
        self.salvar()
