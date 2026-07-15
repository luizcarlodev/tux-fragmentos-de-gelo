import config
from entidade import Entidade


class Projetil(Entidade):

    def __init__(self, x, y, direcao):
        super().__init__(x, y, config.PROJETIL_LARGURA, config.PROJETIL_ALTURA, vida=0)
        self.direcao = direcao

    def atualizar(self):
        self.mover(self.direcao * config.PROJETIL_VELOCIDADE, 0)

    def fora_da_tela(self):
        return self.x < 0 or self.x > config.LARGURA_MUNDO

    def desenhar(self, tela, camera_x=0):
        super().desenhar(tela, config.COR_PROJETIL, camera_x)