"""Sequência de conclusão de uma fase: coleta do Fragmento de Gelo → (chave mágica) → portal.

Etapas: ``pouso`` (o Tux termina o salto) → ``coleta`` (o fragmento sobe e brilha) →
[``chave``: os três fragmentos se fundem na Chave Mágica — só na fase 3] →
``portal`` (o portal se abre) → ``andando`` (o Tux caminha até ele) → ``entrando`` → ``concluida``.
"""
import math
import random

import pygame

from entidades.efeitos import criar_explosao_gelo, criar_fogos
from entidades.objetos import ChaveMagica
from sistemas.animacoes import Animador

DURACAO_COLETA = 2.4
DURACAO_CHAVE = 3.4
VOO_DA_CHAVE = 1.5


class SequenciaFragmento:
    """Roteiro automático executado quando o Tux toca o Fragmento de Gelo da fase."""

    def __init__(self, fase):
        self.fase = fase
        self.altar = fase.altar
        self.numero = self.altar.numero
        self.com_chave = fase.dados.get("final") == "chave"
        fase.pontuacao.contando_tempo = False
        fase.projeteis.clear()
        fase.audio.parar_musica()
        jogador = fase.jogador
        jogador.tempo_cristal = 0.0
        jogador.tempo_ataque = jogador.tempo_dash = 0.0
        self.estado = "pouso"
        self.tempo = 0.0
        self.proxima_faisca = 0.0
        self.chave = None
        self.fragmentos = []          # animadores dos 3 fragmentos orbitando (fase 3)
        self.centro_chave = (0.0, 0.0)
        self.concluida = False

    @staticmethod
    def _entrada_vazia():
        return {"esquerda": False, "direita": False, "pular": False, "correr": False}

    def atualizar(self, dt):
        metodo = getattr(self, f"_{self.estado}", None)
        if metodo:
            metodo(dt)

    def desenhar(self, tela, camera):
        if self.chave is not None:
            self.chave.desenhar(tela, camera)
        for angulo, raio, animador in self.fragmentos:
            imagem = animador.imagem()
            cx, cy = self.centro_chave
            sx, sy = camera.mundo_para_tela(cx + math.cos(angulo) * raio, cy + math.sin(angulo) * raio * 0.6)
            tela.blit(imagem, imagem.get_rect(center=(round(sx), round(sy))))

    # ------------------------------------------------------------------ etapas
    def _pouso(self, dt):
        fase = self.fase
        jogador = fase.jogador
        self.tempo += dt
        jogador.atualizar(dt, self._entrada_vazia(), fase.colisoes)
        jogador.eventos.clear()
        if (jogador.no_chao and abs(jogador.vx) < 25) or self.tempo > 1.4:
            jogador.vx = jogador.vy = 0.0
            jogador.congelado = True
            jogador.espelhado = False
            jogador.comemorar()
            self.estado, self.tempo = "coleta", 0.0
            self._iniciar_coleta()

    def _iniciar_coleta(self):
        fase, altar = self.fase, self.altar
        altar.coletado = True
        altar.ativar()
        fase.pontuacao.coletar_fragmento()
        fase.audio.tocar_efeito("fragmento")
        fase.audio.tocar_musica("conclusao", repetir=False)
        fase.flash = 0.9
        fase.camera.tremer(6.0, 0.5)
        cx, cy = altar.centro_do_fragmento
        fase._texto(cx, cy - 70, f"FRAGMENTO DE GELO {self.numero}/3", (150, 235, 255), 34)
        fase._texto(cx, cy - 30, "+1000", (255, 230, 120), 28)
        fase.efeitos.extend(criar_explosao_gelo(cx, cy, 30, [(210, 246, 255), (255, 255, 255), (170, 150, 246),
                                                             (255, 214, 96)]))

    def _coleta(self, dt):
        fase, altar, jogador = self.fase, self.altar, self.fase.jogador
        self.tempo += dt
        progresso = min(1.0, self.tempo / 1.6)
        altar.elevacao = 110 * progresso * progresso * (3 - 2 * progresso) + 8
        altar.escala_brilho = 1.0 + 0.6 * progresso
        jogador.animador.atualizar(dt)
        if self.tempo >= self.proxima_faisca:
            cx, cy = altar.centro_do_fragmento
            fase.efeitos.extend(criar_explosao_gelo(cx, cy, 4))
            self.proxima_faisca = self.tempo + 0.1
        if self.tempo >= DURACAO_COLETA:
            altar.coletado = True
            if self.com_chave:
                self._iniciar_chave()
            else:
                self.estado, self.tempo = "portal", 0.0
                self._abrir_portal()

    def _iniciar_chave(self):
        fase, altar = self.fase, self.altar
        self.estado, self.tempo = "chave", 0.0
        self.centro_chave = (altar.centro_x, altar.y - 130)
        folha = fase.recursos.folha("objetos/fragmento_de_gelo")
        self.fragmentos = []
        for n in (1, 2, 3):
            animador = Animador(folha, f"fragmento_{n}")
            self.fragmentos.append([n * 2.094, 120.0, animador])
        altar.elevacao = 0.0
        altar.coletado = True
        fase.audio.tocar_efeito("chave")
        fase._texto(altar.centro_x, altar.y - 190, "OS TRÊS FRAGMENTOS SE UNEM...", (255, 235, 160), 30)

    def _chave(self, dt):
        fase = self.fase
        self.tempo += dt
        fase.jogador.animador.atualizar(dt)
        orbita = min(1.0, self.tempo / 2.2)
        for item in self.fragmentos:
            item[0] += dt * (2.0 + 7.0 * orbita)
            item[1] = 120.0 * (1.0 - orbita * orbita)
            item[2].atualizar(dt)
        if self.chave is None and self.tempo >= 2.2:
            self.fragmentos = []
            self.chave = ChaveMagica(*self.centro_chave, fase.recursos)
            self.chave.escala = 0.5
            fase.flash = 1.0
            fase.camera.tremer(8.0, 0.6)
            fase.audio.tocar_efeito("chave")
            fase.efeitos.extend(criar_fogos(self.centro_chave[0], self.centro_chave[1], quantidade=30))
        if self.chave is not None:
            self.chave.atualizar(dt)
            crescimento = min(1.0, (self.tempo - 2.2) / 0.5)
            self.chave.escala = 0.5 + 1.1 * crescimento
        if self.tempo >= DURACAO_CHAVE + VOO_DA_CHAVE and self.chave is not None:
            self._abrir_portal()
            self.estado, self.tempo = "portal", 0.0
        elif self.chave is not None and self.tempo >= DURACAO_CHAVE:
            # a chave voa até o portão do castelo
            alvo = self.fase.portal
            t = (self.tempo - DURACAO_CHAVE) / VOO_DA_CHAVE
            t = t * t * (3 - 2 * t)
            origem = self.centro_chave
            destino = (alvo.centro_x, alvo.y + alvo.altura * 0.45) if alvo else origem
            self.chave.centro = (origem[0] + (destino[0] - origem[0]) * t, origem[1] + (destino[1] - origem[1]) * t)
            if random.random() < 0.5:
                fase.efeitos.extend(criar_explosao_gelo(*self.chave.centro, 2, [(255, 235, 160), (255, 255, 255)]))

    def _abrir_portal(self):
        fase = self.fase
        if fase.portal is not None:
            fase.portal.abrir()
            fase.audio.tocar_efeito("portal")
            fase.flash = max(fase.flash, 0.5)
        self.chave = None

    def _portal(self, dt):
        fase = self.fase
        self.tempo += dt
        fase.jogador.animador.atualizar(dt)
        if self.tempo >= 1.2:
            jogador = fase.jogador
            jogador.congelado = False
            jogador.espelhado = False
            self.estado, self.tempo = "andando", 0.0

    def _andando(self, dt):
        fase = self.fase
        jogador, portal = fase.jogador, fase.portal
        self.tempo += dt
        alvo = portal.centro_x if portal else jogador.centro_x + 200
        distancia = alvo - jogador.centro_x
        entrada = self._entrada_vazia()
        entrada["direita"] = distancia > 6
        entrada["esquerda"] = distancia < -6
        jogador.atualizar(dt, entrada, fase.colisoes)
        jogador.eventos.clear()
        if abs(distancia) <= 10 or self.tempo > 8.0:
            self.estado, self.tempo = "entrando", 0.0
            jogador.vx = 0.0
            fase.audio.tocar_efeito("portal")

    def _entrando(self, dt):
        fase = self.fase
        self.tempo += dt
        jogador = fase.jogador
        jogador.animador.atualizar(dt)
        if self.tempo > 0.15 and not jogador.oculto:
            jogador.oculto = True
            fase.efeitos.extend(criar_explosao_gelo(jogador.centro_x, jogador.centro_y, 24,
                                                    [(170, 230, 255), (255, 255, 255), (170, 150, 246)]))
        if self.tempo >= 1.0:
            self.estado = "concluida"
            self.concluida = True
