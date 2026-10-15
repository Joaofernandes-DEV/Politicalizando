# Roteiro do capítulo 1 — A biblioteca de Novátria

Estrutura do primeiro capítulo: locais, personagens, flags e caminho do início ao fechamento. Este documento guia os PRs da Fase 2 (mapa, caderno, comparação, matéria e capítulo jogável) e a escrita dos textos na Fase 4. **Nenhum texto final está aqui**: as falas são descritas, não escritas, e os nomes das personagens e dos locais são decididos pelo João.

Estrutura aprovada pelo João em 2026-10-14 (briefing, D13 e D14). Tudo segue os princípios C1 a C6 e as salvaguardas E1 a E5 do [briefing](../briefing.md).

---

## 1. Resumo

Você recebe do jornal do grêmio a missão de escrever uma matéria sobre o fechamento da biblioteca pública de Novátria. Na praça, conhece o Feed e aprende a checar um post. Depois, o mapa abre a cidade: você consulta os documentos da biblioteca, conversa com quatro moradores que pensam diferente e checa o que circula no Feed. Por fim, compara as propostas e monta a matéria, que é avaliada pelos três critérios do J7, nunca pela posição.

**Duração estimada:** 20 a 30 minutos (seção 6).

---

## 2. Três atos

### Ato 1 — A missão (escola e praça)

| Passo | Onde | O que acontece | Flag marcada |
|-------|------|----------------|--------------|
| 1 | Escola, sala do grêmio | A pessoa que edita o jornal apresenta a missão e os três critérios da matéria (fatos com fonte, opiniões atribuídas, visões com justiça) | `escola.editoria.missao` |
| 2 | Escola | Você recebe o celular, que dá acesso ao Feed | item `celular` |
| 3 | Praça | Telões do Feed; um post de exemplo serve de tutorial da checagem. É um caso **sem lado** (um golpe ou caça-clique), para que o primeiro contato com a manipulação não aponte para nenhuma corrente | `<caso tutorial>.checou` |
| 4 | Praça | Checar o tutorial abre o mapa da cidade | (a flag do passo 3) |

Na praça do Ato 1 não há nenhum morador de corrente: ninguém "fala primeiro".

### Ato 2 — A investigação (cidade aberta, em qualquer ordem)

O mapa (J1) libera ao mesmo tempo:

| Local | Quem está | Para quê |
|-------|-----------|----------|
| Biblioteca | Bibliotecária (neutra) e um morador | Documentos do problema (fatos) e uma conversa |
| Praça | Um morador (aparece no Ato 2) | Uma conversa e casos do Feed |
| Mercado | Um morador | Uma conversa e casos do Feed |
| Rádio comunitária | Um morador | Uma conversa e casos do Feed |
| Escola, sala do grêmio | Editoria | Comparação de propostas e matéria (Ato 3), disponíveis desde já |

Nenhum local é pré-requisito de outro, e a ordem do mapa é fixa e não segue as correntes.

### Ato 3 — O fechamento (sala do grêmio)

- **Comparação de propostas (J5):** mostra lado a lado as propostas das correntes já ouvidas, com prós, contras e valores em jogo, sempre na ordem fixa das correntes e sem resposta certa. Ver a comparação marca uma flag de investigação (`comparou`).
- **Matéria (J7):** você escolhe as peças (fatos, opiniões e, sem saber, alguma manipulação) e decide citar a fonte e quem disse. A editoria comenta cada critério e explica o que faltou, sem rótulo e sem nota sobre a posição.
- **Sem bloqueio (D14, J11):** a matéria fica disponível desde o fim do Ato 1. Se você tentar escrever cedo, a editoria sugere investigar mais, mas não impede. A avaliação mostra o que faltou.

---

## 3. Personagens

| Personagem | Papel | Corrente |
|------------|-------|----------|
| Editoria do jornal do grêmio | Dá a missão, explica os critérios e comenta a matéria | nenhuma (neutra) |
| Bibliotecária | Mostra os documentos e os números do fechamento; diz que prefere mostrar os dados a defender um lado | nenhuma (neutra) |
| Morador da biblioteca | Frequenta a biblioteca | uma das 4 |
| Morador da praça | Passa pela praça | uma das 4 |
| Morador do mercado | Trabalha ou faz compras no mercado | uma das 4 |
| Morador da rádio | Participa da rádio comunitária | uma das 4 |

**Regra contra estereótipo (D13, R2):** nem o local nem a ocupação de um morador podem "combinar" com a corrente dele. Ficam proibidas combinações que reforçam um clichê, por exemplo:

- liberalismo no mercado ou numa empresa;
- conservadorismo associado a templo, a uma família tradicional caricata ou ao "antigo" da biblioteca;
- socialismo associado a fábrica, sindicato ou à rádio *comunitária* por ser coletiva;
- social-democracia associada à prefeitura ou a um cargo público.

**Distribuição proposta** (a confirmar pelo João no PR do capítulo jogável):

| Local | Corrente |
|-------|----------|
| Biblioteca | liberalismo |
| Praça | social-democracia |
| Mercado | socialismo |
| Rádio comunitária | conservadorismo |

Cada morador é uma pessoa comum, afetada pelo Feed como todo mundo, e defende a sua posição sobre a biblioteca com os melhores argumentos da corrente (C1, C5). Nenhum é vilão, e ninguém é retratado como mais inteligente ou mais simpático que os outros.

**Mesma estrutura para os quatro (E3):** todos têm as mesmas quatro perguntas do J2, na mesma ordem e com os mesmos níveis:

1. "Qual é a sua posição?" — a posição sobre a biblioteca;
2. "Por que você pensa assim?" — os valores e o argumento;
3. "De onde vem essa informação?" — a fonte do que disse (pode ser um documento, um dado ou um post do Feed, que vira caso de checagem);
4. "E quem discorda, o que diria?" — a pessoa apresenta com honestidade a principal objeção que recebe.

As perguntas são de uso único e somem depois de feitas; a despedida fica sempre disponível.

---

## 4. Fatos, opiniões e manipulação

### Fatos do mundo do jogo (D14)

Novátria é fictícia. Os fatos sobre o problema do capítulo (orçamento da biblioteca, horários, número de visitantes, data do fechamento) são **fatos do mundo do jogo**: checáveis em documentos que existem dentro do jogo, como o diário oficial de Novátria, o relatório anual da biblioteca e o painel de visitantes. Esses documentos são marcados nos dados como **fontes do jogo (fictícias)** e aparecem assim para quem joga.

Fontes reais continuam obrigatórias para tudo o que fala do mundo real (C4): as fichas das correntes, os pensadores, as técnicas de manipulação e qualquer dado histórico. Um fato do mundo real nunca usa fonte fictícia.

Isso pede uma mudança no domínio (`dominio/fontes.py`), feita no PR que trouxer os primeiros documentos: a `Fonte` ganha a marca de fonte do jogo, e um teste impede o uso dela nas fichas.

### Casos de checagem previstos

| Onde | Casos | Origem |
|------|-------|--------|
| Praça, Ato 1 | 1 tutorial | sem lado |
| Feed, Ato 2 (praça, mercado, rádio) | 4 manipulações | uma de cada corrente (E5) |
| Feed, Ato 2 | 1 manipulação | sem lado |
| Biblioteca | 1 ou 2 fatos | documentos do jogo |
| Qualquer local | 1 opinião | sem resposta certa |

São 8 ou 9 casos. As manipulações de cada corrente usam técnicas diferentes, mas o mesmo peso, e nenhuma é mais grosseira que as outras.

### Peças da matéria

- **Fatos:** um por documento conferido na biblioteca. A fonte pode ser citada quando o documento foi lido (`fonte_se`).
- **Opiniões:** uma por morador, disponível depois de "Qual é a sua posição?" e marcada com a corrente dele (justiça, E2).
- **Manipulações:** as dos casos do Feed, como armadilhas. Quem checou o caso tende a reconhecê-las, mas a tela não avisa.

---

## 5. Flags de investigação (E1)

Os nomes abaixo são provisórios; a convenção é `<local ou personagem>.<ação>`. Nenhuma flag registra concordância, preferência ou alinhamento.

| Flag | Marcada quando | Libera |
|------|----------------|--------|
| `escola.editoria.missao` | a editoria apresenta a missão | a praça no mapa |
| `<caso tutorial>.checou` | o tutorial é checado | o mapa inteiro, a comparação e a matéria |
| `<morador>.posicao` | "Qual é a sua posição?" | a ficha da corrente (J3), a opinião na matéria e a proposta na comparação |
| `<morador>.porque`, `<morador>.fonte`, `<morador>.discorda` | as outras perguntas | o registro no caderno (J6) |
| `biblioteca.bibliotecaria.documentos` | a bibliotecária mostra os documentos | os fatos na matéria |
| `<documento>.leu` | um documento é lido | a citação da fonte daquele fato |
| `<caso>.checou`, `<caso>.acertou` | um caso é checado | o registro no caderno |
| `comparacao.comparou` | a comparação é vista com pelo menos duas propostas | o registro no caderno |
| `materia.publicou` | a matéria é entregue | o fim do capítulo |

---

## 6. Caminhos e duração

**Caminho mínimo** (cerca de 5 minutos): missão → tutorial na praça → matéria na sala do grêmio. É possível terminar, e a avaliação mostra que faltaram fatos, opiniões e visões. Não há derrota (J11).

**Caminho completo** (20 a 30 minutos):

| Parte | Tempo |
|-------|-------|
| Ato 1: missão e tutorial | ~3 min |
| 4 conversas de cerca de 3 min | ~12 min |
| Biblioteca e documentos | ~2 min |
| 8 ou 9 casos de checagem | ~5 min |
| Comparação de propostas | ~3 min |
| Matéria e comentário da editoria | ~3 min |

---

## 7. Em aberto

Decisões do João, a tomar no PR indicado:

- nomes de Novátria, dos locais e das personagens, e o visual de cada uma (Fase 3; antes da arte, o João mostra o exemplo da tela de início do jogo dele);
- a distribuição das correntes pelos locais (seção 3), no PR `feat/capitulo-1-jogavel`;
- se a matéria pode ser reescrita depois do comentário da editoria antes de publicar (`feat/tela-da-materia`);
- o que o caderno mostra de cada conversa (`feat/caderno`);
- o formato da marca de fonte do jogo (PR dos primeiros documentos).
