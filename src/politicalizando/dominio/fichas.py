"""Fichas das correntes: o mesmo modelo de 9 itens para todas (J3, D19, briefing seção 5).

Formato de `conteudo/fichas.toml` (os textos ficam no `textos.toml`, por ID):

    [fichas.liberalismo]
    se = ["biblioteca.bibliotecaria.posicao"]
    ideia_central = "ficha.liberalismo.ideia"
    valores = ["ficha.liberalismo.valor.1"]
    estado = "ficha.liberalismo.estado"
    mercado = "ficha.liberalismo.mercado"
    sociedade = "ficha.liberalismo.sociedade"
    origem = "ficha.liberalismo.origem"
    pensadores = ["ficha.liberalismo.pensador.1"]
    proposta = "ficha.liberalismo.proposta"
    confusoes = ["ficha.liberalismo.confusao.1"]
    diferencas_internas = [
      "ficha.liberalismo.vertente.1",
      "ficha.liberalismo.vertente.2",
    ]

    [[fichas.liberalismo.criticas]]
    texto = "ficha.liberalismo.critica.1"
    de = "socialismo"

    [[fichas.liberalismo.fontes]]
    autor = "Sobrenome, Nome"
    titulo = "Título da obra"
    ano = 1999
    editora = "Editora"

A chave da ficha é a corrente, então há no máximo uma por corrente. Todos os itens são
obrigatórios; as críticas vêm de pelo menos 2 origens diferentes (outras correntes ou
"outras", para críticas de fora das 4) e nunca da própria corrente; as diferenças internas
trazem pelo menos 2 vertentes, para mostrar que nenhuma corrente é um bloco único; toda ficha
tem fonte. A ficha aparece quando as flags de `se` estão marcadas, e as desbloqueadas saem
sempre na ordem fixa das correntes, nunca numa ordem que favoreça uma delas.
"""

from __future__ import annotations

import tomllib
from collections.abc import Iterator, Mapping
from dataclasses import dataclass

from politicalizando.dominio.correntes import CORRENTES, validar_corrente
from politicalizando.dominio.estado_jogo import EstadoJogo, validar_id
from politicalizando.dominio.fontes import Fonte, ler_fonte

# Crítica que vem de fora das 4 correntes da V1 (ex.: ecologismo, libertarianismo).
ORIGEM_EXTERNA = "outras"
MINIMO_ORIGENS_DE_CRITICA = 2
MINIMO_DE_VERTENTES = 2

_ITENS_TEXTO = ("ideia_central", "estado", "mercado", "sociedade", "origem", "proposta")
_ITENS_LISTA = ("valores", "pensadores", "confusoes", "diferencas_internas")
_CHAVES_FICHA = frozenset({*_ITENS_TEXTO, *_ITENS_LISTA, "criticas", "fontes", "se"})
_CHAVES_CRITICA = frozenset({"texto", "de"})


class FichaInvalida(ValueError):  # noqa: N818 - nomes em português, sem o sufixo "Error"
    """Arquivo de fichas malformado ou fora do modelo comum."""


@dataclass(frozen=True)
class Critica:
    texto: str
    de: str


@dataclass(frozen=True)
class Ficha:
    corrente: str
    ideia_central: str
    valores: tuple[str, ...]
    estado: str
    mercado: str
    sociedade: str
    origem: str
    pensadores: tuple[str, ...]
    proposta: str
    criticas: tuple[Critica, ...]
    confusoes: tuple[str, ...]
    # As vertentes da corrente e no que divergem (D19).
    diferencas_internas: tuple[str, ...]
    fontes: tuple[Fonte, ...]
    se: frozenset[str] = frozenset()

    def desbloqueada(self, estado: EstadoJogo) -> bool:
        return all(estado.tem_flag(flag) for flag in self.se)

    def ids_de_texto(self) -> tuple[str, ...]:
        """Os textos da ficha, na ordem do modelo."""
        return (
            self.ideia_central,
            *self.valores,
            self.estado,
            self.mercado,
            self.sociedade,
            self.origem,
            *self.pensadores,
            self.proposta,
            *(critica.texto for critica in self.criticas),
            *self.confusoes,
            *self.diferencas_internas,
        )


class Fichas(Mapping[str, Ficha]):
    """Catálogo das fichas, sempre na ordem fixa de `CORRENTES`."""

    def __init__(self, fichas: dict[str, Ficha] | None = None) -> None:
        fichas = fichas or {}
        self._fichas = {corrente: fichas[corrente] for corrente in CORRENTES if corrente in fichas}

    def __getitem__(self, corrente: str) -> Ficha:
        try:
            return self._fichas[corrente]
        except KeyError:
            raise KeyError(f"ficha inexistente: {corrente!r}") from None

    def __iter__(self) -> Iterator[str]:
        return iter(self._fichas)

    def __len__(self) -> int:
        return len(self._fichas)

    def desbloqueadas(self, estado: EstadoJogo) -> tuple[Ficha, ...]:
        return tuple(ficha for ficha in self.values() if ficha.desbloqueada(estado))

    def ids_de_texto(self) -> set[str]:
        return {id_texto for ficha in self.values() for id_texto in ficha.ids_de_texto()}

    def flags_exigidas(self) -> set[str]:
        return set().union(*(ficha.se for ficha in self.values()))

    @classmethod
    def de_toml(cls, conteudo: str) -> Fichas:
        try:
            dados = tomllib.loads(conteudo)
        except tomllib.TOMLDecodeError as erro:
            raise FichaInvalida(f"TOML inválido: {erro}") from erro
        return cls.de_dict(dados)

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> Fichas:
        try:
            extras = set(dados) - {"fichas"}
            if extras:
                raise ValueError(f"chaves inesperadas no arquivo de fichas: {sorted(extras)}")
            tabela = dados.get("fichas", {})
            if not isinstance(tabela, dict):
                raise ValueError("'fichas' deveria ser uma tabela")
            fichas = {}
            for corrente, valor in tabela.items():
                validar_corrente(corrente)
                fichas[corrente] = _ficha(corrente, valor)
        except ValueError as erro:
            raise FichaInvalida(str(erro)) from erro
        return cls(fichas)


# As funções abaixo levantam `ValueError`; `Fichas.de_dict` converte em `FichaInvalida`.


def _id(onde: str, valor: object) -> str:
    try:
        return validar_id(valor)
    except ValueError as erro:
        raise ValueError(f"{onde}: {erro}") from None


def _lista(onde: str, valor: object) -> list[object]:
    if not isinstance(valor, list) or not valor:
        raise ValueError(f"{onde}: deveria ser uma lista com pelo menos um item")
    return valor


def _ficha(corrente: str, dados: object) -> Ficha:
    onde = f"ficha {corrente!r}"
    if not isinstance(dados, dict):
        raise ValueError(f"{onde}: uma ficha é uma tabela")
    extras = set(dados) - _CHAVES_FICHA
    if extras:
        raise ValueError(f"{onde}: chaves inesperadas {sorted(extras)}")
    faltando = sorted(_CHAVES_FICHA - {"se"} - set(dados))
    if faltando:
        raise ValueError(f"{onde}: faltam itens do modelo {faltando}")

    textos = {nome: _id(f"{onde}, {nome}", dados[nome]) for nome in _ITENS_TEXTO}
    listas = {
        nome: tuple(_id(f"{onde}, {nome}", item) for item in _lista(f"{onde}, {nome}", dados[nome]))
        for nome in _ITENS_LISTA
    }
    if len(set(listas["diferencas_internas"])) < MINIMO_DE_VERTENTES:
        raise ValueError(
            f"{onde}: as diferenças internas precisam de pelo menos {MINIMO_DE_VERTENTES} "
            "vertentes diferentes"
        )
    criticas = tuple(
        _critica(corrente, f"{onde}, crítica {numero}", item)
        for numero, item in enumerate(_lista(f"{onde}, criticas", dados["criticas"]), 1)
    )
    origens = {critica.de for critica in criticas}
    if len(origens) < MINIMO_ORIGENS_DE_CRITICA:
        raise ValueError(
            f"{onde}: as críticas precisam vir de pelo menos {MINIMO_ORIGENS_DE_CRITICA} "
            f"origens diferentes (há {sorted(origens)})"
        )
    fontes = tuple(
        ler_fonte(item, f"{onde}, fonte {numero}")
        for numero, item in enumerate(_lista(f"{onde}, fontes", dados["fontes"]), 1)
    )
    if any(fonte.do_jogo for fonte in fontes):
        raise ValueError(f"{onde}: as fichas falam do mundo real e não usam fontes do jogo")
    se = dados.get("se", [])
    if not isinstance(se, list):
        raise ValueError(f"{onde}, se: deveria ser uma lista de flags")
    flags = frozenset(_id(f"{onde}, se", flag) for flag in se)
    return Ficha(corrente=corrente, criticas=criticas, fontes=fontes, se=flags, **textos, **listas)


def _critica(corrente: str, onde: str, dados: object) -> Critica:
    if not isinstance(dados, dict):
        raise ValueError(f"{onde}: uma crítica é uma tabela com 'texto' e 'de'")
    if set(dados) != _CHAVES_CRITICA:
        raise ValueError(f"{onde}: use exatamente as chaves 'texto' e 'de'")
    de = dados["de"]
    if de == corrente:
        raise ValueError(f"{onde}: a crítica não pode vir da própria corrente")
    if de != ORIGEM_EXTERNA and de not in CORRENTES:
        raise ValueError(f"{onde}: origem desconhecida {de!r} (use outra corrente ou 'outras')")
    return Critica(texto=_id(onde, dados["texto"]), de=de)
