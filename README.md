# Tux: A Era dos Fragmentos de Gelo

Jogo de plataforma 2D (Python + Pygame) com temática de era glacial. Você controla **Tux**, um pinguim
aventureiro, através de três regiões congeladas para reunir os **três Fragmentos de Gelo**, restaurar a
chave mágica e resgatar a **Princesa do Gelo**, presa no Castelo do Inverno Eterno.

O projeto nasceu como uma base de plataforma estilo *Super Mario Bros.* e foi **tematizado sobre o mesmo
motor**: física, câmera, colisões, controles e a geometria da Fase 1 foram preservados. Tudo o que é arte
ou som vem de arquivos (PNG, JSON, WAV) e pode ser trocado sem mexer na lógica.

Todo o código, comentários, documentação e nomes de arquivos estão em português brasileiro.

## História

O Reino Glacial vivia em paz até um antigo desastre despertar uma força que congela e corrompe o reino. A
Princesa do Gelo desapareceu, aprisionada num castelo de gelo. Tux descobre que três Fragmentos de Gelo,
espalhados por três regiões, restauram a chave mágica que abre o castelo. A história é contada por pequenos
diálogos nos cenários, por uma lembrança escondida e pela cena final, sem telas de texto longas.

## O que o jogo tem

- **3 fases completas e distintas**, com checkpoints, desafios próprios e um Fragmento de Gelo no fim de cada uma:

| Fase | Região | Tamanho | Destaques |
|------|--------|---------|-----------|
| 1 | A Geleira Perdida | 11,7 telas | **Mapa original preservado** (só o visual mudou): montanhas nevadas, pinheiros, cristais, plataformas móveis |
| 2 | As Cavernas Congeladas | 10,8 telas | Subterrâneo vertical (22 linhas), cristais luminosos, estalactites, lagos gélidos, caminhos alto/baixo, Golem |
| 3 | O Castelo do Inverno Eterno | 12,0 telas | Tempestade de neve, pontes de gelo, plataformas móveis, inimigos mais resistentes, aproximação do castelo |

- **4 inimigos** com comportamento e animações próprias: Criatura de Neve, Pinguim Selvagem, Morcego Glacial e Golem de Gelo.
- **Combate**: pisar, **ataque** (quebra blocos de gelo) e **dash** (atropela criaturas e cruza vãos).
- **Progressão real**: concluir a fase N libera a N+1; os fragmentos são registrados; a fase 3 leva à cena do castelo.
- **Seleção de fases** com ilustração, nome, estado (bloqueada/disponível/concluída), fragmentos e melhor pontuação. Fases concluídas podem ser rejogadas sem perder a campanha.
- **Final**: os três fragmentos se fundem na chave mágica, a prisão de gelo se desfaz, Tux e a princesa se reencontram e há um epílogo.
- **Um segredo** opcional (veja a seção "Spoiler" no fim).
- Menu com castelo ao fundo, neve, Tux animado, botões por mouse/teclado e transições (fade e íris).
- HUD com pontos, cristais, vidas (corações de gelo), fragmentos, progresso e tempo; pausa real; GAME OVER; dano com knockback, efeito de congelamento e invulnerabilidade temporária.
- Pontuação: criatura 100, cristal 10, conclusão 500, bônus de tempo (100 cristais dão uma vida extra).
- Salvamento seguro em JSON (arquivos ausentes ou corrompidos nunca impedem o jogo de abrir).
- Configurações funcionais: volumes (geral, música, efeitos), resolução, janela/tela cheia (**F11**) e remapeamento de teclas.

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

## Controles padrão

| Ação | Teclas |
|------|--------|
| Andar para a esquerda / direita | A, D ou ← → |
| Pular (segure para pular mais alto) | Espaço ou ↑ |
| Correr | Shift |
| Atacar | J ou Z |
| Dash | K ou X |
| Pausar | ESC ou P |
| Tela cheia | F11 |

**Configurar os controles:** `CONFIGURAÇÕES → Controles`: escolha a ação, pressione Enter e então a nova
tecla (ESC cancela). Se a tecla já estava em outra ação, as duas trocam de lugar. Os valores ficam em
`dados/configuracoes.json` (campo `controles`, nomes de tecla do Pygame como `"space"` ou `"left shift"`).
"Restaurar controles padrão" está na própria tela.

## Estrutura das pastas

```
jogo_plataforma/
├── principal.py              # janela, laço principal, escala 1280x720 → resolução escolhida
├── configuracoes.py          # constantes (física, cores, ataque/dash), caminhos, classe Configuracoes
├── requisitos.txt
├── cenas/                    # menu_principal, selecao_de_fases, cena_jogo, menu_pausa, configuracoes_menu,
│                             # como_jogar, creditos, tela_vitoria, tela_game_over, cena_final, camara_secreta
├── entidades/                # jogador, inimigo (4 criaturas), objetos, blocos, efeitos, entidade
├── sistemas/                 # animacoes (spritesheets), camera, colisoes, cenario (parallax), neve,
│                             # pontuacao, salvamento, audio, controles, gerenciador_de_cenas
├── interface/                # botoes, hud, textos, efeitos_de_tela
├── fases/                    # fase.py (motor), fase_01/02/03.py, gerenciador_de_fases.py, sequencia_final.py
│   └── mapas/                # fase_01.json, fase_02.json, fase_03.json, camara_secreta.json, salao_final.json
├── recursos/                 # personagens (tux, tux_filhote, princesa), inimigos (4), blocos, objetos,
│                             # cenarios (geleira, cavernas, castelo, menu, salao, epilogo, camara, decoracoes),
│                             # efeitos, interface, fontes, sons (musicas, efeitos)
├── dados/                    # configuracoes.json e salvamento.json (criados ao jogar)
├── ferramentas/              # geradores de arte/sons/mapas, validador de mapas, contrato dos recursos
└── testes/teste_integracao.py
```

## Principais classes

| Classe | Arquivo | Papel |
|--------|---------|-------|
| `Aplicacao` | `principal.py` | Janela, serviços compartilhados e laço principal (delta time) |
| `GerenciadorDeCenas` | `sistemas/gerenciador_de_cenas.py` | Pilha de cenas (pausa por cima do jogo) e transições |
| `GerenciadorDeRecursos`, `FolhaDeSprites`, `Animador`, `Animacao` | `sistemas/animacoes.py` | Carrega spritesheets, recorta quadros, anima, escala e espelha |
| `Fase` | `fases/fase.py` | Lê o mapa JSON, cria o mundo e coordena a simulação |
| `GerenciadorDeFases` | `fases/gerenciador_de_fases.py` | Cria a fase pelo número (1 a 3) e guarda nomes/ilustrações |
| `SequenciaFragmento` | `fases/sequencia_final.py` | Coleta do fragmento → (chave mágica) → portal |
| `Jogador`, `EstadoJogador` | `entidades/jogador.py` | Física estilo plataforma com máquina de estados (inclui ataque e dash) |
| `Inimigo`, `CriaturaDeNeve`, `PinguimSelvagem`, `MorcegoGlacial`, `GolemDeGelo` | `entidades/inimigo.py` | Criaturas independentes |
| `AltarDoFragmento`, `Portal`, `Totem`, `Cristal`, `PlataformaMovel`, `ChaveMagica` … | `entidades/objetos.py` | Objetos do mundo |
| `MapaDeBlocos`, `Bloco`, `Tileset` | `entidades/blocos.py` | Grade de blocos (sólidos, quebráveis, de recompensa, perigos) |
| `SistemaDeColisoes` | `sistemas/colisoes.py` | Colisão por eixo com blocos e plataformas móveis |
| `Camera`, `Cenario`, `SistemaDeNeve` | `sistemas/` | Rolagem suave, parallax por tema e neve |
| `SistemaDePontuacao` | `sistemas/pontuacao.py` | Pontos, cristais, vidas, tempo e estatísticas |
| `Salvamento`, `Configuracoes` | `sistemas/salvamento.py`, `configuracoes.py` | Persistência segura em JSON |
| `GerenciadorDeAudio` | `sistemas/audio.py` | Músicas e efeitos; arquivo ausente só gera um aviso |
| `SelecaoDeFases`, `CenaFinal`, `CamaraSecreta` | `cenas/` | Seleção, final da campanha e câmara secreta |

## Salvamento

`dados/salvamento.json` guarda: melhor pontuação, fases concluídas e desbloqueadas, fragmentos coletados,
melhor pontuação por fase, segredo descoberto, campanha concluída e o último checkpoint.
Ele tem número de versão e é validado campo a campo ao carregar: salvamentos da versão anterior continuam
valendo (o recorde é mantido) e arquivos corrompidos são renomeados para `.corrompido` e substituídos por um novo.
**CONTINUAR** retoma do último checkpoint ou, sem ele, da próxima fase ainda não concluída.

## Como substituir sprites

Cada recurso animado é uma pasta com **um PNG e um `configuracao.json`**, por exemplo:

```
recursos/personagens/tux/
    personagem.png
    configuracao.json
```

Sobrescreva o PNG mantendo o nome. Se o novo desenho tiver outro tamanho de quadro, ajuste o JSON. O contrato
completo (tamanho de quadro, hitbox e animações de **cada** recurso) está em
[`ferramentas/CONTRATO_RECURSOS.md`](ferramentas/CONTRATO_RECURSOS.md). Os sprites devem olhar para a **direita**
(o motor espelha) e ter os pés na borda inferior do quadro. Blocos usam um único tileset
(`recursos/blocos/tileset/`) e os fundos usam camadas PNG por região (`recursos/cenarios/<região>/`).

## Como adicionar ou alterar animações

```json
{
  "arquivo": "personagem.png",
  "largura_quadro": 16,
  "altura_quadro": 22,
  "escala": 3,
  "caixa_colisao": [34, 58],
  "animacoes": {
    "andando": {"linha": 1, "quadro_inicial": 0, "quadros": 4, "duracao_quadro": 0.12, "repetir": true}
  }
}
```

`linha`/`quadro_inicial`/`quadros` indicam onde os quadros estão no PNG (recorte automático),
`duracao_quadro` é a velocidade individual da animação e `repetir: false` faz tocar uma vez só.
Animações do Tux: `parado`, `andando`, `correndo`, `pulando`, `caindo`, `dash`, `atacando`, `dano`,
`morrendo`, `vitoria`. Para criar uma nova, adicione a entrada no JSON e peça-a no código com
`animador.tocar("nome")` (veja a tabela estado → animação em `entidades/jogador.py`).

## Como modificar o mapa

Cada mapa é uma **grade de texto** (blocos de 48 px) mais uma `legenda` que liga cada caractere a um
elemento. Alguns caracteres: `G` neve · `T` solo congelado · `B` gelo quebrável · `?` bloco de cristal com
cristais · `M` com coração de gelo (vida) · `*` com Cristal Mágico (invencibilidade) · `S` pedra · `E` espinhos ·
`V` água gélida (mata) · `o` cristal · `1`–`5` inimigos · `C` totem (checkpoint) · `J` início do Tux ·
`F` altar do fragmento · `P` portal de saída. A legenda completa está em `ferramentas/legendas_glaciais.py`.

O mapa também define `plataformas_moveis`, `decoracoes`, `dialogos`, `temas` (camadas de parallax, música e
neve) e `zonas` (a partir de qual coluna cada tema vale). Personagens e objetos são marcados na linha onde a
**base** deles encosta.

Há duas formas de editar: alterar o JSON à mão, ou alterar o gerador da fase (`ferramentas/gerar_fase_0N.py`,
que usa `construtor_de_mapas.py`) e executá-lo de novo. Depois, **valide a jogabilidade**:

```bash
python ferramentas/validar_mapas.py          # prova que o fragmento é alcançável com os pulos reais do Tux
```

> A grade da Fase 1 é a do jogo original e é protegida pelo teste de integração (hash). Se você quiser
> mudá-la de propósito, atualize `HASH_GRADE_FASE_1` em `testes/teste_integracao.py`.

Para criar uma 4ª fase: crie o JSON, um módulo `fases/fase_04.py`, registre-a em `GerenciadorDeFases`
e aumente `TOTAL_DE_FASES` em `configuracoes.py`.

## Como adicionar inimigos

1. Crie `recursos/inimigos/meu_inimigo/` com `inimigo.png` e `configuracao.json` (por exemplo `andando` e `esmagado`).
2. Em `entidades/inimigo.py`, crie uma subclasse de `Inimigo` (implemente `comportamento(self, dt, colisoes, jogador)`)
   e registre-a em `TIPOS_DE_INIMIGO`.
3. Na `legenda` do mapa, adicione um caractere: `{"tipo": "inimigo", "inimigo": "meu_inimigo"}` e use-o na grade.

| Inimigo | Comportamento |
|---------|---------------|
| Criatura de Neve | Anda de um lado a outro e vira na borda; um pisão ou golpe derrota |
| Pinguim Selvagem | Rápido, persegue o Tux e aguenta **dois** golpes |
| Morcego Glacial | Patrulha no ar e solta estilhaços de gelo quando o Tux passa embaixo; há uma variante que mergulha |
| Golem de Gelo | Lento e imponente, aguenta **três** golpes e fica furioso quando resta uma vida ao jogador |

## Áudio

Arquivos `.ogg`, `.wav` ou `.mp3` em `recursos/sons/musicas/` (`menu`, `geleira`, `cavernas`, `castelo`, `conclusao`,
`final`) e `recursos/sons/efeitos/`. O nome do arquivo é o nome do som. Se um arquivo faltar, o jogo avisa no console e
segue sem som.

## Ferramentas, testes e backup

| Comando | O que faz |
|---------|-----------|
| `python testes/teste_integracao.py` | Teste sem janela: menu, seleção, 3 fases, fragmentos, desbloqueios, pausa, checkpoint, segredo, game over, final e salvamento. Usa uma pasta temporária: não mexe no seu save. |
| `python ferramentas/validar_mapas.py` | Prova de alcançabilidade dos fragmentos nas 3 fases |
| `python ferramentas/gerar_recursos.py [grupo ...]` | Recria TODA a arte e os sons provisórios (grupos: personagens, inimigos, blocos, objetos, efeitos, decoracoes, cenarios, interface, sons) |
| `python ferramentas/gerar_fase_01.py` (e 02, 03) | Recria os mapas a partir dos geradores |

> **Atenção:** `gerar_recursos.py` **sobrescreve** os arquivos de mesmo nome em `recursos/`. Depois de trocar um PNG
> pela sua arte final, não rode o grupo correspondente (ou rode só os grupos que ainda precisa).
> O gerador do tema antigo (clássico) ficou em `ferramentas/legado/` apenas como histórico.

## Assets provisórios (a substituir)

**Toda a arte e todos os sons atuais são provisórios**: foram gerados por código (`ferramentas/arte/` e
`ferramentas/arte/sons.py`), são originais e não usam nenhum recurso externo ou protegido. Nada depende de internet.

| Grupo | Onde | Observação |
|-------|------|------------|
| Personagens | `recursos/personagens/{tux,tux_filhote,princesa}` | Tux com 10 animações; princesa com 5 |
| Inimigos | `recursos/inimigos/{criatura_de_neve,pinguim_selvagem,morcego_glacial,golem_de_gelo}` | Cada um com spritesheet e hitbox próprias |
| Blocos | `recursos/blocos/tileset` | Neve, solo congelado, gelo, cristal, pedra, pilares, castelo, perigos |
| Objetos | `recursos/objetos/*` | Cristal, coração de gelo, Cristal Mágico, totem, altar, **fragmentos 1/2/3**, portal, chave mágica, castelo, prisão de gelo... |
| Cenários | `recursos/cenarios/*` | Camadas de parallax por região, menu, salão final, epílogo, câmara e decorações |
| Efeitos | `recursos/efeitos/*` | Neve, brilho, explosão de gelo, congelamento, poeira do dash, estilhaços |
| Interface | `recursos/interface/*` | Logo, ícones, ilustrações das regiões |
| Fonte | `recursos/fontes/fonte_principal.ttf` | Troque por uma fonte com acentos que combine com a sua identidade |
| Músicas | `recursos/sons/musicas/*.wav` | Faixas sintetizadas simples |
| Efeitos sonoros | `recursos/sons/efeitos/*.wav` | 29 sons sintetizados |

Os recursos que mais valem substituir primeiro: **Tux e a princesa**, **inimigos**, **tileset** e **músicas**.

<details>
<summary><b>Spoiler: o segredo do jogo (leia só se quiser)</b></summary>

Na **Fase 2**, uma parede de gelo rachada (coluna 182) é derrubada com **3 ataques**. Ela revela um portal que leva
à **Câmara da Lembrança**, uma pequena sala jogável com um orbe dourado. Tocá-lo exibe uma lembrança do passado de
Tux e da princesa quando eram filhotes. A recompensa é única: +pontos, um **rastro dourado** que acompanha o Tux
nas fases seguintes e o registro `segredo_descoberto` no salvamento. Não é necessário para concluir a campanha e não
é anunciado no menu nem no tutorial. O mapa é `fases/mapas/camara_secreta.json` e a cena é `cenas/camara_secreta.py`.

</details>
