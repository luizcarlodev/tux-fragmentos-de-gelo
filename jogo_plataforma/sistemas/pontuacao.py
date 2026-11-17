"""Estado numérico da partida: pontos, moedas, vidas, tempo e estatísticas."""
from configuracoes import (
    PONTOS_CONCLUSAO, PONTOS_INIMIGO, PONTOS_MOEDA, PONTOS_POR_SEGUNDO,
    PONTOS_VIDA_EXTRA, VIDAS_INICIAIS,
)


class SistemaDePontuacao:
    """Controla pontuação, moedas, vidas, cronômetro e estatísticas da partida."""

    def __init__(self, tempo_limite):
        self.tempo_limite = float(tempo_limite)
        self.pontos = 0
        self.moedas = 0
        self.vidas = VIDAS_INICIAIS
        self.inimigos_derrotados = 0
        self.tempo_restante = float(tempo_limite)
        self.contando_tempo = True
        self.bonus_mastro = 0
        self.mortes = 0

    # ------------------------------------------------------------ eventos de pontuação
    def adicionar_pontos(self, quantidade):
        self.pontos += int(quantidade)

    def coletar_moeda(self):
        self.moedas += 1
        self.pontos += PONTOS_MOEDA
        if self.moedas % 100 == 0:          # 100 moedas = vida extra (tradição do gênero)
            self.vidas += 1
            self.pontos += PONTOS_VIDA_EXTRA
            return True
        return False

    def derrotar_inimigo(self):
        self.inimigos_derrotados += 1
        self.pontos += PONTOS_INIMIGO
        return PONTOS_INIMIGO

    def ganhar_vida(self):
        self.vidas += 1
        self.pontos += PONTOS_VIDA_EXTRA

    def perder_vida(self):
        self.vidas = max(0, self.vidas - 1)

    # ------------------------------------------------------------ tempo
    def atualizar_tempo(self, dt):
        """Desconta o cronômetro (só se estiver contando)."""
        if self.contando_tempo:
            self.tempo_restante = max(0.0, self.tempo_restante - dt)

    @property
    def tempo_esgotado(self):
        return self.tempo_restante <= 0.0

    @property
    def tempo_decorrido(self):
        return self.tempo_limite - self.tempo_restante

    # ------------------------------------------------------------ progresso salvo
    def exportar_progresso(self, indice_checkpoint):
        return {
            "checkpoint": int(indice_checkpoint), "pontos": self.pontos, "moedas": self.moedas,
            "vidas": max(1, self.vidas), "inimigos_derrotados": self.inimigos_derrotados,
            "tempo_restante": round(max(1.0, self.tempo_restante), 2),
        }

    def importar_progresso(self, progresso):
        self.pontos = progresso["pontos"]
        self.moedas = progresso["moedas"]
        self.vidas = progresso["vidas"]
        self.inimigos_derrotados = progresso["inimigos_derrotados"]
        self.tempo_restante = min(self.tempo_limite, progresso["tempo_restante"])

    # ------------------------------------------------------------ final da fase
    def calcular_final(self):
        """Congela o tempo e devolve o detalhamento da pontuação final."""
        self.contando_tempo = False
        bonus_tempo = int(self.tempo_restante) * PONTOS_POR_SEGUNDO
        total = self.pontos + PONTOS_CONCLUSAO + bonus_tempo
        return {
            "pontos_coletados": self.pontos,
            "bonus_conclusao": PONTOS_CONCLUSAO,
            "bonus_tempo": bonus_tempo,
            "total": total,
            "moedas": self.moedas,
            "inimigos": self.inimigos_derrotados,
            "tempo_gasto": self.tempo_decorrido,
            "tempo_restante": int(self.tempo_restante),
            "vidas": self.vidas,
            "bonus_mastro": self.bonus_mastro,
            "mortes": self.mortes,
        }
