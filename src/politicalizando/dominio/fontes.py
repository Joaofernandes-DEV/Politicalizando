"""Fontes bibliográficas do conteúdo factual (C4, R5).

Uma fonte é um dado, não um texto de tela: fica junto do conteúdo que ela sustenta (fichas e,
depois, casos de checagem), no formato:

    { autor = "Sobrenome, Nome", titulo = "Título", ano = 1999, editora = "Editora" }
    { autor = "Instituição", titulo = "Página", ano = 2024,
      url = "https://...", acesso = 2026-10-14 }

É preciso `editora` ou `url`; uma `url` exige `https://` e a data de `acesso` (data TOML).
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass

ANO_MINIMO = 1000
ANO_MAXIMO = 2100

_CHAVES = frozenset({"autor", "titulo", "ano", "editora", "url", "acesso"})


@dataclass(frozen=True)
class Fonte:
    autor: str
    titulo: str
    ano: int
    editora: str | None = None
    url: str | None = None
    acesso: datetime.date | None = None

    def __post_init__(self) -> None:
        for nome in ("autor", "titulo"):
            valor = getattr(self, nome)
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(f"a fonte precisa de '{nome}' não vazio")
        if isinstance(self.ano, bool) or not isinstance(self.ano, int):
            raise ValueError(f"ano inválido: {self.ano!r}")
        if not ANO_MINIMO <= self.ano <= ANO_MAXIMO:
            raise ValueError(f"ano fora de {ANO_MINIMO} a {ANO_MAXIMO}: {self.ano}")
        if self.editora is None and self.url is None:
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
