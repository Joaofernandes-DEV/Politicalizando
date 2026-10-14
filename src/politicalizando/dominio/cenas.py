"""Cenas em dados: telas fixas com objetos interativos (D8, J9, J10).

Formato de `conteudo/cenas.toml`:

    [recusas]
    olhar = ["recusa.olhar.1", "recusa.olhar.2"]
    usar = ["recusa.usar.1"]
    falar = ["recusa.falar.1"]

    [cenas.praca]
    entrada = { roteiro = "praca.apresentacao" }

    [[cenas.praca.objetos]]
    id = "folheto"
    nome = "praca.folheto.nome"
    area = [40, 100, 16, 12]
    olhar = [{ fala = "praca.folheto.olhar" }]
    usar = [{ dar_item = "folheto" }]
    se_nao_item = ["folheto"]

Cada tabela de `cenas` com `objetos` é uma cena, e o caminho dela é o ID. A resposta a um verbo
(e a `entrada`, que roda só na primeira visita) é uma lista de passos no formato dos roteiros,
`{ roteiro = "id" }` ou `{ dialogo = "id" }`. Um verbo sem resposta usa a recusa genérica do
verbo, em rodízio; as recusas nunca falam de correntes (E4). `area` é x, y, largura e altura na
resolução lógica. `se` e `se_nao` são flags; `se_item` e `se_nao_item` são itens: um item
coletado pode fazer o objeto sumir.
"""

from __future__ import annotations

import tomllib
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType

from politicalizando.config import ALTURA_TELA, LARGURA_TELA
from politicalizando.dominio.acoes import Acao, DarItem, Fala, MarcarFlag
from politicalizando.dominio.estado_jogo import EstadoJogo, validar_id
from politicalizando.dominio.roteiro import ler_passos


class Verbo(StrEnum):
    OLHAR = "olhar"
    USAR = "usar"
    FALAR = "falar"


_CHAVES_RAIZ = frozenset({"recusas", "cenas"})
_CHAVES_CENA = frozenset({"objetos", "entrada"})
_CONDICOES = ("se", "se_nao", "se_item", "se_nao_item")
_CHAVES_OBJETO = frozenset({"id", "nome", "area", *Verbo, *_CONDICOES})


class CenaInvalida(ValueError):  # noqa: N818 - nomes em português, sem o sufixo "Error"
    """Arquivo de cenas malformado, ou com referência a roteiro ou diálogo inexistente."""


@dataclass(frozen=True)
class Area:
    """Retângulo clicável na resolução lógica (320×180)."""

    x: int
    y: int
    largura: int
    altura: int

    def __post_init__(self) -> None:
        valores = (self.x, self.y, self.largura, self.altura)
        if any(isinstance(valor, bool) or not isinstance(valor, int) for valor in valores):
            raise ValueError(f"a área precisa de 4 números inteiros: {valores}")
        if self.largura <= 0 or self.altura <= 0:
            raise ValueError(f"a área precisa de largura e altura positivas: {valores}")
        if (
            self.x < 0
            or self.y < 0
            or self.x + self.largura > LARGURA_TELA
            or self.y + self.altura > ALTURA_TELA
        ):
            raise ValueError(f"a área sai da tela de {LARGURA_TELA}×{ALTURA_TELA}: {valores}")

    def contem(self, x: float, y: float) -> bool:
        return self.x <= x < self.x + self.largura and self.y <= y < self.y + self.altura


@dataclass(frozen=True)
class Resposta:
    """O que acontece num verbo ou na entrada: passos em linha, um roteiro ou um diálogo."""

    passos: tuple[Acao, ...] = ()
    roteiro: str | None = None
    dialogo: str | None = None


@dataclass(frozen=True)
class Objeto:
    id: str
    nome: str
    area: Area
    respostas: Mapping[Verbo, Resposta] = field(default_factory=dict)
    se: frozenset[str] = frozenset()
    se_nao: frozenset[str] = frozenset()
    se_item: frozenset[str] = frozenset()
    se_nao_item: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        object.__setattr__(self, "respostas", MappingProxyType(dict(self.respostas)))

    def visivel(self, estado: EstadoJogo) -> bool:
        return (
            all(estado.tem_flag(flag) for flag in self.se)
            and not any(estado.tem_flag(flag) for flag in self.se_nao)
            and all(estado.tem_item(item) for item in self.se_item)
            and not any(estado.tem_item(item) for item in self.se_nao_item)
        )


@dataclass(frozen=True)
class Cena:
    id: str
    objetos: tuple[Objeto, ...]
    entrada: Resposta | None = None

    @property
    def flag_visitou(self) -> str:
        """Marcada ao entrar na cena; a `entrada` só roda enquanto ela não existe."""
        return f"{self.id}.visitou"

    def respostas(self) -> Iterator[Resposta]:
        if self.entrada is not None:
            yield self.entrada
        for objeto in self.objetos:
            yield from objeto.respostas.values()


class Cenas(Mapping[str, Cena]):
    """Catálogo imutável de cenas e as recusas genéricas de cada verbo."""

    def __init__(
        self,
        cenas: dict[str, Cena] | None = None,
        recusas: Mapping[Verbo, tuple[str, ...]] | None = None,
    ) -> None:
        self._cenas = dict(cenas or {})
        self.recusas: Mapping[Verbo, tuple[str, ...]] = MappingProxyType(dict(recusas or {}))

    def __getitem__(self, id_cena: str) -> Cena:
        try:
            return self._cenas[id_cena]
        except KeyError:
            raise KeyError(f"cena inexistente: {id_cena!r}") from None

    def __iter__(self) -> Iterator[str]:
        return iter(self._cenas)

    def __len__(self) -> int:
        return len(self._cenas)

    def _acoes(self) -> Iterator[Acao]:
        for cena in self.values():
            for resposta in cena.respostas():
                yield from resposta.passos

    def _objetos(self) -> Iterator[Objeto]:
        for cena in self.values():
            yield from cena.objetos

    def ids_de_texto(self) -> set[str]:
        """Nomes dos objetos, falas dos passos em linha e recusas."""
        ids = {objeto.nome for objeto in self._objetos()}
        ids |= {acao.id_texto for acao in self._acoes() if isinstance(acao, Fala)}
        return ids.union(*self.recusas.values())

    def flags_exigidas(self) -> set[str]:
        return set().union(*(objeto.se | objeto.se_nao for objeto in self._objetos()))

    def flags_marcadas(self) -> set[str]:
        """As `<cena>.visitou` e as flags marcadas nos passos em linha."""
        flags = {cena.flag_visitou for cena in self.values()}
        return flags | {acao.flag for acao in self._acoes() if isinstance(acao, MarcarFlag)}

    def itens_exigidos(self) -> set[str]:
        return set().union(*(objeto.se_item | objeto.se_nao_item for objeto in self._objetos()))

    def itens_dados(self) -> set[str]:
        return {acao.item for acao in self._acoes() if isinstance(acao, DarItem)}

    def roteiros_usados(self) -> set[str]:
        return {
            resposta.roteiro
            for cena in self.values()
            for resposta in cena.respostas()
            if resposta.roteiro is not None
        }

    def dialogos_usados(self) -> set[str]:
        return {
            resposta.dialogo
            for cena in self.values()
            for resposta in cena.respostas()
            if resposta.dialogo is not None
        }

    @classmethod
    def de_toml(cls, conteudo: str) -> Cenas:
        try:
            dados = tomllib.loads(conteudo)
        except tomllib.TOMLDecodeError as erro:
            raise CenaInvalida(f"TOML inválido: {erro}") from erro
        return cls.de_dict(dados)

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> Cenas:
        try:
            _chaves("o arquivo de cenas", dados, _CHAVES_RAIZ)
            tabela_cenas = dados.get("cenas", {})
            if not isinstance(tabela_cenas, dict):
                raise ValueError("'cenas' deveria ser uma tabela")
            cenas: dict[str, Cena] = {}
            _coletar(tabela_cenas, (), cenas)
            recusas = _recusas(dados.get("recusas"), obrigatorias=bool(cenas))
        except CenaInvalida:
            raise
        except ValueError as erro:
            raise CenaInvalida(str(erro)) from erro
        return cls(cenas, recusas)


def conferir_referencias(cenas: Cenas, roteiros: Mapping, dialogos: Mapping) -> None:
    """Levanta `CenaInvalida` se uma cena cita um roteiro ou diálogo que não existe."""
    faltando = [f"roteiro {nome!r}" for nome in sorted(cenas.roteiros_usados() - set(roteiros))]
    faltando += [f"diálogo {nome!r}" for nome in sorted(cenas.dialogos_usados() - set(dialogos))]
    if faltando:
        raise CenaInvalida(f"as cenas citam o que não existe: {', '.join(faltando)}")


# As funções abaixo levantam `ValueError`; `Cenas.de_dict` converte em `CenaInvalida`.


def _chaves(onde: str, tabela: dict[str, object], aceitas: frozenset[str]) -> None:
    extras = set(tabela) - aceitas
    if extras:
        raise ValueError(f"{onde}: chaves inesperadas {sorted(extras)}")


def _ids(onde: str, valor: object) -> frozenset[str]:
    if not isinstance(valor, list):
        raise ValueError(f"{onde}: deveria ser uma lista de IDs")
    try:
        return frozenset(validar_id(item) for item in valor)
    except ValueError as erro:
        raise ValueError(f"{onde}: {erro}") from None


def _recusas(dados: object, obrigatorias: bool) -> dict[Verbo, tuple[str, ...]]:
    if dados is None:
        if obrigatorias:
            raise ValueError("faltam as recusas genéricas: [recusas] com olhar, usar e falar")
        return {}
    if not isinstance(dados, dict):
        raise ValueError("'recusas' deveria ser uma tabela")
    _chaves("recusas", dados, frozenset(Verbo))
    recusas = {}
    for verbo in Verbo:
        lista = dados.get(verbo)
        if not isinstance(lista, list) or not lista:
            raise ValueError(f"recusas: '{verbo}' precisa de pelo menos um ID de texto")
        if len(_ids(f"recusas.{verbo}", lista)) != len(lista):
            raise ValueError(f"recusas: '{verbo}' tem IDs repetidos")
        recusas[verbo] = tuple(lista)
    return recusas


def _coletar(tabela: dict[str, object], caminho: tuple[str, ...], saida: dict[str, Cena]) -> None:
    for chave, valor in tabela.items():
        trecho = (*caminho, chave)
        nome = ".".join(trecho)
        if "." in chave:
            raise ValueError(f"ID inválido: {nome!r} (use tabelas aninhadas, não pontos)")
        validar_id(nome)
        if not isinstance(valor, dict):
            raise ValueError(f"valor solto em {nome!r}: uma cena é uma tabela com 'objetos'")
        if "objetos" in valor:
            saida[nome] = _cena(nome, valor)
        else:
            _coletar(valor, trecho, saida)


def _cena(id_cena: str, dados: dict[str, object]) -> Cena:
    onde = f"cena {id_cena!r}"
    _chaves(onde, dados, _CHAVES_CENA)
    lista = dados["objetos"]
    if not isinstance(lista, list) or not lista:
        raise ValueError(f"{onde}: 'objetos' precisa de pelo menos um objeto")
    objetos = tuple(_objeto(onde, numero, item) for numero, item in enumerate(lista, 1))
    ids = [objeto.id for objeto in objetos]
    repetidos = sorted({id_objeto for id_objeto in ids if ids.count(id_objeto) > 1})
    if repetidos:
        raise ValueError(f"{onde}: objetos repetidos {repetidos}")
    entrada = None
    if "entrada" in dados:
        entrada = _resposta(f"{onde}, entrada", dados["entrada"])
    return Cena(id=id_cena, objetos=objetos, entrada=entrada)


def _objeto(onde_cena: str, numero: int, dados: object) -> Objeto:
    onde = f"{onde_cena}, objeto {numero}"
    if not isinstance(dados, dict):
        raise ValueError(f"{onde}: um objeto é uma tabela")
    _chaves(onde, dados, _CHAVES_OBJETO)
    for obrigatoria in ("id", "nome", "area"):
        if obrigatoria not in dados:
            raise ValueError(f"{onde}: falta a chave {obrigatoria!r}")
    id_objeto = dados["id"]
    if not isinstance(id_objeto, str) or "." in id_objeto:
        raise ValueError(f"{onde}: id inválido {id_objeto!r}")
    try:
        validar_id(id_objeto)
        nome = validar_id(dados["nome"])
    except ValueError as erro:
        raise ValueError(f"{onde}: {erro}") from None
    onde = f"{onde_cena}, objeto {id_objeto!r}"

    area = dados["area"]
    if not isinstance(area, list) or len(area) != 4:
        raise ValueError(f"{onde}: 'area' deveria ser [x, y, largura, altura]")
    try:
        area = Area(*area)
    except ValueError as erro:
        raise ValueError(f"{onde}: {erro}") from None

    respostas = {
        verbo: _resposta(f"{onde}, {verbo}", dados[verbo]) for verbo in Verbo if verbo in dados
    }
    condicoes = {nome: _ids(f"{onde}, {nome}", dados.get(nome, [])) for nome in _CONDICOES}
    return Objeto(id=id_objeto, nome=nome, area=area, respostas=respostas, **condicoes)


def _resposta(onde: str, dados: object) -> Resposta:
    if isinstance(dados, list):
        if not dados:
            raise ValueError(f"{onde}: a lista de passos está vazia")
        return Resposta(passos=ler_passos(dados, onde))
    if isinstance(dados, dict) and len(dados) == 1:
        ((tipo, alvo),) = dados.items()
        if tipo in ("roteiro", "dialogo"):
            try:
                return Resposta(**{tipo: validar_id(alvo)})
            except ValueError as erro:
                raise ValueError(f"{onde}: {erro}") from None
    raise ValueError(f"{onde}: use uma lista de passos, {{ roteiro = ... }} ou {{ dialogo = ... }}")
