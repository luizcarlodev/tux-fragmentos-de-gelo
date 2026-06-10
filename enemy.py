from entidade import Entidade


class Enemy(Entidade):

    def __init__(self, x, y, vida):
        super().__init__(
            x,
            y,
            40,
            40,
            vida
        )

    def comportamento(self):
        pass


class CriaturaCongelada(Enemy):

    def __init__(self, x, y):
        super().__init__(x, y, 2)

    def comportamento(self):
        self.mover(-2, 0)


class Macaco(Enemy):

    def __init__(self, x, y):
        super().__init__(x, y, 3)

    def comportamento(self):
        self.mover(3, 0)


class Escorpiao(Enemy):

    def __init__(self, x, y):
        super().__init__(x, y, 2)

    def comportamento(self):
        self.mover(1, 0)