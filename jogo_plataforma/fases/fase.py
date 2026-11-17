"""A fase: carrega o mapa JSON e simula todo o mundo do jogo.

A ``Fase`` NÃO cuida de menus, HUD ou transições (isso é papel das cenas).
Ela guarda e atualiza: blocos, jogador, inimigos, moedas, itens, checkpoints,
plataformas móveis, projéteis, efeitos e a sequência final.

Formato do mapa (``fases/mapas/<nome>.json``): veja o README, seção
"Como modificar o mapa".
"""
import json
import math
from pathlib import Path

import pygame

from configuracoes import ALTURA_BASE, LARGURA_BASE, TAMANHO_BLOCO as T, registrar_aviso
from entidades.blocos import Bloco, MapaDeBlocos, Tileset
from entidades.efeitos import EfeitoAnimado, Fragmento, MoedaDeBloco, TextoFlutuante
from entidades.inimigo import criar_inimigo
from entidades.jogador import Jogador
from entidades.objetos import (
    RECOMPENSAS, Castelo, Checkpoint, CogumeloVida, Decoracao, Estrela, MastroFinal, Moeda,
    PlataformaMovel, Princesa, Projetil,
)
from fases.sequencia_final import SequenciaFinal
from sistemas.camera import Camera
from sistemas.cenario import Cenario
from sistemas.colisoes import SistemaDeColisoes

PASTA_MAPAS = Path(__file__).resolve().parent / "mapas"
MOEDAS_POR_BLOCO = 3


class ErroDeFase(Exception):
    """Mapa ausente ou inválido (a mensagem explica o problema em português)."""


class Fase:
    """Mundo jogável carregado de um mapa JSON."""

    def __init__(self, recursos, audio, pontuacao, nome_do_mapa="fase_01", ao_checkpoint=None):
        self.recursos = recursos
        self.audio = audio
        self.pontuacao = pontuacao
        self.nome_do_mapa = nome_do_mapa
        self.ao_checkpoint = ao_checkpoint
        self.dados = self._ler_mapa()
        self.nome = self.dados.get("nome", nome_do_mapa)
        self.relogio = 0.0
        self.checkpoint_atual = -1            # -1 = ponto de partida
        self.final = None                     # SequenciaFinal quando o jogador toca o mastro
        self.efeitos = []
        self.projeteis = []
        self.itens = []
        self.golpes_restantes = {}
        self._construir_mundo()

    # ------------------------------------------------------------------ carregamento
    def _ler_mapa(self):
        caminho = PASTA_MAPAS / f"{self.nome_do_mapa}.json"
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            raise ErroDeFase(f"O mapa '{caminho}' não foi encontrado. "
                             "Rode 'python ferramentas/gerar_fase_01.py' para recriá-lo.")
        except (OSError, ValueError) as erro:
            raise ErroDeFase(f"O mapa '{caminho}' é inválido: {erro}")
        grade = dados.get("grade")
        if not isinstance(grade, list) or not grade or not all(isinstance(l, str) for l in grade):
            raise ErroDeFase(f"O mapa '{caminho}' precisa de uma 'grade' (lista de textos).")
        if len({len(linha) for linha in grade}) != 1:
            raise ErroDeFase(f"Todas as linhas da grade de '{caminho}' devem ter o mesmo tamanho.")
        if not isinstance(dados.get("legenda"), dict):
            raise ErroDeFase(f"O mapa '{caminho}' precisa de uma 'legenda'.")
        return dados

    def _construir_mundo(self):
        r = self.recursos
        grade = self.dados["grade"]
        legenda = self.dados["legenda"]
        linhas, colunas = len(grade), len(grade[0])
        self.mapa = MapaDeBlocos(colunas, linhas, Tileset(r.folha(self.dados.get("tileset", "blocos/tileset"))))
        self.moedas, self.inimigos, self.checkpoints = [], [], []
        self.mastro = self.castelo = self.princesa = None
        self.ponto_inicial = (2 * T + T / 2, 13 * T)
        desconhecidos = set()
        for linha, texto in enumerate(grade):
            for coluna, caractere in enumerate(texto):
                if caractere == " ":
                    continue
                definicao = legenda.get(caractere)
                if definicao is None:
                    desconhecidos.add(caractere)
                    continue
                self._criar_elemento(definicao, coluna, linha)
        if desconhecidos:
            registrar_aviso(f"Caracteres sem legenda no mapa foram ignorados: {sorted(desconhecidos)}")
        self.checkpoints.sort(key=lambda c: c.x)
        for indice, ponto in enumerate(self.checkpoints):
            ponto.indice = indice
        self.plataformas = [PlataformaMovel(d, r) for d in self.dados.get("plataformas_moveis", [])]
        self.decoracoes = []
        for d in self.dados.get("decoracoes", []):
            try:
                self.decoracoes.append(Decoracao(d, r))
            except (KeyError, TypeError) as erro:
                registrar_aviso(f"Decoração inválida ignorada ({erro}).")
        self.colisoes = SistemaDeColisoes(self.mapa, self.plataformas)
        self.camera = Camera(LARGURA_BASE, ALTURA_BASE, self.mapa.largura_pixels, self.mapa.altura_pixels)
        self.temas = self.dados.get("temas", {})
        self.zonas = sorted(self.dados.get("zonas", []), key=lambda z: z.get("coluna_inicio", 0))
        if not self.temas or not self.zonas:
            raise ErroDeFase("O mapa precisa definir 'temas' e 'zonas' (cenário de fundo).")
        self.cenario = Cenario(r, self.temas, self.zonas[0]["tema"])
        self.jogador = Jogador(self.ponto_inicial[0], self.ponto_inicial[1], r)
        self.renascer(primeira_vez=True)

    def _criar_elemento(self, definicao, coluna, linha):
        r = self.recursos
        tipo = definicao.get("tipo")
        centro_x = coluna * T + T / 2
        base = (linha + 1) * T
        if tipo == "bloco":
            self.mapa.definir(coluna, linha, Bloco(coluna, linha, definicao))
        elif tipo == "moeda":
            self.moedas.append(Moeda(centro_x, linha * T + T / 2, r))
        elif tipo == "inimigo":
            try:
                self.inimigos.append(criar_inimigo(definicao["inimigo"], centro_x, base, r))
            except (ValueError, KeyError) as erro:
                registrar_aviso(f"Inimigo inválido em ({coluna},{linha}): {erro}")
        elif tipo == "checkpoint":
            self.checkpoints.append(Checkpoint(centro_x, base, r, len(self.checkpoints)))
        elif tipo == "inicio":
            self.ponto_inicial = (centro_x, base)
        elif tipo == "mastro":
            self.mastro = MastroFinal(centro_x, base, r)
        elif tipo == "princesa":
            self.princesa = Princesa(centro_x, base, r)
        elif tipo == "castelo":
            self.castelo = Castelo(coluna * T, base, r)
        else:
            registrar_aviso(f"Tipo de elemento desconhecido na legenda: '{tipo}'.")

    # ------------------------------------------------------------------ estado
    @property
    def jogador_morto(self):
        return not self.jogador.vivo

    @property
    def concluida(self):
        return self.final is not None and self.final.concluida

    @property
    def progresso(self):
        """Fração (0..1) do caminho percorrido."""
        return max(0.0, min(1.0, self.jogador.centro_x / max(1, self.mapa.largura_pixels)))

    @property
    def ponto_de_retorno(self):
        if 0 <= self.checkpoint_atual < len(self.checkpoints):
            return self.checkpoints[self.checkpoint_atual].ponto_de_retorno
        return self.ponto_inicial

    def tema_na_coluna(self, coluna):
        tema = self.zonas[0]["tema"]
        for zona in self.zonas:
            if coluna >= zona.get("coluna_inicio", 0):
                tema = zona["tema"]
        return tema

    def musica_atual_do_tema(self):
        return self.temas.get(self.cenario.tema_atual, {}).get("musica")

    def renascer(self, primeira_vez=False):
        """(Re)coloca o jogador no último checkpoint (ou no início) e limpa o que for temporário."""
        self.projeteis.clear()
        self.itens.clear()
        self.final = None
        cx, base = self.ponto_de_retorno
        if primeira_vez:
            self.jogador.reaparecer(cx, base, invulneravel=0.0)
        else:
            self.jogador.reaparecer(cx, base)
        self.camera.centralizar_em(cx)
        self.cenario.definir_tema(self.tema_na_coluna(int(cx // T)), instantaneo=True)
        self.cenario.tema_anterior = None

    def restaurar_checkpoint(self, indice):
        """Retoma a partir de um checkpoint salvo. Devolve ``False`` se o índice for inválido."""
        if not 0 <= indice < len(self.checkpoints):
            return False
        for ponto in self.checkpoints[:indice + 1]:
            ponto.ativar()
        self.checkpoint_atual = indice
        limite = self.checkpoints[indice].x
        self.moedas = [m for m in self.moedas if m.x > limite]
        self.inimigos = [e for e in self.inimigos if e.x > limite]
        self.renascer()
        return True

    def matar_jogador(self):
        """Inicia a morte do jogador (a perda da vida é feita por quem chama)."""
        if self.jogador.vivo:
            self.jogador.morrer()
            self.audio.parar_musica()
            self.audio.tocar_efeito("derrota")

    def perder_vida_fatal(self):
        self.pontuacao.perder_vida()
        self.pontuacao.mortes += 1
        self.matar_jogador()

    def pedir_pulo(self):
        if self.final is None:
            self.jogador.pedir_pulo()

    # ------------------------------------------------------------------ atualização
    def atualizar(self, dt, entrada):
        """Avança a simulação. ``entrada``: dict com esquerda, direita, pular, correr."""
        self.relogio += dt
        self._pulo_segurado = bool(entrada.get("pular"))
        self.cenario.atualizar(dt)
        self.mapa.atualizar(dt)
        for plataforma in self.plataformas:
            plataforma.atualizar(dt)
        for moeda in self.moedas:
            moeda.atualizar(dt)
        for ponto in self.checkpoints:
            ponto.atualizar(dt)
        for decoracao in self.decoracoes:
            decoracao.atualizar(dt)
        if self.mastro:
            self.mastro.atualizar(dt)
        if self.princesa:
            self.princesa.atualizar(dt)

        if self.final is not None:
            self.final.atualizar(dt)
        else:
            self._atualizar_jogador(dt, entrada)
            if self.jogador.vivo:
                self._atualizar_itens(dt)
                self._atualizar_inimigos(dt)
                self._atualizar_projeteis(dt)
                self._verificar_perigos()
                self._verificar_mastro()
        self._limitar_jogador()
        self.camera.seguir(self.jogador.rect, dt)
        if self.jogador.vivo and self.final is None:
            self._atualizar_tema()
        for efeito in self.efeitos:
            efeito.atualizar(dt)
        self.efeitos = [e for e in self.efeitos if e.ativo]

    def _atualizar_jogador(self, dt, entrada):
        jogador = self.jogador
        jogador.atualizar(dt, entrada, self.colisoes)
        for evento in jogador.eventos:
            if evento == "pulo":
                self.audio.tocar_efeito("pulo")
        jogador.eventos.clear()
        if not jogador.vivo:
            return
        if jogador.bloco_cabeca is not None:
            self._bater_bloco(jogador.bloco_cabeca)
        self._coletar_moedas()
        self._verificar_checkpoints()
        if jogador.y > self.mapa.altura_pixels + 40:       # caiu em um buraco
            self.perder_vida_fatal()

    def _limitar_jogador(self):
        """Impede o jogador de sair pelas laterais do mundo."""
        jogador = self.jogador
        if not jogador.vivo:
            return
        minimo, maximo = 0.0, self.mapa.largura_pixels - jogador.largura
        if jogador.x < minimo:
            jogador.x, jogador.vx = minimo, 0.0
        elif jogador.x > maximo:
            jogador.x, jogador.vx = maximo, 0.0

    def _atualizar_tema(self):
        tema = self.tema_na_coluna(int(self.jogador.centro_x // T))
        if self.cenario.definir_tema(tema):
            musica = self.temas.get(tema, {}).get("musica")
            if musica:
                self.audio.tocar_musica(musica)

    # ------------------------------------------------------------------ blocos
    def _bater_bloco(self, bloco):
        """O jogador bateu com a cabeça em ``bloco``."""
        self.mapa.impactar(bloco)
        self._derrotar_inimigos_sobre(bloco)
        centro_x = bloco.x + T / 2
        if bloco.recompensa == "moeda" and not bloco.usado:
            chave = (bloco.coluna, bloco.linha)
            restantes = self.golpes_restantes.get(chave, MOEDAS_POR_BLOCO) - 1
            self.golpes_restantes[chave] = restantes
            self.efeitos.append(MoedaDeBloco(self.recursos.folha("objetos/moeda"), centro_x, bloco.y))
            self.audio.tocar_efeito("moeda")
            if self.pontuacao.coletar_moeda():
                self.audio.tocar_efeito("vida_extra")
            if restantes <= 0:
                self._esgotar_bloco(bloco)
        elif bloco.recompensa in RECOMPENSAS and not bloco.usado:
            self.itens.append(RECOMPENSAS[bloco.recompensa](bloco, self.recursos))
            self.audio.tocar_efeito("item_surge")
            self._esgotar_bloco(bloco)
        elif bloco.quebravel:
            self._quebrar_bloco(bloco)
        else:
            self.audio.tocar_efeito("bloco_bater")

    def _esgotar_bloco(self, bloco):
        bloco.usado = True
        bloco.recompensa = None
        bloco.sprite = "bloco_usado"

    def _quebrar_bloco(self, bloco):
        self.audio.tocar_efeito("bloco_quebrar")
        imagem = self.recursos.folha("efeitos/fragmento").obter("parado").quadros[0]
        for dx, dy, vx, vy in ((8, 8, -170, -520), (T - 8, 8, 170, -520), (8, T - 8, -120, -330), (T - 8, T - 8, 120, -330)):
            self.efeitos.append(Fragmento(bloco.x + dx, bloco.y + dy, vx, vy, imagem, self.mapa.altura_pixels))
        self.mapa.remover(bloco.coluna, bloco.linha)

    def _derrotar_inimigos_sobre(self, bloco):
        """Inimigos que estavam em cima do bloco atingido são arremessados."""
        for inimigo in self.inimigos:
            if inimigo.estado != "vivo":
                continue
            sobre = abs(inimigo.base - bloco.y) <= 8
            alinhado = inimigo.x < bloco.x + T and inimigo.x + inimigo.largura > bloco.x
            if sobre and alinhado:
                inimigo.ser_derrotado(origem_x=self.jogador.centro_x)
                self._pontuar_inimigo(inimigo)

    # ------------------------------------------------------------------ coletáveis
    def _coletar_moedas(self):
        area = self.jogador.rect
        restantes = []
        for moeda in self.moedas:
            if moeda.rect.colliderect(area):
                self.audio.tocar_efeito("moeda")
                if self.pontuacao.coletar_moeda():
                    self.audio.tocar_efeito("vida_extra")
                    self._texto(moeda.centro_x, moeda.y, "1UP", (140, 255, 160))
                self.efeitos.append(EfeitoAnimado(self.recursos.folha("efeitos/brilho"), "brilho",
                                                  moeda.centro_x, moeda.centro_y))
            else:
                restantes.append(moeda)
        self.moedas = restantes

    def _atualizar_itens(self, dt):
        area = self.jogador.rect
        for item in self.itens:
            item.atualizar(dt, self.colisoes)
            if item.ativo and not item.emergindo and item.rect.colliderect(area):
                item.ativo = False
                if isinstance(item, CogumeloVida):
                    self.pontuacao.ganhar_vida()
                    self.audio.tocar_efeito("vida_extra")
                    self._texto(item.centro_x, item.y, "1UP", (140, 255, 160))
                elif isinstance(item, Estrela):
                    self.jogador.ativar_estrela()
                    self.audio.tocar_efeito("estrela")
                    self._texto(item.centro_x, item.y, "ESTRELA!", (255, 230, 90))
        self.itens = [i for i in self.itens if i.ativo]

    def _verificar_checkpoints(self):
        area = self.jogador.rect
        for ponto in self.checkpoints:
            if not ponto.ativado and ponto.rect.colliderect(area):
                ponto.ativar()
                self.checkpoint_atual = ponto.indice
                self.audio.tocar_efeito("checkpoint")
                self._texto(ponto.centro_x, ponto.y, "CHECKPOINT", (255, 230, 90), 26)
                if self.ao_checkpoint:
                    self.ao_checkpoint(ponto.indice)

    # ------------------------------------------------------------------ inimigos e perigos
    def _atualizar_inimigos(self, dt):
        jogador = self.jogador
        for inimigo in self.inimigos:
            if inimigo.estado == "vivo" and not self.camera.visivel(inimigo.rect, 320):
                continue                                    # inimigos distantes "dormem"
            inimigo.atualizar(dt, self.colisoes, jogador)
            if inimigo.pedido_tiro:
                inimigo.pedido_tiro = False
                sentido = 1 if jogador.centro_x > inimigo.centro_x else -1
                self.projeteis.append(Projetil(inimigo.centro_x, inimigo.base, self.recursos, vx=70.0 * sentido))
                self.audio.tocar_efeito("projetil")
            if not inimigo.ativo or inimigo.estado == "arremessado":
                continue
            self._interagir(inimigo)
        self.inimigos = [e for e in self.inimigos if e.ativo]

    def _interagir(self, inimigo):
        jogador = self.jogador
        if not jogador.vivo or not inimigo.rect.colliderect(jogador.rect):
            return
        if inimigo.estado != "vivo":
            return
        if jogador.com_estrela:
            inimigo.ser_derrotado(origem_x=jogador.centro_x)
            self._pontuar_inimigo(inimigo)
            self.audio.tocar_efeito("esmagar")
            return
        pisando = jogador.vy > 0 and jogador.base - inimigo.y <= 34
        if pisando and inimigo.pisavel:
            resultado = inimigo.ser_pisado()
            jogador.quicar(self._pulo_segurado)
            self.audio.tocar_efeito("esmagar")
            self.efeitos.append(EfeitoAnimado(self.recursos.folha("efeitos/nuvem_poeira"), "explosao",
                                              inimigo.centro_x, inimigo.base - 10))
            if resultado == "morto":
                self._pontuar_inimigo(inimigo)
        elif inimigo.perigoso:
            self._machucar(inimigo.centro_x)

    _pulo_segurado = False       # atualizado pela cena a cada quadro (altura do quique)

    def _pontuar_inimigo(self, inimigo):
        pontos = self.pontuacao.derrotar_inimigo()
        self._texto(inimigo.centro_x, inimigo.y, f"+{pontos}", (255, 255, 255))

    def _atualizar_projeteis(self, dt):
        area = self.jogador.rect
        for projetil in self.projeteis:
            projetil.atualizar(dt, self.colisoes)
            if projetil.ativo and projetil.rect.colliderect(area):
                if self._machucar(projetil.centro_x):
                    projetil.ativo = False
        self.projeteis = [p for p in self.projeteis if p.ativo]

    def _machucar(self, origem_x):
        """Dano normal: custa uma vida, com knockback e invulnerabilidade temporária."""
        jogador = self.jogador
        if not jogador.receber_dano(origem_x):
            return False
        self.pontuacao.perder_vida()
        self.camera.tremer(7.0, 0.3)
        if self.pontuacao.vidas <= 0:
            self.pontuacao.mortes += 1
            self.matar_jogador()
        else:
            self.audio.tocar_efeito("dano")
        return True

    def _verificar_perigos(self):
        jogador = self.jogador
        perigo = self.colisoes.perigo_em(jogador.rect.inflate(-8, -6))
        if perigo == "morte":
            self.perder_vida_fatal()
        elif perigo == "dano":
            sentido = -1 if jogador.espelhado else 1
            self._machucar(jogador.centro_x + sentido)

    def _verificar_mastro(self):
        if self.mastro and self.jogador.rect.colliderect(self.mastro.rect.inflate(10, 0)):
            self.final = SequenciaFinal(self)

    def _texto(self, x, y, texto, cor=(255, 255, 255), tamanho=24):
        self.efeitos.append(TextoFlutuante(x, y, texto, cor, tamanho))

    # ------------------------------------------------------------------ desenho
    def desenhar(self, tela):
        camera = self.camera
        self.cenario.desenhar(tela, camera.x)
        for decoracao in self.decoracoes:
            if camera.visivel(pygame.Rect(decoracao.x, decoracao.y, decoracao.largura, 10), 200):
                decoracao.desenhar(tela, camera)
        if self.castelo:
            self.castelo.desenhar(tela, camera)
        self.mapa.desenhar(tela, camera)
        for plataforma in self.plataformas:
            if camera.visivel(plataforma.rect):
                plataforma.desenhar(tela, camera)
        for ponto in self.checkpoints:
            ponto.desenhar(tela, camera)
        if self.mastro:
            self.mastro.desenhar(tela, camera)
        if self.princesa:
            self.princesa.desenhar(tela, camera)
        for moeda in self.moedas:
            if camera.visivel(moeda.rect):
                moeda.desenhar(tela, camera)
        for item in self.itens:
            item.desenhar(tela, camera)
        for inimigo in self.inimigos:
            if not camera.visivel(inimigo.rect, 100):
                continue
            if inimigo.estado == "arremessado":
                imagem = pygame.transform.flip(inimigo.animador.imagem(inimigo.espelhado), False, True)
                inimigo.desenhar(tela, camera, imagem)
            else:
                inimigo.desenhar(tela, camera)
        for projetil in self.projeteis:
            projetil.desenhar(tela, camera)
        self.jogador.desenhar(tela, camera)
        for efeito in self.efeitos:
            efeito.desenhar(tela, camera)
