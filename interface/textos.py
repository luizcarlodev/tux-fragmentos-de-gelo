"""Utilitários para renderizar texto com fonte do projeto, sombra e contorno."""
import pygame

from configuracoes import PASTA_RECURSOS, registrar_aviso

ANCORAS = {
    "centro": "center", "esquerda": "midleft", "direita": "midright",
    "topo_esquerda": "topleft", "topo_direita": "topright", "topo_centro": "midtop",
    "base_centro": "midbottom",
}


class Fontes:
    """Cache de fontes por tamanho (usa ``recursos/fontes/fonte_principal.ttf`` se existir)."""

    _cache = {}
    _avisou = False

    @classmethod
    def obter(cls, tamanho):
        if tamanho not in cls._cache:
            caminho = PASTA_RECURSOS / "fontes" / "fonte_principal.ttf"
            try:
                cls._cache[tamanho] = pygame.font.Font(str(caminho), tamanho)
            except (FileNotFoundError, OSError, pygame.error):
                if not cls._avisou:
                    registrar_aviso("Fonte do projeto não encontrada; usando a fonte padrão do Pygame.")
                    cls._avisou = True
                cls._cache[tamanho] = pygame.font.Font(None, int(tamanho * 1.2))
        return cls._cache[tamanho]


def tamanho_para_caber(texto, tamanho, largura_maxima, minimo=14):
    """Reduz o tamanho da fonte até que ``texto`` caiba em ``largura_maxima`` pixels."""
    while tamanho > minimo and Fontes.obter(tamanho).size(texto)[0] > largura_maxima:
        tamanho -= 1
    return tamanho


_cache_textos = {}


def renderizar_texto(texto, tamanho, cor, sombra=(0, 0, 0), deslocamento=2, contorno=False):
    """Renderiza o texto em uma superfície (com cache) incluindo sombra ou contorno."""
    chave = (texto, tamanho, cor, sombra, deslocamento, contorno)
    superficie = _cache_textos.get(chave)
    if superficie is None:
        fonte = Fontes.obter(tamanho)
        base = fonte.render(texto, True, cor)
        if sombra is None:
            superficie = base
        else:
            sombreado = fonte.render(texto, True, sombra)
            margem = deslocamento + (2 if contorno else 0)
            superficie = pygame.Surface((base.get_width() + margem * 2, base.get_height() + margem * 2),
                                        pygame.SRCALPHA)
            if contorno:
                for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)):
                    superficie.blit(sombreado, (margem + dx, margem + dy))
            else:
                superficie.blit(sombreado, (margem + deslocamento, margem + deslocamento))
            superficie.blit(base, (margem, margem))
        if len(_cache_textos) > 800:
            _cache_textos.clear()
        _cache_textos[chave] = superficie
    return superficie


def desenhar_texto(tela, texto, tamanho, cor, posicao, ancora="centro", sombra=(0, 0, 0),
                   deslocamento=2, contorno=False, alfa=255):
    """Desenha texto na tela e retorna o retângulo ocupado."""
    superficie = renderizar_texto(texto, tamanho, cor, sombra, deslocamento, contorno)
    retangulo = superficie.get_rect()
    setattr(retangulo, ANCORAS.get(ancora, "center"), posicao)
    if alfa < 255:
        copia = superficie.copy()
        copia.set_alpha(alfa)
        tela.blit(copia, retangulo)
    else:
        tela.blit(superficie, retangulo)
    return retangulo
