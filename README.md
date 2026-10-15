# Politicalizando

[![CI](https://github.com/Joaofernandes-DEV/Politicalizando/actions/workflows/ci.yml/badge.svg)](https://github.com/Joaofernandes-DEV/Politicalizando/actions/workflows/ci.yml)

Jogo 2D em pixel art que ensina como a política funciona, com foco na política brasileira, o que são as ideologias políticas e como se informar, para compreender o Brasil e o mundo atuais e desenvolver um pensamento crítico sólido. A ambientação é contemporânea e distópica, em Novátria, um município fictício brasileiro com as desigualdades e os problemas concretos do país real. O aprendizado parte desses problemas: para entender o fechamento de uma biblioteca, por exemplo, você investiga o orçamento municipal, o papel da prefeitura e da Câmara e a história da educação pública no Brasil.

É um jogo **educativo, não propaganda**:

- apresenta cada corrente pelas suas ideias centrais, com equilíbrio e sem caricaturas;
- convida o jogador a comparar argumentos, checar fontes e reconhecer manipulação, em vez de entregar conclusões prontas;
- usa a distopia como recurso narrativo, sem associá-la a um lado político;
- registra as fontes de todo conteúdo factual e não retrata pessoas reais de forma ofensiva;
- separa fato documentado, interpretação historiográfica e opinião, e não estereotipa grupos sociais, regiões ou classes.

Projeto de extensão da UNIP. Público: 14 anos ou mais.

## Situação

🚧 **Em desenvolvimento.** As Fases 0 (fundação) e 1 (núcleo) estão concluídas: a janela abre com uma tela de título provisória, e as regras do jogo (estado e save, textos, roteiros, diálogos, cenas, fichas, checagem de fontes e avaliação da matéria) estão modeladas como dados e testadas sem janela, com testes de equilíbrio entre as correntes. A próxima etapa é a Fase 2 (fluxo principal), que deixa o capítulo jogável. O roteiro completo, as decisões e o escopo da V1 estão no [briefing.md](briefing.md); o histórico de cada mudança está no [LOG.md](LOG.md).

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

Controles: clique num objeto para Olhar, Usar ou Falar; ou use `Tab` e as setas para escolher o objeto, `Enter` para abrir o menu e `1`, `2` e `3` para os verbos. No título, `Esc` fecha o jogo; numa cena, volta ao título salvando o progresso. Para um teste rápido que fecha sozinho: `python -m politicalizando --fechar-em 2`.

## Como desenvolver

O fluxo completo está no [CONTRIBUTING.md](CONTRIBUTING.md). Antes de cada commit:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
```

Estrutura: regras puras em `src/politicalizando/dominio/` (sem pygame), textos e outros dados revisáveis em `conteudo/` (TOML), telas em `estados/`, componentes visuais em `ui/`, assets gerados por scripts em `ferramentas/` e testes em `tests/`.

## Licença

- **Código:** [MIT](LICENSE).
- **Conteúdo educativo** (textos, fichas, arte e sons): [CC BY 4.0](LICENCA-CONTEUDO.md). Pode ser usado em sala de aula e adaptado, desde que se dê o crédito.
