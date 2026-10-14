# Briefing — Politicalizando V1

Diagnóstico, decisões e roteiro da primeira versão. Este documento vem antes do código e é atualizado quando uma decisão muda; cada mudança é registrada no [LOG.md](LOG.md).

> **Situação:** Fases 0 (fundação) e 1 (núcleo) concluídas; próxima: Fase 2 (fluxo principal). O conteúdo e a narrativa foram revisados em conjunto em 2026-10-14 (seções 5 e 6); os textos finais e as fontes são escritos e revisados na Fase 4.

---

## 1. Visão geral

**O que é:** um jogo 2D em pixel art que ensina o que são as ideologias políticas e como se informar sobre política, para que a pessoa jogadora compreenda o mundo atual e desenvolva um pensamento crítico sólido. A ambientação é contemporânea e distópica.

**Gênero:** aventura point-and-click em telas fixas. O jogador explora a cidade, examina objetos, conversa com moradores e reúne evidências; não há personagem andando pelo cenário nem condição de derrota (D8).

**O que ele não é:** propaganda. O jogo não diz em quem votar nem qual corrente está certa. Ele ensina a **entender** cada corrente pelos seus próprios argumentos, a **comparar** propostas e a **reconhecer** manipulação, venha de onde vier (ver os princípios de conteúdo, seção 6).

**Objetivo da V1:** um capítulo curto, completo e bem acabado, jogável de ponta a ponta em 20 a 30 minutos, que sirva de base para os capítulos seguintes e possa ser usado em sala de aula e em ações do projeto de extensão.

**Público:** pessoas de **14 anos ou mais**, como estudantes do ensino médio, universitários e o público das ações de extensão da UNIP. A linguagem é acessível, sem jargão desnecessário, e não pressupõe conhecimento prévio de política.

---

## 2. Ponto de partida e riscos

O projeto começa do zero: não há código anterior nem bugs a corrigir. Por isso, este diagnóstico lista os **riscos** que o projeto precisa controlar desde o início. Cite os códigos no LOG e nos PRs quando uma mudança tratar de um deles.

| Código | Risco | Como controlar |
|--------|-------|----------------|
| R1 | O jogo ser lido como propaganda de um lado | Princípios C1 a C6, salvaguardas E1 a E5 nas mecânicas, revisão de equilíbrio de todo texto antes do merge (checklist no CONTRIBUTING) e revisão externa (P5) |
| R2 | Caricaturar uma corrente (descrever pelo que os adversários dizem dela) | Fichas com o mesmo modelo para todas; teste do defensor (C5) |
| R3 | Escopo crescer e o capítulo ficar pela metade | Tabela de escopo (seção 9); novidades vão para "Fica para a próxima" |
| R4 | Virar uma apostila com botões (texto demais, pouca decisão) | Toda cena pede uma ação do jogador; textos curtos, com aprofundamento opcional nas fichas |
| R5 | Informação factual errada ou sem fonte | Fontes registradas junto do conteúdo (C4); conteúdo como dados revisáveis; teste que exige fonte |
| R6 | A distopia ser associada a um partido, governo ou corrente real | O antagonista é um mecanismo (o Feed), cujo dono nunca é revelado (C3) |
| R7 | Fonte pixel sem acentos do português | Usar a VT323 (OFL), que já desenhou bem os acentos no Jogo da Cobrinha (I2) |
| R8 | Material de terceiros entrar no repositório (ex.: a referência de game design) | A referência fica fora do repositório e é usada só como ideia; nada de código, textos, nomes ou assets copiados (D12) |
| R9 | Falso equilíbrio: tratar fatos verificáveis como "mais uma opinião" | Separar fato, opinião/valor e manipulação na checagem (J4) e na avaliação (J7); princípio C6 |

---

## 3. Estrutura do código

```plaintext
Politicalizando/
├── CLAUDE.md, CONTRIBUTING.md, README.md, LOG.md, briefing.md
├── LICENSE (MIT, código), LICENCA-CONTEUDO.md (CC BY 4.0, conteúdo)
├── pyproject.toml
├── .github/workflows/ci.yml        # release.yml entra na Fase 5
├── src/politicalizando/
│   ├── __main__.py                 # python -m politicalizando [--fechar-em S]
│   ├── config.py                   # resolução, FPS, paleta
│   ├── jogo.py                     # janela, loop e pilha de estados; executa as ações
│   ├── persistencia.py             # save JSON e autosave (Fase 1)
│   ├── dominio/                    # regras puras, sem pygame
│   │   ├── estado_jogo.py          # flags, inventário, cena atual
│   │   ├── acoes.py, diretor.py    # ações e execução dos roteiros
│   │   ├── roteiro.py              # roteiros em dados → gerador
│   │   ├── dialogo.py              # árvores de diálogo
│   │   ├── cenas.py, interacao.py  # cenas, objetos interativos e verbos
│   │   └── textos.py               # textos por ID
│   ├── conteudo/                   # dados revisáveis (TOML): textos, cenas, diálogos, roteiros
│   ├── estados/                    # telas: título, cena, mapa, fichas
│   ├── ui/                         # texto, caixa de diálogo, menu de verbos
│   └── assets/                     # gerados por ferramentas/
├── ferramentas/                    # geradores de assets e empacotador
├── docs/                           # GIF e notas de release (Fase 5)
└── tests/
```

**Decisões técnicas:**

- **Python 3.11+ e pygame-ce** (D4): o fluxo já foi testado no Jogo da Cobrinha, roda no CI sem janela e o `pygame.SCALED` mantém a pixel art nítida.
- **Resolução lógica de 320×180** (16:9), ampliada por um fator inteiro pelo `pygame.SCALED`. O mouse já é lido nessa resolução, então as áreas clicáveis usam coordenadas lógicas.
- **Domínio sem pygame:** estado, roteiros, diálogos, interação, checagem de fontes e progresso ficam em `dominio/`; `tests/test_dominio.py` impede que o pygame entre ali.
- **Arquitetura de aventura** (D10, D11):
  - **Estado do jogo** = conjunto de flags de evento + inventário + cena atual. Objetos, cenas e diálogos consultam as flags para decidir o que mostrar.
  - **API única de roteiro:** os roteiros leem o estado diretamente e descrevem os efeitos como **ações** (`Fala`, `MarcarFlag`, `DarItem`, `TrocarCena`, `Esperar`, `Escolha`). O domínio produz as ações; o `Jogo` as executa na tela. Assim um roteiro inteiro é testado sem janela.
  - **Diretor com geradores Python:** cada sequência roteirizada é um gerador; o diretor avança uma ação por vez, espera ela terminar (tecla, tempo) e bloqueia o input enquanto a sequência roda. Escolhas voltam ao roteiro por `send()`.
  - **Roteiros em dados:** sequências simples, diálogos e cenas ficam em TOML (lidos pelo `tomllib`), interpretados pelo domínio. Só casos especiais ficam em Python.
  - **Textos por ID:** todo texto fica em `conteudo/pt_BR/textos.toml` (`id → quem fala, texto`). Um teste confere que todo ID usado existe e que não há texto órfão.
  - **Save** em JSON, 1 slot, com autosave ao entrar numa cena quando houve mudança e nada está bloqueado (D10).
- **Assets por código:** sprites e sons gerados por scripts determinísticos em `ferramentas/`.

---

## 4. Interface

| Código | Item |
|--------|------|
| I1 | Pixel art em 320×180 com paleta restrita, gerada por código. Clima distópico (cores frias, telas e painéis luminosos), sem símbolos de partidos ou movimentos reais |
| I2 | Fonte VT323 (OFL) para todo o texto, com acentos do português conferidos |
| I3 | Caixa de diálogo com texto que aparece aos poucos; uma tecla ou clique completa e o seguinte avança |
| I4 | Mouse e teclado (D9): clique nos objetos; ou Tab/setas para percorrer os objetos, 1/2/3 para os verbos, Enter/Espaço para confirmar e Esc para voltar ou pausar |
| I5 | Leitura sem pressa: nenhum texto com tempo limite, contraste alto e velocidade do texto ajustável |
| I6 | Efeitos sonoros e trilha simples, gerados por código (Fase 3) |
| I7 | Menus: título (novo jogo, continuar), como jogar, fichas, créditos e fontes, sair |
| I8 | "Mostrar objetos": uma tecla destaca todos os objetos interativos da cena (acessibilidade para quem nunca jogou o gênero) |
| I9 | Menu de verbos **Olhar / Usar / Falar** ao selecionar um objeto |

---

## 5. Funcionalidades

**Premissa narrativa:** em **Novátria**, uma cidade fictícia de hoje, quase toda a informação passa por um único aplicativo, o **Feed**, cujo algoritmo premia o que gera mais raiva e engajamento. **Quem controla o Feed nunca é revelado**: o tema é o mecanismo (engajamento pela raiva), não um dono que possa ser lido como "o mercado" ou "o governo". A narração é em **"você"**: você é estudante e precisa escrever para o jornal do grêmio estudantil uma matéria sobre **o fechamento da biblioteca pública**. Para isso, conversa com moradores que pensam diferente, consulta fontes e separa fato de opinião e de manipulação. A distopia não é "obra" de nenhuma corrente: todas as personagens, de todas as visões, são afetadas pelo Feed, e algumas também o usam para manipular.

O problema da biblioteca foi escolhido porque cada corrente tem uma posição genuína e defensável sobre ele (eficiência e liberdade de escolha; preservar uma instituição da comunidade; um bem público que não depende do lucro; serviço público financiado por impostos, com reforma da gestão) e porque não remete a um episódio político recente.

| Código | Funcionalidade |
|--------|----------------|
| J1 | Mapa de Novátria com os locais (praça, escola, mercado, biblioteca, rádio comunitária…); cada local é uma tela fixa |
| J2 | Diálogos em árvore com personagens fictícias que defendem visões diferentes, cada uma com seus melhores argumentos. Todas seguem o mesmo padrão de investigação: "Qual é a sua posição?", "Por que você pensa assim?", "De onde vem essa informação?", "E quem discorda, o que diria?". Opções de uso único somem depois de usadas |
| J3 | Fichas das 4 correntes, desbloqueadas pelas conversas, todas com o mesmo modelo (ver abaixo) |
| J4 | Checagem de fontes: posts, manchetes e falas são classificados como **fato verificável**, **opinião ou valor** ou **manipulação**. Fatos têm resposta checável; opiniões não têm resposta certa. Cada caso termina com uma explicação, e os exemplos de manipulação vêm de todas as visões e também de fontes sem lado (golpes, caça-cliques) |
| J5 | Comparação de propostas: diante do fechamento da biblioteca, o jogador vê como cada corrente propõe resolver, com prós, contras e valores em jogo, sem uma resposta "certa" |
| J6 | Caderno do jogador: guarda as fichas, os argumentos ouvidos e as fontes consultadas |
| J7 | Fechamento: você monta a matéria escolhendo argumentos e fontes. A avaliação considera três critérios: fatos com fonte, opiniões atribuídas a quem as disse e visões apresentadas com justiça. **Nunca** a posição escolhida. O jogo não dá um "rótulo ideológico" ao jogador |
| J8 | Progresso: flags de evento + inventário salvos em JSON (1 slot), com autosave |
| J9 | Objetos interativos: cada objeto da cena responde a Olhar, Usar e Falar com falas próprias; um item coletado some da cena nas visitas seguintes; recusas genéricas se alternam e nunca falam de correntes |
| J10 | Cenas de entrada: entrar num local pela primeira vez pode disparar uma sequência roteirizada (ex.: a apresentação de uma personagem) |
| J11 | Sem derrota: ações erradas geram falas explicativas, nunca game over (C2) |

**As 4 correntes da V1:** liberalismo, conservadorismo, socialismo e social-democracia. Elas formam o núcleo clássico do debate político moderno e se equilibram: duas mais à esquerda e duas mais à direita ou ao centro. Outras correntes entram nos próximos capítulos; o autoritarismo, de esquerda e de direita, pode ser um tema transversal de um capítulo futuro (seção 9).

**Modelo de ficha (igual para todas, com tamanho semelhante):**

1. Ideia central em uma frase, escrita como um defensor a escreveria.
2. Valores que prioriza.
3. Como vê o papel do Estado, do mercado e da sociedade.
4. Origem histórica e pensadores de referência.
5. O que propõe para o problema do capítulo.
6. Principais críticas que recebe, de mais de um lado.
7. Confusões de nome (só terminologia: ex.: "liberal" no Brasil e nos EUA; conservador e reacionário; socialismos democráticos e revolucionários; a corrente social-democrata e partidos com nomes parecidos).
8. Fontes.

Ideias centrais, a serem refinadas e com as fontes registradas na Fase 4:

- **Liberalismo:** a liberdade individual e os direitos de cada pessoa vêm em primeiro lugar, com um Estado limitado pela lei e uma economia baseada na livre iniciativa.
- **Conservadorismo:** as tradições, as instituições e a experiência acumulada da sociedade têm valor, e as mudanças devem ser graduais e prudentes.
- **Socialismo:** a riqueza é produzida coletivamente, e por isso os meios de produção devem ser de propriedade ou controle social, para que seus frutos sirvam ao conjunto da sociedade.
- **Social-democracia:** a economia de mercado deve conviver com um Estado de bem-estar que garanta direitos sociais e reduza desigualdades, por meio de reformas democráticas.

---

## 6. Princípios de conteúdo

Valem para todo texto, diálogo, ficha, imagem, som e mecânica do jogo, e são conferidos na revisão de cada PR de conteúdo.

| Código | Princípio |
|--------|-----------|
| C1 | **Equilíbrio e honestidade.** Apresentar as ideologias pelas ideias centrais de cada uma, sem caricaturar nem favorecer nenhuma |
| C2 | **Pensamento crítico, não conclusões prontas.** Estimular o jogador a comparar argumentos, checar fontes e reconhecer manipulação, em vez de entregar respostas |
| C3 | **A distopia é recurso narrativo.** Ela existe para provocar reflexão e não é associada a um lado político específico |
| C4 | **Fatos com fontes e respeito a pessoas reais.** Todo conteúdo factual tem fonte registrada, e nenhuma pessoa real é retratada de forma ofensiva |
| C5 | **Teste do defensor.** Antes do merge, a descrição de cada corrente passa pela pergunta: "uma pessoa que defende esta corrente se reconheceria neste texto?". Nenhum político vivo ou partido atual aparece ou é aludido; pensadores históricos são citados apenas por suas ideias e obras |
| C6 | **Equilíbrio não é falso equilíbrio.** As correntes e seus valores recebem tratamento igual, mas fatos verificáveis não são relativizados |

### 6.1 Salvaguardas de equilíbrio nas mecânicas

| Código | Salvaguarda |
|--------|-------------|
| E1 | Nenhuma flag representa alinhamento ideológico; não existe "medidor de corrente". As flags registram só ações de investigação (ouviu, perguntou a fonte, checou, comparou) |
| E2 | A avaliação da matéria (J7) lê apenas flags de investigação. Um teste de **troca de correntes** garante que duas matérias de mesma qualidade, com as correntes permutadas, recebem a mesma nota |
| E3 | Mesmo espaço para cada corrente: as personagens de cada corrente têm a mesma estrutura de diálogo (tópicos e níveis), conferida por teste a partir dos dados marcados com `corrente` |
| E4 | Recusas genéricas e humor nunca falam de correntes; o humor vem dos absurdos do Feed (P4) |
| E5 | Exemplos de manipulação ficam marcados pela origem nos dados, e um teste confere que se distribuem por igual entre as 4 correntes, além dos exemplos sem lado |

---

## 7. Desempenho, qualidade e entrega

- **Desempenho:** 60 FPS estáveis em computadores modestos de escola; o jogo abre em poucos segundos.
- **Testes:** `pytest`; regras do domínio e roteiros testados sem janela e telas testadas com o driver `dummy` do SDL. Testes de conteúdo: toda ficha tem fonte, todo ID de texto existe e as salvaguardas E2, E3 e E5.
- **Lint:** `ruff` (`line-length = 100`, regras `E, F, W, I, UP, B, SIM, N`).
- **CI:** Ubuntu 24.04 com Python 3.11, 3.12 e 3.13, mais Windows com 3.11, e `fail-fast: false`.
- **Distribuição:** executável Windows (`.exe`), gerado pelo `release.yml` a partir de uma tag `v*` e conferido depois de publicado.
- **Documentação:** README com GIF, CONTRIBUTING, CLAUDE.md, LOG completo e notas de cada release.

---

## 8. Decisões tomadas

| # | Pergunta | Decisão | Motivo |
|---|----------|---------|--------|
| D1 | Onde fica o clone local? | `Documents\Estudos\UNIP\ProjetoExtensao\Politicalizando`, com o plano de desenvolvimento fora do repositório | Mesmo padrão da `V2_JogoCobrinha`, ao lado da pasta do plano |
| D2 | Público e faixa etária? | 14 anos ou mais (ensino médio, universitários e público da extensão) | Temas políticos e distopia pedem alguma maturidade; é a idade em que redes sociais e desinformação já fazem parte da rotina |
| D3 | Plataforma? | Windows `.exe` na V1; versão web (pygbag) fica para a próxima | O fluxo de release com executável já foi testado; a web exige adaptar o loop |
| D4 | Biblioteca? | Python 3.11+ e pygame-ce, com resolução lógica de 320×180 e `pygame.SCALED` | Já usada no método; roda no CI sem janela. O Pyxel limita a paleta e a fonte não tem acentos |
| D5 | Licença? | Código sob MIT; conteúdo educativo sob CC BY 4.0 | Professores podem reutilizar o material citando a fonte |
| D6 | Escopo da V1? | 1 cidade, 1 capítulo de 20 a 30 minutos, 4 correntes e a checagem de fontes | Entregar um capítulo completo em vez de vários pela metade (R3) |
| D7 | Versão? | `0.1.0` no desenvolvimento; `1.0.0` na entrega da V1 | Versionamento semântico do plano; a tag só é criada quando o João pedir |
| D8 | Como o jogador se move? | Telas fixas, sem personagem andando nem pathfinding; clicar num objeto já executa a ação | Economiza arte e código; nada no jogo depende de deslocamento |
| D9 | Controles? | Mouse e teclado na V1 | O point-and-click pede mouse; o teclado mantém a acessibilidade |
| D10 | Como salvar? | JSON, 1 slot, autosave ao entrar numa cena (só se houve mudança e nada está bloqueado) | Legível, seguro e testável; vários perfis de save ficam para a próxima |
| D11 | Como roteirizar cutscenes e diálogos? | Dados em TOML interpretados pelo domínio como geradores Python, executados por um diretor que bloqueia o input | Equivalente às corrotinas de motores comerciais, testável sem janela e revisável por quem não programa |
| D12 | Como usar referências de outros jogos? | Só como ideia de arquitetura e de mecânica. A referência atual é um relatório próprio de engenharia reversa do *Unusual Findings* (demo), guardado **fora do repositório**. Nada de código, textos, nomes, personagens ou assets é copiado | Respeito a direitos de terceiros (R8) |

**Perguntas respondidas na revisão de 2026-10-14:**

- **P1.** Nome da cidade: **Novátria** (nenhum município ou bairro real com esse nome foi encontrado).
- **P2.** As 4 correntes estão confirmadas.
- **P3.** Narração em **"você"**, com textos escritos sem adjetivos de gênero para a pessoa jogadora.
- **P4.** Tom **sério, com leveza pontual**: humor que vem dos absurdos do Feed, nunca às custas de uma corrente ou de quem pensa diferente.
- **P5.** **Sim**: um professor ou professora de Sociologia, Filosofia ou História revisa o conteúdo antes da Fase 4, e um grupo de estudantes testa o jogo antes da release.

---

## 9. Escopo

| Entra nesta versão (V1) | Fica para a próxima |
|-------------------------|---------------------|
| 1 cidade (Novátria) e 1 capítulo (20 a 30 min) | Novos capítulos e cidades |
| 4 correntes: liberalismo, conservadorismo, socialismo e social-democracia | Outras correntes (ex.: anarquismo, ecologismo político, libertarianismo, democracia cristã) e o autoritarismo como tema transversal |
| Fichas com fontes, no mesmo modelo para todas | Glossário completo e linha do tempo das ideias |
| Checagem de fontes (fato, opinião, manipulação) com casos explicados | Minijogos variados de checagem; combinar itens para "cruzar fontes" |
| Comparação de propostas para o problema do capítulo | Debates com várias rodadas |
| Caderno do jogador; save de 1 slot com autosave | Vários perfis de save e estatísticas |
| Telas fixas com objetos interativos (Olhar / Usar / Falar) | Personagem andando pelo cenário |
| Mouse e teclado | Controle de videogame |
| Executável Windows | Versão web (pygbag) e outras plataformas |
| Texto em português | Outros idiomas |
| Sons e trilha simples gerados por código | Dublagem e trilha elaborada |
| — | Material de apoio para professores (roteiro de aula) |

---

## 10. Roteiro em fases

| Fase | Foco | Itens | Pronto quando… |
|------|------|-------|----------------|
| 0. Fundação ✅ | Esqueleto, lint, CI, briefing | D1 a D7 | O jogo abre e fecha sem erro; lint e CI passando; `main` protegida |
| 1. Núcleo ✅ | Domínio e conteúdo como dados | D10, D11, J2, J3, J4, J8, J9, J10, E1 a E5, R5, C4 | Estado e save, textos por ID, diretor de ações, roteiros, diálogos, cenas e objetos interativos, fichas, checagem e avaliação da matéria modelados e testados sem janela; teste que exige fonte em toda ficha; testes de equilíbrio |
| 2. Fluxo principal | Capítulo jogável com formas simples | J1, J5, J6, J7, J11, I4, I8, I9 | O capítulo 1 pode ser jogado do início ao fim, com retângulos no lugar da arte, por mouse e por teclado |
| 3. Interface | Visual e som | I1 a I7, R7 | Arte gerada por código, fonte com acentos, menus e sons |
| 4. Conteúdo | Textos finais e revisão | C1 a C6, R1, R2, R6, R9, P5 | Todos os textos revisados pelo checklist de equilíbrio e pela revisão externa, fontes registradas e créditos completos |
| 5. Entrega | Portfólio e release | — | README com GIF, CI verde, `release.yml`, executável na release v1.0.0 conferido e LOG completo |

Marque ✅ na fase ao concluí-la e registre no LOG.
