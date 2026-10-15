"""Fontes bibliográficas do conteúdo factual (C4, R5).

Uma fonte é um dado, não um texto de tela: fica junto do conteúdo que ela sustenta (fichas e,
depois, casos de checagem), no formato:

    { autor = "Sobrenome, Nome", titulo = "Título", ano = 1999, editora = "Editora" }
    { autor = "Instituição", titulo = "Página", ano = 2024,
      url = "https://...", acesso = 2026-10-14 }

É preciso `editora` ou `url`; uma `url` exige `https://` e a data de `acesso` (data TOML).

Uma **fonte do jogo** (`do_jogo = true`) é um documento que só existe em Novátria, como o
relatório da biblioteca ou o orçamento do município (D14, D16). Ela aparece marcada assim para
quem joga e dispensa `editora` e `url`. Nunca serve para o que fala do mundo real: as fichas,
por exemplo, recusam fontes do jogo.

    { autor = "Prefeitura de Novátria", titulo = "Orçamento de 2026", ano = 2026, do_jogo = true }
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass

ANO_MINIMO = 1000
ANO_MAXIMO = 2100

_CHAVES = frozenset({"autor", "titulo", "ano", "editora", "url", "acesso", "do_jogo"})


@dataclass(frozen=True)
class Fonte:
    autor: str
    titulo: str
    ano: int
    editora: str | None = None
    url: str | None = None
    acesso: datetime.date | None = None
    # Documento fictício de Novátria (D14); dispensa editora e url.
    do_jogo: bool = False

    def __post_init__(self) -> None:
        for nome in ("autor", "titulo"):
            valor = getattr(self, nome)
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(f"a fonte precisa de '{nome}' não vazio")
        if isinstance(self.ano, bool) or not isinstance(self.ano, int):
            raise ValueError(f"ano inválido: {self.ano!r}")
        if not ANO_MINIMO <= self.ano <= ANO_MAXIMO:
            raise ValueError(f"ano fora de {ANO_MINIMO} a {ANO_MAXIMO}: {self.ano}")
        if not isinstance(self.do_jogo, bool):
            raise ValueError(f"'do_jogo' deveria ser true ou false: {self.do_jogo!r}")
        if self.editora is None and self.url is None and not self.do_jogo:
            raise ValueError("a fonte precisa de 'editora' ou 'url'")
        if self.editora is not None and (
            not isinstance(self.editora, str) or not self.editora.strip()
        ):
            raise ValueError("'editora' não pode ficar vazia")
        if self.url is not None:
            if not isinstance(self.url, str) or not self.url.startswith("https://"):
                raise ValueError(f"a url precisa começar com https://: {self.url!r}")
            if self.acesso is None:
                raise ValueError("uma fonte com url precisa da data de 'acesso'")
        if self.acesso is not None and (
            isinstance(self.acesso, datetime.datetime) or not isinstance(self.acesso, datetime.date)
        ):
            raise ValueError(f"'acesso' deveria ser uma data (AAAA-MM-DD): {self.acesso!r}")


def ler_fonte(dados: object, onde: str) -> Fonte:
    """Converte uma tabela do TOML em `Fonte`; levanta `ValueError` com `onde` na mensagem."""
    if not isinstance(dados, dict):
        raise ValueError(f"{onde}: uma fonte é uma tabela")
    extras = set(dados) - _CHAVES
    if extras:
        raise ValueError(f"{onde}: chaves inesperadas {sorted(extras)}")
    for obrigatoria in ("autor", "titulo", "ano"):
        if obrigatoria not in dados:
            raise ValueError(f"{onde}: falta a chave {obrigatoria!r}")
    try:
        return Fonte(**dados)
    except ValueError as erro:
        raise ValueError(f"{onde}: {erro}") from None
