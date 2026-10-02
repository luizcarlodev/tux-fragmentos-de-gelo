import pygame

import config
import utils
import map as mapa_modulo
import background
from ui import UI
from player import Player
from enemy import Golem
from projetil import Projetil, CristalGelo


class Jogo:
    """Uma partida inteira: câmera, colisões, combate, void, HUD e vitória/derrota."""

    def __init__(self, tela):
        self.tela = tela
        self.clock = pygame.time.Clock()
        self.ui = UI(tela)

        self._montar_partida()

    def _montar_partida(self):
        dados_mapa = mapa_modulo.criar_mapa_fase1()

        self.plataformas = dados_mapa["plataformas"]
        self.mini_golens = dados_mapa["mini_golens"]
        self.golem = dados_mapa["golem"]
        self.porta = dados_mapa["porta"]
        self.largura_mundo = dados_mapa["largura_mundo"]
        self.limite_direita = self.largura_mundo - config.MARGEM_DIREITA_MUNDO

        self.tux = Player(dados_mapa["x_spawn"], dados_mapa["y_spawn"], self.limite_direita)
        self.camera_x = 0

        self.x_checkpoint = dados_mapa["x_checkpoint"]
        self.y_checkpoint = dados_mapa["y_checkpoint"]
        self.checkpoint_ativado = False

        # parâmetros para recriar o golem ao voltar do checkpoint
        self._golem_params = (
            self.golem.x, self.golem.y,
            self.golem.arena_inicio, self.golem.arena_fim,
        )

        self.projeteis_tux = []
        self.projeteis_golem = []
        self.avisos_chuva = []

        self.fragmentos_coletados = 0
        self.arena_ativa = False

        self.fade_void_timer = 0
        self.resultado = None   # None | "vitoria" | "derrota"

    def reiniciar_do_checkpoint(self):
        """Tux com vida cheia e golem resetado. Mini golens e fragmentos continuam."""
        self.tux = Player(self.x_checkpoint, self.y_checkpoint, self.limite_direita)

        gx, gy, arena_inicio, arena_fim = self._golem_params
        self.golem = Golem(gx, gy, arena_inicio=arena_inicio, arena_fim=arena_fim)

        self.camera_x = max(0, self.x_checkpoint - config.LARGURA_TELA // 2)

        self.projeteis_tux = []
        self.projeteis_golem = []
        self.avisos_chuva = []

        self.arena_ativa = False
        self.fade_void_timer = 0
        self.resultado = None

    def executar(self):
        """Retorna 'vitoria', 'derrota', 'sair' ou 'menu_pausa'."""
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return "sair"

                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    escolha = self.ui.menu_pausa()

                    if escolha == "sair":
                        return "sair"
                    if escolha == "menu":
                        return "menu_pausa"

            self._atualizar()
            self._desenhar()

            pygame.display.update()
            self.clock.tick(config.FPS)

            if self.resultado == "derrota" and self.checkpoint_ativado:
                # morte depois do checkpoint: respawn em vez de Game Over
                self.reiniciar_do_checkpoint()
                self._desenhar()
                pygame.display.update()

                escolha = self.ui.menu_pausa(titulo="Você caiu!", texto_opcao_principal="Respawn")
                if escolha == "sair":
                    return "sair"
                if escolha == "menu":
                    return "menu_pausa"

            elif self.resultado:
                return self.resultado

    # Atualização
    def _atualizar(self):
        teclas = pygame.key.get_pressed()

        self._atualizar_movimento(teclas)
        self._atualizar_void()
        self._atualizar_ataque_tux(teclas)
        self._atualizar_mini_golens()
        self._atualizar_arena_boss()
        self.tux.atualizar_timers()

        if self.tux.esta_morto:
            self.resultado = "derrota"

    def _atualizar_movimento(self, teclas):
        self.tux.mover_player(teclas)
        self._colisao_horizontal_com_golem()
        self._colisao_com_porta()
        self.tux.pular(teclas, self.plataformas)

        if not self.checkpoint_ativado and self.tux.x >= self.x_checkpoint:
            self.checkpoint_ativado = True

        self.camera_x = self.tux.x - config.LARGURA_TELA // 2
        limite_camera = max(0, self.largura_mundo - config.LARGURA_TELA)
        self.camera_x = utils.limitar(self.camera_x, 0, limite_camera)

    def _colisao_horizontal_com_golem(self):
        """O golem vivo é sólido e causa dano com knockback forte ao encostar."""
        if self.golem.vida <= 0:
            return

        if not utils.checar_colisao(self.tux.rect, self.golem.rect):
            return

        houve_dano_agora = self.tux.sofrer_dano(self.golem.x, forca_knockback=config.GOLEM_KNOCKBACK_FORCA)

        if houve_dano_agora:
            return   # deixa o knockback empurrar o Tux neste frame

        if self.tux.x < self.golem.x:
            self.tux.x = self.golem.x - self.tux.largura
        else:
            self.tux.x = self.golem.x + self.golem.largura
        self.tux.rect.x = self.tux.x

    def _colisao_com_porta(self):
        """Trancada: parede sólida. Destrancada: encostar vence o jogo."""
        if not utils.checar_colisao(self.tux.rect, self.porta.rect):
            return

        if self.fragmentos_coletados >= config.FRAGMENTOS_NECESSARIOS_TOTAL:
            self.resultado = "vitoria"
            return

        if self.tux.x < self.porta.x:
            self.tux.x = self.porta.x - self.tux.largura
        else:
            self.tux.x = self.porta.x + self.porta.largura
        self.tux.rect.x = self.tux.x

    def _atualizar_void(self):
        if self.tux.y > config.ALTURA_TELA:
            self.tux.cair_no_void()
            self.fade_void_timer = config.VOID_FADE_ENTRADA_DURACAO
        elif self.fade_void_timer > 0:
            self.fade_void_timer -= 1

    def _atualizar_ataque_tux(self, teclas):
        novo_projetil = self.tux.atacar(teclas)
        if novo_projetil:
            self.projeteis_tux.append(novo_projetil)

        for projetil in self.projeteis_tux[:]:
            projetil.atualizar()
            atingiu = False

            for mini_golem in self.mini_golens:
                if mini_golem.vida > 0 and utils.checar_colisao(projetil.rect, mini_golem.rect):
                    mini_golem.receber_dano(config.PROJETIL_DANO)
                    atingiu = True
                    if mini_golem.vida <= 0:
                        self.fragmentos_coletados += 1

            if self.golem.vida > 0 and utils.checar_colisao(projetil.rect, self.golem.rect):
                self.golem.receber_dano(config.PROJETIL_DANO)
                atingiu = True
                if self.golem.vida <= 0:
                    self.fragmentos_coletados += 1

            if atingiu or projetil.fora_da_tela(self.camera_x):
                self.projeteis_tux.remove(projetil)

    def _atualizar_mini_golens(self):
        for mini_golem in self.mini_golens:
            if mini_golem.vida <= 0 and not mini_golem.esta_morrendo():
                continue

            mini_golem.comportamento()

            if mini_golem.vida > 0 and utils.checar_colisao(self.tux.rect, mini_golem.rect):
                self.tux.sofrer_dano(mini_golem.x)

    def _atualizar_arena_boss(self):
        if self.golem.vida <= 0:
            return

        if not self.arena_ativa and self.tux.x >= self.golem.arena_inicio:
            self.arena_ativa = True

        if not self.arena_ativa:
            return

        self.golem.comportamento()

        projetil_pedra = self.golem.atacar_pedra(self.tux.x)
        if projetil_pedra:
            self.projeteis_golem.append(projetil_pedra)

        self.avisos_chuva.extend(self.golem.atacar_chuva())

        for aviso in self.avisos_chuva[:]:
            aviso.atualizar()
            if aviso.pronto():
                self.projeteis_golem.append(CristalGelo(aviso.x, 0))
                self.avisos_chuva.remove(aviso)

        for projetil in self.projeteis_golem[:]:
            projetil.atualizar()
            remover = False

            if utils.checar_colisao(projetil.rect, self.tux.rect):
                self.tux.sofrer_dano(projetil.x)
                remover = True
            elif isinstance(projetil, CristalGelo) and projetil.atingiu_chao():
                remover = True
            elif isinstance(projetil, Projetil) and projetil.fora_da_tela(self.camera_x):
                remover = True

            if remover:
                self.projeteis_golem.remove(projetil)

    # Desenho
    def _desenhar(self):
        background.desenhar(self.tela, self.camera_x)

        for plataforma in self.plataformas:
            plataforma.desenhar(self.tela, self.camera_x)

        for mini_golem in self.mini_golens:
            if mini_golem.vida > 0 or mini_golem.esta_morrendo():
                mini_golem.desenhar(self.tela, self.camera_x)

        if self.golem.vida > 0:
            self.golem.desenhar(self.tela, self.camera_x)

        destrancada = self.fragmentos_coletados >= config.FRAGMENTOS_NECESSARIOS_TOTAL
        self.porta.desenhar(self.tela, self.camera_x, destrancada=destrancada)

        for projetil in self.projeteis_tux:
            projetil.desenhar(self.tela, self.camera_x)

        for projetil in self.projeteis_golem:
            projetil.desenhar(self.tela, self.camera_x)

        for aviso in self.avisos_chuva:
            aviso.desenhar(self.tela, self.camera_x)

        self.tux.desenhar(self.tela, self.camera_x)

        self.ui.desenhar_hud(self.tux, self.fragmentos_coletados, config.FRAGMENTOS_NECESSARIOS_TOTAL)

        if self.arena_ativa and self.golem.vida > 0:
            self.ui.desenhar_barra_vida_golem(self.golem)

        if self.fade_void_timer > 0:
            self.ui.desenhar_fade_void(self.fade_void_timer)
