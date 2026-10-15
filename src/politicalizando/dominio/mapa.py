"""Mapa de Novátria: os locais da cidade e quando cada um aparece (J1, D8).

Formato de `conteudo/mapa.toml`:

    se = ["praca.tutorial.checou"]

    [[locais]]
    id = "biblioteca"
    nome = "mapa.biblioteca"
    cena = "biblioteca.salao"
    area = [40, 60, 64, 28]
    se = ["escola.editoria.missao"]

`se` na raiz (opcional) são as flags que liberam o mapa; sem elas, o mapa não abre. Cada local
leva a uma cena, ocupa uma `area` na tela do mapa (resolução lógica) e só aparece quando as
flags do seu `se` estão marcadas: um local bloqueado fica escondido. A ordem dos locais é a do
arquivo, que também é a ordem de percorrer com o teclado, e nunca segue as correntes.
"""

from __future__ import annotations

import tomllib
from collections.abc import Iterable
from dataclasses import dataclass

from politicalizando.dominio.cenas import Area
from politicalizando.dominio.estado_jogo import EstadoJogo, validar_id

_CHAVES_RAIZ = frozenset({"se", "locais"})
_CHAVES_LOCAL = frozenset({"id", "nome", "cena", "area", "se"})


class MapaInvalido(ValueError):  # noqa: N818 - nomes em português, sem o sufixo "Error"
    """Arquivo do mapa malformado, ou com um local que leva a uma cena inexistente."""


@dataclass(frozen=True)
class Local:
    id: str
    nome: str
    cena: str
    area: Area
    se: frozenset[str] = frozenset()

    def liberado(self, estado: EstadoJogo) -> bool:
        return all(estado.tem_flag(flag) for flag in self.se)


@dataclass(frozen=True)
class Mapa:
    locais: tuple[Local, ...] = ()
    se: frozenset[str] = frozenset()

    def liberado(self, estado: EstadoJogo) -> bool:
        """O mapa abre quando as flags dele estão marcadas e há algum local liberado."""
        return all(estado.tem_flag(flag) for flag in self.se) and bool(
            self.locais_liberados(estado)
        )

    def locais_liberados(self, estado: EstadoJogo) -> tuple[Local, ...]:
        """Na ordem do arquivo; os bloqueados ficam de fora (escondidos)."""
        return tuple(local for local in self.locais if local.liberado(estado))

    def local_em(self, estado: EstadoJogo, x: float, y: float) -> Local | None:
        return next(
            (local for local in self.locais_liberados(estado) if local.area.contem(x, y)), None
        )

    def ids_de_texto(self) -> set[str]:
        return {local.nome for local in self.locais}

    def flags_exigidas(self) -> set[str]:
        return set(self.se).union(*(local.se for local in self.locais))

    def cenas_usadas(self) -> set[str]:
        return {local.cena for local in self.locais}

    @classmethod
    def de_toml(cls, conteudo: str) -> Mapa:
        try:
            dados = tomllib.loads(conteudo)
        except tomllib.TOMLDecodeError as erro:
            raise MapaInvalido(f"TOML inválido: {erro}") from erro
        return cls.de_dict(dados)

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> Mapa:
        try:
            extras = set(dados) - _CHAVES_RAIZ
            if extras:
                raise ValueError(f"chaves inesperadas no mapa: {sorted(extras)}")
            lista = dados.get("locais", [])
            if not isinstance(lista, list):
                raise ValueError("'locais' deveria ser uma lista de tabelas [[locais]]")
            locais = tuple(_local(numero, item) for numero, item in enumerate(lista, 1))
            for campo in ("id", "cena", "area"):
                _sem_repetidos(campo, (getattr(local, campo) for local in locais))
            se = _flags("mapa, se", dados.get("se", []))
        except ValueError as erro:
            raise MapaInvalido(str(erro)) from erro
        return cls(locais=locais, se=se)


def conferir_cenas(mapa: Mapa, cenas: Iterable[str]) -> None:
    """Levanta `MapaInvalido` se algum local leva a uma cena que não existe."""
    faltando = sorted(mapa.cenas_usadas() - set(cenas))
    if faltando:
        raise MapaInvalido(f"o mapa leva a cenas que não existem: {', '.join(faltando)}")


# As funções abaixo levantam `ValueError`; `Mapa.de_dict` converte em `MapaInvalido`.


def _flags(onde: str, valor: object) -> frozenset[str]:
    if not isinstance(valor, list):
        raise ValueError(f"{onde}: deveria ser uma lista de flags")
    try:
        return frozenset(validar_id(flag) for flag in valor)
    except ValueError as erro:
        raise ValueError(f"{onde}: {erro}") from None


def _sem_repetidos(campo: str, valores: Iterable[object]) -> None:
    vistos: list[object] = []
    for valor in valores:
        if valor in vistos:
            raise ValueError(f"mapa: dois locais com o mesmo '{campo}': {valor!r}")
        vistos.append(valor)


def _local(numero: int, dados: object) -> Local:
    onde = f"local {numero}"
    if not isinstance(dados, dict):
        raise ValueError(f"{onde}: um local é uma tabela")
    extras = set(dados) - _CHAVES_LOCAL
    if extras:
        raise ValueError(f"{onde}: chaves inesperadas {sorted(extras)}")
    faltando = sorted(_CHAVES_LOCAL - {"se"} - set(dados))
    if faltando:
        raise ValueError(f"{onde}: faltam as chaves {faltando}")
    id_local = dados["id"]
    if not isinstance(id_local, str) or "." in id_local:
        raise ValueError(f"{onde}: id inválido {id_local!r}")
    try:
        validar_id(id_local)
        onde = f"local {id_local!r}"
        nome = validar_id(dados["nome"])
        cena = validar_id(dados["cena"])
    except ValueError as erro:
        raise ValueError(f"{onde}: {erro}") from None
    area = dados["area"]
    if not isinstance(area, list) or len(area) != 4:
        raise ValueError(f"{onde}: 'area' deveria ser [x, y, largura, altura]")
    try:
        area = Area(*area)
    except ValueError as erro:
        raise ValueError(f"{onde}: {erro}") from None
    se = _flags(f"{onde}, se", dados.get("se", []))
    return Local(id=id_local, nome=nome, cena=cena, area=area, se=se)
