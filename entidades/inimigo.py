"""Inimigos da Era Glacial: quatro criaturas com comportamentos próprios.

* ``CriaturaDeNeve``  — patrulha o chão e acelera ao notar o Tux;
* ``PinguimSelvagem`` — persegue o jogador e aguenta dois golpes (fica furioso);
* ``MorcegoGlacial``  — voa em arco, solta estilhaços de gelo e, se configurado, mergulha;
* ``GolemDeGelo``     — lento, resistente (3 golpes) e muda de comportamento ao ficar ferido.

Todos usam o mesmo contrato de combate: ``ser_pisado``, ``ser_atingido`` (ataque/dash),
``ser_derrotado`` (arremesso) e as propriedades ``perigoso`` / ``pisavel``.
"""
import math

from configuracoes import PONTOS_INIMIGO
from entidades.entidade import Entidade
from sistemas.animacoes import Animador

GRAVIDADE_INIMIGO = 2400.0


class Inimigo(Entidade):
    """Base dos inimigos: estados "vivo", "esmagado" e "arremessado"."""

    nome = "base"
    pasta = ""
    animacao_inicial = "andando"
    velocidade = 60.0
    pontos = PONTOS_INIMIGO

    def __init__(self, centro_x, y_base, recursos, opcoes=None):
        folha = recursos.folha(self.pasta)
        largura, altura = folha.caixa_colisao or (40, 40)
        super().__init__(centro_x - largura / 2, y_base - altura, largura, altura)
        self.animador = Animador(folha, self.animacao_inicial)
        self.opcoes = dict(opcoes or {})
        self.estado = "vivo"
        self.tempo_estado = 0.0
        self.direcao = -1
        self.no_chao = False
        self.x_origem = centro_x
        self.pedido_tiro = False
        self.eventos = []                # sons/efeitos pedidos pelo inimigo ("grito", "golem_passo"...)

    # ------------------------------------------------------------ propriedades
    @property
    def perigoso(self):
        """``True`` se tocar nele machuca o jogador."""
        return self.estado == "vivo"

    @property
    def pisavel(self):
        return self.estado == "vivo"

    # ------------------------------------------------------------ ciclo
    def atualizar(self, dt, colisoes, jogador):
        self.animador.atualizar(dt)
        if self.estado == "vivo":
            self.comportamento(dt, colisoes, jogador)
        elif self.estado == "esmagado":
            self.tempo_estado += dt
            if self.tempo_estado > 0.45:
                self.ativo = False
        else:  # arremessado: cai girando para fora da tela
            self.vy += GRAVIDADE_INIMIGO * dt
            self.x += self.vx * dt
            self.y += self.vy * dt
            if self.y > colisoes.mapa.altura_pixels + 200:
                self.ativo = False
        if self.estado == "vivo" and self.y > colisoes.mapa.altura_pixels + 200:
            self.ativo = False                              # caiu em um buraco

    def comportamento(self, dt, colisoes, jogador):
        """Sobrescrito por cada tipo de inimigo."""

    # ------------------------------------------------------------ combate
    def ser_pisado(self):
        """O jogador pulou em cima. Retorna ``"morto"`` ou ``"ferido"``."""
        self._esmagar()
        return "morto"

    def ser_atingido(self, origem_x=None):
        """Golpe de ataque/dash. Retorna ``"morto"``, ``"ferido"`` ou ``"imune"``."""
        self.ser_derrotado(origem_x)
        return "morto"

    def _esmagar(self):
        self.estado = "esmagado"
        self.tempo_estado = 0.0
        self.vx = 0.0
        self.animador.tocar("esmagado", reiniciar=True)

    def ser_derrotado(self, origem_x=None):
        """Derrota o inimigo arremessando-o (cristal mágico, bloco por baixo, golpe...)."""
        if self.estado == "arremessado":
            return
        self.estado = "arremessado"
        sentido = 1 if origem_x is None or origem_x < self.centro_x else -1
        self.vx = sentido * 160.0
        self.vy = -520.0

    # ------------------------------------------------------------ movimento
    def _borda_a_frente(self, colisoes):
        x_frente = self.x + self.largura + 3 if self.direcao > 0 else self.x - 3
        return not colisoes.ponto_solido(x_frente, self.y + self.altura + 4)

    def mover_no_chao(self, dt, colisoes, velocidade, modo_borda="virar"):
        """Anda pelo chão. ``modo_borda``: ``"virar"``, ``"parar"`` ou ``"cair"``."""
        self.espelhado = self.direcao < 0
        passo = self.direcao * velocidade * dt
        if self.no_chao and velocidade > 0 and modo_borda != "cair" and self._borda_a_frente(colisoes):
            if modo_borda == "virar":
                self.direcao = -self.direcao
            passo = 0.0
        if colisoes.mover_horizontal(self, passo):
            if modo_borda != "parar":
                self.direcao = -self.direcao
        self.vy = min(self.vy + GRAVIDADE_INIMIGO * dt, 900.0)
        no_chao, _, _ = colisoes.mover_vertical(self, self.vy * dt, usar_plataformas=False)
        if no_chao:
            self.vy = 0.0
        self.no_chao = no_chao


class CriaturaDeNeve(Inimigo):
    """Monstrinho de neve compactada: anda de um lado para o outro e vira na borda.

    Personalidade: ao notar o Tux à frente (perto e no mesmo nível) ele se anima e acelera.
    """

    nome = "criatura_de_neve"
    pasta = "inimigos/criatura_de_neve"
    velocidade = 70.0

    def comportamento(self, dt, colisoes, jogador):
        velocidade = self.velocidade
        distancia = jogador.centro_x - self.centro_x
        if (jogador.vivo and abs(distancia) < 230 and abs(jogador.centro_y - self.centro_y) < 90
                and distancia * self.direcao > 0):
            velocidade *= 1.5
            self.animador.velocidade = 1.5
        else:
            self.animador.velocidade = 1.0
        self.mover_no_chao(dt, colisoes, velocidade, "virar")


class PinguimSelvagem(Inimigo):
    """Pinguim agressivo: persegue o jogador e aguenta DOIS golpes.

    O primeiro golpe (pisão, ataque ou dash) o atordoa e o deixa furioso (mais rápido);
    o segundo o derrota. O Cristal Mágico o derrota de uma vez.
    """

    nome = "pinguim_selvagem"
    pasta = "inimigos/pinguim_selvagem"
    velocidade = 60.0

    def __init__(self, centro_x, y_base, recursos, opcoes=None):
        super().__init__(centro_x, y_base, recursos, opcoes)
        self.vida = 2
        self.furioso = False
        self.tempo_atordoado = 0.0
        self.alcance = 440.0
        self.perseguindo = False

    @property
    def perigoso(self):
        return self.estado == "vivo" and self.tempo_atordoado <= 0

    def _ferir(self):
        self.vida -= 1
        if self.vida <= 0:
            return "morto"
        self.tempo_atordoado = 0.8
        self.animador.tocar("atordoado", reiniciar=True)
        return "ferido"

    def ser_pisado(self):
        if self._ferir() == "morto":
            self._esmagar()
            return "morto"
        return "ferido"

    def ser_atingido(self, origem_x=None):
        if self.tempo_atordoado > 0:
            return "imune"
        if self._ferir() == "morto":
            self.ser_derrotado(origem_x)
            return "morto"
        return "ferido"

    def comportamento(self, dt, colisoes, jogador):
        if self.tempo_atordoado > 0:
            self.tempo_atordoado -= dt
            self.mover_no_chao(dt, colisoes, 0.0, "parar")
            if self.tempo_atordoado <= 0:
                self.furioso = True
            return
        self.animador.tocar("furioso" if self.furioso else "andando")
        distancia = jogador.centro_x - self.centro_x
        if abs(distancia) < self.alcance and abs(jogador.centro_y - self.centro_y) < 170 and jogador.vivo:
            if not self.perseguindo:
                self.perseguindo = True
                self.eventos.append("pinguim_grito")
            self.direcao = 1 if distancia > 0 else -1
            velocidade = 250.0 if self.furioso else 150.0
            self.mover_no_chao(dt, colisoes, velocidade if abs(distancia) > 6 else 0.0, "parar")
        else:
            self.perseguindo = False
            # patrulha perto do ponto de origem
            if self.centro_x > self.x_origem + 144:
                self.direcao = -1
            elif self.centro_x < self.x_origem - 144:
                self.direcao = 1
            self.mover_no_chao(dt, colisoes, self.velocidade * (1.6 if self.furioso else 1.0), "virar")


class MorcegoGlacial(Inimigo):
    """Morcego das cavernas: patrulha uma região no ar e solta estilhaços de gelo.

    Opção do mapa ``{"mergulha": true}``: quando o Tux passa por baixo, o morcego mergulha
    em sua direção e depois volta à rota de patrulha.
    """

    nome = "morcego_glacial"
    pasta = "inimigos/morcego_glacial"
    animacao_inicial = "voando"

    def __init__(self, centro_x, y_base, recursos, opcoes=None):
        super().__init__(centro_x, y_base, recursos, opcoes)
        self.y0 = self.y
        self.raio_x = float(self.opcoes.get("raio", 170.0))
        self.velocidade_angular = 0.9
        self.tempo = (centro_x % 13) * 0.3
        self.tempo_tiro = 1.6
        self.mergulha = bool(self.opcoes.get("mergulha", False))
        self.atira = bool(self.opcoes.get("atira", True))
        self.modo = "patrulha"
        self.tempo_modo = 0.0
        self.alvo = (self.x, self.y)
        self.recarga_mergulho = 1.5

    def _posicao_de_patrulha(self):
        x = self.x_origem - self.largura / 2 + self.raio_x * math.sin(self.tempo * self.velocidade_angular)
        y = self.y0 + 34.0 * math.sin(self.tempo * 2.4)
        return x, y

    def comportamento(self, dt, colisoes, jogador):
        self.tempo += dt
        self.recarga_mergulho = max(0.0, self.recarga_mergulho - dt)
        if self.modo == "patrulha":
            novo_x, novo_y = self._posicao_de_patrulha()
            self.espelhado = (novo_x - self.x) < 0
            self.x, self.y = novo_x, novo_y
            self.tempo_tiro -= dt
            if (self.atira and self.tempo_tiro <= 0 and abs(jogador.centro_x - self.centro_x) < 330
                    and jogador.centro_y > self.centro_y and jogador.vivo):
                self.pedido_tiro = True
                self.tempo_tiro = 2.8
                self.eventos.append("morcego")
            if (self.mergulha and self.recarga_mergulho <= 0 and jogador.vivo
                    and abs(jogador.centro_x - self.centro_x) < 150
                    and 60 < jogador.centro_y - self.centro_y < 340):
                self.modo, self.tempo_modo = "mergulho", 0.0
                self.alvo = (jogador.centro_x - self.largura / 2, jogador.base - self.altura)
                self.eventos.append("morcego")
        elif self.modo == "mergulho":
            self.tempo_modo += dt
            self._ir_para(self.alvo, 430.0, dt)
            if self.tempo_modo > 0.8 or math.hypot(self.x - self.alvo[0], self.y - self.alvo[1]) < 10:
                self.modo, self.tempo_modo = "retorno", 0.0
        else:  # retorno
            self.tempo_modo += dt
            alvo = self._posicao_de_patrulha()
            self._ir_para(alvo, 260.0, dt)
            if math.hypot(self.x - alvo[0], self.y - alvo[1]) < 14 or self.tempo_modo > 2.0:
                self.modo = "patrulha"
                self.recarga_mergulho = 2.4

    def _ir_para(self, alvo, velocidade, dt):
        dx, dy = alvo[0] - self.x, alvo[1] - self.y
        distancia = math.hypot(dx, dy)
        if distancia > 1e-3:
            passo = min(distancia, velocidade * dt)
            self.x += dx / distancia * passo
            self.y += dy / distancia * passo
        if abs(dx) > 2:
            self.espelhado = dx < 0


class GolemDeGelo(Inimigo):
    """Golem imponente: lento, aguenta TRÊS golpes e fica furioso quando só resta uma vida.

    Ele atordoa por um instante a cada ferimento (aproveite para fugir ou golpear de novo).
    Cada passo faz o chão tremer um pouco.
    """

    nome = "golem_de_gelo"
    pasta = "inimigos/golem_de_gelo"
    velocidade = 45.0
    pontos = 300

    def __init__(self, centro_x, y_base, recursos, opcoes=None):
        super().__init__(centro_x, y_base, recursos, opcoes)
        self.vida = 3
        self.tempo_atordoado = 0.0
        self.tempo_imune = 0.0
        self.tempo_passo = 0.0
        self.alcance = 380.0

    @property
    def furioso(self):
        return self.vida <= 1

    @property
    def perigoso(self):
        return self.estado == "vivo" and self.tempo_atordoado <= 0

    def _ferir(self):
        self.vida -= 1
        self.tempo_imune = 0.5
        self.eventos.append("golem_dano")
        if self.vida <= 0:
            return "morto"
        self.tempo_atordoado = 0.9
        self.animador.tocar("dano", reiniciar=True)
        return "ferido"

    def ser_pisado(self):
        if self.tempo_imune > 0:
            return "ferido"
        if self._ferir() == "morto":
            self._esmagar()
            return "morto"
        return "ferido"

    def ser_atingido(self, origem_x=None):
        if self.tempo_imune > 0 or self.tempo_atordoado > 0:
            return "imune"
        if self._ferir() == "morto":
            self.ser_derrotado(origem_x)
            return "morto"
        return "ferido"

    def comportamento(self, dt, colisoes, jogador):
        self.tempo_imune = max(0.0, self.tempo_imune - dt)
        if self.tempo_atordoado > 0:
            self.tempo_atordoado -= dt
            self.mover_no_chao(dt, colisoes, 0.0, "parar")
            return
        self.animador.tocar("furioso" if self.furioso else "andando")
        distancia = jogador.centro_x - self.centro_x
        alerta = abs(distancia) < self.alcance and abs(jogador.centro_y - self.centro_y) < 120 and jogador.vivo
        if alerta and (self.furioso or abs(distancia) < 260):
            self.direcao = 1 if distancia > 0 else -1
            velocidade = 150.0 if self.furioso else 85.0
            self.mover_no_chao(dt, colisoes, velocidade if abs(distancia) > 10 else 0.0, "virar")
        else:
            if self.centro_x > self.x_origem + 120:
                self.direcao = -1
            elif self.centro_x < self.x_origem - 120:
                self.direcao = 1
            self.mover_no_chao(dt, colisoes, self.velocidade, "virar")
        self.tempo_passo -= dt
        if self.no_chao and self.tempo_passo <= 0:
            self.tempo_passo = 0.55 if self.furioso else 0.85
            self.eventos.append("golem_passo")


TIPOS_DE_INIMIGO = {
    "criatura_de_neve": CriaturaDeNeve,
    "pinguim_selvagem": PinguimSelvagem,
    "morcego_glacial": MorcegoGlacial,
    "golem_de_gelo": GolemDeGelo,
}


def criar_inimigo(tipo, centro_x, y_base, recursos, opcoes=None):
    """Cria um inimigo pelo nome usado na legenda do mapa."""
    classe = TIPOS_DE_INIMIGO.get(tipo)
    if classe is None:
        raise ValueError(f"Tipo de inimigo desconhecido: '{tipo}'. Disponíveis: {', '.join(TIPOS_DE_INIMIGO)}")
    return classe(centro_x, y_base, recursos, opcoes)
