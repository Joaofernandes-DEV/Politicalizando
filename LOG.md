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
