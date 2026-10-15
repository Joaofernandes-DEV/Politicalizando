# Roteiro do capítulo 1 — A biblioteca de Novátria

Estrutura do primeiro capítulo: locais, personagens, o que se aprende de política e de história, flags e caminho do início ao fechamento. Este documento guia os PRs da Fase 2 (mapa, caderno, comparação, matéria e capítulo jogável) e a escrita dos textos na Fase 4. **Nenhum texto final está aqui**: as falas são descritas, não escritas, e os nomes das personagens, dos bairros e dos locais são decididos pelo João.

Estrutura aprovada pelo João em 2026-10-14 (briefing, D13 a D19). Tudo segue os princípios C1 a C8 e as salvaguardas E1 a E5 do [briefing](../briefing.md).

---

## 1. Resumo

Novátria é um município fictício brasileiro, com centro, bairros de alta renda, periferias e serviços públicos desiguais (D16). O jornal do grêmio da sua escola pede uma matéria sobre o fechamento da biblioteca pública municipal. Na praça, você conhece o Feed e aprende a checar um post. Depois, a cidade se abre:

- na biblioteca, os documentos mostram quem usa o serviço e de onde vem, e o arquivo conta a história da educação pública e das bibliotecas no Brasil;
- na prefeitura e no portal da transparência, você descobre quem decide o fechamento e como o orçamento é dividido;
- na Câmara Municipal, acompanha uma audiência pública sobre o orçamento e pode fazer uma pergunta;
- nos bairros e nos espaços públicos, conversa com quatro moradores que pensam diferente e vê como o fechamento afeta cada lugar.

Por fim, compara as propostas e monta a matéria, avaliada pelos três critérios do J7, nunca pela posição.

**Duração estimada:** 30 a 40 minutos (seção 7).

---

## 2. Três atos

### Ato 1 — A missão (escola e praça)

| Passo | Onde | O que acontece | Flag marcada |
|-------|------|----------------|--------------|
| 1 | Escola pública, sala do grêmio | A editoria do jornal apresenta a missão e os três critérios da matéria (fatos com fonte, opiniões atribuídas, visões com justiça) | `escola.editoria.missao` |
| 2 | Escola | Você recebe o celular, que dá acesso ao Feed. Um cartaz da escola mostra que ela é estadual, e a biblioteca, municipal: a primeira pista de que cada nível cuida de uma coisa | item `celular` |
| 3 | Praça central | Telões do Feed anunciam o fechamento. Um post serve de tutorial da checagem; é um caso **sem lado** (golpe ou caça-clique), para que o primeiro contato com a manipulação não aponte para nenhuma corrente | `<caso tutorial>.checou` |
| 4 | Praça | Checar o tutorial abre o mapa da cidade | (a flag do passo 3) |

Na praça do Ato 1 não há nenhum morador de corrente: ninguém "fala primeiro".

### Ato 2 — A investigação (cidade aberta, em qualquer ordem)

| Local | Quem está | O que se investiga |
|-------|-----------|--------------------|
| Biblioteca municipal (centro) | Bibliotecária (neutra) e um morador na sala de leitura | Relatório de uso (visitantes por bairro e por motivo), orçamento da biblioteca e o arquivo histórico (seção 4) |
| Prefeitura | Servidora ou servidor da Secretaria de Cultura (neutra) | Quem decide o fechamento (o Executivo) e o terminal do portal da transparência com o orçamento municipal (seção 3) |
| Câmara Municipal | Técnica ou técnico legislativo (neutra), vereadores em função institucional e um morador na galeria | A audiência pública sobre o orçamento, o papel da Câmara e a chance de fazer uma pergunta |
| Terminal de ônibus | Um morador | O caminho entre a periferia e o centro: tempo, custo e horários |
| Praça central (Ato 2) | Um morador | Casos do Feed e uma conversa |
| Bairro periférico (nome a definir) | Moradores sem corrente marcada | Condições de vida: a escola mais próxima sem sala de leitura, ônibus pouco frequente, ruas sem saneamento completo |
| Bairro de alta renda (nome a definir) | Moradores sem corrente marcada | Outras condições de vida: acesso fácil a internet e livrarias, e quem ali também usa a biblioteca |
| Escola, sala do grêmio | Editoria | Comparação de propostas e matéria (Ato 3), disponíveis desde já |

Nenhum local é pré-requisito de outro, e a ordem do mapa é fixa e não segue as correntes. Os dois bairros mostram a desigualdade pelas condições de vida e pelos dados, nunca por caricaturas de quem mora neles (C8): cada bairro tem pessoas diferentes entre si.

### Ato 3 — O fechamento (sala do grêmio)

- **Comparação de propostas (J5):** mostra lado a lado as propostas das correntes já ouvidas, com prós, contras e valores em jogo, sempre na ordem fixa das correntes e sem resposta certa. Ver a comparação marca `comparacao.comparou`.
- **Matéria (J7):** você escolhe as peças (fatos, opiniões e, sem saber, alguma manipulação) e decide citar a fonte e quem disse. A editoria comenta cada critério e explica o que faltou, sem rótulo e sem nota sobre a posição.
- **Sem bloqueio (D14, J11):** a matéria fica disponível desde o fim do Ato 1. Se você tentar escrever cedo, a editoria sugere investigar mais, mas não impede.

---

## 3. Política municipal na prática (J12)

O jogador aprende fazendo perguntas concretas sobre a biblioteca. Cada conceito aparece num documento, numa fala ou numa ação, nunca numa aula. As leis abaixo são reais (D16) e têm a fonte conferida e registrada na Fase 4; os números de Novátria são fictícios (D14).

| Pergunta do jogador | O que descobre | Onde | Base real (a conferir) |
|---------------------|----------------|------|------------------------|
| Quem cuida da biblioteca e quem cuida da escola? | Município, estado e União têm atribuições diferentes; a biblioteca é municipal, e a escola de ensino médio, estadual | Cartaz da escola, prefeitura | Constituição de 1988, arts. 23, 30 e 211; LDB (Lei 9.394/1996), arts. 10 e 11 |
| Quem decidiu fechar? | O Executivo municipal (prefeitura) administra os serviços e propõe o orçamento | Prefeitura | Constituição, art. 30 |
| Quem pode mudar isso? | A Câmara Municipal vota as leis do orçamento e fiscaliza o Executivo, com o apoio do Tribunal de Contas | Câmara | Constituição, arts. 29, 31 e 165 |
| De onde vem o dinheiro? | Impostos municipais (como IPTU e ISS) e transferências do estado e da União | Portal da transparência | Constituição, arts. 156, 158 e 159 |
| Por que a cultura perde verba? | Educação e saúde têm um mínimo obrigatório no orçamento; a cultura não tem | Portal, servidora da prefeitura | Constituição, art. 212; Lei Complementar 141/2012 |
| Como o orçamento é planejado? | Plano plurianual, diretrizes e lei orçamentária anual | Câmara, audiência | Constituição, art. 165 |
| Como saber o que a prefeitura gasta? | Portal da transparência e pedido de informação | Prefeitura | Lei de Acesso à Informação (Lei 12.527/2011); Lei Complementar 131/2009 |
| Como participar? | Audiência pública, pedido de informação e iniciativa popular de lei municipal | Câmara | Lei de Responsabilidade Fiscal (LC 101/2000), art. 48; Constituição, art. 29 |

**Na Câmara:** a audiência pública acontece "hoje", em qualquer momento do Ato 2. Você pode se inscrever para fazer uma pergunta. As perguntas disponíveis dependem do que você checou: quem leu o portal pode perguntar sobre a verba da cultura. Perguntar marca `camara.audiencia.perguntou` (participação, nunca posição). Os vereadores aparecem só em funções institucionais (conduzir a audiência, explicar o rito), sem partido e sem defender uma corrente.

---

## 4. Camada histórica (J14)

No arquivo da biblioteca, documentos e um painel ligam o fechamento de hoje à história da educação pública e das bibliotecas no Brasil. Cada informação é marcada pela origem (J13, C7):

- **Fato documentado:** marcos com data e fonte. Candidatos, a confirmar com fonte e com a revisão de História (P5): a chegada da Real Biblioteca ao Rio de Janeiro com a corte portuguesa (1810), a criação do Instituto Nacional do Livro (1937), a educação como direito de todos na Constituição de 1988 (art. 205) e o Sistema Nacional de Bibliotecas Públicas (1992).
- **Interpretação:** uma leitura de historiadores sobre o acesso desigual à educação e à leitura no Brasil, sempre com autor e obra, e com mais de uma interpretação quando houver debate.
- **Opinião de personagem:** o que a bibliotecária e os moradores acham dessa história, apresentado como opinião.

A história de Novátria (a fundação da biblioteca, recortes do jornal local) é fictícia e marcada como fonte do jogo (D14). A checagem segue com 3 classes neste capítulo; a classe "interpretação" estreia no capítulo de história (D18).

---

## 5. Personagens

| Personagem | Papel | Corrente |
|------------|-------|----------|
| Editoria do jornal do grêmio | Dá a missão, explica os critérios e comenta a matéria | nenhuma (neutra) |
| Bibliotecária | Mostra os documentos e o arquivo; prefere mostrar os dados a defender um lado | nenhuma (neutra) |
| Servidora ou servidor da prefeitura | Explica quem decide e como ler o portal da transparência | nenhuma (neutra) |
| Técnica ou técnico legislativo | Explica a audiência pública e o papel da Câmara | nenhuma (neutra) |
| Vereadores | Conduzem a audiência; só função institucional | nenhuma |
| Moradores dos bairros | Mostram as condições de vida de cada lugar | nenhuma marcada |
| Morador da biblioteca | Usa a sala de leitura | uma das 4 |
| Morador do terminal de ônibus | Espera o ônibus | uma das 4 |
| Morador da Câmara | Assiste à audiência na galeria | uma das 4 |
| Morador da praça | Passa pela praça no Ato 2 | uma das 4 |

**Espaços públicos usados por todos:** os quatro moradores de corrente estão em lugares que gente de todos os bairros e de todas as classes usa. O bairro onde cada um mora, a ocupação, a renda, a idade e a origem são variados e **não se correlacionam com a corrente** (C8, R11).

**Regra contra estereótipo (D13, C8, R2, R11):** nem o local, nem a ocupação, nem o bairro, nem a classe de um morador podem "combinar" com a corrente dele. Ficam proibidas, por exemplo:

- liberalismo no mercado, numa empresa ou no bairro de alta renda;
- conservadorismo associado a templo, a uma família tradicional caricata ou ao "antigo" da biblioteca;
- socialismo associado a fábrica, sindicato, periferia ou à universidade;
- social-democracia associada à prefeitura ou a um cargo público;
- qualquer corrente apresentada como "a da periferia" ou "a dos ricos", e qualquer grupo social apresentado como ingênuo, violento, privilegiado ou manipulado em bloco.

A distribuição das correntes pelos quatro espaços é decidida pelo João no PR do capítulo jogável, conferindo essa regra.

Cada morador é uma pessoa comum, afetada pelo Feed como todo mundo, e defende a sua posição sobre a biblioteca com os melhores argumentos da corrente (C1, C5). Nenhum é vilão, e ninguém é retratado como mais inteligente ou mais simpático que os outros.

**Mesma estrutura para os quatro (E3):** todos têm as mesmas quatro perguntas do J2, na mesma ordem e com os mesmos níveis:

1. "Qual é a sua posição?" — a posição sobre a biblioteca;
2. "Por que você pensa assim?" — os valores e o argumento;
3. "De onde vem essa informação?" — a fonte do que disse (um documento, um dado ou um post do Feed, que vira caso de checagem);
4. "E quem discorda, o que diria?" — a pessoa apresenta com honestidade a principal objeção que recebe.

As perguntas são de uso único e somem depois de feitas; a despedida fica sempre disponível.

---

## 6. Fatos, opiniões e manipulação

### Fontes reais e fontes do jogo (D14, D16)

- **Fontes reais** para tudo o que vale no Brasil de verdade: leis, instituições, história do Brasil, fichas, pensadores e técnicas de manipulação.
- **Fontes do jogo (fictícias)** para o que só existe em Novátria: o orçamento municipal, o relatório de uso da biblioteca, o diário oficial e o jornal da cidade. Elas aparecem marcadas assim para quem joga.
- Um fato do mundo real nunca usa fonte fictícia. A marca de fonte do jogo pede uma mudança em `dominio/fontes.py`, feita no PR dos primeiros documentos, com um teste que impede o uso dela nas fichas.

### Casos de checagem previstos

| Onde | Casos | Origem |
|------|-------|--------|
| Praça, Ato 1 | 1 tutorial | sem lado |
| Feed, Ato 2 (praça, terminal, Câmara) | 4 manipulações | uma de cada corrente (E5) |
| Feed, Ato 2 | 1 manipulação | sem lado |
| Portal da transparência e biblioteca | 2 fatos | fontes do jogo (números de Novátria) |
| Prefeitura ou Câmara | 1 fato | fonte real (uma regra da Constituição) |
| Qualquer local | 1 opinião | sem resposta certa |

São 10 casos. As manipulações de cada corrente usam técnicas diferentes, mas o mesmo peso, e nenhuma é mais grosseira que as outras.

### Peças da matéria

- **Fatos:** dos documentos da biblioteca, do portal e das regras do orçamento. A fonte pode ser citada quando o documento foi lido (`fonte_se`).
- **Opiniões:** uma por morador, disponível depois de "Qual é a sua posição?" e marcada com a corrente dele (justiça, E2).
- **Manipulações:** as dos casos do Feed, como armadilhas. A tela não avisa quais são.

---

## 7. Flags, caminhos e duração

### Flags de investigação (E1)

Os nomes são provisórios; a convenção é `<local ou personagem>.<ação>`. Nenhuma flag registra concordância, preferência ou alinhamento.

| Flag | Marcada quando | Libera |
|------|----------------|--------|
| `escola.editoria.missao` | a editoria apresenta a missão | a praça no mapa |
| `<caso tutorial>.checou` | o tutorial é checado | o mapa inteiro, a comparação e a matéria |
| `<morador>.posicao` | "Qual é a sua posição?" | a ficha da corrente (J3), a opinião na matéria e a proposta na comparação |
| `<morador>.porque`, `<morador>.fonte`, `<morador>.discorda` | as outras perguntas | o registro no caderno (J6) |
| `biblioteca.bibliotecaria.documentos` | a bibliotecária mostra os documentos | fatos na matéria |
| `biblioteca.arquivo.leu` | o arquivo histórico é lido | o registro no caderno |
| `prefeitura.portal.leu` | o portal da transparência é consultado | fatos do orçamento e uma pergunta na audiência |
| `<documento>.leu` | um documento é lido | a citação da fonte daquele fato |
| `camara.audiencia.perguntou` | você faz uma pergunta na audiência | o registro no caderno |
| `<caso>.checou`, `<caso>.acertou` | um caso é checado | o registro no caderno |
| `comparacao.comparou` | a comparação é vista com pelo menos duas propostas | o registro no caderno |
| `materia.publicou` | a matéria é entregue | o fim do capítulo |

### Caminhos

**Caminho mínimo** (cerca de 5 minutos): missão → tutorial na praça → matéria na sala do grêmio. É possível terminar, e a avaliação mostra o que faltou. Não há derrota (J11).

**Caminho completo** (30 a 40 minutos):

| Parte | Tempo |
|-------|-------|
| Ato 1: missão e tutorial | ~3 min |
| 4 conversas de cerca de 3 min | ~12 min |
| Biblioteca, documentos e arquivo | ~4 min |
| Prefeitura e portal da transparência | ~3 min |
| Câmara e audiência pública | ~4 min |
| Bairros | ~3 min |
| 10 casos de checagem | ~5 min |
| Comparação e matéria | ~6 min |

---

## 8. Em aberto

Decisões do João, a tomar no PR indicado:

- nomes dos bairros, dos locais e das personagens, e o visual de Novátria e de cada personagem (Fase 3; antes da arte, o João mostra o exemplo da tela de início do jogo dele);
- a distribuição das correntes pelos quatro espaços públicos (seção 5), no PR `feat/capitulo-1-jogavel`;
- se a matéria pode ser reescrita depois do comentário da editoria antes de publicar (`feat/tela-da-materia`);
- o que o caderno mostra de cada conversa e de cada documento (`feat/caderno`);
- o formato da marca de origem (fato documentado, interpretação, opinião) e da fonte do jogo (PR dos primeiros documentos);
- os marcos históricos e as interpretações do arquivo, com a revisão de História (Fase 4, P5).
