# Como contribuir

O fluxo é sempre o mesmo: **branch → mudança pequena → teste → entrada no LOG → um commit por arquivo → Pull Request → merge com o CI verde**.

## 1. Preparar o ambiente

```bash
git clone https://github.com/Joaofernandes-DEV/Politicalizando.git
cd Politicalizando
python -m venv .venv
```

Ative o ambiente virtual (Windows: `.venv\Scripts\activate`; Linux/macOS: `source .venv/bin/activate`) e instale:

```bash
python -m pip install -e ".[dev]"
```

> Se o caminho da pasta tiver espaços, use aspas nos comandos. Prefira `python -m pytest` e `python -m ruff`, que funcionam mesmo com acentos no caminho.

## 2. Criar uma branch

Nunca trabalhe direto na `main`. Parta dela atualizada:

```bash
git switch main
git pull
git switch -c feat/nome-curto-da-mudanca
```

Prefixos: `feat/`, `fix/`, `docs/`, `test/`, `chore/`.

## 3. Implementar com testes

- Regras do jogo ficam em `src/politicalizando/dominio/` (sem pygame) e têm teste em `tests/`.
- Toda mudança de comportamento traz teste novo ou ajustado.
- Testes de tela rodam sem janela (`SDL_VIDEODRIVER=dummy`, já configurado em `tests/conftest.py`).
- Assets (imagens, sons) são gerados por `ferramentas/gerar_*.py`. Edite o gerador e regenere; não edite os binários à mão.

Antes de seguir, rode os três comandos. Só avance se todos passarem:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
```

## 4. Testar de verdade

Abra o jogo (`python -m politicalizando`) e use o que mudou. Teste automático não substitui jogar. Se outra pessoa pediu a mudança, ela testa antes do commit.

## 5. Conteúdo: checklist de equilíbrio

Todo PR que cria ou altera textos, diálogos, fichas, arte ou mecânicas segue os princípios de conteúdo e as salvaguardas do [briefing.md](briefing.md) (seção 6). Antes de abrir o PR, confira:

- [ ] A corrente está descrita pelas suas próprias ideias centrais, não pelo que os adversários dizem dela.
- [ ] Uma pessoa que defende essa corrente se reconheceria no texto.
- [ ] As fichas seguem o mesmo modelo e têm tamanho parecido; as críticas aparecem para todas.
- [ ] O texto convida a comparar e a checar, sem entregar a conclusão.
- [ ] A distopia não aponta para um partido, governo ou corrente real.
- [ ] Todo dado factual tem fonte registrada.
- [ ] Nenhuma pessoa real é retratada de forma ofensiva; nenhum político vivo ou partido atual aparece ou é aludido.
- [ ] Fatos verificáveis não foram tratados como "mais uma opinião" (falso equilíbrio).
- [ ] Nenhuma flag, pontuação ou escolha mede o alinhamento ideológico do jogador.

## Referências de outros jogos

Outros jogos podem inspirar a arquitetura e as mecânicas, mas **nada** deles entra no repositório: código (inclusive decompilado), textos, nomes, personagens ou assets. Materiais de referência ficam fora da pasta do projeto.

## 6. Registrar no LOG.md

Adicione **uma entrada no final** do [LOG.md](LOG.md), no modelo descrito no topo dele:

- horário local no momento em que a mudança foi concluída;
- o **quê** e o **porquê** (o "como" fica no código e nos commits);
- o número de testes antes e depois;
- o que foi testado à mão e o que ficou para conferir;
- os itens do briefing resolvidos (ex.: `J4`, `R5`).

## 7. Um commit por arquivo

Cada arquivo alterado vira um commit próprio, com mensagem curta em português no formato [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add src/politicalizando/dominio/fichas.py
git commit -m "feat: carrega as fichas das ideologias a partir dos dados"

git add tests/test_fichas.py
git commit -m "test: exige fonte em toda ficha"

git add LOG.md
git commit -m "docs: registra as fichas no diário de bordo"
```

- Tipos: `feat`, `fix`, `test`, `docs`, `build`, `ci`, `chore`.
- Ordem: código → testes → documentação → LOG por último.
- **Nunca** use `git add .` nem `git add -A`.

## 8. Abrir o Pull Request

```bash
git push -u origin feat/nome-curto-da-mudanca
gh pr create
```

Use esta descrição:

```markdown
## O que muda
- ...

## Como testar
`python -m pytest` e <como abrir o jogo e o que conferir>.
```

## 9. Merge

- Só com o CI verde e a branch em dia com a `main`.
- Use **merge commit** (preserva os commits por arquivo). Depois, apague a branch.
- PRs que dependem uns dos outros: abra empilhados e faça o merge na ordem. Atualize cada um (`gh pr update-branch N`) e espere o CI antes do próximo. Conflitos no `LOG.md` se resolvem mantendo a ordem cronológica.

## Versões

Versionamento semântico, publicado por tag `vX.Y.Z` pelo mantenedor, depois de um PR `chore/release-vX.Y.Z`.
