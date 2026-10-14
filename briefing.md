# Briefing — Politicalizando V1

Diagnóstico, decisões e roteiro da primeira versão. Este documento vem antes do código e é atualizado quando uma decisão muda; cada mudança é registrada no [LOG.md](LOG.md).

> **Situação:** Fase 0 (fundação) concluída; próxima: Fase 1 (núcleo). As seções marcadas com **[RASCUNHO]** tratam de conteúdo e narrativa e ainda vão ser revisadas em conjunto antes da Fase 1.

---

## 1. Visão geral

**O que é:** um jogo 2D em pixel art que ensina o que são as ideologias políticas e como se informar sobre política, para que a pessoa jogadora compreenda o mundo atual e desenvolva um pensamento crítico sólido. A ambientação é contemporânea e distópica.

**O que ele não é:** propaganda. O jogo não diz em quem votar nem qual corrente está certa. Ele ensina a **entender** cada corrente pelos seus próprios argumentos, a **comparar** propostas e a **reconhecer** manipulação, venha de onde vier (ver os princípios de conteúdo, seção 6).

**Objetivo da V1:** um capítulo curto, completo e bem acabado, jogável de ponta a ponta em 20 a 30 minutos, que sirva de base para os capítulos seguintes e possa ser usado em sala de aula e em ações do projeto de extensão.

**Público:** pessoas de **14 anos ou mais**, como estudantes do ensino médio, universitários e o público das ações de extensão da UNIP. A linguagem é acessível, sem jargão desnecessário, e não pressupõe conhecimento prévio de política.

---

## 2. Ponto de partida e riscos

O projeto começa do zero: não há código anterior nem bugs a corrigir. Por isso, este diagnóstico lista os **riscos** que o projeto precisa controlar desde o início. Cite os códigos no LOG e nos PRs quando uma mudança tratar de um deles.

| Código | Risco | Como controlar |
|--------|-------|----------------|
| R1 | O jogo ser lido como propaganda de um lado | Princípios C1 a C5, revisão de equilíbrio de todo texto antes do merge (checklist no CONTRIBUTING) |
| R2 | Caricaturar uma corrente (descrever pelo que os adversários dizem dela) | Fichas com o mesmo modelo para todas; teste do "defensor se reconheceria?" (C5) |
| R3 | Escopo crescer e o capítulo ficar pela metade | Tabela de escopo (seção 9); novidades vão para "Fica para a próxima" |
| R4 | Virar uma apostila com botões (texto demais, pouca decisão) | Toda cena pede uma ação do jogador; textos curtos, com aprofundamento opcional nas fichas |
| R5 | Informação factual errada ou sem fonte | Fontes registradas junto do conteúdo (C4); conteúdo como dados revisáveis |
| R6 | A distopia ser associada a um partido, governo ou corrente real | O antagonista é um mecanismo (desinformação, polarização), não uma ideologia (C3) |
| R7 | Fonte pixel sem acentos do português | Usar a VT323 (OFL), que já desenhou bem os acentos no Jogo da Cobrinha (I2) |

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
│   ├── jogo.py                     # janela, loop e troca de estados
│   ├── dominio/                    # regras puras, sem pygame
│   ├── estados/                    # telas: título, menu, cenas, fichas
│   ├── ui/                         # texto, caixa de diálogo, botões
│   └── assets/                     # gerados por ferramentas/
├── ferramentas/                    # geradores de assets e empacotador
├── docs/                           # GIF e notas de release (Fase 5)
└── tests/
```

**Decisões técnicas:**

- **Python 3.11+ e pygame-ce** (D4): o fluxo já foi testado no Jogo da Cobrinha, roda no CI sem janela e o `pygame.SCALED` mantém a pixel art nítida.
- **Resolução lógica de 320×180** (16:9), ampliada por um fator inteiro pelo `pygame.SCALED`.
- **Domínio sem pygame:** ideologias, diálogos, checagem de fontes e progresso ficam em `dominio/`; `tests/test_dominio.py` impede que o pygame entre ali.
- **Conteúdo como dados [proposta para a Fase 1]:** textos, diálogos e fichas em arquivos de dados (ex.: TOML) separados do código, com o campo de fontes obrigatório. Assim o conteúdo pode ser revisado por quem não programa, e um teste confere que nenhuma ficha está sem fonte.
- **Assets por código:** sprites e sons gerados por scripts determinísticos em `ferramentas/`.

---

## 4. Interface

| Código | Item |
|--------|------|
| I1 | Pixel art em 320×180 com paleta restrita, gerada por código. Clima distópico (cores frias, telas e painéis luminosos), sem símbolos de partidos ou movimentos reais |
| I2 | Fonte VT323 (OFL) para todo o texto, com acentos do português conferidos |
| I3 | Caixa de diálogo com texto que aparece aos poucos; uma tecla completa e a seguinte avança |
| I4 | Controles só por teclado: setas/WASD, Enter/Espaço para confirmar e Esc para voltar ou pausar |
| I5 | Leitura sem pressa: nenhum texto com tempo limite, contraste alto e velocidade do texto ajustável |
| I6 | Efeitos sonoros e trilha simples, gerados por código (Fase 3) |
| I7 | Menus: título, jogar, como jogar, fichas, créditos e fontes, sair |

---

## 5. Funcionalidades [RASCUNHO]

**Premissa narrativa (proposta):** numa cidade fictícia de hoje (nome a definir, ver P1), quase toda a informação passa por um único aplicativo, o **Feed**, cujo algoritmo premia o que gera mais raiva e engajamento. A protagonista ou o protagonista (a definir, P3), estudante de 17 anos, precisa escrever para o jornal do grêmio estudantil uma matéria sobre um problema real da cidade (ex.: o fechamento da biblioteca pública ou o preço da passagem do ônibus). Para isso, conversa com moradores que pensam diferente, consulta fontes e separa fato de manipulação. A distopia não é "obra" de nenhuma corrente: todas as personagens, de todas as visões, são afetadas pelo Feed, e algumas também o usam para manipular.

| Código | Funcionalidade |
|--------|----------------|
| J1 | Navegação entre os locais da cidade (praça, escola, mercado, biblioteca, rádio comunitária…) por um mapa de cenas |
| J2 | Diálogos com personagens fictícias que defendem visões diferentes sobre o problema do capítulo, cada uma com seus melhores argumentos |
| J3 | Fichas das 4 correntes, desbloqueadas pelas conversas, todas com o mesmo modelo (ver abaixo) |
| J4 | Checagem de fontes: o jogador recebe posts, manchetes e falas e avalia quem disse, qual a evidência, o que outras fontes dizem e se há apelo emocional. Cada caso termina com uma explicação, e os exemplos de manipulação vêm de todas as visões |
| J5 | Comparação de propostas: diante do problema do capítulo, o jogador vê como cada corrente propõe resolvê-lo, com prós, contras e valores em jogo, sem uma resposta "certa" |
| J6 | Caderno do jogador: guarda as fichas, os argumentos ouvidos e as fontes consultadas |
| J7 | Fechamento: o jogador monta a matéria escolhendo argumentos e fontes. A avaliação considera a qualidade das fontes e se as visões foram apresentadas com justiça, **nunca** a posição escolhida. O jogo não dá um "rótulo ideológico" ao jogador |
| J8 | Progresso simples: capítulo concluído e fichas desbloqueadas ficam salvos |

**As 4 correntes da V1 (proposta):** liberalismo, conservadorismo, socialismo e social-democracia. Elas formam o núcleo clássico do debate político moderno, e outras entram nos próximos capítulos (seção 9).

**Modelo de ficha (igual para todas, com tamanho semelhante):**

1. Ideia central em uma frase, escrita como um defensor a escreveria.
2. Valores que prioriza.
3. Como vê o papel do Estado, do mercado e da sociedade.
4. Origem histórica e pensadores de referência.
5. O que propõe para o problema do capítulo.
6. Principais críticas que recebe, de mais de um lado.
7. Fontes.

Esboço das ideias centrais, a ser revisado e com as fontes registradas na Fase 4:

- **Liberalismo:** a liberdade individual e os direitos de cada pessoa vêm em primeiro lugar, com um Estado limitado pela lei e uma economia baseada na livre iniciativa.
- **Conservadorismo:** as tradições, as instituições e a experiência acumulada da sociedade têm valor, e as mudanças devem ser graduais e prudentes.
- **Socialismo:** a desigualdade nasce da forma como a economia é organizada, e a riqueza e os meios de produção devem servir à coletividade, não a poucos.
- **Social-democracia:** a economia de mercado deve conviver com um Estado de bem-estar que garanta direitos sociais e reduza desigualdades, por meio de reformas democráticas.

---

## 6. Princípios de conteúdo

Valem para todo texto, diálogo, ficha, imagem e som do jogo, e são conferidos na revisão de cada PR de conteúdo.

| Código | Princípio |
|--------|-----------|
| C1 | **Equilíbrio e honestidade.** Apresentar as ideologias pelas ideias centrais de cada uma, sem caricaturar nem favorecer nenhuma |
| C2 | **Pensamento crítico, não conclusões prontas.** Estimular o jogador a comparar argumentos, checar fontes e reconhecer manipulação, em vez de entregar respostas |
| C3 | **A distopia é recurso narrativo.** Ela existe para provocar reflexão e não é associada a um lado político específico |
| C4 | **Fatos com fontes e respeito a pessoas reais.** Todo conteúdo factual tem fonte registrada, e nenhuma pessoa real é retratada de forma ofensiva |
| C5 | **[Proposta] Teste do defensor.** Antes do merge, a descrição de cada corrente passa pela pergunta: "uma pessoa que defende esta corrente se reconheceria neste texto?". Políticos em atividade não aparecem no jogo, e pensadores são citados apenas por suas ideias e obras |

---

## 7. Desempenho, qualidade e entrega

- **Desempenho:** 60 FPS estáveis em computadores modestos de escola; o jogo abre em poucos segundos.
- **Testes:** `pytest`; regras do domínio testadas sem janela e telas testadas com o driver `dummy` do SDL. Um teste confere que toda ficha tem fonte (a partir da Fase 1).
- **Lint:** `ruff` (`line-length = 100`, regras `E, F, W, I, UP, B, SIM, N`).
- **CI:** Ubuntu com Python 3.11, 3.12 e 3.13, mais Windows com 3.11, e `fail-fast: false`.
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

**Perguntas em aberto (para revisar juntos antes da Fase 1):**

- **P1.** Nome da cidade fictícia.
- **P2.** As 4 correntes estão confirmadas, ou alguma deve ser trocada?
- **P3.** Protagonista com gênero definido, escolhido pelo jogador ou neutro? Qual é o problema da cidade no capítulo 1?
- **P4.** Tom: sério e sóbrio ou com algum humor (sem ridicularizar ninguém)?
- **P5.** Alguém de fora (professor ou professora de Sociologia, Filosofia ou História) revisa o conteúdo antes da release?

---

## 9. Escopo

| Entra nesta versão (V1) | Fica para a próxima |
|-------------------------|---------------------|
| 1 cidade e 1 capítulo (20 a 30 min) | Novos capítulos e cidades |
| 4 correntes: liberalismo, conservadorismo, socialismo e social-democracia | Outras correntes (ex.: anarquismo, ecologismo político, libertarianismo, democracia cristã) |
| Fichas com fontes, no mesmo modelo para todas | Glossário completo e linha do tempo das ideias |
| Checagem de fontes com casos explicados | Minijogos variados de checagem |
| Comparação de propostas para o problema do capítulo | Debates com várias rodadas |
| Caderno do jogador e progresso simples | Vários perfis de save e estatísticas |
| Teclado | Controle de videogame e mouse |
| Executável Windows | Versão web (pygbag) e outras plataformas |
| Texto em português | Outros idiomas |
| Sons e trilha simples gerados por código | Dublagem e trilha elaborada |
| — | Material de apoio para professores (roteiro de aula) |

---

## 10. Roteiro em fases

| Fase | Foco | Itens | Pronto quando… |
|------|------|-------|----------------|
| 0. Fundação ✅ | Esqueleto, lint, CI, briefing | D1 a D7 | O jogo abre e fecha sem erro; lint e CI passando; `main` protegida |
| 1. Núcleo | Domínio e conteúdo como dados | J2, J3, J4, J8, R5, C4 | Ideologias, diálogos, checagem e progresso modelados e testados sem janela; teste que exige fonte em toda ficha; perguntas P1 a P5 respondidas |
| 2. Fluxo principal | Capítulo jogável com formas simples | J1, J5, J6, J7 | O capítulo 1 pode ser jogado do início ao fim, com retângulos no lugar da arte |
| 3. Interface | Visual e som | I1 a I7, R7 | Arte gerada por código, fonte com acentos, menus e sons |
| 4. Conteúdo | Textos finais e revisão | C1 a C5, R1, R2, R6 | Todos os textos revisados pelo checklist de equilíbrio, fontes registradas e créditos completos |
| 5. Entrega | Portfólio e release | — | README com GIF, CI verde, `release.yml`, executável na release v1.0.0 conferido e LOG completo |

Marque ✅ na fase ao concluí-la e registre no LOG.
