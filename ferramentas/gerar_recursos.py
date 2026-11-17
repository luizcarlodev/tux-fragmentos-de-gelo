"""Gera TODOS os recursos provisórios do jogo (PNG + JSON de animação + sons WAV).

Uso (a partir da pasta do projeto):

    python ferramentas/gerar_recursos.py                 # tudo
    python ferramentas/gerar_recursos.py cenarios sons   # só alguns grupos

Grupos: personagens, inimigos, blocos, objetos, efeitos, decoracoes, interface, cenarios, sons.

ATENÇÃO: isto SOBRESCREVE os arquivos de mesmo nome em ``recursos/``. Se você já trocou algum
PNG pela sua arte final, gere apenas os grupos que ainda precisa (ou não rode este script).
O gerador do jogo anterior (tema clássico) foi preservado em ``ferramentas/legado/``.
"""
import importlib
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

# ordem importa: a interface usa imagens geradas antes
GRUPOS = ["personagens", "inimigos", "blocos", "objetos", "efeitos", "decoracoes", "cenarios", "interface", "sons"]


def principal(argumentos):
    from ferramentas.arte.base import iniciar_pygame
    iniciar_pygame()
    escolhidos = argumentos or GRUPOS
    desconhecidos = [g for g in escolhidos if g not in GRUPOS]
    if desconhecidos:
        print(f"Grupo(s) desconhecido(s): {desconhecidos}. Disponíveis: {GRUPOS}")
        return 1
    for grupo in GRUPOS:
        if grupo in escolhidos:
            print(f"== {grupo}")
            importlib.import_module(f"ferramentas.arte.{grupo}").gerar()
    print("Recursos gerados em", RAIZ / "recursos")
    return 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
