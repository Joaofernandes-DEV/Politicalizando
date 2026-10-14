"""Estado do jogo: flags de evento, inventário e cena atual (D10, J8).

As flags registram só o que aconteceu na investigação (ouviu, perguntou, checou, comparou).
Não há pontuação nem medidor de corrente: o estado guarda apenas booleanos, itens e a cena (E1).
"""

from __future__ import annotations

import re
from typing import Any

VERSAO_SAVE = 1

# IDs em minúsculas, sem acento, com pontos separando os trechos: `biblioteca.ouviu_bibliotecaria`.
_FORMATO_ID = re.compile(r"[a-z0-9_]+(\.[a-z0-9_]+)*")

_CHAVES_SAVE = frozenset({"versao", "cena_atual", "flags", "inventario"})


class SaveInvalido(ValueError):  # noqa: N818 - nomes em português, sem o sufixo "Error"
    """Dados de save malformados ou de uma versão que este jogo não sabe ler."""


def validar_id(texto: object) -> str:
    """Devolve o ID se ele estiver no formato aceito; senão levanta `ValueError`."""
    if not isinstance(texto, str) or not _FORMATO_ID.fullmatch(texto):
        raise ValueError(f"ID inválido: {texto!r}")
    return texto


class EstadoJogo:
    """Progresso da partida. `alterado` diz se algo mudou desde o último save."""

    def __init__(self) -> None:
        self.cena_atual: str | None = None
        self._flags: set[str] = set()
        self._inventario: list[str] = []
        self.alterado = False

    @property
    def flags(self) -> frozenset[str]:
        return frozenset(self._flags)

    @property
    def inventario(self) -> tuple[str, ...]:
        """Itens na ordem em que foram pegos."""
        return tuple(self._inventario)

    def marcar_flag(self, flag: str) -> bool:
        """Marca a flag; devolve `False` se ela já estava marcada."""
        if validar_id(flag) in self._flags:
            return False
        self._flags.add(flag)
        self.alterado = True
        return True

    def tem_flag(self, flag: str) -> bool:
        return validar_id(flag) in self._flags

    def dar_item(self, item: str) -> bool:
        """Põe o item no inventário; devolve `False` se ele já estava lá."""
        if validar_id(item) in self._inventario:
            return False
        self._inventario.append(item)
        self.alterado = True
        return True

    def tirar_item(self, item: str) -> bool:
        """Tira o item do inventário; devolve `False` se ele não estava lá."""
        if validar_id(item) not in self._inventario:
            return False
        self._inventario.remove(item)
        self.alterado = True
        return True

    def tem_item(self, item: str) -> bool:
        return validar_id(item) in self._inventario

    def entrar_na_cena(self, cena: str) -> bool:
        """Troca a cena atual; devolve `False` se já era essa a cena."""
        if validar_id(cena) == self.cena_atual:
            return False
        self.cena_atual = cena
        self.alterado = True
        return True

    def marcar_salvo(self) -> None:
        self.alterado = False

    def para_dict(self) -> dict[str, Any]:
        """Dados do save, prontos para virar JSON. As flags saem ordenadas."""
        return {
            "versao": VERSAO_SAVE,
            "cena_atual": self.cena_atual,
            "flags": sorted(self._flags),
            "inventario": list(self._inventario),
        }

    @classmethod
    def de_dict(cls, dados: object) -> EstadoJogo:
        """Reconstrói o estado a partir de `para_dict`; levanta `SaveInvalido` se algo não bate."""
        if not isinstance(dados, dict):
            raise SaveInvalido("o save não é um objeto JSON")
        if set(dados) != _CHAVES_SAVE:
            raise SaveInvalido(f"chaves inesperadas no save: {sorted(dados)}")
        versao = dados["versao"]
        if type(versao) is not int or versao != VERSAO_SAVE:
            raise SaveInvalido(f"versão de save não suportada: {versao!r}")

        estado = cls()
        try:
            if dados["cena_atual"] is not None:
                estado.cena_atual = validar_id(dados["cena_atual"])
            estado._flags = set(_lista_de_ids(dados["flags"], "flags"))
            estado._inventario = _lista_de_ids(dados["inventario"], "inventario")
        except ValueError as erro:
            raise SaveInvalido(str(erro)) from erro
        return estado


def _lista_de_ids(valor: object, nome: str) -> list[str]:
    if not isinstance(valor, list):
        raise ValueError(f"'{nome}' deveria ser uma lista")
    ids = [validar_id(item) for item in valor]
    if len(set(ids)) != len(ids):
        raise ValueError(f"'{nome}' tem IDs repetidos")
    return ids
