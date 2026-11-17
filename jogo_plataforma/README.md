# Super Aventura — base de jogo de plataforma 2D (Python + Pygame)

Jogo de plataforma lateral inspirado nos clássicos de *Super Mario Bros.*, feito para ser
**uma base sólida de personalização**: todo o visual e o áudio vêm de arquivos (PNG, JSON, WAV)
que podem ser trocados sem tocar na lógica. A arte atual é **provisória e original**
(gerada por `ferramentas/gerar_recursos.py`).

Todo o código, comentários, documentação e nomes de arquivos estão em português brasileiro.

## O que o jogo tem

- Menu principal (PLAY, CONTINUE, SETTINGS, HOW TO PLAY, CREDITS, EXIT) com fundo animado,
  personagens em espera, mouse + teclado, sons e transições (fade, íris).
- Configurações funcionais: volume geral/música/efeitos, resolução, janela/tela cheia
  (também **F11**) e remapeamento de teclas. Tudo é salvo em JSON.
- **Uma fase extensa**: ~11,7 telas de largura (312 colunas × 48 px = 14 976 px), 100 moedas,
  22 inimigos, 3 tipos de inimigo, plataformas móveis, buracos, espinhos, lava, tubos, blocos
  quebráveis, blocos `?` (moedas, vida extra, estrela), caminhos alternativos, 2 checkpoints,
  área final de castelo (tema visual diferente), mastro, castelo e princesa.
- Final especial: mastro → caminhada até a princesa → corações e fogos → transição em íris →
  tela de vitória com pontuação, estatísticas e confetes.
- Pontuação (inimigo 100, moeda 10, fase 500, bônus de tempo), 3 vidas, HUD fixo
  (pontos, moedas, vidas, tempo, barra de progresso com checkpoints), pausa real,
  GAME OVER com reinício, dano com knockback e invulnerabilidade temporária.
- Salvamento seguro em JSON (arquivos ausentes ou corrompidos não impedem o jogo de abrir).

## Requisitos

- Python 3.9 ou superior
- Pygame 2.5 ou superior (`requisitos.txt`)

## Instalação e execução

```bash
cd jogo_plataforma
python -m venv .venv                 # opcional
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requisitos.txt
python principal.py
```

Se a pasta `recursos/` for apagada, recrie a arte e os sons provisórios com:

```bash
python ferramentas/gerar_recursos.py
python ferramentas/gerar_fase_01.py   # recria fases/mapas/fase_01.json
```

Teste automático (sem janela): `python testes/teste_integracao.py`

## Controles padrão

| Ação | Teclas |
|------|--------|
| Andar para a esquerda | A / ← |
| Andar para a direita | D / → |
| Pular (segure para pular mais alto) | Espaço / ↑ |
| Correr | Shift |
| Pausar | ESC / P |
| Tela cheia | F11 |

### Como configurar os controles

Menu **SETTINGS → Controles**: escolha a ação, pressione Enter e então a nova tecla
(ESC cancela). Se a tecla já estava em outra ação, as duas trocam de lugar. Os valores ficam em
`dados/configuracoes.json` (campo `controles`, nomes de tecla do Pygame, ex.: `"space"`, `"left shift"`).
Para voltar ao padrão use "Restaurar controles padrão" na própria tela, ou apague o arquivo.

## Estrutura das pastas

```
jogo_plataforma/
├── principal.py              # janela, laço principal, escala 1280x720 → resolução escolhida
├── configuracoes.py          # constantes, cores, caminhos e classe Configuracoes (JSON)
├── requisitos.txt
├── cenas/                    # telas: menu_principal, cena_jogo, menu_pausa, configuracoes_menu,
│                             #        como_jogar, creditos, tela_vitoria, tela_game_over
├── entidades/                # jogador, inimigo, objetos, blocos, efeitos
├── sistemas/                 # animacoes (spritesheets), camera, colisoes, pontuacao,
│                             # salvamento, audio, controles, cenario (parallax), gerenciador_de_cenas
├── interface/                # botoes, hud, textos, efeitos_de_tela
├── fases/                    # fase.py (motor), fase_01.py, sequencia_final.py,
│   └── mapas/fase_01.json    # o mapa em si
├── recursos/                 # personagens, inimigos, blocos, objetos, cenarios, efeitos,
│                             # interface, fontes, sons (musicas/ e efeitos/)
├── dados/                    # configuracoes.json e salvamento.json (criados ao jogar)
├── ferramentas/              # geradores dos recursos provisórios e do mapa
└── testes/                   # teste_integracao.py
```

## Principais classes

| Classe | Arquivo | Papel |
|--------|---------|-------|
| `Aplicacao` | `principal.py` | Janela, serviços compartilhados e laço principal (delta time, máx. 50 ms) |
| `GerenciadorDeCenas` | `sistemas/gerenciador_de_cenas.py` | Pilha de cenas (pausa por cima do jogo) e transições |
| `GerenciadorDeRecursos`, `FolhaDeSprites`, `Animador`, `Animacao` | `sistemas/animacoes.py` | Carrega spritesheets, recorta quadros, anima, escala e espelha |
| `Fase` | `fases/fase.py` | Lê o mapa JSON, cria o mundo e coordena a simulação |
| `SequenciaFinal` | `fases/sequencia_final.py` | Animação de conclusão (máquina de estados) |
| `Jogador`, `EstadoJogador` | `entidades/jogador.py` | Física estilo Mario com máquina de estados |
| `Inimigo`, `Cogumelo`, `Voador`, `Perseguidor` | `entidades/inimigo.py` | Inimigos independentes |
| `MapaDeBlocos`, `Bloco`, `Tileset` | `entidades/blocos.py` | Grade de blocos (sólidos, quebráveis, `?`, perigos) |
| `SistemaDeColisoes` | `sistemas/colisoes.py` | Colisão por eixo com blocos e plataformas móveis |
| `Camera` | `sistemas/camera.py` | Rolagem suave, limites e conversão mundo → tela |
| `Cenario` | `sistemas/cenario.py` | Camadas de parallax e troca de tema (campo → castelo) |
| `SistemaDePontuacao` | `sistemas/pontuacao.py` | Pontos, moedas, vidas, tempo e estatísticas |
| `Salvamento`, `Configuracoes` | `sistemas/salvamento.py`, `configuracoes.py` | Persistência segura em JSON |
| `GerenciadorDeAudio` | `sistemas/audio.py` | Músicas e efeitos; se o arquivo faltar, apenas avisa |
| `Hud` | `interface/hud.py` | Interface fixa durante a partida |

## Como substituir sprites

Cada recurso animado é uma pasta com **um PNG e um `configuracao.json`**:

```
recursos/personagens/jogador/
    personagem.png
    configuracao.json
```

Basta sobrescrever o PNG mantendo o nome (ou alterar o campo `arquivo`). Se o novo desenho tiver
outro tamanho de quadro, ajuste o JSON. O mesmo vale para `recursos/inimigos/*`, `recursos/objetos/*`,
`recursos/efeitos/*` e `recursos/cenarios/decoracoes/*`. Os blocos usam um único tileset
(`recursos/blocos/tileset/`) e o fundo usa camadas PNG (`recursos/cenarios/campo|castelo/`).
O personagem é desenhado olhando para a direita; o jogo espelha o sprite automaticamente.

## Como adicionar ou alterar animações

Cada animação é uma faixa da spritesheet descrita no JSON:

```json
{
  "arquivo": "personagem.png",
  "largura_quadro": 16,
  "altura_quadro": 22,
  "escala": 3,
  "margem": 0,
  "espacamento": 0,
  "caixa_colisao": [34, 58],
  "animacoes": {
    "andando": {"linha": 1, "quadro_inicial": 0, "quadros": 4, "duracao_quadro": 0.12, "repetir": true}
  }
}
```

- `linha` / `quadro_inicial` / `quadros`: onde estão os quadros no PNG (recorte automático);
- `duracao_quadro`: segundos por quadro (velocidade individual por animação);
- `repetir`: `false` para animações que tocam uma vez;
- `escala`: ampliação inteira aplicada na carga; `caixa_colisao`: tamanho (px finais) da hitbox.

Animações do jogador: `parado`, `andando`, `correndo`, `pulando`, `caindo`, `morrendo`, `dano`.
Para criar uma animação nova, adicione a entrada no JSON e peça-a no código com
`animador.tocar("nome")` (veja `entidades/jogador.py`, tabela estado → animação).

## Como modificar o mapa

O mapa é `fases/mapas/fase_01.json`: uma **grade de texto** (15 linhas × 312 colunas, blocos de 48 px)
mais uma `legenda` que liga cada caractere a um elemento. Principais caracteres:

| Char | Elemento | Char | Elemento |
|------|----------|------|----------|
| `G` / `T` | grama / terra | `o` | moeda |
| `B` | bloco quebrável | `?` | bloco com moedas |
| `M` | `?` com vida extra | `*` | `?` com estrela |
| `S` | bloco sólido | `a b c d` | tubo (topo/corpo) |
| `K` | tijolo de castelo | `E` | espinhos (dano) |
| `V` | lava (mata) | `C` | checkpoint |
| `J` | início do jogador | `F` | mastro final |
| `P` | princesa | `H` | castelo |
| `1` `2` `3` | inimigos | | |

Há também `plataformas_moveis` (coluna, linha, largura, eixo `x`/`y`, amplitude, período),
`decoracoes`, `temas` (camadas de parallax + música) e `zonas` (a partir de qual coluna cada tema vale).
Você pode editar o JSON à mão ou alterar `ferramentas/gerar_fase_01.py` e executá-lo de novo.
Objetos de personagem são marcados na linha onde a **base** deles encosta.

Para criar outra fase: crie o JSON, um módulo `fases/fase_NN.py` com `criar_fase_NN(...)` e registre-o
em `GerenciadorDeFases.FASES`.

## Como adicionar inimigos

1. Crie `recursos/inimigos/meu_inimigo/` com `inimigo.png` e `configuracao.json`
   (animações `andando`/`voando` e `esmagado`, conforme o tipo).
2. Em `entidades/inimigo.py`, crie uma subclasse de `Inimigo` (sobrescreva `comportamento(self, dt, colisoes, jogador)`) e registre-a em `TIPOS_DE_INIMIGO`.
3. Na `legenda` do mapa, adicione um caractere: `{"tipo": "inimigo", "inimigo": "meu_inimigo"}`
   e coloque o caractere na grade.

Inimigos atuais: **cogumelo** (anda e vira na borda/parede), **voador** (patrulha e atira
projéteis) e **perseguidor** (corre atrás do jogador; exige dois pisões).

## Áudio

Coloque arquivos `.ogg`, `.wav` ou `.mp3` em `recursos/sons/musicas/` (`menu`, `fase`, `castelo`,
`conclusao`) e `recursos/sons/efeitos/` (`pulo`, `moeda`, `dano`, `derrota`, `selecao`, `confirmacao`…).
O nome do arquivo é o nome do som. Se um arquivo não existir, o jogo avisa no console e segue sem som.

## Salvamento

- `dados/configuracoes.json`: volumes, resolução, tela cheia e controles.
- `dados/salvamento.json`: melhor pontuação e progresso (último checkpoint, pontos, moedas, vidas).
- **CONTINUE** retoma do último checkpoint. Arquivos corrompidos são ignorados e recriados.
