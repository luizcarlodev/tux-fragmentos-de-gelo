"""Tela de conclusão: pontuação final, estatísticas e o Fragmento de Gelo conquistado."""
import math

import pygame

from cenas.cena import Cena
from configuracoes import CORES, LARGURA_BASE, PONTOS_SEGREDO, TOTAL_DE_FASES
from fases.gerenciador_de_fases import INFORMACOES
from interface.botoes import MenuDeBotoes
from interface.efeitos_de_tela import Confetes, gradiente_vertical
from interface.hud import formatar_tempo
from interface.textos import desenhar_texto
from sistemas.neve import SistemaDeNeve


class TelaVitoria(Cena):
    """Revela, linha por linha, o cálculo da pontuação final.

    ``campanha=True`` é a versão exibida após o final do jogo (resgate da princesa).
    """

    INTERVALO = 0.5

    def __init__(self, aplicacao, numero_fase, resultado, novo_recorde=False, campanha=False):
        super().__init__(aplicacao)
        self.numero_fase = numero_fase
        self.resultado = resultado
        self.novo_recorde = novo_recorde
        self.campanha = campanha
        r = aplicacao.recursos
        self.fundo = gradiente_vertical((14, 28, 88), (78, 160, 216))
        self.neve = SistemaDeNeve(r, {"densidade": 90, "vento": -25}, semente=5)
        self.confetes = Confetes(80)
        self.tempo = 0.0
        self.icone = r.imagem(f"interface/icone_fragmento_{min(numero_fase, TOTAL_DE_FASES)}.png", 6)
        self.icone_pequeno = r.imagem("interface/icone_fragmento_1.png", 1)
        linhas = [
            ("Pontos coletados", str(resultado["pontos_coletados"])),
            ("Bônus de conclusão", f"+{resultado['bonus_conclusao']}"),
            (f"Bônus de tempo ({resultado['tempo_restante']}s)", f"+{resultado['bonus_tempo']}"),
            ("Cristais", str(resultado["moedas"])),
            ("Criaturas derrotadas", str(resultado["inimigos"])),
            ("Tempo de jogo", formatar_tempo(resultado["tempo_gasto"])),
            ("Vidas perdidas", str(resultado["mortes"])),
        ]
        if resultado.get("segredo"):
            linhas.append(("Segredo descoberto", f"+{PONTOS_SEGREDO}"))
        self.linhas = linhas
        itens = []
        if not campanha and numero_fase < TOTAL_DE_FASES:
            itens.append(("PRÓXIMA FASE", self.proxima_fase))
        itens.append(("REJOGAR", self.jogar_de_novo))
        itens.append(("FASES", self.selecionar_fase))
        itens.append(("MENU", self.ir_ao_menu))
        self.menu = MenuDeBotoes(aplicacao, itens, centro_x=640, y_inicial=650, espacamento=0, largura=270, altura=52)
        passo = 300
        for i, botao in enumerate(self.menu.botoes):
            botao.base.center = (640 + (i - (len(itens) - 1) / 2) * passo, 664)
        self.musica_checada = False

    # ---------------------------------------------------------------- ações
    def proxima_fase(self):
        from cenas.cena_jogo import CenaJogo
        self.app.cenas.trocar(CenaJogo(self.app, self.numero_fase + 1), "fade")

    def jogar_de_novo(self):
        from cenas.cena_jogo import CenaJogo
        self.app.cenas.trocar(CenaJogo(self.app, self.numero_fase), "fade")

    def selecionar_fase(self):
        from cenas.selecao_de_fases import SelecaoDeFases
        self.app.cenas.trocar(SelecaoDeFases(self.app), "fade")

    def ir_ao_menu(self):
        from cenas.menu_principal import MenuPrincipal
        self.app.cenas.trocar(MenuPrincipal(self.app), "fade")

    # ---------------------------------------------------------------- ciclo
    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_LEFT, pygame.K_a):
            self.menu.selecionar(self.menu.selecionado - 1)
        elif evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RIGHT, pygame.K_d):
            self.menu.selecionar(self.menu.selecionado + 1)
        else:
            self.menu.tratar_evento(evento)

    def atualizar(self, dt):
        self.tempo += dt
        self.neve.atualizar(dt)
        self.confetes.atualizar(dt)
        self.menu.atualizar(dt)
        if not self.musica_checada and self.tempo > 0.2:
            self.musica_checada = True
            if pygame.mixer.get_init() and not pygame.mixer.music.get_busy():
                self.app.audio.tocar_musica("menu")

    def desenhar(self, tela):
        tela.blit(self.fundo, (0, 0))
        self.neve.desenhar(tela)
        self.confetes.desenhar(tela)
        escala = 1.0 + 0.04 * math.sin(self.tempo * 3)
        titulo = "AVENTURA CONCLUÍDA!" if self.campanha else "FASE CONCLUÍDA!"
        desenhar_texto(tela, titulo, int(72 * escala), CORES["branco"], (LARGURA_BASE // 2, 56), contorno=True)
        desenhar_texto(tela, self._subtitulo(), 30, CORES["destaque"], (LARGURA_BASE // 2, 112))
        self._desenhar_fragmento(tela)
        painel = pygame.Surface((640, 440), pygame.SRCALPHA)
        pygame.draw.rect(painel, (8, 14, 46, 205), painel.get_rect(), border_radius=20)
        pygame.draw.rect(painel, (170, 230, 255, 220), painel.get_rect(), width=3, border_radius=20)
        tela.blit(painel, painel.get_rect(center=(LARGURA_BASE // 2 - 60, 366)))
        for i, (rotulo, valor) in enumerate(self.linhas):
            if self.tempo < 0.5 + i * self.INTERVALO:
                break
            y = 178 + i * 34
            desenhar_texto(tela, rotulo, 27, CORES["texto_suave"], (280, y), "esquerda", deslocamento=1)
            desenhar_texto(tela, valor, 29, CORES["texto"], (860, y), "direita", deslocamento=1)
        revelar_total = 0.5 + len(self.linhas) * self.INTERVALO
        if self.tempo >= revelar_total:
            cresc = min(1.0, (self.tempo - revelar_total) * 3)
            pygame.draw.line(tela, CORES["branco"], (280, 462), (860, 462), 2)
            desenhar_texto(tela, "TOTAL", int(38 * cresc) + 1, CORES["destaque"], (280, 497), "esquerda")
            desenhar_texto(tela, str(self.resultado["total"]), int(50 * cresc) + 1, CORES["destaque"],
                           (860, 497), "direita")
            if self.novo_recorde and int(self.tempo * 3) % 2 == 0:
                desenhar_texto(tela, "NOVO RECORDE!", 32, CORES["sucesso"], (580, 552))
            elif not self.novo_recorde:
                desenhar_texto(tela, f"Melhor: {self.app.salvamento.melhor_pontuacao}", 26,
                               CORES["texto_suave"], (580, 552))
            if self.campanha:
                desenhar_texto(tela, f"Pontuação da campanha: {self.app.salvamento.pontuacao_da_campanha}", 26,
                               CORES["titulo"], (580, 586))
            self.menu.desenhar(tela)

    def _subtitulo(self):
        if self.campanha:
            return "A Princesa do Gelo está a salvo e o Reino Glacial renasceu!"
        texto = f"Fragmento de Gelo {self.numero_fase}/{TOTAL_DE_FASES} conquistado!"
        if self.numero_fase < TOTAL_DE_FASES:
            proxima = INFORMACOES[self.numero_fase + 1]["nome"]
            texto += f"   Nova região liberada: {proxima}"
        return texto

    def _desenhar_fragmento(self, tela):
        """Fragmento conquistado, pulsando à direita do painel (ou os três, no final)."""
        pulso = math.sin(self.tempo * 3) * 6
        if self.campanha:
            for n in range(TOTAL_DE_FASES):
                icone = self.app.recursos.imagem(f"interface/icone_fragmento_{n + 1}.png", 4)
                tela.blit(icone, icone.get_rect(center=(1090, 230 + n * 100 + (pulso if n % 2 else -pulso))))
            return
        tela.blit(self.icone, self.icone.get_rect(center=(1090, 300 + pulso)))
        desenhar_texto(tela, f"FRAGMENTO {self.numero_fase}", 28, CORES["titulo"], (1090, 390), contorno=True)
        for n in range(1, TOTAL_DE_FASES + 1):
            tem = self.app.salvamento.fase_concluida(n)
            imagem = self.app.recursos.imagem(f"interface/icone_fragmento_{n}.png" if tem
                                              else "interface/icone_fragmento_vazio.png", 2)
            tela.blit(imagem, imagem.get_rect(center=(1030 + (n - 1) * 60, 440)))
