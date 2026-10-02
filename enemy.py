import random
import pygame
import config
from entidade import Entidade
from projetil import Projetil, AvisoQueda
from animacao import Animacao

_PASTA_MINIGOLEM = "assets/minigolem"
_PASTA_GOLEM = "assets/golem"

# Escala dos PNGs (canvas 160x128 e 200x200) para o tamanho em tela
_ESCALA_MINIGOLEM = 0.427
_ESCALA_GOLEM = 0.917

_DURACAO_ANIM_DANO = 10   # frames


class Enemy(Entidade):
    def __init__(self, x, y, vida, cor, largura, altura):
        super().__init__(x, y, largura, altura, vida)
        self.cor = cor

    def desenhar(self, tela, camera_x=0):
        super().desenhar(tela, self.cor, camera_x)


def _desenhar_frame(tela, frame, rect, camera_x, direcao=1):
    """Desenha o sprite centralizado no hitbox, com a base alinhada."""
    if direcao == -1:
        frame = pygame.transform.flip(frame, True, False)

    pos_x = rect.x - camera_x - (frame.get_width() - rect.width) // 2
    pos_y = rect.y - (frame.get_height() - rect.height)
    tela.blit(frame, (pos_x, pos_y))


class MiniGolem(Enemy):
    """Patrulha de um lado para o outro dentro da plataforma onde nasceu."""

    def __init__(self, x, y, limite_esq, limite_dir):
        super().__init__(
            x, y,
            config.MINI_GOLEM_VIDA,
            config.COR_MINI_GOLEM,
            config.MINI_GOLEM_LARGURA,
            config.MINI_GOLEM_ALTURA,
        )
        self.limite_esq = limite_esq
        self.limite_dir = limite_dir
        self.direcao_patrulha = 1

        self.animacoes = {
            "andar": Animacao(_PASTA_MINIGOLEM, "andar", ticks_por_frame=8, escala=_ESCALA_MINIGOLEM),
            "dano": Animacao(_PASTA_MINIGOLEM, "dano", ticks_por_frame=8, escala=_ESCALA_MINIGOLEM),
            "morte": Animacao(_PASTA_MINIGOLEM, "morte", ticks_por_frame=8, loop=False, escala=_ESCALA_MINIGOLEM),
        }
        self.dano_timer = 0
        self.morte_timer = 0
        self._duracao_morte = len(self.animacoes["morte"].frames) * 8

    def esta_morrendo(self):
        return self.morte_timer > 0

    def comportamento(self):
        if self.morte_timer > 0:
            self.morte_timer -= 1
            self.animacoes["morte"].atualizar()
            return

        self.mover(self.direcao_patrulha * config.MINI_GOLEM_VELOCIDADE_PATRULHA, 0)

        if self.x <= self.limite_esq:
            self.x = self.limite_esq
            self.rect.x = self.x
            self.direcao_patrulha = 1
        elif self.x >= self.limite_dir:
            self.x = self.limite_dir
            self.rect.x = self.x
            self.direcao_patrulha = -1

        if self.dano_timer > 0:
            self.dano_timer -= 1

        estado = "dano" if self.dano_timer > 0 else "andar"
        self.animacoes[estado].atualizar()

    def receber_dano(self, dano):
        super().receber_dano(dano)
        if self.vida <= 0:
            self.morte_timer = self._duracao_morte
            self.animacoes["morte"].reiniciar()
        else:
            self.dano_timer = _DURACAO_ANIM_DANO

    def desenhar(self, tela, camera_x=0):
        if self.morte_timer > 0:
            estado = "morte"
        elif self.dano_timer > 0:
            estado = "dano"
        else:
            estado = "andar"

        frame = self.animacoes[estado].frame_atual()
        if frame is None:
            super().desenhar(tela, camera_x)
            return
        _desenhar_frame(tela, frame, self.rect, camera_x, direcao=self.direcao_patrulha)


class Golem(Enemy):
    """Boss parado no canto da arena. Alterna entre atacar sem parar (pedras e
    chuva de cristais) e uma janela curta de vulnerabilidade, única hora em
    que leva dano."""

    def __init__(self, x, y, arena_inicio, arena_fim):
        super().__init__(
            x, y,
            config.GOLEM_VIDA,
            config.COR_GOLEM,
            config.GOLEM_LARGURA,
            config.GOLEM_ALTURA,
        )
        self.arena_inicio = arena_inicio
        self.arena_fim = arena_fim
        self.vida_maxima = config.GOLEM_VIDA

        self.pedra_timer = config.GOLEM_PEDRA_INTERVALO
        self.chuva_timer = config.GOLEM_CHUVA_INTERVALO

        self.ciclo_timer = config.GOLEM_CICLO_ATAQUE_DURACAO
        self.vulneravel_timer = 0

        self._pontos_chuva = self._gerar_pontos_chuva()
        self._indices_bloqueados = []

        self.animacoes = {
            "ataque_loop": Animacao(_PASTA_GOLEM, "ataque_loop", ticks_por_frame=10, escala=_ESCALA_GOLEM),
            "arremesso": Animacao(_PASTA_GOLEM, "arremesso", ticks_por_frame=6, escala=_ESCALA_GOLEM),
            "vulneravel": Animacao(_PASTA_GOLEM, "vulneravel", ticks_por_frame=12, escala=_ESCALA_GOLEM),
            "dano": Animacao(_PASTA_GOLEM, "dano", ticks_por_frame=8, escala=_ESCALA_GOLEM),
        }
        self.animacao_arremesso_timer = 0
        self.dano_timer = 0
        self.direcao = -1

    def _gerar_pontos_chuva(self):
        """Pontos fixos no céu, só na zona de combate (à frente do golem)."""
        zona_fim = self.x - config.TILE
        largura_zona = zona_fim - self.arena_inicio
        qtd = config.GOLEM_CHUVA_QTD_PONTOS_SPAWN
        espaco = largura_zona / (qtd + 1)
        return [self.arena_inicio + espaco * (i + 1) for i in range(qtd)]

    @property
    def multiplicador_fase(self):
        return {
            1: config.GOLEM_FASE_1_MULTIPLICADOR,
            2: config.GOLEM_FASE_2_MULTIPLICADOR,
            3: config.GOLEM_FASE_3_MULTIPLICADOR,
        }[self._fase_atual()]

    def _fase_atual(self):
        proporcao_vida = self.vida / self.vida_maxima
        if proporcao_vida > config.GOLEM_FASE_1_LIMIAR:
            return 1
        if proporcao_vida > config.GOLEM_FASE_2_LIMIAR:
            return 2
        return 3

    def esta_vulneravel(self):
        return self.vulneravel_timer > 0

    def _estado_animacao(self):
        if self.dano_timer > 0:
            return "dano"
        if self.esta_vulneravel():
            return "vulneravel"
        if self.animacao_arremesso_timer > 0:
            return "arremesso"
        return "ataque_loop"

    def desenhar(self, tela, camera_x=0):
        frame = self.animacoes[self._estado_animacao()].frame_atual()
        if frame is None:
            cor = config.COR_GOLEM_VULNERAVEL if self.esta_vulneravel() else self.cor
            Entidade.desenhar(self, tela, cor, camera_x)
            return
        _desenhar_frame(tela, frame, self.rect, camera_x, direcao=self.direcao)

    def receber_dano(self, dano):
        if self.esta_vulneravel():
            super().receber_dano(dano)
            self.dano_timer = _DURACAO_ANIM_DANO

    def comportamento(self):
        """Alterna entre atacando e vulnerável. Os timers de pedra e chuva
        avançam em atacar_pedra() e atacar_chuva()."""
        if self.dano_timer > 0:
            self.dano_timer -= 1
        if self.animacao_arremesso_timer > 0:
            self.animacao_arremesso_timer -= 1

        self.animacoes[self._estado_animacao()].atualizar()

        if self.vulneravel_timer > 0:
            self.vulneravel_timer -= 1
            if self.vulneravel_timer <= 0:
                self.ciclo_timer = config.GOLEM_CICLO_ATAQUE_DURACAO
            return

        self.ciclo_timer -= 1
        if self.ciclo_timer <= 0:
            self.vulneravel_timer = config.GOLEM_JANELA_VULNERAVEL

    def atacar_pedra(self, alvo_x):
        """Lança uma pedra na direção do Tux: rasteira (pular) ou aérea (ficar no chão)."""
        if self.esta_vulneravel():
            return None

        self.pedra_timer -= self.multiplicador_fase
        if self.pedra_timer > 0:
            return None

        self.pedra_timer = config.GOLEM_PEDRA_INTERVALO

        direcao = 1 if alvo_x is not None and alvo_x > self.x else -1
        self.direcao = direcao
        tipo = random.choice(["rasteira", "aerea"])
        y = config.GOLEM_PEDRA_RASTEIRA_Y if tipo == "rasteira" else config.GOLEM_PEDRA_AEREA_Y

        self.animacao_arremesso_timer = config.GOLEM_ANIM_ARREMESSO_DURACAO
        return Projetil(self.x, y, direcao, origem="golem")

    def atacar_chuva(self):
        """Retorna os avisos (nuvens) dos pontos sorteados. O cristal só cai
        depois que a nuvem termina de crescer (feito em game.py). Evita repetir
        o mesmo ponto ou o vizinho na onda seguinte."""
        if self.esta_vulneravel():
            return []

        self.chuva_timer -= self.multiplicador_fase
        if self.chuva_timer > 0:
            return []

        self.chuva_timer = config.GOLEM_CHUVA_INTERVALO

        fase = self._fase_atual()
        qtd_min = config.GOLEM_CHUVA_QTD_MIN_POR_FASE[fase]
        qtd_max = config.GOLEM_CHUVA_QTD_MAX_POR_FASE[fase]
        qtd = min(random.randint(qtd_min, qtd_max), len(self._pontos_chuva))

        disponiveis = [
            i for i in range(len(self._pontos_chuva))
            if i not in self._indices_bloqueados
        ]
        if len(disponiveis) < qtd:
            disponiveis = list(range(len(self._pontos_chuva)))

        indices_escolhidos = random.sample(disponiveis, qtd)

        bloqueados = set()
        for indice in indices_escolhidos:
            bloqueados.update(self._vizinhos_bloqueados(indice))
        self._indices_bloqueados = list(bloqueados)

        return [AvisoQueda(self._pontos_chuva[i]) for i in indices_escolhidos]

    def _vizinhos_bloqueados(self, indice):
        raio = config.GOLEM_CHUVA_MIN_PONTOS_SEM_REPETIR
        return [indice + delta for delta in range(-raio, raio + 1)]
