"""Sistema de salvamento em JSON (melhor pontuação e progresso da partida)."""
import json
import os
from pathlib import Path

from configuracoes import ARQUIVO_SALVAMENTO, registrar_aviso

CAMPOS_PROGRESSO = {
    "checkpoint": int, "pontos": int, "moedas": int, "vidas": int,
    "inimigos_derrotados": int, "tempo_restante": float,
}


class Salvamento:
    """Guarda a melhor pontuação e o último checkpoint alcançado.

    Arquivos ausentes ou corrompidos nunca impedem o jogo de iniciar:
    o arquivo ruim é renomeado (``.corrompido``) e um salvamento limpo é usado.
    """

    def __init__(self, caminho=ARQUIVO_SALVAMENTO):
        self.caminho = Path(caminho)
        self.dados = self._padrao()
        self.carregar()

    @staticmethod
    def _padrao():
        return {"versao": 1, "melhor_pontuacao": 0, "progresso": None}

    # ------------------------------------------------------------ leitura/gravação
    def carregar(self):
        self.dados = self._padrao()
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                bruto = json.load(arquivo)
            if not isinstance(bruto, dict):
                raise ValueError("conteúdo inesperado")
            melhor = bruto.get("melhor_pontuacao", 0)
            if isinstance(melhor, int) and not isinstance(melhor, bool) and melhor >= 0:
                self.dados["melhor_pontuacao"] = melhor
            self.dados["progresso"] = self._validar_progresso(bruto.get("progresso"))
        except FileNotFoundError:
            pass
        except (OSError, ValueError, json.JSONDecodeError) as erro:
            registrar_aviso(f"Salvamento inválido ({erro}); iniciando um novo.")
            try:
                os.replace(self.caminho, self.caminho.with_suffix(".corrompido"))
            except OSError:
                pass
            self.dados = self._padrao()

    def salvar(self):
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            temporario = self.caminho.with_suffix(".tmp")
            with open(temporario, "w", encoding="utf-8") as arquivo:
                json.dump(self.dados, arquivo, ensure_ascii=False, indent=2)
            os.replace(temporario, self.caminho)
        except OSError as erro:
            registrar_aviso(f"Não foi possível gravar o salvamento: {erro}")

    # ------------------------------------------------------------ progresso
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
