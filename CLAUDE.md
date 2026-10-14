# Politicalizando

Python 3.11+ com pygame-ce. Código em `src/politicalizando/`, testes em `tests/`. Idioma do projeto: português (código, commits, LOG, README). Decisões, escopo e roteiro estão no `briefing.md`.

## Fluxo obrigatório

Siga o [CONTRIBUTING.md](CONTRIBUTING.md). Em resumo, a cada mudança:

1. Trabalhe em uma branch (`feat/...`, `fix/...`), nunca na `main`.
2. Escreva ou ajuste testes. Regras ficam em `src/politicalizando/dominio/` (sem pygame).
3. Rode `python -m ruff check .`, `python -m ruff format --check .` e `python -m pytest`; só avance se passarem.
4. Abra o jogo para quem pediu testar antes do commit.
5. Adicione uma entrada **no final** do `LOG.md`, no modelo descrito no topo dele (horário local, o quê e por quê, arquivos, testes antes/depois, o que foi testado à mão).
6. Faça **um commit por arquivo**, com mensagem Conventional Commits em português. Ordem: código, testes, docs, LOG por último.
7. Não use `git add .` nem `git add -A`; adicione arquivo por arquivo.

## Cuidados

- Jogo educativo, não propaganda: todo conteúdo segue os princípios C1 a C6 e as salvaguardas E1 a E5 do `briefing.md`, além do checklist de equilíbrio do CONTRIBUTING. Nunca escreva texto ou mecânica que favoreça ou ridicularize uma corrente, partido ou pessoa real.
- Referências de outros jogos servem só como ideia (D12): nunca copie código, textos, nomes, personagens ou assets, e nunca adicione materiais de referência ao repositório.
- Conteúdo factual sempre com fonte registrada. Na dúvida sobre um fato, pergunte em vez de inventar.
- Assets são gerados por `ferramentas/gerar_*.py`; não edite os binários à mão.
- Decisões de produto e de gosto (nomes, versão, licença, tom do conteúdo, publicar) são do João: pergunte.
- Não faça merge, push na `main`, tag nem release sem pedido explícito.
