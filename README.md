# Tux

## Fragmentos de Gelo

---

## 1. Descrição Geral

*Tux* é um jogo 2D dos gêneros plataforma, aventura e ação, desenvolvido com a biblioteca Pygame.

O jogo se passa em diferentes partes do mundo, onde cada fase representa um continente distinto, com cenários únicos que refletem o ambiente local.

A história acompanha Tux, um pinguim que, após o descongelamento de uma geleira, perde seu grande amor, que é levado para o mar aberto e desaparece pelo mundo. Determinado a encontrá-la, Tux embarca em uma jornada global, atravessando diversos continentes e enfrentando desafios para resgatar seu amor perdido.

---

## 2. Objetivo do Jogo

O objetivo principal do jogo é guiar Tux através de diferentes fases distribuídas em continentes ao redor do mundo, enfrentando desafios e obstáculos até reunir todos os fragmentos de gelo.

Cada fase concluída com sucesso recompensa o jogador com um fragmento de gelo. Ao coletar os 5 fragmentos, eles se unem para formar uma chave especial, que desbloqueia a fase final do jogo, onde o amor perdido de Tux está localizado.

Para concluir cada fase, o jogador deverá atravessar o cenário utilizando mecânicas de plataforma (como saltos e movimentação estilo parkour), enfrentar inimigos e superar obstáculos até alcançar o objetivo final da fase.

O jogador perde ao esgotar todas as suas vidas. Durante as fases, é possível perder vidas ao cair em buracos, sofrer dano de inimigos, projéteis ou armadilhas.

---

## 3. Personagem Principal

O personagem principal do jogo é Tux, um pinguim inspirado no mascote do sistema GNU/Linux. Na história, ele embarca em uma jornada ao redor do mundo em busca de seu amor perdido.

Tux possui as seguintes habilidades:

* Movimentação lateral (direita e esquerda)
* Pulo
* Pulo duplo
* Agachar
* Dash
* Ataque básico
* Ataque especial

Seus principais atributos incluem:

* Vida (3 vidas)
* Velocidade
* Pontuação
* Ataque
* Energia (utilizada para habilidades especiais)

---

## 4. Inimigos e Obstáculos

Os inimigos do jogo são inspirados nos continentes visitados por Tux, trazendo variedade a cada fase.

Exemplos:

* Floresta: macacos e criaturas ágeis
* Gelo: inimigos congelados
* Deserto: escorpiões
* Montanhas: aves
* Praias/oceano: caranguejos

Os inimigos comuns se movimentam automaticamente em padrões simples. Já os chefes (bosses) possuem comportamentos mais complexos e atacam o jogador ao se aproximar.

Interações:

* Ao encostar em inimigos ou projéteis, o jogador perde vida, sofre knockback e ganha invencibilidade temporária
* Ao atacar inimigos, eles recebem dano e podem ser derrotados

Obstáculos incluem:

* Buracos
* Plataformas (parkour)
* Superfícies escorregadias
* Espinhos e armadilhas

---

## 5. Cenário (Mapa)

O jogo apresenta mapas 2D com progressão linear (da esquerda para a direita).

Características:

* Chão sólido e plataformas
* Estrutura linear
* Possíveis áreas secretas (easter eggs)

Os fragmentos de gelo estão localizados ao final de cada fase, geralmente após um desafio final.

Ao coletar o fragmento:

* A fase é concluída automaticamente
* A próxima fase é desbloqueada

O jogo não possui checkpoints, exigindo consistência do jogador.

---

## 6. Sistema de Pontuação

A pontuação é baseada na eliminação de inimigos e conclusão da fase.

Para obter a pontuação máxima, o jogador deve:

* Derrotar todos os inimigos
* Derrotar o boss
* Completar a fase

A pontuação total pode atingir um valor máximo (ex: 100 pontos por fase).

---

## 7. Sistema de Vida

O jogador inicia com 3 vidas.

Perde vida ao:

* Cair em buracos
* Encostar em inimigos
* Ser atingido por projéteis
* Tocar em armadilhas

Ao sofrer dano:

* Perde uma vida
* Sofre knockback
* Recebe invencibilidade temporária

Ao perder todas as vidas:

* A fase é reiniciada do início

O jogo possui itens de cura (corações) espalhados pelo mapa.

---

## 8. Controles

* **A / D** → Movimentação
* **Espaço** → Pular
* **Q** → Dash
* **J** → Ataque básico
* **K** → Ataque especial
* **Esc** → Menu de pausa

O menu de pausa permite continuar ou sair do jogo.

---

## 9. Fluxo do Jogo

O jogo inicia com uma tela de abertura, seguida por um menu principal.

O jogador pode selecionar fases desbloqueadas e iniciar a jogabilidade.

Durante o jogo:

* As fases seguem progressão linear
* Ao concluir uma fase, uma tela de conclusão pode ser exibida com pontuação e opções

Caso o jogador perca todas as vidas:

* Uma tela de "Game Over" é exibida
* O jogador reinicia a fase atual (sem perder progresso geral)

O jogo é vencido ao completar todas as fases e resgatar o amor perdido de Tux.

---

## 10. Regras do Jogo

* O jogador não pode atravessar paredes (exceto em áreas secretas)
* Não é possível sair dos limites do mapa
* Colisão com paredes bloqueia movimento
* É necessário coletar o fragmento para concluir a fase
* Derrotar inimigos contribui para pontuação e progressão (regra pode ser ajustada)

---

## 11. Estrutura do Projeto

O projeto será modularizado utilizando programação orientada a objetos.

Estrutura sugerida:

* `main.py`
* `player.py`
* `enemy.py`
* `boss.py`
* `map.py`
* `items.py`
* `config.py`
* `utils.py`

Essa organização facilita manutenção e expansão do projeto.

---

## 12. Funcionalidades Mínimas

A primeira versão do jogo deve conter:

* Movimentação do personagem
* Sistema de pulo
* Pelo menos uma fase jogável
* Inimigos funcionando
* Sistema de vida

O objetivo é garantir um jogo funcional básico antes de expansões.

---

## 13. Melhorias Futuras

* Novas habilidades (wall jump, upgrades)
* Sistema de evolução do personagem
* Mais fases e continentes
* Novos inimigos
* Bosses mais complexos
* Sistema de ranking/pontuação
* Itens colecionáveis
* Sistema de energia (stamina)
* Checkpoints
* HUD aprimorado
* Sons e trilha sonora
* Melhorias visuais e animações
* Menu de configurações
* Expansão da história

---
