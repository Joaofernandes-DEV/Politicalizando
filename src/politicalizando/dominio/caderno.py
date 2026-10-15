"""Caderno do jogador: o que foi ouvido, as fontes consultadas e os itens (J6, J13).

Formato de `conteudo/caderno.toml` (os textos ficam no `textos.toml`, por ID):

    [itens]
    folheto = "item.folheto"

    [[entradas]]
    id = "guia_posicao"
    texto = "caderno.guia.posicao"
    origem = "opiniao"
    de = "praca.guia.nome"
    se = ["praca.guia.posicao"]

    [[entradas]]
    id = "orcamento"
    texto = "caderno.orcamento"
    origem = "fato"
    fontes = [{ autor = "Prefeitura", titulo = "Orçamento de 2026", ano = 2026, do_jogo = true }]
    se = ["prefeitura.portal.leu"]

`[itens]` dá o nome (ID de texto) de cada item do inventário. Cada `[[entradas]]` é uma anotação
que aparece quando as flags de `se` estão marcadas, sempre com a origem marcada (C7):

- `opiniao`: o que uma personagem pensa; leva `de`, o ID do texto com o nome de quem disse;
- `fato`: um fato documentado; leva `fontes` (reais, ou do jogo para o que só existe em Novátria);
- `interpretacao`: a leitura de um autor sobre um fato; leva `fontes` com o autor e a obra.

As entradas saem na ordem do arquivo. O caderno só mostra; ele nunca marca flags (E1).
"""

from __future__ import annotations

import tomllib
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType

from politicalizando.dominio.estado_jogo import EstadoJogo, validar_id
from politicalizando.dominio.fontes import Fonte, ler_fonte

_CHAVES_RAIZ = frozenset({"itens", "entradas"})
_CHAVES_ENTRADA = frozenset({"id", "texto", "origem", "de", "fontes", "se"})


class Origem(StrEnum):
    FATO = "fato"
    INTERPRETACAO = "interpretacao"
    OPINIAO = "opiniao"


class CadernoInvalido(ValueError):  # noqa: N818 - nomes em português, sem o sufixo "Error"
    """Arquivo do caderno malformado ou com uma origem sem os campos que ela pede."""


@dataclass(frozen=True)
class Entrada:
    id: str
    texto: str
    origem: Origem
    de: str | None = None
    fontes: tuple[Fonte, ...] = ()
    se: frozenset[str] = frozenset()

    def liberada(self, estado: EstadoJogo) -> bool:
        return all(estado.tem_flag(flag) for flag in self.se)


@dataclass(frozen=True)
class Caderno:
    entradas: tuple[Entrada, ...] = ()
    itens: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "itens", MappingProxyType(dict(self.itens)))

    def _liberadas(self, estado: EstadoJogo) -> Iterator[Entrada]:
        return (entrada for entrada in self.entradas if entrada.liberada(estado))

    def conversas(self, estado: EstadoJogo) -> tuple[Entrada, ...]:
        """As opiniões ouvidas, na ordem do arquivo."""
        return tuple(e for e in self._liberadas(estado) if e.origem is Origem.OPINIAO)

    def fontes(self, estado: EstadoJogo) -> tuple[Entrada, ...]:
        """Os fatos e as interpretações consultados, na ordem do arquivo."""
        return tuple(e for e in self._liberadas(estado) if e.origem is not Origem.OPINIAO)

    def itens_do_inventario(self, estado: EstadoJogo) -> tuple[str, ...]:
        """Os IDs de texto dos nomes dos itens, na ordem de coleta.

        Um item sem nome (de um save antigo) fica de fora em vez de quebrar a tela.
        """
        return tuple(self.itens[item] for item in estado.inventario if item in self.itens)

    def ids_de_texto(self) -> set[str]:
        ids = set(self.itens.values())
        for entrada in self.entradas:
            ids.add(entrada.texto)
            if entrada.de is not None:
                ids.add(entrada.de)
        return ids

    def flags_exigidas(self) -> set[str]:
        return set().union(*(entrada.se for entrada in self.entradas))

    @classmethod
    def de_toml(cls, conteudo: str) -> Caderno:
        try:
            dados = tomllib.loads(conteudo)
        except tomllib.TOMLDecodeError as erro:
            raise CadernoInvalido(f"TOML inválido: {erro}") from erro
        return cls.de_dict(dados)

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> Caderno:
        try:
            extras = set(dados) - _CHAVES_RAIZ
            if extras:
                raise ValueError(f"chaves inesperadas no caderno: {sorted(extras)}")
            itens = _itens(dados.get("itens", {}))
            lista = dados.get("entradas", [])
            if not isinstance(lista, list):
                raise ValueError("'entradas' deveria ser uma lista de tabelas [[entradas]]")
            entradas = tuple(_entrada(numero, item) for numero, item in enumerate(lista, 1))
            ids = [entrada.id for entrada in entradas]
            repetidos = sorted({id_entrada for id_entrada in ids if ids.count(id_entrada) > 1})
            if repetidos:
                raise ValueError(f"entradas repetidas: {repetidos}")
        except ValueError as erro:
            raise CadernoInvalido(str(erro)) from erro
        return cls(entradas=entradas, itens=itens)


# As funções abaixo levantam `ValueError`; `Caderno.de_dict` converte em `CadernoInvalido`.


def _id(onde: str, valor: object) -> str:
    try:
        return validar_id(valor)
    except ValueError as erro:
        raise ValueError(f"{onde}: {erro}") from None


def _itens(dados: object) -> dict[str, str]:
    if not isinstance(dados, dict):
        raise ValueError("'itens' deveria ser uma tabela de item = ID do nome")
    return {_id("itens", item): _id(f"itens, {item}", nome) for item, nome in dados.items()}


def _entrada(numero: int, dados: object) -> Entrada:
    onde = f"entrada {numero}"
    if not isinstance(dados, dict):
        raise ValueError(f"{onde}: uma entrada é uma tabela")
    extras = set(dados) - _CHAVES_ENTRADA
    if extras:
        raise ValueError(f"{onde}: chaves inesperadas {sorted(extras)}")
    for obrigatoria in ("id", "texto", "origem"):
        if obrigatoria not in dados:
            raise ValueError(f"{onde}: falta a chave {obrigatoria!r}")
    id_entrada = dados["id"]
    if not isinstance(id_entrada, str) or "." in id_entrada:
        raise ValueError(f"{onde}: id inválido {id_entrada!r}")
    onde = f"entrada {_id(onde, id_entrada)!r}"
    try:
        origem = Origem(dados["origem"])
    except ValueError:
        aceitas = ", ".join(Origem)
        raise ValueError(f"{onde}: origem desconhecida {dados['origem']!r} ({aceitas})") from None

    de = None
    fontes: tuple[Fonte, ...] = ()
    if origem is Origem.OPINIAO:
        if "fontes" in dados:
            raise ValueError(f"{onde}: uma opinião não leva 'fontes'; diga quem disse com 'de'")
        if "de" not in dados:
            raise ValueError(f"{onde}: uma opinião precisa de 'de' (quem disse)")
        de = _id(f"{onde}, de", dados["de"])
    else:
        if "de" in dados:
            raise ValueError(f"{onde}: '{origem}' não leva 'de'; a autoria fica nas fontes")
        lista = dados.get("fontes")
        if not isinstance(lista, list) or not lista:
            raise ValueError(f"{onde}: '{origem}' precisa de pelo menos uma fonte")
        fontes = tuple(
            ler_fonte(item, f"{onde}, fonte {numero}") for numero, item in enumerate(lista, 1)
        )

    se = dados.get("se", [])
    if not isinstance(se, list):
        raise ValueError(f"{onde}, se: deveria ser uma lista de flags")
    return Entrada(
        id=id_entrada,
        texto=_id(f"{onde}, texto", dados["texto"]),
        origem=origem,
        de=de,
        fontes=fontes,
        se=frozenset(_id(f"{onde}, se", flag) for flag in se),
    )
