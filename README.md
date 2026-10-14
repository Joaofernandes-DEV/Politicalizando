# Politicalizando

[![CI](https://github.com/Joaofernandes-DEV/Politicalizando/actions/workflows/ci.yml/badge.svg)](https://github.com/Joaofernandes-DEV/Politicalizando/actions/workflows/ci.yml)

Jogo 2D em pixel art que ensina sobre ideologias políticas e sobre como se informar para compreender o mundo atual e desenvolver um pensamento crítico sólido. A ambientação é contemporânea e distópica.

É um jogo **educativo, não propaganda**:

- apresenta cada corrente pelas suas ideias centrais, com equilíbrio e sem caricaturas;
- convida o jogador a comparar argumentos, checar fontes e reconhecer manipulação, em vez de entregar conclusões prontas;
- usa a distopia como recurso narrativo, sem associá-la a um lado político;
- registra as fontes de todo conteúdo factual e não retrata pessoas reais de forma ofensiva.

Projeto de extensão da UNIP. Público: 14 anos ou mais.

## Situação

🚧 **Em desenvolvimento.** A Fase 0 (fundação) está concluída: a janela abre com uma tela de título provisória, e o lint e os testes rodam no CI. A próxima etapa é a Fase 1 (núcleo). O roteiro completo, as decisões e o escopo da V1 estão no [briefing.md](briefing.md); o histórico de cada mudança está no [LOG.md](LOG.md).

O executável para Windows será publicado nas [releases](https://github.com/Joaofernandes-DEV/Politicalizando/releases) na entrega da V1.

## Como rodar (código-fonte)

Requer Python 3.11 ou mais recente.

```bash
git clone https://github.com/Joaofernandes-DEV/Politicalizando.git
cd Politicalizando
python -m venv .venv
```

Ative o ambiente virtual (Windows: `.venv\Scripts\activate`; Linux/macOS: `source .venv/bin/activate`) e rode:

```bash
python -m pip install -e ".[dev]"
python -m politicalizando
```

`Esc` fecha o jogo. Para um teste rápido que fecha sozinho: `python -m politicalizando --fechar-em 2`.

## Como desenvolver

O fluxo completo está no [CONTRIBUTING.md](CONTRIBUTING.md). Antes de cada commit:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
```

Estrutura: regras puras em `src/politicalizando/dominio/` (sem pygame), telas em `estados/`, componentes visuais em `ui/`, assets gerados por scripts em `ferramentas/` e testes em `tests/`.

## Licença

- **Código:** [MIT](LICENSE).
- **Conteúdo educativo** (textos, fichas, arte e sons): [CC BY 4.0](LICENCA-CONTEUDO.md). Pode ser usado em sala de aula e adaptado, desde que se dê o crédito.
