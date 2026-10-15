# Diário de Bordo — Politicalizando

Registro cronológico de **todas** as alterações feitas no projeto. Cada entrada traz a data, o que foi feito, os arquivos afetados e o motivo da mudança.

## Como registrar

- Uma entrada por mudança (ou por PR), **a mais recente no final**.
- Data e horário no formato `AAAA-MM-DD HH:MM` (horário local), no momento em que a mudança foi concluída.
- Descreva **o quê** mudou e **por quê**; o "como" detalhado fica no código e nos commits.
- Informe o número de testes antes e depois, e o que foi testado à mão (e o que ficou para conferir).
- Se a mudança trata de um item do [briefing.md](briefing.md), cite o código (ex.: `J4`, `R5`, `C1`).

Modelo:

```markdown
### AAAA-MM-DD HH:MM — Título curto

**Feito:**
- O que mudou (o "como" detalhado fica no código e nos commits).

**Arquivos:** `caminho/arquivo.py`, `tests/test_x.py` (novo), `LOG.md`.

**Motivo / observações:**
- Por que mudou, item do briefing resolvido (ex.: `B3`), limitações conhecidas e próximos passos.
```

---

## Entradas

### 2026-10-13 21:50 — Fase 0: fundação do projeto

**Feito:**
- Configuração do projeto: `pyproject.toml` (versão 0.1.0, pygame-ce, extra `[dev]` com pytest e ruff, ruff com `line-length = 100` e regras `E, F, W, I, UP, B, SIM, N`), `.gitignore` e licenças (MIT para o código, CC BY 4.0 para o conteúdo educativo).
- Esqueleto do jogo em `src/politicalizando/`: janela de 320×180 ampliada com `pygame.SCALED`, loop com troca de estados, tela de título provisória (Esc fecha) e a opção `--fechar-em SEGUNDOS` para testes automáticos.
- Pastas `dominio/` (regras puras, sem pygame), `estados/`, `ui/`, `assets/` e `ferramentas/` com as convenções.
- Testes: a versão do pacote igual à do `pyproject.toml`, a janela na resolução lógica, o Esc encerrando sem erro, o `--fechar-em` abrindo e fechando sozinho, e o domínio sem importar o pygame.
- CI (`ci.yml`): ruff e pytest no Ubuntu (Python 3.11, 3.12 e 3.13) e no Windows (3.11), com `fail-fast: false`.
- Documentação: `README.md`, `CONTRIBUTING.md` (com o checklist de equilíbrio do conteúdo), `CLAUDE.md` e `briefing.md` (visão geral, riscos R1 a R7, interface I1 a I7, funcionalidades J1 a J8, princípios de conteúdo C1 a C5, decisões D1 a D7, escopo e roteiro em fases).

**Arquivos:** `.gitignore`, `LICENSE`, `LICENCA-CONTEUDO.md`, `pyproject.toml`, `src/politicalizando/__init__.py`, `src/politicalizando/__main__.py`, `src/politicalizando/config.py`, `src/politicalizando/jogo.py`, `src/politicalizando/estados/__init__.py`, `src/politicalizando/estados/base.py`, `src/politicalizando/estados/titulo.py`, `src/politicalizando/dominio/__init__.py`, `src/politicalizando/ui/__init__.py`, `src/politicalizando/assets/.gitkeep`, `ferramentas/README.md`, `tests/conftest.py`, `tests/test_versao.py`, `tests/test_jogo.py`, `tests/test_dominio.py`, `.github/workflows/ci.yml`, `README.md`, `CONTRIBUTING.md`, `CLAUDE.md`, `briefing.md`, `LOG.md` (todos novos).

**Motivo / observações:**
- Início do projeto, seguindo o método do plano de desenvolvimento (Fase 0 e checklist da seção 11). Decisões D1 a D7 registradas no briefing.
- Testes: 0 → 5, todos passando localmente (Windows, Python 3.11.8, pygame-ce 2.5.8). `ruff check` e `ruff format --check` sem apontamentos.
- **Testado à mão (João):** a janela abriu com o título, a frase, a dica "Esc: sair" e a versão v0.1.0; a pixel art ficou nítida ao redimensionar; o Esc fechou o jogo sem erro (código de saída 0).
- As seções de conteúdo e narrativa do briefing (J1 a J8, as 4 correntes, C5) são **rascunho** para revisão conjunta; as perguntas P1 a P5 ficam em aberto até a Fase 1.
- A fonte e a frase da tela de título são provisórias (fonte final na Fase 3, `I2`).
- Pendente para concluir a Fase 0: CI verde no GitHub e proteção da `main`.

### 2026-10-13 21:57 — Fase 0 concluída: CI verde e `main` protegida

**Feito:**
- O CI do PR #1 passou nos 4 jobs (Ubuntu com Python 3.11, 3.12 e 3.13; Windows com 3.11), e o PR entrou na `main` por merge commit, com a branch apagada em seguida.
- A `main` foi protegida pelo `gh`: Pull Request obrigatório (sem aprovação mínima, por ser trabalho solo), os 4 checks do CI obrigatórios, branch em dia com a `main`, force-push e exclusão proibidos. O dono pode ignorar em emergência.
- A Fase 0 foi marcada como ✅ no roteiro do briefing, e a situação do README foi atualizada.

**Arquivos:** `briefing.md`, `README.md`, `LOG.md`.

**Motivo / observações:**
- Fecha o critério "Pronto quando…" da Fase 0 (o jogo abre e fecha sem erro; lint e CI passando; `main` protegida).
- Testes: 5 → 5 (só documentação).
- Antes, a `main` recebeu um único commit direto (o commit inicial vazio, autorizado pelo João), necessário porque o repositório estava vazio. Daqui em diante, tudo entra por PR.
- Próximo passo: revisar o rascunho de conteúdo do briefing, responder às perguntas P1 a P5 e iniciar a Fase 1 (núcleo) numa sessão nova.

### 2026-10-13 22:08 — CI: fixa o Ubuntu 24.04 nos jobs Linux

**Feito:**
- Os jobs Linux do `ci.yml` passam a usar `ubuntu-24.04` em vez de `ubuntu-latest`. O Windows continua em `windows-latest`.
- Os checks exigidos na proteção da `main` foram trocados para os novos nomes (`Lint e testes (ubuntu-24.04, Python 3.11/3.12/3.13)`), mantendo o do Windows.

**Arquivos:** `.github/workflows/ci.yml`, `LOG.md`.

**Motivo / observações:**
- O GitHub avisou que o `ubuntu-latest` migra para o Ubuntu 26 a partir de 2026-10-19. Fixar a versão evita que o CI quebre sozinho se o `setup-python` ainda não tiver o Python 3.11 pronto para o sistema novo.
- Testes: 5 → 5 (só CI).
- Rever a fixação quando o Ubuntu 26 estiver estável nas actions.

### 2026-10-14 16:59 — Revisão de conteúdo e arquitetura de aventura no briefing

**Feito:**
- Revisão conjunta das partes de conteúdo do briefing: Novátria como cidade (P1), as 4 correntes mantidas (P2), narração em "você" (P3), tom sério com leveza pontual (P4) e revisão externa por um professor ou professora (P5).
- Premissa ajustada: o dono do Feed nunca é revelado e o problema do capítulo é o fechamento da biblioteca pública. A frase do socialismo foi reescrita para ficar simétrica às outras, e a ficha ganhou o item "Confusões de nome".
- Checagem (J4) e avaliação da matéria (J7) passam a separar fato, opinião/valor e manipulação. Novo princípio C6 ("equilíbrio não é falso equilíbrio"), nova redação do C5 e salvaguardas de equilíbrio nas mecânicas (E1 a E5).
- Arquitetura de aventura point-and-click registrada: telas fixas sem personagem andando (D8), mouse e teclado (D9), save JSON de 1 slot com autosave (D10), roteiros em dados executados por geradores (D11) e uso só conceitual de referências externas (D12). Novos itens J9 a J11, I8, I9 e riscos R8 e R9; escopo e roteiro das Fases 1 e 2 atualizados.
- CONTRIBUTING e CLAUDE.md: checklist de equilíbrio ampliado (político vivo, falso equilíbrio, nenhuma métrica de alinhamento) e regra para referências de outros jogos.

**Arquivos:** `briefing.md`, `CONTRIBUTING.md`, `CLAUDE.md`, `LOG.md`.

**Motivo / observações:**
- Fecha as perguntas P1 a P5 exigidas para a Fase 1.
- Os padrões de arquitetura vieram de um relatório próprio de engenharia reversa do *Unusual Findings* (demo), usado só como referência conceitual. O relatório e o código decompilado ficam fora do repositório (`ProjetoExtensao\Referencias\`); uma cópia que estava em `ferramentas/` sem ser versionada foi enviada para a Lixeira antes deste PR. Nada foi copiado.
- Busca na web por "Novátria" não encontrou município ou bairro real com esse nome.
- Testes: 5 → 5 (só documentação).
- Próximo: PR `feat/estado-do-jogo` (flags, inventário, save JSON e autosave), o primeiro da Fase 1.

### 2026-10-14 17:13 — Fase 1: estado do jogo e save em JSON

**Feito:**
- `dominio/estado_jogo.py`: o `EstadoJogo` guarda as flags de evento, o inventário (na ordem de coleta) e a cena atual, e sabe se houve mudança desde o último save. Os IDs seguem um formato único (`biblioteca.ouviu_bibliotecaria`), para que erros de digitação nos dados dos próximos PRs falhem cedo. O estado vira dicionário e volta (`para_dict` / `de_dict`), com validação estrita.
- `persistencia.py`: save de 1 slot em `dados/save.json`, ao lado do jogo (do `.exe` empacotado ou da raiz do projeto), com gravação atômica (arquivo temporário + troca). Um save ilegível ou de versão futura gera erro e nunca é apagado. O `autosalvar` só grava se houve mudança e nada está bloqueado. A variável `POLITICALIZANDO_DADOS` troca a pasta.
- `tests/conftest.py`: fixture automática que aponta a pasta de dados para uma pasta temporária, para nenhum teste tocar no save real.
- Formato do save: `{"versao": 1, "cena_atual": ..., "flags": [...], "inventario": [...]}`, com as flags ordenadas.

**Arquivos:** `src/politicalizando/dominio/estado_jogo.py` (novo), `src/politicalizando/persistencia.py` (novo), `tests/conftest.py`, `tests/test_estado_jogo.py` (novo), `tests/test_persistencia.py` (novo), `LOG.md`.

**Motivo / observações:**
- Primeiro PR da Fase 1 (`D10`, `J8`). `E1` por construção: o estado só tem flags booleanas, itens e a cena, e um teste confere que o save não tem nenhum outro campo (pontuação, medidor de corrente).
- Pasta do save escolhida pelo João: `dados/` ao lado do jogo (portátil, combina com o `.gitignore`). Limitação: se o `.exe` ficar numa pasta sem permissão de escrita, o save falha; tratar a mensagem ao jogador na Fase 2.
- O "bloqueado" do autosave ainda vem de quem chama; passa a vir do diretor de ações (`feat/diretor-de-acoes`). A tela de título ainda não usa o save ("Continuar" entra na Fase 2).
- A exceção `SaveInvalido` mantém o nome em português, com `noqa: N818` (o ruff pede o sufixo "Error").
- Testes: 5 → 55, todos passando localmente (Windows, Python 3.11.8, pygame-ce 2.5.8). `ruff check` e `ruff format --check` sem apontamentos.
- **Testado à mão:** `python -m politicalizando --fechar-em 1` abriu e fechou com código 0, sem criar `dados/`. Nada mudou na tela, então não houve teste visual.
- Próximo: PR `feat/textos-por-id`.

### 2026-10-14 17:32 — Fase 1: textos por ID

**Feito:**
- `dominio/textos.py`: o catálogo `Textos` (um `Mapping` imutável de ID para `Texto`, com `id`, `texto` e `quem`) é lido do TOML com validação estrita. Os IDs usam o mesmo formato do `estado_jogo.py` (`titulo.frase`). Um ID inexistente gera erro com o ID na mensagem.
- Formato: cada tabela com `texto` é uma entrada, e o caminho dela é o ID. `quem` é opcional (o ID de quem fala); sem ele, o texto é narração ou interface. São recusados: sintaxe quebrada, ID repetido, ID fora do formato, texto vazio, `quem` inválido, chave a mais, valor solto e ID que é prefixo de outro texto.
- `conteudo/__init__.py` lê `conteudo/pt_BR/textos.toml` por `importlib.resources`; o `pyproject.toml` inclui os TOML no pacote.
- A tela de título passa a ler a frase e a dica "Esc: sair" do `textos.toml` (o `Jogo` carrega os textos ao iniciar). Nada muda na tela.
- `tests/test_textos_usados.py`: uma varredura com `ast` coleta todo `textos["id"]` do código e confere que todo ID usado existe, que nenhum texto ficou órfão e que o código só acessa textos com ID literal.
- README e CONTRIBUTING: textos de tela ficam no `textos.toml`, nunca no código.

**Arquivos:** `src/politicalizando/dominio/textos.py` (novo), `src/politicalizando/conteudo/__init__.py` (novo), `src/politicalizando/conteudo/pt_BR/textos.toml` (novo), `pyproject.toml`, `src/politicalizando/jogo.py`, `src/politicalizando/estados/titulo.py`, `tests/test_textos.py` (novo), `tests/test_textos_usados.py` (novo), `README.md`, `CONTRIBUTING.md`, `LOG.md`.

**Motivo / observações:**
- Segundo PR da Fase 1 (briefing, seção 3: "Textos por ID"; `D11`). Empilhado sobre o `feat/estado-do-jogo` (PR #5), que ainda não entrou na `main`.
- Decisões do João: o arquivo real tem só os textos em uso (os da tela de título); os exemplos com `quem` ficam nos testes, neutros e provisórios. `quem` é opcional. Os textos finais são da Fase 4.
- A leitura do arquivo fica em `conteudo/`, fora do domínio, pelo mesmo motivo da `persistencia.py`.
- Quando os roteiros, diálogos e cenas chegarem, cada tipo carregado dos dados expõe os IDs de texto que usa, e o teste de usados e órfãos passa a juntá-los aos do código. Quando houver personagens, um teste exige que todo `quem` seja uma personagem conhecida.
- Testes: 55 → 87, todos passando localmente (Windows, Python 3.11.8, pygame-ce 2.5.8). `ruff check` e `ruff format --check` sem apontamentos.
- Conferido o pacote: um wheel gerado fora do repositório contém `conteudo/pt_BR/textos.toml`, e `carregar_textos()` leu os textos da cópia instalada.
- **Testado à mão (João):** a tela de título ficou igual à de antes, e o Esc fechou o jogo (código de saída 0).
- Próximo: PR `feat/diretor-de-acoes`.

### 2026-10-14 17:38 — Fase 1: ações e diretor dos roteiros

**Feito:**
- `dominio/acoes.py`: as seis ações dos roteiros, imutáveis e validadas ao serem criadas. São elas `Fala` (um ID de texto), `Escolha` (IDs de texto das opções), `Esperar` (segundos), `MarcarFlag`, `DarItem` e `TrocarCena`. Um roteiro é um gerador que recebe o `EstadoJogo`, lê o estado direto e produz ações; a resposta de uma `Escolha` volta pelo `yield`.
- `dominio/diretor.py`: o `Diretor` executa uma sequência por vez. As ações instantâneas mudam o estado na hora, e o roteiro já vê o resultado na linha seguinte. Nas de espera, ele para: `confirmar()` encerra uma fala, `escolher(i)` devolve o índice ao roteiro e `atualizar(dt)` desconta o tempo. `ocupado` bloqueia o input e o autosave (`autosalvar(estado, bloqueado=diretor.ocupado)`).
- Erros de programação falham cedo e não travam o diretor em "ocupado": iniciar com outra sequência rodando, roteiro que não é gerador, item que não é ação, índice de escolha inválido e exceção dentro do roteiro.
- A varredura de `tests/test_textos_usados.py` passa a coletar também os IDs de `Fala("id")` e `Escolha(("a", "b"))` escritos em Python e acusa os não literais.

**Arquivos:** `src/politicalizando/dominio/acoes.py` (novo), `src/politicalizando/dominio/diretor.py` (novo), `tests/test_acoes.py` (novo), `tests/test_diretor.py` (novo), `tests/test_textos_usados.py`, `LOG.md`.

**Motivo / observações:**
- Terceiro PR da Fase 1 (`D11`, briefing seção 3: "API única de roteiro" e "Diretor com geradores Python"). Empilhado sobre o `feat/textos-por-id` (PR #6), que depende do #5; nenhum dos dois entrou na `main` ainda.
- Decisões do João: `TrocarCena` é instantânea no domínio (só muda `cena_atual`; o `Jogo` percebe e troca a tela; uma transição visual fica para a Fase 3), e a ligação do diretor ao `Jogo` (input, caixa de diálogo, autosave ao entrar na cena) entra no `feat/cenas-e-interacao`.
- `TirarItem` ficou de fora: não está no briefing e nenhum roteiro precisa dela ainda.
- Os roteiros de exemplo dos testes são neutros e provisórios; nenhum roteiro real entrou no jogo.
- Testes: 87 → 166, todos passando localmente (Windows, Python 3.11.8, pygame-ce 2.5.8). `ruff check` e `ruff format --check` sem apontamentos.
- **Testado à mão:** `python -m politicalizando --fechar-em 1` abriu e fechou com código 0. Nada mudou na tela, então não houve teste visual.
- Próximo: PR `feat/roteiros-em-dados`.

### 2026-10-14 17:48 — Fase 1: roteiros em dados

**Feito:**
- `dominio/roteiro.py`: os roteiros simples saem do código e vão para `conteudo/roteiros.toml`. Cada lista é um roteiro (o caminho é o ID) e cada passo tem exatamente uma ação: `fala`, `esperar`, `marcar_flag`, `dar_item` ou `trocar_cena`. A `Sequencia` gera as ações para o `Diretor` (`diretor.iniciar(sequencia.executar(estado))`), a mesma forma de uso dos roteiros especiais em Python.
- Validação estrita, com o ID do roteiro e o número do passo na mensagem. São recusados: sintaxe quebrada, ID fora do formato, valor solto, roteiro vazio, passo com zero ou duas ações, ação desconhecida, `escolha` (fica nas árvores de diálogo) e valor inválido na ação.
- `conteudo.carregar_roteiros()` lê o arquivo, e o `pyproject.toml` passa a empacotar também os TOML da raiz de `conteudo/`.
- O teste de IDs de texto usados e órfãos passa a juntar as falas dos roteiros às do código.
- Merges do João, na ordem: #5 (estado do jogo), #6 (textos por ID) e #7 (ações e diretor), todos por merge commit e com as branches apagadas. Auto-fix ligado no #7.

**Arquivos:** `src/politicalizando/dominio/roteiro.py` (novo), `src/politicalizando/conteudo/__init__.py`, `src/politicalizando/conteudo/roteiros.toml` (novo), `pyproject.toml`, `tests/test_roteiro.py` (novo), `tests/test_textos_usados.py`, `LOG.md`.

**Motivo / observações:**
- Quarto PR da Fase 1 (`D11`, briefing seção 3: "Roteiros em dados").
- Decisões do João: `escolha` fica fora dos roteiros em dados (os ramos são da árvore de diálogo); não há condições por passo por enquanto (a condição de disparo é da cena, no `feat/cenas-e-interacao`); o `roteiros.toml` começa só com o comentário de formato, e os exemplos ficam nos testes.
- O `roteiros.toml` fica fora de `pt_BR/` porque guarda só IDs; os textos ficam no `textos.toml` do idioma.
- Incidente nos merges: ao apagar a branch do #5, o GitHub fechou o #6, que ainda tinha base nela. A branch foi recriada no mesmo commit, o #6 foi reaberto com base na `main` e a branch foi apagada de novo; o #7 teve a base trocada para a `main` antes do merge do #6. Para PRs empilhados: trocar a base do PR de cima para a `main` **antes** de apagar a branch de baixo.
- Testes: 166 → 192, todos passando localmente (Windows, Python 3.11.8, pygame-ce 2.5.8). `ruff check` e `ruff format --check` sem apontamentos.
- Conferido o pacote: o wheel contém `conteudo/roteiros.toml` e `conteudo/pt_BR/textos.toml`, e os dois são lidos da cópia instalada.
- **Testado à mão:** `python -m politicalizando --fechar-em 1` abriu e fechou com código 0. Nada mudou na tela, então não houve teste visual.
- Próximo: PR `feat/arvore-de-dialogo`.

### 2026-10-14 17:59 — Fase 1: árvores de diálogo

**Feito:**
- `dominio/dialogo.py`: as árvores de diálogo ficam em `conteudo/dialogos.toml` e rodam no `Diretor` como um roteiro comum, só com as ações que já existiam. Cada nó tem `passos` no formato dos roteiros e depois oferece `opcoes`, segue sozinho (`vai_para`) ou termina.
- Escolher uma opção marca a flag `<diálogo>.<opção>` ("perguntou"). Ela esconde as opções de `uso_unico` (também nas conversas seguintes, porque vai no save) e alimenta as condições `se` e `se_nao`. Se todas as opções de um nó estiverem escondidas, o diálogo termina.
- Validação estrita, com o diálogo, o nó e a opção na mensagem: início e destinos existentes, `fim` reservado, nó vazio, `opcoes` e `vai_para` juntos, ids de opção repetidos no diálogo, textos repetidos no nó, nó que nunca é alcançado, laço só de `vai_para` (rodaria sem fim), chaves e tipos fora do formato.
- `dominio/correntes.py`: os IDs das 4 correntes (`liberalismo`, `conservadorismo`, `socialismo`, `social_democracia`), usados pela marcação opcional `corrente` dos diálogos.
- `roteiro.py`: a leitura dos passos virou a função `ler_passos`, usada também pelos nós de diálogo (sem mudar o comportamento dos roteiros).
- Testes de conteúdo: as falas e as opções dos diálogos entram no teste de IDs de texto usados e órfãos, e um teste novo exige que toda flag citada em `se` ou `se_nao` seja marcada por algum roteiro ou diálogo (pega erros de digitação). Na varredura do código, a marca `# ids-de-texto: dados` libera os usos cujos IDs vêm dos dados, como o motor de diálogos.

**Arquivos:** `src/politicalizando/dominio/roteiro.py`, `src/politicalizando/dominio/correntes.py` (novo), `src/politicalizando/dominio/dialogo.py` (novo), `src/politicalizando/conteudo/__init__.py`, `src/politicalizando/conteudo/dialogos.toml` (novo), `tests/test_dialogo.py` (novo), `tests/test_flags_exigidas.py` (novo), `tests/test_textos_usados.py`, `LOG.md`.

**Motivo / observações:**
- Quinto PR da Fase 1 (`J2`, `D11`, `E1`). O João fez o merge do #8 (roteiros em dados) antes deste PR.
- Decisões do João: a flag automática `<diálogo>.<opção>` é a base do uso único e das condições; as condições usam só flags (por item, quando uma cena precisar); os IDs das correntes ficam em `dominio/correntes.py`; o `dialogos.toml` começa só com o formato documentado, e os exemplos neutros ficam nos testes.
- `E1`: as únicas flags que um diálogo cria são as de "perguntou" das opções e as dos passos; a marcação `corrente` não vira flag (há teste). O teste `E3` (mesma estrutura de diálogo por corrente) entra no `feat/checagem-de-fontes`, como na ordem aprovada; este PR deixa a marcação pronta nos dados.
- Um teste confere que o exemplo do comentário do `dialogos.toml` é um diálogo válido, para a documentação não envelhecer.
- Testes: 192 → 247, todos passando localmente (Windows, Python 3.11.8, pygame-ce 2.5.8). `ruff check` e `ruff format --check` sem apontamentos.
- **Testado à mão:** `python -m politicalizando --fechar-em 1` abriu e fechou com código 0. Nada mudou na tela, então não houve teste visual.
- Próximo: PR `feat/cenas-e-interacao` (cenas, objetos com Olhar/Usar/Falar, disparo de roteiros e diálogos, e a ligação do diretor com o `Jogo`).

### 2026-10-14 18:10 — Fase 1: cenas e interação

**Feito:**
- `dominio/cenas.py`: as cenas ficam em `conteudo/cenas.toml`. Cada cena tem objetos com `id`, `nome` (ID de texto), `area` (x, y, largura e altura em 320×180, validada contra a tela) e respostas aos verbos Olhar, Usar e Falar. Uma resposta é uma lista de passos em linha, `{ roteiro = "id" }` ou `{ dialogo = "id" }`. As condições de objeto são `se` e `se_nao` (flags) e `se_item` e `se_nao_item` (itens): um item coletado pode fazer o objeto sumir (J9).
- `[recusas]` traz as falas genéricas de cada verbo, obrigatórias quando há cenas; um verbo sem resposta usa a próxima recusa daquele verbo, em rodízio determinístico.
- `dominio/interacao.py`: `objetos_visiveis` (na ordem do arquivo, que será a do Tab), `objeto_em` (o clique: o último objeto fica por cima e os invisíveis são ignorados) e `Interacao`, que transforma verbos e entradas em roteiros para o `Diretor`. `ao_entrar` marca `<cena>.visitou` e roda a `entrada` só na primeira visita (J10).
- `conteudo.carregar_cenas()` confere que todo roteiro e diálogo citado existe.
- Testes de conteúdo: os textos das cenas entram no teste de usados e órfãos; flags **e itens** exigidos precisam ter origem nos dados; nenhum roteiro ou diálogo fica sem uso por alguma cena; e o novo `tests/test_equilibrio.py` traz o teste `E4` (o texto das recusas não pode citar nenhuma corrente).

**Arquivos:** `src/politicalizando/dominio/cenas.py` (novo), `src/politicalizando/dominio/interacao.py` (novo), `src/politicalizando/conteudo/__init__.py`, `src/politicalizando/conteudo/cenas.toml` (novo), `tests/test_cenas.py` (novo), `tests/test_interacao.py` (novo), `tests/test_textos_usados.py`, `tests/test_flags_exigidas.py`, `tests/test_conteudo_sem_uso.py` (novo), `tests/test_equilibrio.py` (novo), `LOG.md`.

**Motivo / observações:**
- Sexto PR da Fase 1 (`J9`, `J10`, `D8`, `E4`; prepara `I4` e `I9`). O João fez o merge do #9 (árvores de diálogo) e ligou o auto-merge e a exclusão automática de branches no repositório: daqui em diante, cada PR entra sozinho quando o CI fica verde.
- Decisões do João: a ligação do diretor com o `Jogo` (input, caixa de diálogo, autosave ao entrar na cena) passa para o primeiro PR da Fase 2, junto com a primeira tela de cena (antes estava prevista para este PR); a flag `<cena>.visitou` é automática e a `entrada` roda só na primeira visita; condições de objeto por flags e itens; recusas por verbo em rodízio; objetos com `nome` e `area`. O `cenas.toml` começa só com o formato documentado; as cenas e os textos das recusas chegam na Fase 2.
- `ao_entrar` deve ser chamado pelo jogo quando a cena muda **e** o diretor está livre, para não iniciar uma sequência por cima de outra (uma `TrocarCena` dentro de um roteiro só dispara a entrada depois que ele termina).
- `dominio/cenas.py` importa `config.py` (resolução lógica), que não importa o pygame; o teste do domínio sem pygame continua passando.
- Testes: 247 → 323, todos passando localmente (Windows, Python 3.11.8, pygame-ce 2.5.8), também com `--import-mode=importlib`. `ruff check` e `ruff format --check` sem apontamentos.
- **Testado à mão:** `python -m politicalizando --fechar-em 1` abriu e fechou com código 0. Nada mudou na tela, então não houve teste visual.
- Próximo: PR `feat/fichas-das-correntes`.

### 2026-10-14 18:19 — Fase 1: fichas das correntes e fontes

**Feito:**
- `dominio/fichas.py`: as fichas ficam em `conteudo/fichas.toml`, uma por corrente (a chave é a corrente), todas no modelo de 8 itens do briefing: ideia central, valores, papel do Estado, do mercado e da sociedade, origem e pensadores, proposta para o problema do capítulo, críticas, confusões de nome e fontes. Os textos ficam no `textos.toml`, por ID.
- Validação do modelo comum: todos os itens obrigatórios e listas não vazias; pelo menos uma fonte (R5, C4); críticas de pelo menos 2 origens diferentes (outra corrente ou `"outras"`), nunca da própria corrente.
- Desbloqueio por flags (`se`, J3); as fichas desbloqueadas saem sempre na ordem fixa das correntes, nunca numa ordem que favoreça uma delas.
- `dominio/fontes.py`: `Fonte` (autor, título, ano e editora; ou url `https://` com a data de acesso), separada para ser reaproveitada nos casos de checagem.
- Testes de conteúdo: os textos das fichas entram no teste de usados e órfãos, e as flags de desbloqueio precisam de origem. Em `tests/test_equilibrio.py`: a ficha mais longa pode ter no máximo 1,3× os caracteres da mais curta, e um teste exige uma ficha para cada uma das 4 correntes.

**Arquivos:** `src/politicalizando/dominio/fontes.py` (novo), `src/politicalizando/dominio/fichas.py` (novo), `src/politicalizando/conteudo/__init__.py`, `src/politicalizando/conteudo/fichas.toml` (novo), `tests/test_fontes.py` (novo), `tests/test_fichas.py` (novo), `tests/test_textos_usados.py`, `tests/test_flags_exigidas.py`, `tests/test_equilibrio.py`, `LOG.md`.

**Motivo / observações:**
- Sétimo PR da Fase 1 (`J3`, `R5`, `C4`; prepara `C1`, `R2`). O #10 (cenas e interação) entrou na `main` pelo auto-merge.
- Decisões do João: textos no `textos.toml` e fontes como dados no `fichas.toml`; críticas com `de` = outra corrente ou `"outras"`, de pelo menos 2 origens; limite de tamanho de 1,3×; teste das 4 correntes como `xfail` estrito até a Fase 4; desbloqueio por `se`.
- O `fichas.toml` começa só com o formato documentado; os exemplos dos testes são fictícios (IDs `exemplo.*` e "Autor Exemplo"), sem nenhum conteúdo político. O texto das fichas é da Fase 4 e passa pelo teste do defensor (C5), pelo checklist de equilíbrio e pela revisão externa (P5).
- O `xfail` estrito é um lembrete automático: quando as 4 fichas chegarem, o teste passa, o pytest acusa e a marcação precisa ser removida para o teste virar obrigatório.
- Testes: 323 → 386 (mais 1 `xfail` esperado), todos passando localmente (Windows, Python 3.11.8, pygame-ce 2.5.8), também com `--import-mode=importlib`. `ruff check` e `ruff format --check` sem apontamentos.
- **Testado à mão:** `python -m politicalizando --fechar-em 1` abriu e fechou com código 0. Nada mudou na tela, então não houve teste visual.
- Próximo: PR `feat/checagem-de-fontes`, o último da Fase 1, com os testes de equilíbrio E2, E3 e E5.

### 2026-10-14 18:30 — Fase 1: checagem de fontes e testes E3 e E5

**Feito:**
- `dominio/checagem.py`: os casos de checagem ficam em `conteudo/checagem.toml`. Cada caso (post, manchete ou fala) tem conteúdo, classe e explicação. **Fato** leva `confere` e fontes obrigatórias (C6: fato não é "mais uma opinião"); **opinião** não tem resposta certa nem origem; **manipulação** leva `origem` (uma das 4 correntes ou `sem_lado`) e a `tecnica` usada (fora de contexto, dado falso, manchete enganosa, apelo à emoção, falsa autoridade, caça-clique ou golpe). Campos que não combinam com a classe são recusados.
- O caso roda no `Diretor`: mostra o conteúdo, oferece as 3 classes sempre na mesma ordem, marca `<caso>.checou` (e `<caso>.acertou` se acertou), diz se acertou e sempre mostra a explicação. Errar nunca pune (J11).
- As cenas aceitam `{ checagem = "id" }` como resposta de um objeto, e o carregamento confere que o caso existe.
- `textos.toml`: os primeiros textos de interface, provisórios e neutros: "Fato verificável", "Opinião ou valor", "Manipulação", "Isso mesmo." e "Não é bem isso.".
- Testes de equilíbrio em `tests/test_equilibrio.py`: **E3** (os diálogos marcados com `corrente` precisam ter o mesmo perfil de tópicos e níveis, isto é, o número de opções por nó em cada nível, nas 4 correntes) e **E5** (os exemplos de manipulação se distribuem por igual entre as 4 correntes, com pelo menos um sem lado).
- Testes de conteúdo: os textos dos casos entram no teste de usados e órfãos; `checou` e `acertou` contam como origem de flag; nenhum caso fica sem uso por alguma cena.

**Arquivos:** `src/politicalizando/dominio/checagem.py` (novo), `src/politicalizando/dominio/cenas.py`, `src/politicalizando/dominio/interacao.py`, `src/politicalizando/conteudo/__init__.py`, `src/politicalizando/conteudo/checagem.toml` (novo), `src/politicalizando/conteudo/pt_BR/textos.toml`, `tests/test_checagem.py` (novo), `tests/test_cenas.py`, `tests/test_interacao.py`, `tests/test_textos_usados.py`, `tests/test_flags_exigidas.py`, `tests/test_conteudo_sem_uso.py`, `tests/test_equilibrio.py`, `LOG.md`.

**Motivo / observações:**
- Oitavo PR da Fase 1 (`J4`, `C6`, `R9`, `E3`, `E5`). O #11 (fichas) entrou na `main` pelo auto-merge.
- Decisões do João: o **E2** e o modelo de avaliação da matéria (J7) saem deste PR e ganham um PR próprio, `feat/avaliacao-da-materia`, que fecha a Fase 1; as regras por classe; as 7 técnicas iniciais; os 5 rótulos provisórios; o perfil do E3 como opções por nó em cada nível; e a ligação dos casos às cenas por `{ checagem = "id" }`.
- O `checagem.toml` começa só com o formato documentado; os casos reais (com fontes verificadas e revisão externa, P5) são da Fase 4. Os exemplos dos testes são fictícios e neutros.
- Registrado também: o João quer propor um exemplo de arte, a partir da tela de início de um jogo que ele desenvolveu, antes de criar a arte e as personagens (Fase 3).
- Testes: 386 → 445 (mais 1 `xfail` esperado), todos passando localmente (Windows, Python 3.11.8, pygame-ce 2.5.8), também com `--import-mode=importlib`. `ruff check` e `ruff format --check` sem apontamentos.
- **Testado à mão:** `python -m politicalizando --fechar-em 1` abriu e fechou com código 0. Nada mudou na tela, então não houve teste visual.
- Próximo: PR `feat/avaliacao-da-materia` (J7 no domínio e o teste E2), o último da Fase 1.

### 2026-10-14 18:39 — Fase 1 concluída: avaliação da matéria e teste E2

**Feito:**
- `dominio/materia.py`: as peças da matéria do fechamento ficam em `conteudo/materia.toml`: fatos (que podem citar a fonte quando as flags de `fonte_se` estão marcadas), opiniões (que podem dizer quem disse, com `de`, e marcam a visão com `corrente`) e manipulações (armadilhas). Cada peça fica disponível pelas flags de `se`.
- `avaliar` dá três critérios, cada um de 0 a 2, e uma nota total de 0 a 6, sem rótulo: **fatos com fonte** (fatos citados ÷ fatos e manipulações incluídos), **opiniões atribuídas** (atribuídas ÷ incluídas) e **visões com justiça** (todas as correntes ouvidas presentes, pelo menos 2, com no máximo 1 peça de diferença). 100% é "bem feito"; 50% ou mais, "em parte"; menos, ou nada incluído, "precisa melhorar". Opiniões sem corrente contam para a atribuição, mas não para a justiça.
- Uma matéria impossível (peça inexistente, repetida, indisponível, fonte citada sem ter sido conferida, manipulação "citada") é erro de programação da tela, não do jogador.
- Testes de equilíbrio: **E2** avalia 9 matérias de qualidades diferentes, em 3 estados de investigação, com as 24 permutações das 4 correntes, e exige a mesma nota em todas; **E1** confere que a avaliação só tem os três critérios, sem rótulo nem corrente.
- Testes de conteúdo: os textos das peças entram no teste de usados e órfãos, e as flags de `se` e `fonte_se` precisam de origem.
- Fase 1 marcada como ✅ no roteiro do briefing, e a situação do README atualizada.

**Arquivos:** `src/politicalizando/dominio/materia.py` (novo), `src/politicalizando/conteudo/__init__.py`, `src/politicalizando/conteudo/materia.toml` (novo), `tests/test_materia.py` (novo), `tests/test_equilibrio.py`, `tests/test_textos_usados.py`, `tests/test_flags_exigidas.py`, `briefing.md`, `README.md`, `LOG.md`.

**Motivo / observações:**
- Nono e último PR da Fase 1 (`J7` no domínio, `E1`, `E2`). O #12 (checagem) entrou na `main` pelo auto-merge.
- Decisões do João: peças com "citar" (fonte no fato, atribuição na opinião) e manipulação como armadilha; três níveis por critério e nota de 0 a 6, sem rótulo; limites de 100% e 50%; critério sem nada incluído fica em "precisa melhorar"; justiça exige todas as correntes ouvidas, pelo menos 2, com no máximo 1 peça de diferença; fechar a Fase 1 neste PR.
- `E2` por construção: a avaliação lê o estado só por flags de investigação e trata as correntes apenas por contagem, sem citar nenhuma pelo nome. A posição da matéria nunca é medida.
- O `materia.toml` começa só com o formato documentado; as peças do capítulo entram na Fase 2, com a tela da matéria.
- **Fase 1 concluída.** Ficam para a Fase 2: ligar o diretor e a interação ao `Jogo` (input, caixa de diálogo, autosave ao entrar na cena), as telas de cena, mapa, caderno e matéria, e os primeiros dados do capítulo com formas simples. Antes da arte e das personagens (Fase 3), o João vai propor um exemplo a partir da tela de início de um jogo dele.
- Testes: 445 → 505 (mais 1 `xfail` esperado), todos passando localmente (Windows, Python 3.11.8, pygame-ce 2.5.8), também com `--import-mode=importlib`. `ruff check` e `ruff format --check` sem apontamentos.
- **Testado à mão:** `python -m politicalizando --fechar-em 1` abriu e fechou com código 0. Nada mudou na tela, então não houve teste visual.
- Próximo: planejar a Fase 2 (fluxo principal).

### 2026-10-14 18:59 — Fase 2: partida e tela de cena

**Feito:**
- `dominio/partida.py`: a `Partida` junta o estado, o `Diretor` e a `Interacao`. Enquanto o diretor está ocupado (ou a cena nova ainda não foi preparada), ela fica `ocupada` e recusa verbos: o input fica bloqueado. Quando a cena muda e o diretor está livre, ela roda `ao_entrar`; uma `TrocarCena` no meio de um roteiro troca a cena da tela na hora, mas a entrada da cena nova só roda quando o roteiro termina. `atualizar` avisa quando a entrada numa cena terminou, e a tela chama `autosalvar(estado, bloqueado=partida.ocupada)`. Um save com uma cena que não existe é `SaveInvalido`.
- `cenas.toml` ganha `inicio`, a cena onde o novo jogo começa (validada no domínio).
- Tela de cena (`estados/cena.py`): objetos como retângulos; o objeto sob o mouse ou com o foco fica destacado e mostra o nome no alto. Clique abre o menu Olhar/Usar/Falar; Tab, Shift+Tab e as setas percorrem os objetos, Enter ou Espaço abrem o menu, 1, 2 e 3 usam o verbo direto. Esc fecha o menu ou volta ao título, salvando se nada estiver bloqueado.
- `ui/`: quebra de linhas com a fonte provisória (`texto.py`), teclas comuns (`teclas.py`), caixa de diálogo (`caixa_dialogo.py`: a fala aparece inteira e avança com clique, Enter ou Espaço; as escolhas aparecem numeradas e respondem ao mouse, às setas e aos números) e menu de verbos (`menu_verbos.py`, sempre dentro da tela).
- Tela de título: Novo jogo e Continuar (só com save). Um save ilegível ou de cena inexistente mostra um aviso e o arquivo é mantido. Se o save falhar ao gravar, um aviso aparece na caixa (ou no título, ao sair com Esc) e o jogo segue.
- O `Jogo` carrega e confere as cenas, os roteiros, os diálogos e os casos ao abrir (`carregar_interacao`).
- Cena de teste provisória e neutra (IDs `teste.*`): sala com porta, mesa, caderno (item que some), relógio (espera), mural (checagem de uma opinião sobre os dias da semana) e pessoa de testes (diálogo com opção de uso único e opção com `se`), e um corredor. Textos de interface: verbos, opções do título, avisos e 2 recusas por verbo.
- Testes: a `Partida` sem janela; as telas com o driver `dummy` (mouse, teclado, input bloqueado, autosave, Esc, Continuar, save inválido); todo texto do jogo cabe na caixa em até 4 linhas e toda opção cabe numa linha.

**Arquivos:** `src/politicalizando/dominio/partida.py` (novo), `src/politicalizando/dominio/cenas.py`, `src/politicalizando/estados/cena.py` (novo), `src/politicalizando/estados/titulo.py`, `src/politicalizando/ui/texto.py` (novo), `src/politicalizando/ui/teclas.py` (novo), `src/politicalizando/ui/caixa_dialogo.py` (novo), `src/politicalizando/ui/menu_verbos.py` (novo), `src/politicalizando/jogo.py`, `src/politicalizando/config.py`, `src/politicalizando/conteudo/__init__.py`, `src/politicalizando/conteudo/cenas.toml`, `src/politicalizando/conteudo/roteiros.toml`, `src/politicalizando/conteudo/dialogos.toml`, `src/politicalizando/conteudo/checagem.toml`, `src/politicalizando/conteudo/pt_BR/textos.toml`, `tests/test_partida.py` (novo), `tests/test_tela_cena.py` (novo), `tests/test_ui.py` (novo), `tests/test_cenas.py`, `README.md`, `LOG.md`.

**Motivo / observações:**
- Primeiro PR da Fase 2 (`I9`, parte de `I4`, `J9` e `J10` na tela, `D10`, `J8`). Ordem da Fase 2 aprovada pelo João: partida e tela de cena; roteiro do capítulo 1 (documento); mapa (`J1`); caderno (`J6`); comparação de propostas (`J5`); tela da matéria (`J7`, `J11`); mostrar objetos (`I8`) e revisão do teclado; capítulo 1 jogável, que tira a cena de teste e fecha a fase.
- Decisões do João: autosave quando a entrada da cena termina (a entrada não se repete ao continuar); Esc na cena volta ao título salvando; cena inicial no `cenas.toml`; cena de teste nos dados reais com IDs `teste.*`, até o PR do capítulo; Novo jogo sem confirmação (o save antigo só é substituído no primeiro autosave).
- Fechar a janela pelo X não salva: só o Esc e a entrada numa cena salvam. O nome de quem fala (`quem`) ainda não aparece na caixa; entra com as personagens. A fonte padrão do pygame espaça algumas letras de um jeito estranho; a VT323 entra na Fase 3 (`I2`).
- O exemplo do `checagem.toml` sugere IDs como `caso.praca.cartaz.texto`, mas um ID terminado em `.texto` é lido como o texto da tabela de cima e recusado. A cena de teste usa `teste.mural.conteudo`; o exemplo fica para corrigir num PR de documentação.
- Testes: 505 → 566 (mais 1 `xfail` esperado), todos passando localmente (Windows, Python 3.11.8, pygame-ce 2.5.8), também com `--import-mode=importlib`. `ruff check` e `ruff format --check` sem apontamentos.
- **Testado à mão (João):** a cena de teste inteira, por mouse e por teclado: boas-vindas, verbos, recusas, caderno que some, relógio, checagem do mural, diálogo com opção de uso único, ida e volta ao corredor, Esc para o título e Continuar. A janela fechou com código 0, e o save ficou em `teste.sala`.
- Próximo: PR `docs/roteiro-do-capitulo-1`.

### 2026-10-14 23:24 — Fase 2: roteiro do capítulo 1

**Feito:**
- `docs/roteiro-capitulo-1.md` (novo): a estrutura do capítulo 1, com três atos (missão, investigação e fechamento), os locais, as personagens, a regra contra estereótipo, as quatro perguntas iguais para os quatro moradores, os casos de checagem previstos, as peças da matéria, as flags de investigação, os caminhos mínimo e completo e o que ainda está em aberto. Nenhum texto final: as falas são descritas, e os nomes ficam para o João.
- Briefing: novas decisões D13 (organização do capítulo) e D14 (fatos da cidade fictícia em documentos do jogo, marcados como fontes do jogo; matéria sem bloqueio), situação atualizada e `docs/` na estrutura.
- Exemplos de ID de texto terminados em `.texto` trocados no `checagem.toml`, no `roteiros.toml` e na documentação de `dominio/checagem.py`: um ID assim é lido como o texto da tabela de cima e recusado pelo leitor de textos.

**Arquivos:** `docs/roteiro-capitulo-1.md` (novo), `briefing.md`, `src/politicalizando/conteudo/checagem.toml`, `src/politicalizando/conteudo/roteiros.toml`, `src/politicalizando/dominio/checagem.py`, `LOG.md`.

**Motivo / observações:**
- Segundo PR da Fase 2 (`J1`, `J5`, `J6`, `J7` e `J11` planejados; `R2`, `R4`, `C4`, `C6`, `E1`, `E3`, `E5`). O #14 (partida e tela de cena) entrou na `main` pelo auto-merge.
- Decisões do João: três atos; um morador por local, sem que o local ou a ocupação combinem com a corrente; fatos do problema checados em documentos fictícios do jogo, com fontes reais para o mundo real; matéria disponível sem bloqueio desde o fim do Ato 1.
- A distribuição das correntes pelos locais é uma proposta, a confirmar pelo João no PR `feat/capitulo-1-jogavel`. A marca de fonte do jogo pede uma mudança em `dominio/fontes.py` no PR dos primeiros documentos.
- Testes: 566 → 566 (mais 1 `xfail` esperado; só documentação e comentários). `ruff check` e `ruff format --check` sem apontamentos.
- **Testado à mão:** nada mudou no jogo.
- Próximo: PR `feat/mapa-de-novatria` (`J1`).
