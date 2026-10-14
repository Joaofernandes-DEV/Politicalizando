# Ferramentas

Scripts de apoio que **geram** arquivos do projeto. Nenhum binário de `src/politicalizando/assets/` é editado à mão: tudo sai daqui e pode ser recriado e conferido.

## Convenções

- Um gerador por tipo de asset: `gerar_<o_que>.py` (ex.: `gerar_sprites.py`, `gerar_sons.py`).
- **Determinístico:** a mesma execução gera sempre os mesmos arquivos. Se houver sorteio, use semente fixa.
- Ao mudar um gerador, regenere e confira com `git status` se só mudaram os arquivos esperados. Os outros devem sair idênticos.
- Rode a partir da raiz do repositório, com o ambiente virtual ativo:

  ```bash
  python ferramentas/gerar_sprites.py
  ```

Os geradores entram a partir da Fase 3 (interface), e o empacotador do executável entra na Fase 5 (entrega). Veja o roteiro no [briefing.md](../briefing.md).
