# Contrato de recursos — Tux: A Era dos Fragmentos de Gelo

Cada recurso animado = pasta em `recursos/` com um PNG + `configuracao.json`
(gravados por `ferramentas/arte/base.py::salvar_folha`). Tamanhos de quadro são em pixels
BASE (o jogo amplia por `escala`, sempre 3 salvo indicação). `caixa` = hitbox em pixels finais.
Sprites olham para a DIREITA (o motor espelha). Pés/base do sprite encostam na borda inferior do quadro.
Paleta e helpers: `ferramentas/arte/base.py` (usar SEMPRE a paleta glacial de lá).

## Inimigos — `inimigos/<nome>/inimigo.png`
| pasta | quadro | caixa | animações (quadros, duração s) |
|---|---|---|---|
| criatura_de_neve | 16x16 | 40x40 | andando(4,.14) esmagado(1) |
| pinguim_selvagem | 16x16 | 42x42 | andando(4,.14) furioso(4,.07) atordoado(1) esmagado(1) |
| morcego_glacial | 16x16 | 40x36 | voando(4,.10) esmagado(1) |
| golem_de_gelo | 24x24 | 60x66 | andando(4,.20) furioso(4,.10) dano(1) esmagado(1) |

## Objetos — `objetos/<nome>/<nome>.png`
| pasta | quadro | caixa | animações |
|---|---|---|---|
| cristal (moeda) | 16x16 | 30x38 | girando(4,.10) |
| coracao_gelo (vida) | 16x16 | 40x40 | parado(1) |
| cristal_magico (invencibilidade) | 16x16 | 40x40 | brilho(2,.12) |
| totem (checkpoint) | 16x32 | 40x96 | baixada(1) levantada(2,.20) |
| altar (pedestal do fragmento) | 32x32 | — | parado(1) ativo(2,.20) |
| fragmento_de_gelo | 16x16 | 42x42 | fragmento_1(4,.12) fragmento_2(4,.12) fragmento_3(4,.12) — 1 ciano/branco, 2 roxo-gelo, 3 dourado/branco; bem mais vistosos que o cristal |
| portal | 32x48 | — | fechado(1) abrindo(4,.12,1x) aberto(4,.12) |
| castelo_gelo | 96x80 | — | parado(1) — porta escura no centro da base |
| plataforma_gelo | 48x8 | 144x24 | parada(1) |
| projetil_gelo | 8x8 | 20x20 | girando(4,.08) |
| coracao | 16x16 | — | flutuando(2,.30) — coração rosa-gelo do final |
| prisao_de_gelo | 24x32 | — | intacta(2,.5) rachando(2,.12) estilhacando(4,.08,1x) — bloco translúcido desenhado SOBRE a princesa |
| chave_magica | 16x16 | — | brilho(2,.20) |
| lembranca | 16x16 | 40x40 | brilhando(4,.15) — orbe dourado (segredo) |

## Personagem extra — `personagens/tux_filhote/personagem.png`
16x16, escala 3: parado(2,.4) andando(4,.12). (Tux bebê, penugem cinza, segredo.)

## Efeitos — `efeitos/<nome>/efeito.png`
| pasta | quadro | animações |
|---|---|---|
| fragmento | 8x8 | parado(1) — caco de gelo (bloco quebrando) |
| brilho | 16x16 | brilho(4,.07,1x) — coleta |
| explosao_gelo | 16x16 | explosao(3,.08,1x) |
| congelamento | 16x16 | congelar(4,.07,1x) |
| poeira_dash | 16x16 | dash(3,.06,1x) |
| floco | 8x8 | pequeno(1) medio(1) grande(1) — partículas de neve |

## Decorações — `cenarios/decoracoes/<nome>/<nome>.png` (anim `parado`(1) salvo indicação)
pinheiro_nevado 32x64 · arbusto_nevado 48x16 · placa_gelo 16x16 · tocha_gelo 16x32 `acesa`(2,.15) ·
estandarte_gelo 16x32 · cristal_grande 32x48 (2 quadros `parado` .4) · estalagmite 16x32 · pedra_gelada 32x16 ·
boneco_de_neve 16x32 · estatua_pinguim 16x32 · cristal_luminoso 16x32 `brilho`(3,.2) · pinheiro_tempestade 32x64 ·
pilar_castelo 16x64 · estalactite_frente 16x32 · neve_frente 48x16.

## Interface — `interface/*.png` (tamanho real em pixels, SEM ampliação; o HUD amplia 2x)
icone_moeda 16x16 (cristal) · icone_vida 16x16 (coração congelado) · icone_relogio 16x16 ·
seta 16x16 (ponteiro de menu em forma de cristal/seta) · icone_fragmento_1/2/3 16x16 · icone_fragmento_vazio 16x16 ·
icone_cadeado 16x16 · icone_check 16x16 · logo.png (~640x190, letras de gelo "TUX" em pixel art, neve no topo, estilhaços).
(`regiao_geleira/cavernas/castelo.png` 384x216 já são gerados por `arte/cenarios.py`.)

## Sons — `sons/musicas/<nome>.wav` (loop) e `sons/efeitos/<nome>.wav`
Músicas: menu, geleira, cavernas, castelo, conclusao (fanfarra curta, sem loop), final (epílogo emotivo).
Efeitos (todos): pulo, moeda, dano, derrota, selecao, confirmacao, mensagem_erro, bloco_bater, bloco_quebrar,
checkpoint, esmagar, estrela, item_surge, vida_extra, mastro, projetil,
dash, ataque, ataque_acerto, fragmento, chave, prisao_quebra, portal, golem_dano, golem_passo, pinguim_grito,
morcego, segredo, congelar, vitoria.
