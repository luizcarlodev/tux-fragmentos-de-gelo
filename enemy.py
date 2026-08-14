import config
from entidade import Entidade
from projetil import Projetil


class Enemy(Entidade):

    def __init__(self, x, y, vida, cor=None, largura=40, altura=40):
        super().__init__(x, y, largura, altura, vida)
        self.cor = cor

    def comportamento(self):
        pass

    def desenhar(self, tela, camera_x=0):
        super().desenhar(tela, self.cor, camera_x)


class Chefe(Enemy):

    def __init__(self, x, y, vida, cor, largura, altura, limite_esq, limite_dir, intervalo_ataque):
        super().__init__(x, y, vida, cor, largura, altura)
        self.limite_esq = limite_esq
        self.limite_dir = limite_dir
        self.direcao_patrulha = 1
        self.intervalo_ataque = intervalo_ataque
        self.ataque_timer = intervalo_ataque

    def comportamento(self, alvo_x=None):
        self.mover(self.direcao_patrulha * 2, 0)

        if self.x <= self.limite_esq or self.x >= self.limite_dir:
            self.direcao_patrulha *= -1

    def atacar(self, alvo_x):
        if self.ataque_timer > 0:
            self.ataque_timer -= 1
            return None

        self.ataque_timer = self.intervalo_ataque
        direcao = 1 if alvo_x > self.x else -1
        return Projetil(self.x + self.largura / 2, self.y + self.altura / 2, direcao)


class ChefeCriaturaCongelada(Chefe):

    def __init__(self, x, y, limite_esq, limite_dir):
        super().__init__(x, y, config.CHEFE1_VIDA, config.COR_CHEFE1, 80, 80, limite_esq, limite_dir, config.CHEFE1_INTERVALO_ATAQUE)

class ChefeMacaco(Chefe):

    def __init__(self, x, y, limite_esq, limite_dir):
        super().__init__(x, y, config.CHEFE2_VIDA, config.COR_CHEFE2, 80, 80, limite_esq, limite_dir, config.CHEFE2_INTERVALO_DASH)
        self.dash_restante = 0
        self.direcao_dash = 1

    def comportamento(self, alvo_x=None):
        if self.dash_restante > 0:
            self.mover(self.direcao_dash * config.CHEFE2_VELOCIDADE_DASH, 0)
            self.dash_restante -= 1
            return

        if self.ataque_timer > 0:
            self.ataque_timer -= 1
        else:
            self.ataque_timer = self.intervalo_ataque
            self.dash_restante = config.CHEFE2_DURACAO_DASH
            self.direcao_dash = 1 if alvo_x is not None and alvo_x > self.x else -1
            return

        self.mover(self.direcao_patrulha * 2, 0)
        if self.x <= self.limite_esq or self.x >= self.limite_dir:
            self.direcao_patrulha *= -1